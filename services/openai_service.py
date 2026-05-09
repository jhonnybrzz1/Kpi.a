import json
import logging
import os
import time
from typing import Any, Dict

from openai import OpenAI
from pydantic import ValidationError

from config import get_prompt
from services.schemas import MetricsAnalysis
from utils.ai_metrics import record_call, validate_json_structure
from utils.retry import retry_with_backoff

# Configure module logger
logger = logging.getLogger(__name__)


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
        self.model = "gpt-5.4-nano"
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
        # Load prompt from configuration
        prompt_template = get_prompt("openai", "generate_metrics", "user")
        system_prompt = get_prompt("openai", "generate_metrics", "system")

        # Format context areas
        areas = context.get("area_impacto", [])
        areas_str = ", ".join(areas) if isinstance(areas, list) else str(areas)

        prompt = prompt_template.format(
            initiative_text=initiative_text,
            context_tipo=context.get("tipo", "N/A"),
            context_objetivo=context.get("objetivo", "N/A"),
            context_etapa_funil=context.get("etapa_funil", "N/A"),
            context_complexidade=context.get("complexidade", "N/A"),
            context_areas=areas_str,
        )

        t0 = time.monotonic()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_completion_tokens=8000,
                timeout=90.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("Empty response from OpenAI")

            # Extract usage when available
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            # Clean content by removing possible markdown code blocks
            raw_content = content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)

            # Validate response using Pydantic schema
            try:
                validated = MetricsAnalysis.model_validate(data)
                data = validated.model_dump()
            except ValidationError as e:
                logger.warning("Validation warning, some fields may use defaults: %s", str(e))
                validated = MetricsAnalysis.model_validate(data, strict=False)
                data = validated.model_dump()

            # ── Observability ──────────────────────────────────────────────
            vr = validate_json_structure(raw_content, "metrics_analysis")
            operation_id = record_call(
                model=self.model,
                provider="openai",
                latency_ms=int((time.monotonic() - t0) * 1000),
                json_valid=vr["json_valid"],
                json_error_type=vr["json_error_type"],
                usage=usage,
                temperature=0.4,
            )
            logger.info(
                "openai generate_metrics operation_id=%s json_valid=%s latency_ms=%d okrs=%d",
                operation_id,
                vr["json_valid"],
                int((time.monotonic() - t0) * 1000),
                len(data.get("okrs", [])),
            )
            return data

        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON response from OpenAI: {str(e)}")
        except ValidationError as e:
            raise Exception(f"Invalid response schema: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in OpenAI service: {str(e)}")

    @retry_with_backoff(max_retries=3, base_delay=2)
    def generate_executive_summary(
        self, initiative_text: str, context: Dict[str, Any], metrics: Dict[str, Any]
    ) -> str:
        """
        Generates an executive summary of the analysis

        Args:
            initiative_text: Initiative text
            context: Analyzed context
            metrics: Generated metrics

        Returns:
            String with executive summary
        """
        # Load prompts from configuration
        prompt_template = get_prompt("openai", "executive_summary", "user")
        system_prompt = get_prompt("openai", "executive_summary", "system")

        # Guard: validate prompts are non-empty
        if not system_prompt.strip():
            raise ValueError("missing_prompt: openai.executive_summary.system")
        if not prompt_template.strip():
            raise ValueError("missing_prompt: openai.executive_summary.user")

        prompt = prompt_template.format(
            initiative_text=initiative_text,
            context=json.dumps(context, indent=2, ensure_ascii=False),
            metrics=json.dumps(metrics, indent=2, ensure_ascii=False),
        )

        # Guard: validate all placeholders were replaced
        for placeholder in ("{initiative_text}", "{context}", "{metrics}"):
            if placeholder in prompt:
                raise ValueError(f"missing_placeholder: {placeholder}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_completion_tokens=600,
                timeout=90.0,
            )

            content = response.choices[0].message.content
            logger.info("Executive summary generated successfully")
            return content if content is not None else "Não foi possível gerar o resumo executivo."

        except Exception as e:
            logger.error("Error generating executive summary: %s", str(e))
            return f"Não foi possível gerar o resumo executivo. Erro: {str(e)}"

    def stream_executive_summary(
        self, initiative_text: str, context: Dict[str, Any], metrics: Dict[str, Any]
    ):
        """
        Stream executive summary tokens as a generator of str chunks.
        Compatible with st.write_stream().
        Falls back to empty string on error (caller handles display).
        """
        from config import get_prompt

        prompt_template = get_prompt("openai", "executive_summary", "user")
        system_prompt = get_prompt("openai", "executive_summary", "system")

        if not system_prompt.strip() or not prompt_template.strip():
            yield "Não foi possível gerar o resumo executivo."
            return

        prompt = prompt_template.format(
            initiative_text=initiative_text,
            context=json.dumps(context, indent=2, ensure_ascii=False),
            metrics=json.dumps(metrics, indent=2, ensure_ascii=False),
        )

        try:
            with self.client.chat.completions.stream(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_completion_tokens=600,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error("Error streaming executive summary: %s", str(e))
            yield f"\n\n_(Erro ao gerar resumo: {str(e)})_"
