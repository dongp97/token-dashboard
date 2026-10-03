"""Flask web server for Token Dashboard."""
import json
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .parser import find_ledger, parse_ledger
from .stats import compute_stats


def create_app() -> Flask:
    """Create and configure the Flask app."""
    web_dir = Path(__file__).parent.parent / "web"
    app = Flask(__name__, static_folder=str(web_dir), static_url_path="")

    @app.route("/")
    def index():
        return send_from_directory(str(web_dir), "index.html")

    @app.route("/api/stats")
    def api_stats():
        ledger_path = find_ledger()
        if ledger_path and ledger_path.exists():
            records = parse_ledger(ledger_path)
        else:
            records = _demo_data()
        stats = compute_stats(records)
        return jsonify(stats)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"})

    return app


def run_web(port: int = 8080):
    """Run the web server."""
    app = create_app()
    print(f"Token Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=port, debug=False)


def _demo_data() -> list[dict]:
    """Generate demo data."""
    import datetime
    records = []
    base = datetime.datetime.now()
    models = ["LongCat-2.0", "deepseek-chat", "gpt-4o", "claude-3.5-sonnet"]
    for i in range(50):
        day_offset = i // 5
        ts = (base - datetime.timedelta(days=day_offset)).isoformat()
        records.append({
            "session_id": f"session-{i:04d}-demo",
            "model": models[i % len(models)],
            "input_tokens": 1000 + i * 200,
            "output_tokens": 500 + i * 100,
            "total_tokens": 1500 + i * 300,
            "cost": round(0.01 + i * 0.005, 4),
            "timestamp": ts,
            "provider": "demo",
        })
    return records


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_web(port)
