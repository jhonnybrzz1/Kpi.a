"""Pydantic schemas for API response validation - Otimizado para PRD e Markdown"""

from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field


class ContextAnalysis(BaseModel):
    """Schema for Mistral context analysis response"""

    tipo: Any = Field(default="funcionalidade")
    business_game: Any = Field(default="productivity")
    objetivo: Any = Field(default="engajamento")
    etapa_funil: Any = Field(default="ativacao")
    complexidade: Any = Field(default="media")
    area_impacto: Any = Field(default_factory=list)
    valor_entregue: Any = Field(default="Não identificado")
    resumo_prd: Any = Field(
        default="", description="Resumo executivo focado no objetivo (PRD Style)"
    )
    dados_atuais: Any = Field(default="Nenhum dado mencionado")
    justificativa: Any = Field(default="")
    palavras_chave: Any = Field(default_factory=list)


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
