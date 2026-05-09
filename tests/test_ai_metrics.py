"""Tests for utils/ai_metrics.py — validate_json_structure, record_call, get_metrics_summary."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Redirect DB to a temp file for tests
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
import utils.ai_metrics as _mod

_mod._DB_PATH = _tmp.name

from utils.ai_metrics import get_metrics_summary, record_call, validate_json_structure


class TestValidateJsonStructure(unittest.TestCase):
    def test_valid_context_analysis(self):
        raw = '{"tipo":"produto","objetivo":"retencao","etapa_funil":"ativacao","resumo_prd":"ok"}'
        r = validate_json_structure(raw, "context_analysis")
        self.assertTrue(r["json_valid"])
        self.assertIsNone(r["json_error_type"])

    def test_valid_metrics_analysis(self):
        raw = '{"north_star":{},"l1_health_indicators":[],"okrs":[]}'
        r = validate_json_structure(raw, "metrics_analysis")
        self.assertTrue(r["json_valid"])

    def test_parse_error(self):
        r = validate_json_structure("{broken json", "metrics_analysis")
        self.assertFalse(r["json_valid"])
        self.assertEqual(r["json_error_type"], "parse_error")

    def test_missing_field(self):
        raw = '{"north_star":{}}'  # missing l1_health_indicators and okrs
        r = validate_json_structure(raw, "metrics_analysis")
        self.assertFalse(r["json_valid"])
        self.assertEqual(r["json_error_type"], "missing_field")

    def test_type_error_not_dict(self):
        r = validate_json_structure("[1,2,3]", "metrics_analysis")
        self.assertFalse(r["json_valid"])
        self.assertEqual(r["json_error_type"], "type_error")

    def test_type_error_null_field(self):
        raw = '{"north_star":null,"l1_health_indicators":[],"okrs":[]}'
        r = validate_json_structure(raw, "metrics_analysis")
        self.assertFalse(r["json_valid"])
        self.assertEqual(r["json_error_type"], "type_error")

    def test_empty_string_is_parse_error(self):
        r = validate_json_structure("", "metrics_analysis")
        self.assertFalse(r["json_valid"])
        self.assertEqual(r["json_error_type"], "parse_error")


class TestRecordCall(unittest.TestCase):
    def test_returns_operation_id(self):
        op_id = record_call(model="m", provider="p", latency_ms=100, json_valid=True)
        self.assertIsInstance(op_id, str)
        self.assertEqual(len(op_id), 36)  # UUID v4

    def test_records_with_usage(self):
        op_id = record_call(
            model="gpt-4",
            provider="openai",
            latency_ms=500,
            json_valid=True,
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        )
        self.assertIsNotNone(op_id)

    def test_records_without_usage(self):
        op_id = record_call(
            model="mistral",
            provider="mistral",
            latency_ms=300,
            json_valid=False,
            json_error_type="parse_error",
        )
        self.assertIsNotNone(op_id)


class TestGetMetricsSummary(unittest.TestCase):
    def setUp(self):
        # Insert known records
        record_call(
            model="test-model",
            provider="test",
            latency_ms=200,
            json_valid=True,
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        )
        record_call(
            model="test-model",
            provider="test",
            latency_ms=400,
            json_valid=False,
            json_error_type="missing_field",
        )
        record_call(
            model="test-model",
            provider="test",
            latency_ms=300,
            json_valid=True,
            usage={"prompt_tokens": 200, "completion_tokens": 80, "total_tokens": 280},
        )

    def test_summary_structure(self):
        s = get_metrics_summary(days=7)
        self.assertIn("lastUpdated", s)
        self.assertIn("byModel", s)
        self.assertIn("windowDays", s)

    def test_total_calls_counted(self):
        s = get_metrics_summary(days=7)
        model_row = next((r for r in s["byModel"] if r["model"] == "test-model"), None)
        self.assertIsNotNone(model_row)
        self.assertGreaterEqual(model_row["totalCalls"], 3)

    def test_invalid_json_rate(self):
        s = get_metrics_summary(days=7)
        model_row = next(r for r in s["byModel"] if r["model"] == "test-model")
        # 1 invalid out of 3 = ~0.333
        self.assertGreater(model_row["invalidJsonRate"], 0)
        self.assertLessEqual(model_row["invalidJsonRate"], 1.0)

    def test_token_coverage_rate(self):
        s = get_metrics_summary(days=7)
        model_row = next(r for r in s["byModel"] if r["model"] == "test-model")
        # 2 out of 3 have usage
        self.assertGreater(model_row["tokenCoverageRate"], 0)

    def test_empty_window_returns_empty_list_or_zero(self):
        s = get_metrics_summary(days=0)
        # Either no rows or all zeros — must not raise
        self.assertIsInstance(s["byModel"], list)


if __name__ == "__main__":
    unittest.main()
