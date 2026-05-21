"""Pydantic schemas for API response validation - Otimizado para PRD e Markdown"""

from typing import Any, List, Literal

from pydantic import BaseModel, ConfigDict, Field

# ─── Closed taxonomies (must match prompts.yaml) ────────────────────────────
TipoIniciativa = Literal["funcionalidade", "processo", "produto", "estrategia"]
BusinessGame = Literal["attention", "transaction", "productivity"]
Objetivo = Literal[
    "aquisicao", "ativacao", "retencao", "receita", "satisfacao", "engajamento"
]
EtapaFunil = Literal["aquisicao", "ativacao", "retencao", "receita", "referencia"]
Complexidade = Literal["baixa", "media", "alta"]


class ContextAnalysis(BaseModel):
    """Schema for Mistral context analysis response (strict taxonomies)"""

    model_config = ConfigDict(extra="ignore")

    tipo: TipoIniciativa = Field(default="funcionalidade")
    business_game: BusinessGame = Field(default="productivity")
    objetivo: Objetivo = Field(default="engajamento")
    etapa_funil: EtapaFunil = Field(default="ativacao")
    complexidade: Complexidade = Field(default="media")
    area_impacto: List[str] = Field(default_factory=list)
    valor_entregue: str = Field(default="Não identificado")
    resumo_prd: str = Field(
        default="", description="Resumo executivo focado no objetivo (PRD Style)"
    )
    dados_atuais: str = Field(default="Nenhum dado mencionado")
    justificativa: str = Field(default="")
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
    baseline: Any  # Aceita str, int ou float da API
    meta: Any  # Aceita str, int ou float da API


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
