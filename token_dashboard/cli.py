"""Terminal CLI dashboard using rich.

Features:
- Visual Bar charts for model/session/daily breakdown
- Sparkline trend for daily usage
- Color coding by cost threshold (green / yellow / red)
- Footer with timestamp
"""
import datetime
import sys

from .parser import find_ledger, parse_ledger
from .stats import compute_stats
from .demo import generate_demo_data


# ── Cost threshold color coding ──────────────────────────────
# Below LOW  → green
# LOW–HIGH   → yellow
# Above HIGH → red
LOW_COST = 0.05
HIGH_COST = 0.20


def _cost_style(cost: float) -> str:
    """Return rich style string based on cost threshold."""
    if cost < LOW_COST:
        return "green"
    elif cost < HIGH_COST:
        return "yellow"
    else:
        return "red"


def _cost_bar(value: float, max_value: float, width: int = 20) -> str:
    """Build a horizontal bar string using block characters (█ / ░)."""
    if max_value <= 0:
        filled = 0
    else:
        filled = int(round(value / max_value * width))
    filled = max(0, min(filled, width))
    empty = width - filled
    return "█" * filled + "░" * empty


def _sparkline(values: list[float]) -> str:
    """Render a sparkline from a list of floats using Unicode blocks."""
    if not values:
        return ""
    blocks = " ▁▂▃▄▅▆▇█"
    max_val = max(values)
    min_val = min(values)
    span = max_val - min_val if max_val != min_val else 1.0
    chars = []
    for v in values:
        idx = int(round((v - min_val) / span * 8))
        idx = max(0, min(idx, 8))
        chars.append(blocks[idx])
    return "".join(chars)


def run_cli() -> None:
    """Run the terminal dashboard."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        from rich import box
        from rich.rule import Rule
    except ImportError:
        print("Error: 'rich' package required. Install: pip install rich")
        sys.exit(1)

    # Force UTF-8 output so Unicode bars/sparklines render on Windows GBK consoles.
    import io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    console = Console(legacy_windows=False)

    # ── Find and parse ledger ─────────────────────────────────
    ledger_path = find_ledger()
    demo_mode = False
    if ledger_path is None:
        console.print("[red]No ledger.json found.[/red]")
        console.print("DSH cost-meter plugin may not be installed.")
        console.print(
            "Expected location: ~/.dsh/profiles/*/plugins/dsh-cost-meter/ledger.json"
        )
        records = generate_demo_data()
        demo_mode = True
        console.print("\n[yellow]Showing demo data for illustration.[/yellow]\n")
    else:
        records = parse_ledger(ledger_path)

    if not records:
        console.print("[yellow]No records found in ledger.[/yellow]")
        return

    stats = compute_stats(records)

    # ── Summary Panel ─────────────────────────────────────────
    summary = Text()
    summary.append(f"Sessions: {stats['total_sessions']}\n", style="bold cyan")
    summary.append(f"Records:  {stats['total_records']}\n", style="cyan")
    summary.append(f"Tokens:   {stats['total_tokens']:,}\n", style="bold green")
    summary.append(f"  Input:  {stats['total_input_tokens']:,}\n", style="green")
    summary.append(f"  Output: {stats['total_output_tokens']:,}\n", style="green")
    total_cost = stats["total_cost"]
    cost_color = _cost_style(total_cost)
    summary.append(f"Cost:     ${total_cost:.4f}", style=f"bold {cost_color}")

    title = "[bold]Token Dashboard[/bold]"
    if demo_mode:
        title = "[bold]Token Dashboard[/bold] [dim](demo)[/dim]"
    console.print(Panel(summary, title=title, border_style="blue"))

    # ── Model Breakdown (with Bar) ────────────────────────────
    if stats["by_model"]:
        max_model_cost = max(m["cost"] for m in stats["by_model"]) or 1.0
        max_model_tokens = max(m["tokens"] for m in stats["by_model"]) or 1

        model_table = Table(
            title="By Model",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            title_style="bold magenta",
            padding=(0, 1),
        )
        model_table.add_column("Model", style="cyan", no_wrap=True)
        model_table.add_column("Calls", justify="right")
        model_table.add_column("Token Bar", width=22)
        model_table.add_column("Tokens", justify="right")
        model_table.add_column("Cost Bar", width=22)
        model_table.add_column("Cost", justify="right")

        for m in stats["by_model"]:
            style = _cost_style(m["cost"])
            token_bar = Text(
                _cost_bar(m["tokens"], max_model_tokens, width=20),
                style="blue",
            )
            cost_bar_text = Text(
                _cost_bar(m["cost"], max_model_cost, width=20),
                style=style,
            )
            model_table.add_row(
                m["model"],
                str(m["calls"]),
                token_bar,
                f"{m['tokens']:,}",
                cost_bar_text,
                Text(f"${m['cost']:.4f}", style=style),
            )
        console.print(model_table)

    # ── Daily Breakdown (with Sparkline) ──────────────────────
    if stats["daily"]:
        daily = stats["daily"][-14:]  # last 14 days
        daily_costs = [d["cost"] for d in daily]
        daily_tokens = [d["tokens"] for d in daily]
        cost_spark = _sparkline(daily_costs)
        token_spark = _sparkline(daily_tokens)
        max_daily_cost = max(daily_costs) or 1.0

        daily_table = Table(
            title="Daily Usage (last 14 days)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            title_style="bold magenta",
            padding=(0, 1),
        )
        daily_table.add_column("Date", style="cyan", no_wrap=True)
        daily_table.add_column("Calls", justify="right")
        daily_table.add_column("Tokens", justify="right")
        daily_table.add_column("Cost Bar", width=22)
        daily_table.add_column("Cost", justify="right")

        for d in daily:
            style = _cost_style(d["cost"])
            bar = Text(
                _cost_bar(d["cost"], max_daily_cost, width=20),
                style=style,
            )
            daily_table.add_row(
                d["date"],
                str(d["calls"]),
                f"{d['tokens']:,}",
                bar,
                Text(f"${d['cost']:.4f}", style=style),
            )

        # Sparkline summary row
        sparkline_text = Text()
        sparkline_text.append("  Cost trend:  ", style="dim")
        sparkline_text.append(cost_spark, style="bold yellow")
        spark_line2 = Text()
        spark_line2.append("  Token trend: ", style="dim")
        spark_line2.append(token_spark, style="bold blue")

        console.print(daily_table)
        console.print(sparkline_text)
        console.print(spark_line2)

    # ── Top Sessions (with Bar) ───────────────────────────────
    if stats["by_session"]:
        top = stats["by_session"][:10]
        max_sess_cost = max(s["cost"] for s in top) or 1.0

        sess_table = Table(
            title="Top Sessions by Cost",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            title_style="bold magenta",
            padding=(0, 1),
        )
        sess_table.add_column("Session ID", style="cyan")
        sess_table.add_column("Calls", justify="right")
        sess_table.add_column("Tokens", justify="right")
        sess_table.add_column("Cost Bar", width=22)
        sess_table.add_column("Cost", justify="right")

        for s in top:
            style = _cost_style(s["cost"])
            bar = Text(
                _cost_bar(s["cost"], max_sess_cost, width=20),
                style=style,
            )
            sess_table.add_row(
                s["full_id"][:16] + "...",
                str(s["calls"]),
                f"{s['tokens']:,}",
                bar,
                Text(f"${s['cost']:.4f}", style=style),
            )
        console.print(sess_table)

    # ── Footer with Timestamp ─────────────────────────────────
    console.print(Rule(style="dim"))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threshold_hint = Text()
    threshold_hint.append("  Cost thresholds: ", style="dim")
    threshold_hint.append(f"<${LOW_COST}", style="green")
    threshold_hint.append("  ", style="dim")
    threshold_hint.append(f"${LOW_COST}–${HIGH_COST}", style="yellow")
    threshold_hint.append("  ", style="dim")
    threshold_hint.append(f">=${HIGH_COST}", style="red")
    console.print(threshold_hint)
    console.print(Text(f"  Generated: {now}", style="dim"))
