"""Configuration module for MetricFlow AI"""

import os
import yaml
from typing import Dict, Any
from functools import lru_cache


@lru_cache(maxsize=1)
def load_prompts() -> Dict[str, Any]:
    """
    Load prompts from YAML configuration file.

    Returns:
        Dict containing all prompt configurations
    """
    config_path = os.path.join(os.path.dirname(__file__), "prompts.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
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
