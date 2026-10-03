"""Parse dsh-cost-meter ledger.json into structured data."""
import json
import os
from pathlib import Path
from typing import Any


def find_ledger() -> Path | None:
    """Locate ledger.json from dsh-cost-meter plugin."""
    candidates = [
        Path.home() / ".dsh" / "profiles" / "desktop" / "plugins" / "dsh-cost-meter" / "ledger.json",
        Path.home() / ".dsh" / "profiles" / "web" / "plugins" / "dsh-cost-meter" / "ledger.json",
        Path.home() / ".dsh" / "cost-meter" / "ledger.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def parse_ledger(path: Path | None = None) -> list[dict[str, Any]]:
    """Parse ledger.json and return list of session records."""
    if path is None:
        path = find_ledger()
    if path is None or not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []

    # dsh-cost-meter ledger format varies; handle common structures
    if isinstance(data, list):
        for item in records_from_list(data):
            records.append(item)
    elif isinstance(data, dict):
        # Could be {sessions: {...}} or {entries: [...]} or flat
        if "sessions" in data:
            for item in records_from_list(data["sessions"]):
                records.append(item)
        elif "entries" in data:
            for item in records_from_list(data["entries"]):
                records.append(item)
        else:
            # Try treating the whole dict as a single session map
            records.append(normalize_record(data))

    return records


def records_from_list(items: list) -> list[dict[str, Any]]:
    """Convert a list of raw items to normalized records."""
    result = []
    for item in items:
        if isinstance(item, dict):
            result.append(normalize_record(item))
    return result


def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw record into a standard format."""
    return {
        "session_id": str(raw.get("sessionId") or raw.get("session_id") or raw.get("id") or "unknown"),
        "model": str(raw.get("model") or raw.get("provider") or "unknown"),
        "input_tokens": int(raw.get("inputTokens") or raw.get("input_tokens") or raw.get("prompt_tokens") or 0),
        "output_tokens": int(raw.get("outputTokens") or raw.get("output_tokens") or raw.get("completion_tokens") or 0),
        "total_tokens": int(raw.get("totalTokens") or raw.get("total_tokens") or 0),
        "cost": float(raw.get("cost") or raw.get("totalCost") or raw.get("total_cost") or 0.0),
        "timestamp": str(raw.get("timestamp") or raw.get("createdAt") or raw.get("created_at") or ""),
        "provider": str(raw.get("provider") or raw.get("llmProvider") or "unknown"),
    }


def load_records(path: str | None = None) -> list[dict[str, Any]]:
    """Convenience: parse from a specific path or auto-detect."""
    p = Path(path) if path else None
    return parse_ledger(p)
