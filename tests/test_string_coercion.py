import unittest
import json
from services.schemas import ContextAnalysis

class TestStringCoercion(unittest.TestCase):
    def test_coerce_dict_to_string(self):
        data = {
            "tipo": "funcionalidade",
            "dados_atuais": {"key": "value", "list": [1, 2]}
        }
        obj = ContextAnalysis(**data)
        # Should be a JSON string
        self.assertIsInstance(obj.dados_atuais, str)
        parsed = json.loads(obj.dados_atuais)
        self.assertEqual(parsed["key"], "value")

    def test_coerce_list_to_string(self):
        data = {
            "tipo": "funcionalidade",
            "palavras_chave": ["a", "b"],
            "justificativa": ["ponto 1", "ponto 2"]
        }
        obj = ContextAnalysis(**data)
        self.assertIsInstance(obj.justificativa, str)
        self.assertIn("ponto 1", obj.justificativa)

if __name__ == "__main__":
    unittest.main()
