"""Shared demo data generator for Token Dashboard."""
import datetime
import random


def generate_demo_data(seed: int = 42) -> list[dict]:
    """Generate 50 demo records across 4 models and 10 days.

    Deterministic with a fixed seed so CLI and webapp show identical data.
    Each record has the same schema produced by parser.normalize_record().
    """
    rng = random.Random(seed)
    records: list[dict] = []
    base = datetime.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    models = ["LongCat-2.0", "deepseek-chat", "gpt-4o", "claude-3.5-sonnet"]
    providers = {
        "LongCat-2.0": "longcat",
        "deepseek-chat": "deepseek",
        "gpt-4o": "openai",
        "claude-3.5-sonnet": "anthropic",
    }

    for i in range(50):
        day_offset = i // 5  # 0..9 → 10 days, 5 records each
        model = models[i % len(models)]
        ts = (base - datetime.timedelta(days=day_offset, hours=rng.randint(0, 6))).isoformat()
        input_tokens = rng.randint(500, 5000)
        output_tokens = rng.randint(200, 2000)
        records.append({
            "session_id": f"demo-session-{i:04d}-{model.split('-')[0]}",
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": round((input_tokens * 0.0005 + output_tokens * 0.0015) / 1000, 4),
            "timestamp": ts,
            "provider": providers[model],
        })

    return records
