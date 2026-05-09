import re
from typing import Any, Dict

from utils.validation import sanitize_text, validate_input

MAX_ANALYSES_PER_SESSION: int = 10
MAX_FILE_SIZE_MB: int = 10
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

# Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(previous|all|above)\s+instructions?"
    r"|system\s*prompt"
    r"|you\s+are\s+now"
    r"|act\s+as\s+(a\s+)?(?:different|new|another)"
    r"|<\s*/?(?:system|assistant|user)\s*>"
    r"|###\s*(?:system|instruction)"
    r"|\[INST\]|\[/?SYS\])",
    re.IGNORECASE,
)

# Patterns to redact from log messages
_REDACT_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{10,}"), "sk-***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE), "Bearer ***"),
    (re.compile(r"(api[_-]?key\s*[=:]\s*)[^\s,\"']+", re.IGNORECASE), r"\1***"),
]


def redact_log_message(text: str) -> str:
    """Mask secrets/tokens in a string before logging."""
    for pattern, replacement in _REDACT_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def security_choke_point(prompt_final: str) -> Dict[str, Any]:
    """
    Validate and sanitize the final prompt before any AI call.

    Returns a dict with:
      ok: bool
      sanitized_prompt: str | None
      message_user: str
      reason: str
    """
    if not prompt_final or not prompt_final.strip():
        return {
            "ok": False,
            "sanitized_prompt": None,
            "message_user": "A descrição não pode estar vazia.",
            "reason": "empty_input",
        }

    # Check injection on raw input (before sanitize_text strips HTML tags)
    if _INJECTION_PATTERNS.search(prompt_final):
        return {
            "ok": False,
            "sanitized_prompt": None,
            "message_user": "Entrada inválida. Por favor, descreva sua iniciativa normalmente.",
            "reason": "prompt_injection",
        }

    sanitized = sanitize_text(prompt_final)

    if _INJECTION_PATTERNS.search(sanitized):
        return {
            "ok": False,
            "sanitized_prompt": None,
            "message_user": "Entrada inválida. Por favor, descreva sua iniciativa normalmente.",
            "reason": "prompt_injection",
        }

    result = validate_input(sanitized)
    if not result["valid"]:
        return {
            "ok": False,
            "sanitized_prompt": None,
            "message_user": result["message"],
            "reason": "invalid_input",
        }

    return {"ok": True, "sanitized_prompt": sanitized, "message_user": "", "reason": "ok"}
