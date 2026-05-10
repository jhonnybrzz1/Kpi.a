"""
Persistent analysis history (FIFO, max 10 completed snapshots).
Storage: SQLite (ai_metrics.db) — survives browser refresh.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from utils.ai_metrics import _db

_MAX_ITEMS = 10
_SNAPSHOT_VERSION = "v1"


def _ensure_history_table() -> None:
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                snapshot_id TEXT PRIMARY KEY,
                saved_at TEXT NOT NULL,
                initiative_preview TEXT NOT NULL,
                status TEXT NOT NULL,
                artifact_result TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                version TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_history_saved_at ON history(saved_at DESC)")


def calculate_content_hash(payload: Dict[str, Any]) -> str:
    """Calculate hash of the canonical payload content."""
    # We hash the important bits to detect corruption
    canonical = json.dumps(
        {
            "initiative_text": payload.get("initiative_text"),
            "context": payload.get("context"),
            "metrics": payload.get("metrics"),
        },
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def save_snapshot(
    initiative_text: str,
    responsible: str,
    company: str,
    context: Dict[str, Any],
    metrics: Dict[str, Any],
    executive_summary: str,
    pdf_bytes: bytes,
    artifact_result: str,
) -> str:
    """
    Persist a completed analysis snapshot to SQLite history.
    Returns the generated snapshot_id.
    """
    if artifact_result == "none":
        return ""

    _ensure_history_table()
    snapshot_id = str(uuid.uuid4())[:8].upper()  # Human readable-ish ID for "Snapshot #XXXX"
    saved_at = datetime.now(timezone.utc).isoformat()
    initiative_preview = initiative_text[:80] + ("…" if len(initiative_text) > 80 else "")

    import base64

    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8") if pdf_bytes else ""

    payload = {
        "snapshot_id": snapshot_id,
        "initiative_text": initiative_text,
        "responsible": responsible,
        "company": company,
        "context": context,
        "metrics": metrics,
        "executive_summary": executive_summary,
        "pdf_base64": pdf_b64,
        "artifact_result": artifact_result,
        "version": _SNAPSHOT_VERSION,
    }

    content_hash = calculate_content_hash(payload)

    with _db() as conn:
        conn.execute(
            """INSERT INTO history
               (snapshot_id, saved_at, initiative_preview, status, artifact_result,
                payload_json, content_hash, version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                snapshot_id,
                saved_at,
                initiative_preview,
                "completed",
                artifact_result,
                json.dumps(payload),
                content_hash,
                _SNAPSHOT_VERSION,
            ),
        )

        # Enforce FIFO limit
        rows_to_keep = conn.execute(
            "SELECT snapshot_id FROM history ORDER BY saved_at DESC LIMIT ?", (_MAX_ITEMS,)
        ).fetchall()

        if rows_to_keep:
            keep_ids = [row["snapshot_id"] for row in rows_to_keep]
            placeholders = ",".join("?" * len(keep_ids))
            conn.execute(f"DELETE FROM history WHERE snapshot_id NOT IN ({placeholders})", keep_ids)
    return snapshot_id


def get_history() -> List[Dict[str, Any]]:
    """Return current history list (completed snapshots only) from SQLite."""
    _ensure_history_table()
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM history WHERE status = 'completed' ORDER BY saved_at DESC"
        ).fetchall()

    history = []
    import base64

    for r in rows:
        payload = json.loads(r["payload_json"])
        # Decode PDF bytes back
        if "pdf_base64" in payload and payload["pdf_base64"]:
            payload["pdf_bytes"] = base64.b64decode(payload["pdf_base64"])
        else:
            payload["pdf_bytes"] = b""

        history.append(
            {
                "snapshot_id": r["snapshot_id"],
                "saved_at": r["saved_at"],
                "initiative_preview": r["initiative_preview"],
                "status": r["status"],
                "artifact_result": r["artifact_result"],
                "content_hash": r["content_hash"],
                "version": r["version"],
                "payload": payload,
            }
        )
    return history
