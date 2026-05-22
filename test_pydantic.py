from services.schemas import ContextAnalysis
from pydantic import ValidationError
import json

data = {
    "tipo": "estratégia",  # Com acento, deve falhar
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
    "confidence": 0.9
}

try:
    ContextAnalysis.model_validate(data)
    print("Validation OK")
except ValidationError as e:
    print(f"Validation Error: {e}")
