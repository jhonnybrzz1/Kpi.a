import unittest
from services.schemas import ContextAnalysis

class TestAccentNormalization(unittest.TestCase):
    def test_normalize_accented_fields(self):
        data = {
            "tipo": "Estratégia",
            "objetivo": "Retenção",
            "etapa_funil": "Aquisição",
            "complexidade": "Média"
        }
        obj = ContextAnalysis(**data)
        self.assertEqual(obj.tipo, "estrategia")
        self.assertEqual(obj.objetivo, "retencao")
        self.assertEqual(obj.etapa_funil, "aquisicao")
        self.assertEqual(obj.complexidade, "media")

    def test_lowercase_normalization(self):
        data = {
            "tipo": "PRODUTO",
            "business_game": "TRANSACTION"
        }
        obj = ContextAnalysis(**data)
        self.assertEqual(obj.tipo, "produto")
        self.assertEqual(obj.business_game, "transaction")

if __name__ == "__main__":
    unittest.main()
