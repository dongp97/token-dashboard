"""Terminal CLI dashboard using rich."""
import sys
from .parser import find_ledger, parse_ledger
from .stats import compute_stats


def run_cli():
    """Run the terminal dashboard."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.layout import Layout
        from rich.text import Text
        from rich import box
    except ImportError:
        print("Error: 'rich' package required. Install: pip install rich")
        sys.exit(1)

    console = Console()

    # Find and parse ledger
    ledger_path = find_ledger()
    if ledger_path is None:
        console.print("[red]No ledger.json found.[/red]")
        console.print("DSH cost-meter plugin may not be installed.")
        console.print("Expected location: ~/.dsh/profiles/*/plugins/dsh-cost-meter/ledger.json")
        # Show demo data
        records = _demo_data()
        console.print("\n[yellow]Showing demo data for illustration.[/yellow]\n")
    else:
        records = parse_ledger(ledger_path)

    if not records:
        console.print("[yellow]No records found in ledger.[/yellow]")
        return

    stats = compute_stats(records)

    # === Summary Panel ===
    summary = Text()
    summary.append(f"Sessions: {stats['total_sessions']}\n", style="bold cyan")
    summary.append(f"Records:  {stats['total_records']}\n", style="cyan")
    summary.append(f"Tokens:   {stats['total_tokens']:,}\n", style="bold green")
    summary.append(f"  Input:  {stats['total_input_tokens']:,}\n", style="green")
    summary.append(f"  Output: {stats['total_output_tokens']:,}\n", style="green")
    summary.append(f"Cost:     ${stats['total_cost']:.4f}", style="bold yellow")

    console.print(Panel(summary, title="[bold]Token Dashboard[/bold]", border_style="blue"))

    # === Model Breakdown ===
    if stats["by_model"]:
        model_table = Table(title="By Model", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        model_table.add_column("Model", style="cyan")
        model_table.add_column("Calls", justify="right")
        model_table.add_column("Tokens", justify="right")
        model_table.add_column("Cost", justify="right", style="yellow")

        for m in stats["by_model"]:
            model_table.add_row(
                m["model"],
                str(m["calls"]),
                f"{m['tokens']:,}",
                f"${m['cost']:.4f}",
            )
        console.print(model_table)

    # === Daily Breakdown ===
    if stats["daily"]:
        daily_table = Table(title="Daily Usage", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        daily_table.add_column("Date", style="cyan")
        daily_table.add_column("Calls", justify="right")
        daily_table.add_column("Tokens", justify="right")
        daily_table.add_column("Cost", justify="right", style="yellow")

        for d in stats["daily"][-14:]:  # last 14 days
            daily_table.add_row(
                d["date"],
                str(d["calls"]),
                f"{d['tokens']:,}",
                f"${d['cost']:.4f}",
            )
        console.print(daily_table)

    # === Top Sessions ===
    if stats["by_session"]:
        sess_table = Table(title="Top Sessions by Cost", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        sess_table.add_column("Session ID", style="cyan")
        sess_table.add_column("Calls", justify="right")
        sess_table.add_column("Tokens", justify="right")
        sess_table.add_column("Cost", justify="right", style="yellow")

        for s in stats["by_session"][:10]:
            sess_table.add_row(
                s["full_id"][:16] + "...",
                str(s["calls"]),
                f"{s['tokens']:,}",
                f"${s['cost']:.4f}",
            )
        console.print(sess_table)


def _demo_data() -> list[dict]:
    """Generate demo data for illustration."""
    import datetime
    records = []
    base = datetime.datetime.now()
    models = ["LongCat-2.0", "deepseek-chat", "gpt-4o", "claude-3.5-sonnet"]
    for i in range(50):
        day_offset = i // 5
        ts = (base - datetime.timedelta(days=day_offset)).isoformat()
        records.append({
            "session_id": f"session-{i:04d}-demo-session-id",
            "model": models[i % len(models)],
            "input_tokens": 1000 + i * 200,
            "output_tokens": 500 + i * 100,
            "total_tokens": 1500 + i * 300,
            "cost": round(0.01 + i * 0.005, 4),
            "timestamp": ts,
            "provider": "demo",
        })
    return records
