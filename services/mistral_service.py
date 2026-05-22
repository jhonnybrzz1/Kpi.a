import json
import logging
import os
import time
from typing import Any, Dict, Tuple

import requests
from pydantic import ValidationError

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
        Analyzes initiative context using Mistral AI.
        Includes a dual-temperature recovery path for JSON/Schema errors.
        """
        system_prompt = get_prompt("mistral", "analyze_context", "system")
        prompt_template = get_prompt("mistral", "analyze_context", "user")

        if not system_prompt.strip() or not prompt_template.strip():
            logger.error("Missing prompts for mistral.analyze_context")
            return self._get_default_response()

        prompt = prompt_template.format(initiative_text=initiative_text)
        t0 = time.monotonic()
        
        # We try up to 2 distinct temperatures internally before letting
        # the outer retry_with_backoff handle network/api issues.
        temps_to_try = [0.3, 0.0]
        last_exception = None

        for used_temp in temps_to_try:
            try:
                raw_content, usage = self._post_completion(system_prompt, prompt, used_temp)
                data = self._parse_and_validate(raw_content)
                
                # ── Success Path ───────────────────────────────────────────
                vr = validate_json_structure(raw_content, "context_analysis")
                self._log_call(t0, vr, usage, used_temp)
                return data

            except (json.JSONDecodeError, ValidationError) as e:
                last_exception = e
                logger.warning(
                    "mistral_parse_fail attempt_temp=%s reason=%s",
                    used_temp, type(e).__name__
                )
                continue # Try next temperature
            except Exception as e:
                # Network or API errors should be handled by outer retry
                raise e

        # If we reach here, all internal temperature attempts failed.
        # We raise a specific error that the outer retry will see.
        raise Exception(f"Mistral output failed parse/validate twice: {str(last_exception)}")

    def _log_call(self, t0: float, vr: Dict[str, Any], usage: Dict[str, Any], temp: float):
        """Helper to record telemetry and logs."""
        latency = int((time.monotonic() - t0) * 1000)
        operation_id = record_call(
            model=self.model,
            provider="mistral",
            latency_ms=latency,
            json_valid=vr["json_valid"],
            json_error_type=vr["json_error_type"],
            usage=usage,
            temperature=temp,
            prompt_version=get_prompts_version(),
        )
        logger.info(
            "mistral operation_id=%s json_valid=%s latency=%dms temp=%s",
            operation_id, vr["json_valid"], latency, temp
        )

    # ── HTTP / parsing helpers ──────────────────────────────────────────────

    def _post_completion(
        self, system_prompt: str, user_prompt: str, temperature: float
    ) -> Tuple[str, Dict[str, int] | None]:
        """
        POST a single chat completion to Mistral. Returns (raw_content, usage).
        Raises on non-200 HTTP or network errors so the caller can decide.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 2000,
            # Mistral structured output mode — guarantees parseable JSON
            "response_format": {"type": "json_object"},
        }
        response = requests.post(self.base_url, headers=headers, json=payload, timeout=90)
        if response.status_code != 200:
            raise Exception(f"Mistral API error: {response.status_code} - {response.text}")

        result = response.json()
        raw_content: str = result["choices"][0]["message"]["content"]

        usage: Dict[str, int] | None = None
        u = result.get("usage")
        if u:
            usage = {
                "prompt_tokens": u.get("prompt_tokens", 0),
                "completion_tokens": u.get("completion_tokens", 0),
                "total_tokens": u.get("total_tokens", 0),
            }
        return raw_content, usage

    def _parse_and_validate(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse the raw model output to JSON and validate against ContextAnalysis.

        Raises pydantic.ValidationError on out-of-taxonomy values so the
        caller can trigger the low-temperature recovery path. A pure
        json.JSONDecodeError is caught and routed through the regex
        fallback (which always returns a schema-valid default), so it
        will not usually propagate.
        """
        clean = raw_content.strip()
        if clean.startswith("```"):
            clean = clean[clean.index("\n") + 1 :]
            if clean.endswith("```"):
                clean = clean[: clean.rfind("```")].strip()
        try:
            data = json.loads(clean)
        except json.JSONDecodeError:
            # Should be rare with response_format=json_object set —
            # treat as a real signal the model misbehaved.
            logger.warning(
                "prompt_fallback_used: JSON parse failed (%d chars) despite "
                "response_format=json_object, falling back to regex extraction",
                len(clean),
            )
            data = self._extract_json_from_text(clean)
            # If the regex fallback also fails, _extract_json_from_text returns
            # the default structure which is always schema-valid.
        return self._validate_and_complete_response(data)

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
