"""Compute statistics from parsed ledger records."""
from collections import defaultdict
from typing import Any


def compute_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute comprehensive stats from records."""
    if not records:
        return {
            "total_sessions": 0,
            "total_tokens": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "by_model": [],
            "by_session": [],
            "daily": [],
        }

    total_input = sum(r["input_tokens"] for r in records)
    total_output = sum(r["output_tokens"] for r in records)
    total_cost = sum(r["cost"] for r in records)

    # By model
    model_stats: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
    for r in records:
        m = r["model"]
        model_stats[m]["tokens"] += r["input_tokens"] + r["output_tokens"]
        model_stats[m]["cost"] += r["cost"]
        model_stats[m]["calls"] += 1
    by_model = [
        {"model": k, **v} for k, v in sorted(model_stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    ]

    # By session
    session_stats: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
    for r in records:
        s = r["session_id"][:12]  # truncate for display
        session_stats[s]["tokens"] += r["input_tokens"] + r["output_tokens"]
        session_stats[s]["cost"] += r["cost"]
        session_stats[s]["calls"] += 1
        session_stats[s]["full_id"] = r["session_id"]
    by_session = [
        {"session": k, **v} for k, v in sorted(session_stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    ]

    # Daily breakdown
    daily_stats: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
    for r in records:
        day = r["timestamp"][:10] if r["timestamp"] else "unknown"
        daily_stats[day]["tokens"] += r["input_tokens"] + r["output_tokens"]
        daily_stats[day]["cost"] += r["cost"]
        daily_stats[day]["calls"] += 1
    daily = [
        {"date": k, **v} for k, v in sorted(daily_stats.items())
    ]

    return {
        "total_sessions": len(set(r["session_id"] for r in records)),
        "total_records": len(records),
        "total_tokens": total_input + total_output,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost": round(total_cost, 4),
        "by_model": by_model,
        "by_session": by_session[:20],  # top 20
        "daily": daily,
    }
