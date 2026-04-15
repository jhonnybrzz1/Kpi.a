import os
import json
import time
import logging
from functools import wraps
from openai import OpenAI
from typing import Dict, Any, List

# Configure module logger
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator to retry function calls with exponential backoff"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error("Failed after %d attempts: %s", max_retries, str(e))
                        raise
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        "Attempt %d failed, retrying in %ds: %s", attempt + 1, delay, str(e)
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


class OpenAIService:
    """Service for OpenAI GPT-4 integration"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not configured. "
                "Please set the environment variable before using this service."
            )
        self.client = OpenAI(api_key=self.api_key)
        # Using gpt-4.1-mini for better stability and cost efficiency
        self.model = "gpt-4.1-mini"
        logger.info("OpenAIService initialized with model: %s", self.model)

    @retry_with_backoff(max_retries=3, base_delay=2)
    def generate_metrics(self, initiative_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates metrics, KPIs and OKRs based on initiative and context

        Args:
            initiative_text: Initiative text
            context: Context analyzed by Mistral

        Returns:
            Dict with suggested metrics, KPIs and OKRs
        """

        prompt = f"""
Você é um especialista em métricas de produto, KPIs e OKRs. Com base na iniciativa e contexto fornecidos, 
gere uma análise completa de métricas.

INICIATIVA: {initiative_text}

CONTEXTO ANALISADO:
- Tipo: {context.get("tipo", "N/A")}
- Objetivo: {context.get("objetivo", "N/A")}
- Etapa do funil: {context.get("etapa_funil", "N/A")}
- Complexidade: {context.get("complexidade", "N/A")}
- Áreas de impacto: {", ".join(context.get("area_impacto", []))}

Gere uma resposta em JSON com a seguinte estrutura:

{{
  "north_star_metric": {{
    "nome": "Nome da métrica principal",
    "descricao": "Descrição detalhada da North Star Metric",
    "justificativa": "Por que esta é a métrica mais importante"
  }},
  "kpis": [
    {{
      "nome": "Nome do KPI",
      "descricao": "Descrição do KPI",
      "formula": "Fórmula de cálculo",
      "frequencia_medicao": "diária/semanal/mensal",
      "meta_sugerida": "Meta numérica sugerida",
      "responsavel_area": "Área responsável pela medição"
    }}
  ],
  "okrs": [
    {{
      "objetivo": "Objetivo claro e inspirador",
      "key_results": [
        "Key Result 1 com meta quantificada",
        "Key Result 2 com meta quantificada",
        "Key Result 3 com meta quantificada"
      ],
      "prazo": "Prazo sugerido (ex: trimestral)"
    }}
  ],
  "frameworks_aplicaveis": [
    {{
      "nome": "Nome do framework (ex: HEART, RICE, AARRR)",
      "aplicacao": "Como aplicar este framework na iniciativa"
    }}
  ],
  "implementacao_medicao": {{
    "ferramentas_sugeridas": ["Lista de ferramentas para medição"],
    "setup_tracking": "Instruções para configurar o tracking",
    "dashboards": "Sugestões de dashboards e visualizações"
  }},
  "riscos_metricas": [
    "Risco 1 relacionado às métricas",
    "Risco 2 que pode afetar a medição"
  ]
}}

Seja específico e prático. As métricas devem ser SMART (Específicas, Mensuráveis, Atingíveis, Relevantes, Temporais).
Inclua pelo menos 3-5 KPIs principais e 1-2 OKRs completos.

Responda APENAS com o JSON válido, sem texto adicional.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em métricas de produto e análise de dados. "
                        "Responda sempre em JSON válido conforme solicitado.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=2500,
                timeout=60.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("Empty response from OpenAI")

            # Clean content by removing possible markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)

            # Validate required schema fields
            required_fields = ["north_star_metric", "kpis", "okrs"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Required field missing in response: {field}")

            logger.info(
                "Successfully generated metrics with %d KPIs and %d OKRs",
                len(data.get("kpis", [])),
                len(data.get("okrs", [])),
            )
            return data

        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON response from OpenAI: {str(e)}")
        except ValueError as e:
            raise Exception(f"Invalid response schema: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in OpenAI service: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=2)
    def generate_executive_summary(
        self, initiative_text: str, context: Dict[str, Any], metrics: Dict[str, Any]
    ) -> str:
        """
        Gera um resumo executivo da análise

        Args:
            initiative_text: Texto da iniciativa
            context: Contexto analisado
            metrics: Métricas geradas

        Returns:
            String com resumo executivo
        """

        prompt = f"""
Com base na iniciativa e análises realizadas, escreva um resumo executivo profissional 
que explique de forma clara e concisa:

1. O que é a iniciativa
2. Por que as métricas escolhidas são relevantes
3. Como implementar a medição
4. Benefícios esperados

INICIATIVA: {initiative_text}
CONTEXTO: {json.dumps(context, indent=2, ensure_ascii=False)}
MÉTRICAS: {json.dumps(metrics, indent=2, ensure_ascii=False)}

O resumo deve ter entre 200-400 palavras, ser profissional e focado em resultados de negócio.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um consultor de negócios especializado em redação executiva.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=600,
                timeout=30.0,
            )

            content = response.choices[0].message.content
            logger.info("Executive summary generated successfully")
            return content if content is not None else "Não foi possível gerar o resumo executivo."

        except Exception as e:
            logger.error("Error generating executive summary: %s", str(e))
            return f"Não foi possível gerar o resumo executivo. Erro: {str(e)}"
