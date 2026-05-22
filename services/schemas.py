"""Pydantic schemas for API response validation - Otimizado para PRD e Markdown"""

import re
import unicodedata
from typing import Annotated, Any, List, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator, model_validator


def normalize_taxonomy(v: Any) -> Any:
    """Normalize strings by removing accents and converting to lowercase."""
    if not isinstance(v, str):
        return v
    # Remove accents using NFKD normalization
    nksf = unicodedata.normalize('NFKD', v)
    return "".join([c for c in nksf if not unicodedata.combining(c)]).lower()

# Type alias for normalized taxonomy fields
TaxonomyStr = Annotated[str, BeforeValidator(normalize_taxonomy)]

# ─── Closed taxonomies (must match prompts.yaml) ────────────────────────────
TipoIniciativa = Literal["funcionalidade", "processo", "produto", "estrategia"]
BusinessGame = Literal["attention", "transaction", "productivity"]
Objetivo = Literal[
    "aquisicao", "ativacao", "retencao", "receita", "satisfacao", "engajamento"
]
EtapaFunil = Literal["aquisicao", "ativacao", "retencao", "receita", "referencia"]
Complexidade = Literal["baixa", "media", "alta"]
def coerce_to_string(v: Any) -> str:
    """Force value to be a string, converting dicts/lists to JSON strings if needed."""
    if isinstance(v, (dict, list)):
        import json
        return json.dumps(v, ensure_ascii=False)
    return str(v)

# Type alias for string fields that might receive structured data from LLMs
FlexibleStr = Annotated[str, BeforeValidator(coerce_to_string)]

class ContextAnalysis(BaseModel):
    """Schema for Mistral context analysis response (strict taxonomies)"""

    model_config = ConfigDict(extra="ignore")

    tipo: Annotated[TipoIniciativa, BeforeValidator(normalize_taxonomy)] = Field(
        default="funcionalidade"
    )
    business_game: Annotated[BusinessGame, BeforeValidator(normalize_taxonomy)] = Field(
        default="productivity"
    )
    objetivo: Annotated[Objetivo, BeforeValidator(normalize_taxonomy)] = Field(
        default="engajamento"
    )
    etapa_funil: Annotated[EtapaFunil, BeforeValidator(normalize_taxonomy)] = Field(
        default="ativacao"
    )
    complexidade: Annotated[Complexidade, BeforeValidator(normalize_taxonomy)] = Field(
        default="media"
    )
    area_impacto: List[str] = Field(default_factory=list)
    valor_entregue: FlexibleStr = Field(default="Não identificado")
    resumo_prd: FlexibleStr = Field(
        default="", description="Resumo executivo focado no objetivo (PRD Style)"
    )
    dados_atuais: FlexibleStr = Field(default="Nenhum dado mencionado")
    justificativa: FlexibleStr = Field(default="")
    palavras_chave: List[str] = Field(default_factory=list)

    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description="Model self-reported confidence in classification (0-1)",
    )


class NorthStar(BaseModel):
    nome: str
    definicao: str
    justificativa: str
    validacao_smart: List[str] = Field(default_factory=list)


class L1HealthIndicator(BaseModel):
    pilar: str
    metrica: str
    meta_sugerida: str
    por_que_importa: str


class L2DiagnosticMetric(BaseModel):
    vinculo_l1: str
    metrica: str
    acao_se_cair: str


class CounterMetric(BaseModel):
    nome: str
    protege_contra: str
    trade_off: str


class KeyResult(BaseModel):
    resultado: str
    baseline: Any  # Aceita str, int ou float da API, mas deve conter valor numérico real
    meta: Any  # Aceita str, int ou float da API, mas deve conter valor numérico real

    @field_validator("baseline", "meta")
    @classmethod
    def require_numeric_value(cls, v: Any) -> Any:
        """Reject placeholder KRs; OKRs need measurable baseline and target values."""
        if v is None or isinstance(v, bool):
            raise ValueError("baseline/meta must be a numeric value or a string with a number")

        if isinstance(v, (int, float)):
            return v

        value = str(v).strip()
        if not value:
            raise ValueError("baseline/meta cannot be empty")

        normalized = normalize_taxonomy(value).replace("-", "_").replace(" ", "_")
        placeholder_markers = (
            "tbd",
            "a_definir",
            "nao_mencionado",
            "nao_informado",
            "sem_baseline",
            "sem_meta",
            "manual",
            "n/a",
        )
        if any(marker in normalized for marker in placeholder_markers):
            raise ValueError("baseline/meta cannot be a placeholder")

        if not re.search(r"\d+(?:[.,]\d+)?", value):
            raise ValueError("baseline/meta must include a numeric value")

        return v


class OKR(BaseModel):
    objetivo: str
    key_results: List[KeyResult]


class Implementation(BaseModel):
    ferramentas: List[str]
    queries_exemplo: List[str]
    visualizacao: str


class MetricsAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    north_star: NorthStar
    l1_health_indicators: List[L1HealthIndicator]
    l2_diagnostic_metrics: List[L2DiagnosticMetric]
    counter_metrics: List[CounterMetric]
    okrs: List[OKR]
    implementacao: Implementation
    riscos_e_vieses: List[str]

    @model_validator(mode="after")
    def validate_metric_governance(self) -> "MetricsAnalysis":
        expected_pillars = {
            "Acquisition",
            "Activation",
            "Engagement",
            "Retention",
            "Monetization",
            "Satisfaction",
        }

        pillars = [l1.pilar for l1 in self.l1_health_indicators]
        if len(pillars) != len(set(pillars)):
            raise ValueError("l1_health_indicators must not contain duplicate pillars")

        pillar_set = set(pillars)
        if pillar_set != expected_pillars:
            missing = sorted(expected_pillars - pillar_set)
            extra = sorted(pillar_set - expected_pillars)
            raise ValueError(
                f"l1_health_indicators must contain exactly the 6 required pillars; "
                f"missing={missing}; extra={extra}"
            )

        l1_names = {l1.metrica for l1 in self.l1_health_indicators}
        l2_links = {l2.vinculo_l1 for l2 in self.l2_diagnostic_metrics}
        orphan_links = sorted(l2_links - l1_names)
        if orphan_links:
            raise ValueError(f"l2_diagnostic_metrics link to unknown L1 metrics: {orphan_links}")

        missing_l2 = sorted(l1_names - l2_links)
        if missing_l2:
            raise ValueError(f"every L1 metric must have at least one linked L2: {missing_l2}")

        return self
