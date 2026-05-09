"""
Session-scoped analysis history (FIFO, max 10 completed snapshots).
Storage: st.session_state — persists for the browser session only (MVP).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
import hashlib

import streamlit as st

_HISTORY_KEY = "_analysis_history"
_MAX_ITEMS = 10


def _dedupe_key(initiative_text: str) -> str:
    """Stable 12-char key based on normalized input content."""
    normalized = " ".join(initiative_text.strip().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:12]


def save_snapshot(
    initiative_text: str,
    context: Dict[str, Any],
    metrics: Dict[str, Any],
    executive_summary: str,
    pdf_bytes: bytes,
    artifact_result: str,
) -> None:
    """
    Persist a completed analysis snapshot to session history.
    Only saves when artifact_result != 'none' (i.e., analysis completed).
    """
    if artifact_result == "none":
        return

    history: List[Dict[str, Any]] = st.session_state.get(_HISTORY_KEY, [])

    snapshot: Dict[str, Any] = {
        "snapshot_id": _dedupe_key(initiative_text),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "initiative_preview": initiative_text[:80] + ("…" if len(initiative_text) > 80 else ""),
        "status": "completed",
        "artifact_result": artifact_result,
        "payload": {
            "initiative_text": initiative_text,
            "context": context,
            "metrics": metrics,
            "executive_summary": executive_summary,
            "pdf_bytes": pdf_bytes,
            "artifact_result": artifact_result,
        },
    }

    # Deduplicate: remove existing entry with same snapshot_id
    history = [h for h in history if h["snapshot_id"] != snapshot["snapshot_id"]]

    # Prepend and enforce FIFO limit
    history.insert(0, snapshot)
    st.session_state[_HISTORY_KEY] = history[:_MAX_ITEMS]


def get_history() -> List[Dict[str, Any]]:
    """Return current history list (completed snapshots only)."""
    return [
        h for h in st.session_state.get(_HISTORY_KEY, [])
        if h.get("status") == "completed"
    ]
