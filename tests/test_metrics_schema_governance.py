import os
import sys
import unittest

from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.schemas import MetricsAnalysis


def valid_metrics_payload():
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
            "nome": "Contas ativadas por mês",
            "definicao": "COUNT(DISTINCT account_id) com primeira ação concluída no mês",
            "justificativa": "Mede valor entregue recorrente",
            "validacao_smart": ["específica", "mensurável"],
        },
        "l1_health_indicators": [
            {
                "pilar": pillar,
                "metrica": metric,
                "meta_sugerida": "10%",
                "por_que_importa": "Explica a saúde do funil",
            }
            for pillar, metric in l1
        ],
        "l2_diagnostic_metrics": [
            {
                "vinculo_l1": metric,
                "metrica": f"Diagnóstico de {metric}",
                "acao_se_cair": "Investigar causa raiz",
            }
            for _pillar, metric in l1
        ],
        "counter_metrics": [
            {
                "nome": "Taxa de erro",
                "protege_contra": "Crescer uso com baixa qualidade",
                "trade_off": "Pode reduzir velocidade",
            }
        ],
        "okrs": [
            {
                "objetivo": "Aumentar ativação com qualidade",
                "key_results": [
                    {"resultado": "Ativação", "baseline": "40%", "meta": "60%"},
                    {"resultado": "Erro", "baseline": 5, "meta": 2},
                ],
            }
        ],
        "implementacao": {
            "ferramentas": ["BigQuery"],
            "queries_exemplo": ["SELECT 1"],
            "visualizacao": "Dashboard por pilar",
        },
        "riscos_e_vieses": ["Viés de seleção"],
    }


class TestMetricsSchemaGovernance(unittest.TestCase):
    def test_valid_payload_passes(self):
        result = MetricsAnalysis.model_validate(valid_metrics_payload())
        self.assertEqual(len(result.l1_health_indicators), 6)

    def test_rejects_placeholder_baseline(self):
        payload = valid_metrics_payload()
        payload["okrs"][0]["key_results"][0]["baseline"] = "a_definir_com_3_execucoes"

        with self.assertRaises(ValidationError) as ctx:
            MetricsAnalysis.model_validate(payload)

        self.assertIn("placeholder", str(ctx.exception))

    def test_rejects_non_numeric_target(self):
        payload = valid_metrics_payload()
        payload["okrs"][0]["key_results"][0]["meta"] = "aumentar engajamento"

        with self.assertRaises(ValidationError) as ctx:
            MetricsAnalysis.model_validate(payload)

        self.assertIn("numeric", str(ctx.exception))

    def test_rejects_missing_required_pillar(self):
        payload = valid_metrics_payload()
        payload["l1_health_indicators"] = [
            item for item in payload["l1_health_indicators"] if item["pilar"] != "Monetization"
        ]

        with self.assertRaises(ValidationError) as ctx:
            MetricsAnalysis.model_validate(payload)

        self.assertIn("6 required pillars", str(ctx.exception))

    def test_rejects_l1_without_l2(self):
        payload = valid_metrics_payload()
        payload["l2_diagnostic_metrics"] = [
            item
            for item in payload["l2_diagnostic_metrics"]
            if item["vinculo_l1"] != "CSAT pós-uso"
        ]

        with self.assertRaises(ValidationError) as ctx:
            MetricsAnalysis.model_validate(payload)

        self.assertIn("every L1 metric", str(ctx.exception))

    def test_rejects_orphan_l2_link(self):
        payload = valid_metrics_payload()
        payload["l2_diagnostic_metrics"][0]["vinculo_l1"] = "métrica inexistente"

        with self.assertRaises(ValidationError) as ctx:
            MetricsAnalysis.model_validate(payload)

        self.assertIn("unknown L1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
