"""
Regression tests for executive_summary integration and PDF generation
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.pdf_generator import PDFGenerator

SAMPLE_CONTEXT = {
    "tipo": "funcionalidade",
    "business_game": "productivity",
    "objetivo": "retencao",
    "etapa_funil": "retencao",
    "resumo_prd": "Teste",
    "dados_atuais": {},
    "justificativa": "",
}
SAMPLE_METRICS = {
    "north_star": {
        "nome": "NSM",
        "definicao": "formula",
        "justificativa": "why",
        "validacao_smart": [],
    },
    "l1_health_indicators": [],
    "l2_diagnostic_metrics": [],
    "counter_metrics": [],
    "okrs": [],
    "implementacao": {"ferramentas": [], "queries_exemplo": [], "visualizacao": ""},
    "riscos_e_vieses": [],
}


def _base_report_data(executive_summary=""):
    return {
        "date": "09/05/2026",
        "responsible": "Dev",
        "company": "Acme",
        "context_analysis": SAMPLE_CONTEXT,
        "metrics_analysis": SAMPLE_METRICS,
        "executive_summary": executive_summary,
    }


class TestPDFGeneratorExecutiveSummary(unittest.TestCase):
    """Tests for executive_summary rendering in PDFGenerator"""

    def setUp(self):
        self.gen = PDFGenerator()

    def test_render_executive_summary_with_text(self):
        """Summary present → rendered as HTML block"""
        result = self.gen._render_executive_summary("Este é o resumo executivo.")
        self.assertIn("Resumo Executivo", result)
        self.assertIn("Este é o resumo executivo.", result)

    def test_render_executive_summary_empty_string(self):
        """Empty summary → returns empty string (no block rendered)"""
        self.assertEqual(self.gen._render_executive_summary(""), "")

    def test_render_executive_summary_whitespace_only(self):
        """Whitespace-only summary → returns empty string"""
        self.assertEqual(self.gen._render_executive_summary("   "), "")

    def test_render_executive_summary_none(self):
        """None summary → returns empty string"""
        self.assertEqual(self.gen._render_executive_summary(None), "")

    def test_template_placeholder_replaced(self):
        """{{EXECUTIVE_SUMMARY}} placeholder is always replaced in rendered HTML"""
        with open(self.gen.template_path, "r", encoding="utf-8") as f:
            template = f.read()
        rendered = self.gen._render_template(template, _base_report_data("Resumo aqui."))
        self.assertNotIn("{{EXECUTIVE_SUMMARY}}", rendered)
        self.assertIn("Resumo aqui.", rendered)

    def test_template_placeholder_replaced_when_empty(self):
        """{{EXECUTIVE_SUMMARY}} placeholder replaced even when summary is absent"""
        with open(self.gen.template_path, "r", encoding="utf-8") as f:
            template = f.read()
        rendered = self.gen._render_template(template, _base_report_data(""))
        self.assertNotIn("{{EXECUTIVE_SUMMARY}}", rendered)


class TestPDFGenerationRegressionWithoutSummary(unittest.TestCase):
    """PDF must generate successfully even when executive_summary is absent"""

    def setUp(self):
        self.gen = PDFGenerator()

    def _generate(self, data):
        """Helper: generate PDF and return bytes (raises on failure)"""
        return self.gen.generate_report(data)

    def test_pdf_generates_with_summary(self):
        """Happy path: PDF generates when executive_summary is present"""
        pdf = self._generate(_base_report_data("Resumo executivo completo."))
        self.assertIsInstance(pdf, bytes)
        self.assertGreater(len(pdf), 0)

    def test_pdf_generates_without_summary_key(self):
        """Regression: PDF generates when executive_summary key is absent from report_data"""
        data = _base_report_data()
        del data["executive_summary"]
        pdf = self._generate(data)
        self.assertIsInstance(pdf, bytes)
        self.assertGreater(len(pdf), 0)

    def test_pdf_generates_with_empty_summary(self):
        """Regression: PDF generates when executive_summary is empty string"""
        pdf = self._generate(_base_report_data(""))
        self.assertIsInstance(pdf, bytes)
        self.assertGreater(len(pdf), 0)


class TestExecutiveSummaryFlowGuard(unittest.TestCase):
    """Guard logic: summary is skipped when context/metrics are falsy"""

    def _run_guard(self, context, metrics, mock_service):
        """Replicates the guard logic from app.py"""
        executive_summary = ""
        if context and metrics:
            try:
                executive_summary = mock_service.generate_executive_summary(
                    "input", context, metrics
                )
            except Exception:
                pass
        return executive_summary

    def test_summary_called_when_context_and_metrics_present(self):
        svc = MagicMock()
        svc.generate_executive_summary.return_value = "Resumo gerado."
        result = self._run_guard(SAMPLE_CONTEXT, SAMPLE_METRICS, svc)
        svc.generate_executive_summary.assert_called_once()
        self.assertEqual(result, "Resumo gerado.")

    def test_summary_skipped_when_context_is_none(self):
        svc = MagicMock()
        result = self._run_guard(None, SAMPLE_METRICS, svc)
        svc.generate_executive_summary.assert_not_called()
        self.assertEqual(result, "")

    def test_summary_skipped_when_metrics_is_none(self):
        svc = MagicMock()
        result = self._run_guard(SAMPLE_CONTEXT, None, svc)
        svc.generate_executive_summary.assert_not_called()
        self.assertEqual(result, "")

    def test_summary_empty_on_service_failure(self):
        """If generate_executive_summary raises, summary is empty and PDF flow continues"""
        svc = MagicMock()
        svc.generate_executive_summary.side_effect = Exception("API timeout")
        result = self._run_guard(SAMPLE_CONTEXT, SAMPLE_METRICS, svc)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
