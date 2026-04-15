"""
Unit tests for Mistral service
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.mistral_service import MistralService


class TestMistralServiceJSONExtraction(unittest.TestCase):
    """Test cases for MistralService JSON extraction"""

    def test_extract_json_from_valid_json(self):
        """Test extraction from valid JSON text"""
        service = MistralService.__new__(MistralService)
        service.api_key = "test_key"

        text = '{"tipo": "produto", "objetivo": "retencao"}'
        result = service._extract_json_from_text(text)

        self.assertEqual(result["tipo"], "produto")
        self.assertEqual(result["objetivo"], "retencao")

    def test_extract_json_from_text_with_prefix(self):
        """Test extraction from text with JSON embedded"""
        service = MistralService.__new__(MistralService)
        service.api_key = "test_key"

        text = 'Here is the analysis:\n\n{"tipo": "funcionalidade", "objetivo": "aquisicao"}'
        result = service._extract_json_from_text(text)

        self.assertEqual(result["tipo"], "funcionalidade")

    def test_extract_json_fallback(self):
        """Test fallback to default structure on failure"""
        service = MistralService.__new__(MistralService)
        service.api_key = "test_key"

        text = "No JSON here"
        result = service._extract_json_from_text(text)

        # Should return default structure
        self.assertEqual(result["tipo"], "funcionalidade")
        self.assertEqual(result["objetivo"], "operacao")
        self.assertIn("tecnologia", result["area_impacto"])

    def test_extract_json_with_markdown_block(self):
        """Test extraction from markdown code block"""
        service = MistralService.__new__(MistralService)
        service.api_key = "test_key"

        text = '```json\n{"tipo": "processo", "complexidade": "alta"}\n```'
        result = service._extract_json_from_text(text)

        self.assertEqual(result["tipo"], "processo")
        self.assertEqual(result["complexidade"], "alta")


if __name__ == "__main__":
    unittest.main()
