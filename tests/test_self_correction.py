import json
import unittest
from unittest.mock import MagicMock

from services.openai_service import OpenAIService


def _openai_sdk_response(payload_content: str):
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = payload_content
    resp.usage.prompt_tokens = 10
    resp.usage.completion_tokens = 20
    resp.usage.total_tokens = 30
    return resp


def _valid_metrics(justificativa: str = "Draft J"):
    l1 = [
        ("Acquisition", "visitantes qualificados"),
        ("Activation", "signup → first action"),
        ("Engagement", "ações por usuário ativo"),
        ("Retention", "retenção D30"),
        ("Monetization", "receita por conta ativa"),
        ("Satisfaction", "CSAT pós-uso"),
    ]
    return {
        "north_star": {
            "nome": "NS",
            "definicao": "COUNT(DISTINCT account_id)",
            "justificativa": justificativa,
            "validacao_smart": ["mensurável"],
        },
        "l1_health_indicators": [
            {
                "pilar": pillar,
                "metrica": metric,
                "meta_sugerida": "10%",
                "por_que_importa": "saúde do funil",
            }
            for pillar, metric in l1
        ],
        "l2_diagnostic_metrics": [
            {
                "vinculo_l1": metric,
                "metrica": f"Diagnóstico de {metric}",
                "acao_se_cair": "investigar",
            }
            for _pillar, metric in l1
        ],
        "counter_metrics": [
            {"nome": "Taxa de erro", "protege_contra": "baixa qualidade", "trade_off": "velocidade"}
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
            "visualizacao": "Dashboard",
        },
        "riscos_e_vieses": ["seleção"],
    }


class TestSelfCorrectionLoop(unittest.TestCase):
    def setUp(self):
        self.svc = OpenAIService.__new__(OpenAIService)
        self.svc.api_key = "test"
        self.svc.model = "gpt-test"
        self.svc.client = MagicMock()

    def test_refinement_triggered_on_low_score(self):
        draft = _valid_metrics()

        review_low = {"score": 0.4, "aprovado": False, "criticas": ["Melhore os KRs"]}
        refined = _valid_metrics("Refined J")

        self.svc.client.chat.completions.create.side_effect = [
            _openai_sdk_response(json.dumps(draft)),  # 1. Draft
            _openai_sdk_response(json.dumps(review_low)),  # 2. Review
            _openai_sdk_response(json.dumps(refined)),  # 3. Refinement
        ]

        result = self.svc.generate_metrics("init", {})

        self.assertEqual(self.svc.client.chat.completions.create.call_count, 3)
        self.assertEqual(result["north_star"]["justificativa"], "Refined J")


if __name__ == "__main__":
    unittest.main()
