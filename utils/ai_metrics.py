"""
AI observability: per-call recording and 7-day aggregated metrics.
Storage: SQLite (stdlib only, no extra deps).
"""

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_metrics.db")

# ── Minimum required fields per schema ───────────────────────────────────────
_REQUIRED_FIELDS: Dict[str, List[str]] = {
    "context_analysis": ["tipo", "objetivo", "etapa_funil", "resumo_prd"],
    "metrics_analysis": ["north_star", "l1_health_indicators", "okrs"],
}


# ── JSON validation ───────────────────────────────────────────────────────────

def validate_json_structure(
    raw: str, schema_key: str = "metrics_analysis"
) -> Dict[str, Any]:
    """
    Validate raw JSON string against the minimum schema.

    Returns:
        {
            "json_valid": bool,
            "json_error_type": "parse_error"|"missing_field"|"type_error"|"unknown_error"|None,
            "json_error_detail": str | None,
        }
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as e:
        return {"json_valid": False, "json_error_type": "parse_error",
                "json_error_detail": str(e)[:200]}

    if not isinstance(data, dict):
        return {"json_valid": False, "json_error_type": "type_error",
                "json_error_detail": f"expected dict, got {type(data).__name__}"}

    required = _REQUIRED_FIELDS.get(schema_key, [])
    for field in required:
        if field not in data:
            return {"json_valid": False, "json_error_type": "missing_field",
                    "json_error_detail": f"missing: {field}"}
        if data[field] is None:
            return {"json_valid": False, "json_error_type": "type_error",
                    "json_error_detail": f"null value: {field}"}

    return {"json_valid": True, "json_error_type": None, "json_error_detail": None}


# ── SQLite helpers ────────────────────────────────────────────────────────────

@contextmanager
def _db():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_table() -> None:
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_calls (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id  TEXT NOT NULL,
                ts            TEXT NOT NULL,
                model         TEXT NOT NULL,
                provider      TEXT NOT NULL,
                prompt_version TEXT NOT NULL DEFAULT 'v1',
                temperature   REAL,
                latency_ms    INTEGER NOT NULL,
                json_valid    INTEGER NOT NULL,
                json_error_type TEXT,
                usage_available INTEGER NOT NULL,
                prompt_tokens   INTEGER,
                completion_tokens INTEGER,
                total_tokens    INTEGER
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON ai_calls(ts)")


# ── Public API ────────────────────────────────────────────────────────────────

def record_call(
    *,
    model: str,
    provider: str,
    latency_ms: int,
    json_valid: bool,
    json_error_type: Optional[str] = None,
    usage: Optional[Dict[str, int]] = None,
    temperature: Optional[float] = None,
    prompt_version: str = "v1",
) -> str:
    """Persist one AI call record. Returns the generated operation_id."""
    _ensure_table()
    operation_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    usage_available = usage is not None
    with _db() as conn:
        conn.execute(
            """INSERT INTO ai_calls
               (operation_id, ts, model, provider, prompt_version, temperature,
                latency_ms, json_valid, json_error_type,
                usage_available, prompt_tokens, completion_tokens, total_tokens)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                operation_id, ts, model, provider, prompt_version, temperature,
                latency_ms, int(json_valid), json_error_type,
                int(usage_available),
                usage.get("prompt_tokens") if usage else None,
                usage.get("completion_tokens") if usage else None,
                usage.get("total_tokens") if usage else None,
            ),
        )
    return operation_id


def get_metrics_summary(days: int = 7) -> Dict[str, Any]:
    """
    Return aggregated metrics for the last `days` days, grouped by model.
    Compatible with the /metrics/ai contract.
    """
    _ensure_table()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT
                model,
                COUNT(*)                                        AS total_calls,
                SUM(CASE WHEN json_valid=0 THEN 1 ELSE 0 END)  AS invalid_json_count,
                AVG(latency_ms)                                 AS avg_latency_ms,
                SUM(CASE WHEN usage_available=1 THEN 1 ELSE 0 END) AS usage_available_calls,
                AVG(CASE WHEN usage_available=1 THEN prompt_tokens END)     AS avg_prompt_tokens,
                AVG(CASE WHEN usage_available=1 THEN completion_tokens END) AS avg_completion_tokens
            FROM ai_calls
            WHERE ts >= ?
            GROUP BY model
            """,
            (since,),
        ).fetchall()

    by_model = []
    for r in rows:
        total = r["total_calls"]
        by_model.append({
            "model": r["model"],
            "totalCalls": total,
            "invalidJsonRate": round(r["invalid_json_count"] / total, 4) if total else 0,
            "avgLatencyMs": round(r["avg_latency_ms"], 1) if r["avg_latency_ms"] else None,
            "avgPromptTokens": round(r["avg_prompt_tokens"], 1) if r["avg_prompt_tokens"] else None,
            "avgCompletionTokens": round(r["avg_completion_tokens"], 1) if r["avg_completion_tokens"] else None,
            "tokenCoverageRate": round(r["usage_available_calls"] / total, 4) if total else 0,
        })

    return {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "windowDays": days,
        "byModel": by_model,
    }
