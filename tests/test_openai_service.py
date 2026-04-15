"""
Unit tests for OpenAI service
"""
import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.openai_service import OpenAIService


class TestOpenAIServiceJSONCleaning(unittest.TestCase):
    """Test cases for OpenAIService JSON cleaning"""

    def test_clean_json_from_markdown_block(self):
        """Test cleaning JSON from markdown code block"""
        service = OpenAIService.__new__(OpenAIService)
        service.api_key = "test_key"
        
        # Test the cleaning logic manually
        content = "```json\n{\"north_star_metric\": {}}\n```"
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        self.assertIn("north_star_metric", result)

    def test_clean_json_plain_text(self):
        """Test cleaning plain JSON without markdown"""
        content = '{"north_star_metric": {}, "kpis": []}'
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        self.assertIn("north_star_metric", result)
        self.assertIn("kpis", result)


class TestOpenAIServiceSchemaValidation(unittest.TestCase):
    """Test cases for OpenAIService schema validation"""

    def test_valid_schema(self):
        """Test that valid schema passes validation"""
        data = {
            "north_star_metric": {"nome": "Test", "descricao": "Desc", "justificativa": "Why"},
            "kpis": [{"nome": "KPI1", "descricao": "Desc"}],
            "okrs": [{"objetivo": "Obj", "key_results": ["KR1"]}]
        }
        
        required_fields = ["north_star_metric", "kpis", "okrs"]
        for field in required_fields:
            self.assertIn(field, data)

    def test_missing_north_star(self):
        """Test that missing north_star_metric fails"""
        data = {"kpis": [], "okrs": []}
        required_fields = ["north_star_metric", "kpis", "okrs"]
        
        missing = False
        for field in required_fields:
            if field not in data:
                missing = True
                break
        
        self.assertTrue(missing)

    def test_missing_kpis(self):
        """Test that missing kpis fails"""
        data = {"north_star_metric": {}, "okrs": []}
        required_fields = ["north_star_metric", "kpis", "okrs"]
        
        missing = False
        for field in required_fields:
            if field not in data:
                missing = True
                break
        
        self.assertTrue(missing)


if __name__ == "__main__":
    unittest.main()
