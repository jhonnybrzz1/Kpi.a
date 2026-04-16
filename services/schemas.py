"""Pydantic schemas for API response validation"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ContextAnalysis(BaseModel):
    """Schema for Mistral context analysis response"""

    tipo: str = Field(
        default="funcionalidade",
        description="Initiative type: funcionalidade, processo, produto, estrategia",
    )
    objetivo: str = Field(
        default="operacao",
        description="Main objective: aquisicao, ativacao, retencao, receita, engajamento",
    )
    etapa_funil: str = Field(
        default="ativacao",
        description="AARRR funnel stage: aquisicao, ativacao, retencao, receita, referencia",
    )
    complexidade: str = Field(default="media", description="Complexity level: baixa, media, alta")
    area_impacto: List[str] = Field(
        default_factory=lambda: ["tecnologia"],
        description="List of impacted areas",
    )
    justificativa: str = Field(
        default="Análise automática baseada no texto fornecido.",
        description="Justification for the classification",
    )
    palavras_chave: Optional[List[str]] = Field(
        default_factory=lambda: ["iniciativa", "projeto"],
        description="List of relevant keywords",
    )

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        valid_types = ["funcionalidade", "processo", "produto", "estrategia"]
        if v.lower() not in valid_types:
            return "funcionalidade"
        return v.lower()

    @field_validator("complexidade")
    @classmethod
    def validate_complexidade(cls, v: str) -> str:
        valid_levels = ["baixa", "media", "alta"]
        if v.lower() not in valid_levels:
            return "media"
        return v.lower()


class NorthStarMetric(BaseModel):
    """Schema for North Star Metric"""

    nome: str = Field(description="Metric name")
    descricao: str = Field(default="", description="Metric description")
    justificativa: str = Field(default="", description="Justification")


class KPI(BaseModel):
    """Schema for KPI"""

    nome: str = Field(description="KPI name")
    descricao: str = Field(default="", description="KPI description")
    formula: Optional[str] = Field(default=None, description="Calculation formula")
    frequencia_medicao: Optional[str] = Field(default="mensal", description="Measurement frequency")
    meta_sugerida: Optional[str] = Field(default=None, description="Suggested target")
    responsavel_area: Optional[str] = Field(default=None, description="Responsible area")


class OKR(BaseModel):
    """Schema for OKR"""

    objetivo: str = Field(description="Objective")
    key_results: List[str] = Field(default_factory=list, description="List of key results")
    prazo: Optional[str] = Field(default="trimestral", description="Deadline")


class Framework(BaseModel):
    """Schema for applicable framework"""

    nome: str = Field(description="Framework name")
    aplicacao: str = Field(default="", description="How to apply the framework")


class ImplementationDetails(BaseModel):
    """Schema for implementation details"""

    ferramentas_sugeridas: List[str] = Field(default_factory=list, description="Suggested tools")
    setup_tracking: str = Field(default="", description="Tracking setup instructions")
    dashboards: str = Field(default="", description="Dashboard suggestions")


class MetricsAnalysis(BaseModel):
    """Schema for OpenAI metrics analysis response"""

    north_star_metric: NorthStarMetric = Field(description="North Star Metric")
    kpis: List[KPI] = Field(default_factory=list, description="List of KPIs")
    okrs: List[OKR] = Field(default_factory=list, description="List of OKRs")
    frameworks_aplicaveis: Optional[List[Framework]] = Field(
        default_factory=list, description="Applicable frameworks"
    )
    implementacao_medicao: Optional[ImplementationDetails] = Field(
        default=None, description="Implementation details"
    )
    riscos_metricas: Optional[List[str]] = Field(
        default_factory=list, description="Metrics-related risks"
    )
