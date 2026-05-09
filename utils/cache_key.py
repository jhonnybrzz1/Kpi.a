import hashlib
import json
import re
from typing import Any, Dict


def normalize_input(text: str) -> str:
    """Trim, collapse whitespace and normalize line endings."""
    return re.sub(r"\s+", " ", text.strip())


def prompt_version_hash(prompts_content: str) -> str:
    """SHA-256 (first 16 chars) of the raw prompts.yaml content."""
    return hashlib.sha256(prompts_content.encode()).hexdigest()[:16]


def params_signature(params: Dict[str, Any]) -> str:
    """Stable hash of a params dict (sorted keys)."""
    serialized = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def build_cache_key(
    input_text: str, model: str, prompts_content: str, params: Dict[str, Any]
) -> str:
    """Compose the full deterministic cache key for one API stage."""
    input_hash = hashlib.sha256(normalize_input(input_text).encode()).hexdigest()[:16]
    return f"{input_hash}:{model}:{prompt_version_hash(prompts_content)}:{params_signature(params)}"
