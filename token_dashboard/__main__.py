import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m token_dashboard [cli|web]")
        print("  cli  - Terminal dashboard")
        print("  web  - Web dashboard on http://localhost:8080")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "cli":
        from .cli import run_cli
        run_cli()
    elif cmd == "web":
        from .webapp import run_web
        port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8080
        run_web(port=port)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
