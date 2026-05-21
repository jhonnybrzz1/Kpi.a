import json
import logging
import os
import time
from typing import Any, Dict

import requests

from config import get_prompt, get_prompts_version
from services.schemas import ContextAnalysis
from utils.ai_metrics import record_call, validate_json_structure
from utils.retry import retry_with_backoff

# Configure module logger
logger = logging.getLogger(__name__)


class MistralService:
    """Service for Mistral AI API integration"""

    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not configured. "
                "Please set the environment variable before using this service."
            )
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-2512"
        logger.info("MistralService initialized with model: %s", self.model)

    @retry_with_backoff(max_retries=3, base_delay=2)
    def analyze_context(self, initiative_text: str) -> Dict[str, Any]:
        """
        Analyzes initiative context using Mistral AI

        Args:
            initiative_text: Text describing the initiative

        Returns:
            Dict containing context analysis
        """
        # Load prompts from configuration
        system_prompt = get_prompt("mistral", "analyze_context", "system")
        prompt_template = get_prompt("mistral", "analyze_context", "user")

        # Guard: validate prompts are non-empty (matches openai_service guard)
        if not system_prompt.strip():
            raise ValueError("missing_prompt: mistral.analyze_context.system")
        if not prompt_template.strip():
            raise ValueError("missing_prompt: mistral.analyze_context.user")

        prompt = prompt_template.format(initiative_text=initiative_text)

        # Guard: validate placeholder was replaced
        if "{initiative_text}" in prompt:
            raise ValueError("missing_placeholder: {initiative_text}")

        t0 = time.monotonic()
        raw_content: str = ""
        usage: Dict[str, int] | None = None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                # Mistral structured output mode — guarantees parseable JSON
                "response_format": {"type": "json_object"},
            }

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=90)

            if response.status_code == 200:
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]

                # Extract usage when available
                u = result.get("usage")
                if u:
                    usage = {
                        "prompt_tokens": u.get("prompt_tokens", 0),
                        "completion_tokens": u.get("completion_tokens", 0),
                        "total_tokens": u.get("total_tokens", 0),
                    }

                # Strip markdown code fences if present
                clean = raw_content.strip()
                if clean.startswith("```"):
                    clean = clean[clean.index("\n") + 1 :]
                    if clean.endswith("```"):
                        clean = clean[: clean.rfind("```")].strip()
                try:
                    data = json.loads(clean)
                except json.JSONDecodeError:
                    # Should be rare now that response_format=json_object is set —
                    # treat as a real signal the model misbehaved.
                    logger.warning(
                        "prompt_fallback_used: JSON parse failed (%d chars) despite "
                        "response_format=json_object, falling back to regex extraction",
                        len(clean),
                    )
                    data = self._extract_json_from_text(clean)

                # Validate required fields
                data = self._validate_and_complete_response(data)

                # ── Observability ──────────────────────────────────────────
                vr = validate_json_structure(raw_content, "context_analysis")
                operation_id = record_call(
                    model=self.model,
                    provider="mistral",
                    latency_ms=int((time.monotonic() - t0) * 1000),
                    json_valid=vr["json_valid"],
                    json_error_type=vr["json_error_type"],
                    usage=usage,
                    temperature=0.3,
                    prompt_version=get_prompts_version(),
                )
                logger.info(
                    "mistral analyze_context operation_id=%s json_valid=%s latency_ms=%d",
                    operation_id,
                    vr["json_valid"],
                    int((time.monotonic() - t0) * 1000),
                )
                return data

            else:
                raise Exception(f"Mistral API error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error with Mistral: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in Mistral service: {str(e)}")

    def _validate_and_complete_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strictly validate response against ContextAnalysis schema.

        Raises ValidationError on values outside closed taxonomies — this is
        intentional so retry_with_backoff can re-prompt the model. Silent
        coercion would hide misclassifications.
        """
        validated = ContextAnalysis.model_validate(data)
        return validated.model_dump()

    def _get_default_response(self) -> Dict[str, Any]:
        """Returns default response structure using Pydantic model"""
        return ContextAnalysis().model_dump()

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that may contain other characters"""
        try:
            # Look for { and } to extract JSON
            start = text.find("{")
            end = text.rfind("}") + 1

            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str, strict=False)

            # Fallback: return default structure
            logger.warning("Could not find JSON in response text")
            return self._get_default_response()

        except Exception as e:
            logger.warning("Error extracting JSON from text: %s", str(e))
            return self._get_default_response()
