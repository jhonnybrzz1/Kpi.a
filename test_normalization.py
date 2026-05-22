from typing import Literal, Annotated
from pydantic import BaseModel, Field, field_validator, BeforeValidator
import unicodedata

def normalize_text(v: str) -> str:
    if not isinstance(v, str):
        return v
    # Remove acentos e converte para minúsculas
    nksf = unicodedata.normalize('NFKD', v)
    return "".join([c for c in nksf if not unicodedata.combining(c)]).lower()

NormalizedStr = Annotated[str, BeforeValidator(normalize_text)]

TipoIniciativa = Literal["funcionalidade", "processo", "produto", "estrategia"]

class ContextAnalysis(BaseModel):
    tipo: Annotated[TipoIniciativa, BeforeValidator(normalize_text)]

try:
    obj = ContextAnalysis(tipo="Estratégia")
    print(f"Success: {obj.tipo}")
except Exception as e:
    print(f"Error: {e}")
