"""Flask web server for Token Dashboard."""
import json
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .demo import generate_demo_data
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
            records = generate_demo_data()
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


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_web(port)
