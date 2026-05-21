"""Configuration module for MetricFlow AI"""

import hashlib
import os
from functools import lru_cache
from typing import Any, Dict

import yaml

_PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts.yaml")


@lru_cache(maxsize=1)
def load_prompts() -> Dict[str, Any]:
    """
    Load prompts from YAML configuration file.

    Returns:
        Dict containing all prompt configurations
    """
    with open(_PROMPTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_prompt(service: str, prompt_name: str, prompt_type: str = "user") -> str:
    """
    Get a specific prompt from configuration.

    Args:
        service: Service name ('mistral' or 'openai')
        prompt_name: Name of the prompt (e.g., 'analyze_context')
        prompt_type: Type of prompt ('system' or 'user')

    Returns:
        The prompt string
    """
    prompts = load_prompts()
    return prompts.get(service, {}).get(prompt_name, {}).get(prompt_type, "")


@lru_cache(maxsize=1)
def get_prompts_version() -> str:
    """
    Return a short fingerprint of the current prompts.yaml content.

    Used to stamp every recorded AI call so we can correlate behaviour
    changes (latency, json_valid rate, output quality) with prompt edits
    without needing a full A/B framework.

    Returns:
        First 8 hex chars of the SHA-256 of the file bytes (e.g. "a1b2c3d4").
    """
    with open(_PROMPTS_PATH, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]
