"""
Tests for the low-temperature recovery path added to both LLM services.

Both `MistralService.analyze_context` and `OpenAIService.generate_metrics`
re-prompt ONCE with a lower temperature when the first response fails to
parse or fails Pydantic validation. The outer retry_with_backoff continues
to cover network errors.

These tests stub the HTTP/SDK layer so we can verify:
- happy path: only one upstream call, primary temperature used
- recovery path: two upstream calls; second uses the recovery temperature;
  call still succeeds end-to-end
- double-failure path: both attempts fail to validate → exception escapes
  so the outer retry_with_backoff can take over
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.mistral_service import MistralService
from services.openai_service import OpenAIService

# ── Fixtures ────────────────────────────────────────────────────────────────

VALID_CONTEXT = {
    "tipo": "funcionalidade",
    "business_game": "productivity",
    "objetivo": "engajamento",
    "etapa_funil": "ativacao",
    "complexidade": "media",
    "area_impacto": ["produto"],
    "valor_entregue": "Melhora UX",
    "resumo_prd": "Resumo válido",
    "dados_atuais": "Não mencionado",
    "justificativa": "ok",
    "palavras_chave": ["ux"],
    "confidence": 0.9,
}

INVALID_CONTEXT_OUT_OF_TAXONOMY = {
    # tipo="outro" is NOT in the Literal taxonomy → triggers ValidationError
    "tipo": "outro",
    "objetivo": "engajamento",
}

VALID_METRICS = {
    "north_star": {
        "nome": "Active users / mês",
        "definicao": "COUNT(DISTINCT user_id)",
        "justificativa": "outcome único",
        "validacao_smart": ["mensurável"],
    },
    "l1_health_indicators": [
        {
            "pilar": "Activation",
            "metrica": "signup → first action",
            "meta_sugerida": "60%",
            "por_que_importa": "indica ativação",
        },
        {
            "pilar": "Acquisition",
            "metrica": "visitantes qualificados",
            "meta_sugerida": "1000",
            "por_que_importa": "mede topo de funil",
        },
        {
            "pilar": "Engagement",
            "metrica": "ações por usuário ativo",
            "meta_sugerida": "5",
            "por_que_importa": "mede uso recorrente",
        },
        {
            "pilar": "Retention",
            "metrica": "retenção D30",
            "meta_sugerida": "40%",
            "por_que_importa": "mede retorno",
        },
        {
            "pilar": "Monetization",
            "metrica": "receita por conta ativa",
            "meta_sugerida": "100",
            "por_que_importa": "mede captura de valor",
        },
        {
            "pilar": "Satisfaction",
            "metrica": "CSAT pós-uso",
            "meta_sugerida": "4.5",
            "por_que_importa": "mede satisfação",
        }
    ],
    "l2_diagnostic_metrics": [
        {
            "vinculo_l1": "signup → first action",
            "metrica": "tempo até first action",
            "acao_se_cair": "investigar onboarding",
        },
        {
            "vinculo_l1": "visitantes qualificados",
            "metrica": "taxa de origem qualificada",
            "acao_se_cair": "revisar canais",
        },
        {
            "vinculo_l1": "ações por usuário ativo",
            "metrica": "ações por sessão",
            "acao_se_cair": "revisar fluxo principal",
        },
        {
            "vinculo_l1": "retenção D30",
            "metrica": "retenção D7",
            "acao_se_cair": "investigar ativação",
        },
        {
            "vinculo_l1": "receita por conta ativa",
            "metrica": "conversão para plano pago",
            "acao_se_cair": "revisar oferta",
        },
        {
            "vinculo_l1": "CSAT pós-uso",
            "metrica": "comentários negativos",
            "acao_se_cair": "analisar feedback",
        }
    ],
    "counter_metrics": [
        {"nome": "tickets de suporte", "protege_contra": "complexidade", "trade_off": "custo"}
    ],
    "okrs": [
        {
            "objetivo": "Aumentar ativação",
            "key_results": [{"resultado": "ativação", "baseline": 40, "meta": 60}],
        }
    ],
    "implementacao": {
        "ferramentas": ["BigQuery"],
        "queries_exemplo": ["SELECT 1"],
        "visualizacao": "Looker",
    },
    "riscos_e_vieses": ["seleção"],
}


# ── Mistral ─────────────────────────────────────────────────────────────────


def _make_mistral_service():
    svc = MistralService.__new__(MistralService)
    svc.api_key = "test"
    svc.base_url = "https://api.mistral.ai/v1/chat/completions"
    svc.model = "mistral-test"
    return svc


def _mistral_http_response(payload_content: str, status: int = 200):
    """Build a fake requests.Response."""
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {
        "choices": [{"message": {"content": payload_content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }
    resp.text = payload_content
    return resp


class TestMistralLowTempRecovery(unittest.TestCase):
    def setUp(self):
        self.svc = _make_mistral_service()

    @patch("services.mistral_service.requests.post")
    def test_happy_path_uses_primary_temp_only(self, mock_post):
        import json

        mock_post.return_value = _mistral_http_response(json.dumps(VALID_CONTEXT))

        result = self.svc.analyze_context("Adicionar 2FA.")

        self.assertEqual(mock_post.call_count, 1)
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent["temperature"], 0.3)
        self.assertEqual(result["tipo"], "funcionalidade")
        self.assertEqual(result["confidence"], 0.9)

    @patch("services.mistral_service.requests.post")
    def test_recovery_path_drops_to_zero_on_validation_error(self, mock_post):
        import json

        # First call returns out-of-taxonomy → Pydantic ValidationError.
        # Second call returns a valid payload.
        mock_post.side_effect = [
            _mistral_http_response(json.dumps(INVALID_CONTEXT_OUT_OF_TAXONOMY)),
            _mistral_http_response(json.dumps(VALID_CONTEXT)),
        ]

        result = self.svc.analyze_context("Iniciativa qualquer.")

        self.assertEqual(mock_post.call_count, 2)
        # Primary attempt used 0.3, recovery used 0.0
        self.assertEqual(mock_post.call_args_list[0].kwargs["json"]["temperature"], 0.3)
        self.assertEqual(mock_post.call_args_list[1].kwargs["json"]["temperature"], 0.0)
        self.assertEqual(result["tipo"], "funcionalidade")

    @patch("services.mistral_service.requests.post")
    @patch("utils.retry.time.sleep")  # short-circuit backoff sleeps
    def test_double_failure_propagates(self, _mock_sleep, mock_post):
        """If both attempts return invalid taxonomy, exception must escape."""
        import json

        # retry_with_backoff wraps analyze_context with max_retries=3. Each
        # invocation does primary + recovery = 2 HTTP calls. So we need
        # 2 × 3 = 6 fake responses before the outer wrapper gives up.
        mock_post.side_effect = [
            _mistral_http_response(json.dumps(INVALID_CONTEXT_OUT_OF_TAXONOMY))
        ] * 6

        with self.assertRaises(Exception) as ctx:
            self.svc.analyze_context("Iniciativa.")
        self.assertIn("failed parse/validate twice", str(ctx.exception))
        self.assertEqual(mock_post.call_count, 6)


# ── OpenAI / OpenRouter ─────────────────────────────────────────────────────


def _make_openai_service():
    svc = OpenAIService.__new__(OpenAIService)
    svc.api_key = "test"
    svc.model = "gpt-test"
    svc.client = MagicMock()
    return svc


def _openai_sdk_response(payload_content: str):
    """Build a fake openai SDK ChatCompletion-like response."""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = payload_content
    resp.usage.prompt_tokens = 10
    resp.usage.completion_tokens = 20
    resp.usage.total_tokens = 30
    return resp


class TestOpenAILowTempRecovery(unittest.TestCase):
    def setUp(self):
        self.svc = _make_openai_service()

    def test_happy_path_uses_primary_temp_only(self):
        import json

        # Mock both the generation call and the review call
        self.svc.client.chat.completions.create.side_effect = [
            _openai_sdk_response(json.dumps(VALID_METRICS)),
            _openai_sdk_response(json.dumps({"aprovado": True, "score": 1.0, "criticas": []}))
        ]

        result = self.svc.generate_metrics("Iniciativa qualquer.", VALID_CONTEXT)

        # 1 for generation + 1 for review = 2
        self.assertEqual(self.svc.client.chat.completions.create.call_count, 2)
        call_kwargs = self.svc.client.chat.completions.create.call_args_list[0].kwargs
        self.assertEqual(call_kwargs["temperature"], 0.4)
        self.assertIn("north_star", result)

    def test_recovery_path_drops_temperature_on_invalid_schema(self):
        import json

        # First response: missing required field `okrs` → ValidationError.
        # Second response: valid.
        # Third response: review (aprovado=True).
        invalid = {k: v for k, v in VALID_METRICS.items() if k != "okrs"}
        self.svc.client.chat.completions.create.side_effect = [
            _openai_sdk_response(json.dumps(invalid)),
            _openai_sdk_response(json.dumps(VALID_METRICS)),
            _openai_sdk_response(json.dumps({"aprovado": True, "score": 1.0, "criticas": []}))
        ]

        result = self.svc.generate_metrics("Iniciativa qualquer.", VALID_CONTEXT)

        # 2 for generation attempts + 1 for review = 3
        self.assertEqual(self.svc.client.chat.completions.create.call_count, 3)
        first_temp = self.svc.client.chat.completions.create.call_args_list[0].kwargs[
            "temperature"
        ]
        second_temp = self.svc.client.chat.completions.create.call_args_list[1].kwargs[
            "temperature"
        ]
        self.assertEqual(first_temp, 0.4)
        self.assertEqual(second_temp, 0.1)
        self.assertEqual(len(result["okrs"]), 1)

    @patch("utils.retry.time.sleep")  # short-circuit backoff sleeps
    def test_double_failure_propagates(self, _mock_sleep):
        import json

        invalid = {k: v for k, v in VALID_METRICS.items() if k != "okrs"}
        # 2 invalid per attempt × 3 outer retries = 6 SDK calls before raising
        self.svc.client.chat.completions.create.side_effect = [
            _openai_sdk_response(json.dumps(invalid))
        ] * 6

        with self.assertRaises(Exception) as ctx:
            self.svc.generate_metrics("Iniciativa.", VALID_CONTEXT)
        self.assertIn("Metrics generation failed parse/validate twice", str(ctx.exception))
        self.assertEqual(self.svc.client.chat.completions.create.call_count, 6)


if __name__ == "__main__":
    unittest.main()
