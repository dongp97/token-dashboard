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


def find_all_ledgers() -> list[Path]:
    """Find all ledger.json files under known profile directories.

    Searches ~/.dsh/profiles/*/plugins/*/ledger.json and ~/.dsh/*/ledger.json
    to support multi-profile or multi-plugin installations.
    """
    ledgers: list[Path] = []
    dsh_dir = Path.home() / ".dsh"
    if not dsh_dir.exists():
        return ledgers

    # Profile-scoped plugin ledgers: ~/.dsh/profiles/<profile>/plugins/*/ledger.json
    profiles_dir = dsh_dir / "profiles"
    if profiles_dir.exists():
        for plugin_dir in profiles_dir.glob("plugins/*/"):
            candidate = plugin_dir / "ledger.json"
            if candidate.exists():
                ledgers.append(candidate)

    # Top-level cost-meter variants: ~/.dsh/*/ledger.json
    for candidate in dsh_dir.glob("*/ledger.json"):
        if candidate not in ledgers:
            ledgers.append(candidate)

    # Deduplicate via resolved real paths
    seen: set[str] = set()
    unique: list[Path] = []
    for p in ledgers:
        resolved = str(p.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(p)
    return unique


def parse_ledger(path: Path | None = None) -> list[dict[str, Any]]:
    """Parse ledger.json and return list of session records.

    Handles multiple nested formats:
      - Plain list of records
      - {"sessions": [...]} or {"entries": [...]}
      - {"data": [...]} or {"data": {"sessions": [...]}}
      - {"ledger": {"entries": [...]}}
      - Dict-of-dicts: {"session_id_1": {...}, "session_id_2": {...}}

    JSON parse errors are caught and return an empty list.
    """
    if path is None:
        path = find_ledger()
    if path is None or not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    return _extract_records(data)


def _extract_records(data: Any) -> list[dict[str, Any]]:
    """Recursively extract normalized records from various nested structures."""
    records: list[dict[str, Any]] = []

    if data is None:
        return records

    if isinstance(data, list):
        for item in data:
            records.extend(_extract_records(item))
        return records

    if isinstance(data, dict):
        # Check for known list-wrapped keys at this level
        list_keys = ("sessions", "entries", "records", "data", "items", "ledger", "results")
        for key in list_keys:
            if key in data and data[key] is not None:
                records.extend(_extract_records(data[key]))
                return records

        # Dict-of-dicts: keys are session IDs, values are record dicts
        # Heuristic: every value is a dict → treat as dict-of-dicts
        if data and all(isinstance(v, dict) for v in data.values()):
            for key, value in data.items():
                rec = normalize_record(value)
                # Use the dict key as session_id if record lacks one
                if rec.get("session_id") == "unknown":
                    rec["session_id"] = str(key)
                records.append(rec)
            return records

        # Single record dict
        records.append(normalize_record(data))
        return records

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
