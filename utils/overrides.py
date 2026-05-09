"""
Persistent manual overrides for generated metrics.
Storage: SQLite (ai_metrics.db).
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict

from utils.ai_metrics import _db


def _ensure_overrides_table() -> None:
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS overrides (
                snapshot_id TEXT NOT NULL,
                item_key TEXT NOT NULL,
                field_name TEXT NOT NULL,
                manual_value TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (snapshot_id, item_key, field_name)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_overrides_snapshot ON overrides(snapshot_id)")


def save_override(snapshot_id: str, item_key: str, field_name: str, value: str) -> None:
    """Save a manual override for a specific field in a metric item."""
    _ensure_overrides_table()
    updated_at = datetime.now(timezone.utc).isoformat()
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO overrides (snapshot_id, item_key, field_name, manual_value, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(snapshot_id, item_key, field_name) DO UPDATE SET
            manual_value=excluded.manual_value,
            updated_at=excluded.updated_at
        """,
            (snapshot_id, item_key, field_name, value, updated_at),
        )


def get_overrides(snapshot_id: str) -> Dict[str, Dict[str, str]]:
    """
    Get all overrides for a given snapshot.
    Returns: { item_key: { field_name: manual_value } }
    """
    _ensure_overrides_table()
    with _db() as conn:
        rows = conn.execute(
            "SELECT item_key, field_name, manual_value FROM overrides WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchall()

    overrides = {}
    for r in rows:
        ik = r["item_key"]
        if ik not in overrides:
            overrides[ik] = {}
        overrides[ik][r["field_name"]] = r["manual_value"]
    return overrides


def delete_overrides(snapshot_id: str) -> None:
    """Delete all overrides for a given snapshot (used during Reanalisar)."""
    _ensure_overrides_table()
    with _db() as conn:
        conn.execute("DELETE FROM overrides WHERE snapshot_id = ?", (snapshot_id,))


def generate_item_key(*args: str) -> str:
    """Generate a stable 8-char key based on original content components."""
    content = "|".join(str(a) for a in args)
    return hashlib.sha256(content.encode()).hexdigest()[:8]
