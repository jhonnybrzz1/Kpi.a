import sqlite3
import os
from datetime import datetime, timezone
from utils.ai_metrics import _db, _DB_PATH

def _ensure_telemetry_table() -> None:
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                ts TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_events(ts)")

def record_telemetry_event(event_name: str) -> None:
    """Record a telemetry event to the SQLite database."""
    _ensure_telemetry_table()
    ts = datetime.now(timezone.utc).isoformat()
    with _db() as conn:
        conn.execute(
            "INSERT INTO telemetry_events (event_name, ts) VALUES (?, ?)",
            (event_name, ts)
        )
