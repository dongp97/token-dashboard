"""Compute statistics from parsed ledger records."""
from collections import defaultdict
from typing import Any


def compute_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute comprehensive stats from records.

    Enhanced metrics include:
      - input_output_ratio per model
      - avg_tokens_per_call per model
      - avg_cost_per_call per model
      - cost_per_1k_tokens per model
      - peak_day (day with highest cost)
      - rolling_7day: 7-day rolling average of daily tokens and cost
    """
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
            "peak_day": None,
            "rolling_7day": [],
        }

    total_input = sum(r["input_tokens"] for r in records)
    total_output = sum(r["output_tokens"] for r in records)
    total_cost = sum(r["cost"] for r in records)

    # ── By model ────────────────────────────────────────────────
    model_stats: dict[str, dict] = defaultdict(
        lambda: {"tokens": 0, "cost": 0.0, "calls": 0, "input_tokens": 0, "output_tokens": 0}
    )
    for r in records:
        m = r["model"]
        model_stats[m]["tokens"] += r["input_tokens"] + r["output_tokens"]
        model_stats[m]["input_tokens"] += r["input_tokens"]
        model_stats[m]["output_tokens"] += r["output_tokens"]
        model_stats[m]["cost"] += r["cost"]
        model_stats[m]["calls"] += 1

    by_model = []
    for k, v in sorted(model_stats.items(), key=lambda x: x[1]["cost"], reverse=True):
        calls = v["calls"]
        tokens = v["tokens"]
        cost = v["cost"]
        input_t = v["input_tokens"]
        output_t = v["output_tokens"]
        by_model.append({
            "model": k,
            "calls": calls,
            "tokens": tokens,
            "cost": round(cost, 4),
            "input_tokens": input_t,
            "output_tokens": output_t,
            "input_output_ratio": round(input_t / output_t, 4) if output_t > 0 else 0.0,
            "avg_tokens_per_call": round(tokens / calls, 2) if calls > 0 else 0,
            "avg_cost_per_call": round(cost / calls, 6) if calls > 0 else 0.0,
            "cost_per_1k_tokens": round(cost / (tokens / 1000), 6) if tokens > 0 else 0.0,
        })

    # ── By session ───────────────────────────────────────────────
    session_stats: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
    for r in records:
        s = r["session_id"][:12]  # truncate for display
        session_stats[s]["tokens"] += r["input_tokens"] + r["output_tokens"]
        session_stats[s]["cost"] += r["cost"]
        session_stats[s]["calls"] += 1
        session_stats[s]["full_id"] = r["session_id"]
    by_session = [
        {"session": k, **v} for k, v in sorted(session_stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    ][:20]

    # ── Daily breakdown ──────────────────────────────────────────
    daily_stats: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
    for r in records:
        day = r["timestamp"][:10] if r["timestamp"] else "unknown"
        daily_stats[day]["tokens"] += r["input_tokens"] + r["output_tokens"]
        daily_stats[day]["cost"] += r["cost"]
        daily_stats[day]["calls"] += 1
    daily = [{"date": k, **v} for k, v in sorted(daily_stats.items())]

    # ── Peak day (highest cost) ──────────────────────────────────
    peak_day = max(daily, key=lambda d: d["cost"]) if daily else None

    # ── 7-day rolling average ────────────────────────────────────
    rolling_7day = _rolling_average(days=daily, window=7)

    return {
        "total_sessions": len(set(r["session_id"] for r in records)),
        "total_records": len(records),
        "total_tokens": total_input + total_output,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost": round(total_cost, 4),
        "by_model": by_model,
        "by_session": by_session,
        "daily": daily,
        "peak_day": peak_day,
        "rolling_7day": rolling_7day,
    }


def _rolling_average(days: list[dict], window: int = 7) -> list[dict]:
    """Compute rolling average over the last *window* days.

    Returns one entry per day with the window's avg tokens and avg cost.
    For days where fewer than *window* prior days exist, averages over
    however many are available.
    """
    if not days:
        return []

    result = []
    for i in range(len(days)):
        start = max(0, i - window + 1)
        window_days = days[start : i + 1]
        n = len(window_days)
        avg_tokens = sum(d["tokens"] for d in window_days) / n
        avg_cost = sum(d["cost"] for d in window_days) / n
        result.append({
            "date": days[i]["date"],
            "avg_tokens": round(avg_tokens, 2),
            "avg_cost": round(avg_cost, 6),
            "window_days": n,
        })
    return result
