"""CLI entrypoint: scrape NBC / Ligi Kuu data."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from scraper import __version__
from scraper.core.config import DEFAULT_SOURCE_CONFIG
from scraper.core.pipeline import ScrapePipeline

app = typer.Typer(
    name="nbc-soka",
    help=(
        "NBC Ligi Kuu data: collect match scores & tables, save JSON, serve a simple API. "
        "For journalists, fans, and developers."
    ),
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


@app.command("version")
def version() -> None:
    """Print package version."""
    console.print(__version__)


@app.command("run")
def run(
    config: Path = typer.Option(
        DEFAULT_SOURCE_CONFIG,
        "--config",
        "-c",
        help="Path to source config (config/ligikuu.json)",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Output data directory (default: data/ from config)",
    ),
    full: bool = typer.Option(
        False,
        "--full",
        help="Store all events/tables without season filtering (disables incremental)",
    ),
    incremental: Optional[bool] = typer.Option(
        None,
        "--incremental/--no-incremental",
        help=(
            "Pull only changes since last run (modified_after) and merge by id. "
            "Default: on when not --full and data/meta/last_run.json exists."
        ),
    ),
    seasons: int = typer.Option(
        3,
        "--seasons",
        help="How many most-recent seasons to auto-track (includes upcoming 2026/27)",
    ),
    players: bool = typer.Option(
        False,
        "--players",
        help="Also scrape players (large)",
    ),
    max_pages: Optional[int] = typer.Option(
        None,
        "--max-pages",
        help="Limit pages per resource (useful for smoke tests)",
    ),
) -> None:
    """Run the scraper and write JSON under data/ (auto-tracks NBC 2026/27 when present)."""
    pipeline = ScrapePipeline(
        config_path=config,
        out_dir=out,
        full=full,
        incremental=incremental,
        keep_recent_seasons=seasons,
        include_players=players,
        max_pages=max_pages,
    )
    summary = pipeline.run()

    table = Table(title="Scrape summary")
    table.add_column("Resource")
    table.add_column("Stored", justify="right")
    table.add_column("Fetched", justify="right")
    table.add_column("Δ?")
    for name, info in summary.get("resources", {}).items():
        count = info.get("stored_count", info.get("raw_count", 0))
        fetched = info.get("fetched_count", info.get("raw_count", ""))
        delta = "yes" if info.get("incremental") else ""
        table.add_row(name, str(count), str(fetched), delta)
    console.print(table)

    plan = summary.get("season_plan") or {}
    console.print(
        f"Mode: {summary.get('mode')} | "
        f"Active seasons: {plan.get('active_season_ids')} | "
        f"Active leagues: {len(plan.get('active_league_ids') or [])}"
    )
    if summary.get("modified_after"):
        console.print(f"modified_after: {summary['modified_after']}")
    if not summary.get("ok"):
        raise typer.Exit(code=1)


@app.command("serve")
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Use 0.0.0.0 for live/deploy"),
    port: int = typer.Option(8000, "--port"),
    data_dir: Path = typer.Option(
        Path("data"),
        "--data-dir",
        help="Directory containing scraped JSON (data/ligikuu/...)",
    ),
    reload: bool = typer.Option(False, "--reload"),
) -> None:
    """Serve scores & tables (open / in a browser for a simple home page)."""
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        console.print("[red]uvicorn is required: pip install uvicorn fastapi[/red]")
        raise typer.Exit(code=1) from exc

    import os

    from api.app import create_app

    os.environ["DATA_DIR"] = str(data_dir.resolve())
    app_instance = create_app(data_dir=data_dir)
    console.print(f"[green]NBC Ligi Kuu Data[/green] → http://{host}:{port}/")
    console.print("  Easy paths: /scores  /table  /teams  /docs")
    uvicorn.run(app_instance, host=host, port=port, reload=reload)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
