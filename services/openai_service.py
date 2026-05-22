import json
import logging
import os
import time
from typing import Any, Dict, Tuple

from openai import OpenAI
from pydantic import ValidationError

from config import get_prompt, get_prompts_version
from services.schemas import MetricsAnalysis
from utils.ai_metrics import record_call, validate_json_structure
from utils.retry import retry_with_backoff

# Configure module logger
logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenRouter chat completions integration."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not configured. "
                "Please set the environment variable before using this service."
            )
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1"),
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8501"),
                "X-Title": "MetricFlow AI",
            },
        )
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it")
        logger.info("OpenRouter service initialized with model: %s", self.model)

    @retry_with_backoff(max_retries=3, base_delay=2)
    def generate_metrics(self, initiative_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates metrics with an automatic self-correction loop.
        It generates a first draft, reviews it via an LLM judge,
        and refines it if quality is below threshold.
        """
        # 1. Generate First Draft
        data = self._execute_metrics_generation(initiative_text, context)
        
        # 2. Review Phase (LLM-as-a-Judge)
        review = self._review_metrics(initiative_text, data)
        
        # 3. Refinement Phase (if needed)
        if not review.get("aprovado", False) and review.get("score", 1.0) < 0.8:
            logger.info(
                "Metric refinement triggered. Score: %.2f. Critiques: %s",
                review["score"], review["criticas"]
            )
            data = self._refine_metrics(initiative_text, data, review["criticas"])
            
        return data

    def _execute_metrics_generation(self, initiative_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Original generation logic (encapsulated)"""
        prompt_template = get_prompt("openai", "generate_metrics", "user")
        system_prompt = get_prompt("openai", "generate_metrics", "system")

        prompt = prompt_template.format(
            initiative_text=initiative_text,
            context_json=json.dumps(context, indent=2, ensure_ascii=False),
        )

        t0 = time.monotonic()
        # Internal retry for JSON/Schema errors (dual temperature)
        temps = [0.4, 0.1]
        last_err = None
        
        for temp in temps:
            try:
                raw_content, usage = self._post_metrics_completion(system_prompt, prompt, temp)
                data = self._parse_and_validate_metrics(raw_content)
                
                # Success recording
                self._record_metrics_call(t0, raw_content, usage, temp)
                return data
            except (json.JSONDecodeError, ValidationError) as e:
                last_err = e
                logger.warning("Metrics parse fail temp=%s: %s", temp, type(e).__name__)
                continue
        
        raise Exception(f"Metrics generation failed parse/validate twice: {str(last_err)}")

    def _review_metrics(self, initiative_text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Review the metrics using a critic prompt."""
        system_prompt = get_prompt("openai", "review_metrics", "system")
        prompt_template = get_prompt("openai", "review_metrics", "user")
        
        prompt = prompt_template.format(
            initiative_text=initiative_text,
            metrics_json=json.dumps(metrics, indent=2, ensure_ascii=False)
        )
        
        try:
            # Review is always deterministic (temp=0)
            raw_content, _ = self._post_metrics_completion(system_prompt, prompt, 0.0)
            return json.loads(raw_content)
        except Exception as e:
            logger.warning("Metrics review failed (skipping refinement): %s", str(e))
            return {"aprovado": True, "score": 1.0, "criticas": []}

    def _refine_metrics(self, initiative_text: str, original_metrics: Dict[str, Any], critiques: list) -> Dict[str, Any]:
        """Refine the metrics based on critic feedback."""
        system_prompt = get_prompt("openai", "refine_metrics", "system")
        prompt_template = get_prompt("openai", "refine_metrics", "user")
        
        prompt = prompt_template.format(
            initiative_text=initiative_text,
            metrics_json=json.dumps(original_metrics, indent=2, ensure_ascii=False),
            critiques="\n- ".join(critiques)
        )
        
        t0 = time.monotonic()
        try:
            # Refinement with low temperature
            raw_content, usage = self._post_metrics_completion(system_prompt, prompt, 0.2)
            data = self._parse_and_validate_metrics(raw_content)
            self._record_metrics_call(t0, raw_content, usage, 0.2, suffix=" (refined)")
            return data
        except Exception as e:
            logger.warning("Metrics refinement failed (using original): %s", str(e))
            return original_metrics

    def _record_metrics_call(self, t0: float, raw_content: str, usage: dict, temp: float, suffix: str = ""):
        """Recording helper"""
        vr = validate_json_structure(raw_content, "metrics_analysis")
        latency = int((time.monotonic() - t0) * 1000)
        operation_id = record_call(
            model=self.model,
            provider="openrouter",
            latency_ms=latency,
            json_valid=vr["json_valid"],
            json_error_type=vr["json_error_type"],
            usage=usage,
            temperature=temp,
            prompt_version=get_prompts_version(),
        )
        logger.info(
            "openrouter metrics%s op_id=%s valid=%s lat=%dms",
            suffix, operation_id, vr["json_valid"], latency
        )

    # ── HTTP / parsing helpers for generate_metrics ─────────────────────────

    def _post_metrics_completion(
        self, system_prompt: str, user_prompt: str, temperature: float
    ) -> Tuple[str, Dict[str, int] | None]:
        """
        POST a single metrics generation. Returns (raw_content, usage).
        Raises on empty response or HTTP errors (caller handles network).
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_completion_tokens=8000,
            timeout=90.0,
        )

        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from OpenRouter")

        usage: Dict[str, int] | None = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return content, usage

    def _parse_and_validate_metrics(self, raw_content: str) -> Dict[str, Any]:
        """
        Strip markdown fences, parse JSON and validate against MetricsAnalysis.
        Raises json.JSONDecodeError or ValidationError so the caller can
        trigger the low-temperature recovery path.
        """
        content = raw_content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)
        validated = MetricsAnalysis.model_validate(data)
        return validated.model_dump()

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
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_completion_tokens=600,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("Error streaming executive summary: %s", str(e))
            yield f"\n\n_(Erro ao gerar resumo: {str(e)})_"
