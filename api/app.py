"""NBC Ligi Kuu data API — simple paths for humans, full paths for apps.

Run:
  python -m scraper serve --data-dir data
  DATA_DIR=data uvicorn api.app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from scraper.utils.jsonio import read_json

DEFAULT_DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))

HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NBC Ligi Kuu Data</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { max-width: 40rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
    h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
    .tag { color: #666; font-size: 0.95rem; }
    a { color: #0b57d0; }
    code, .path { font-family: ui-monospace, monospace; font-size: 0.9rem; }
    ul { padding-left: 1.2rem; }
    .box { border: 1px solid #ccc; border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; }
    .sw { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd; }
  </style>
</head>
<body>
  <h1>NBC Ligi Kuu Data</h1>
  <p class="tag">Free match scores &amp; league tables for Tanzania’s NBC Premier League</p>

  <div class="box">
    <strong>In one sentence:</strong>
    We collect public Ligi Kuu scores and share them so journalists, fans, and apps
    can reuse them easily.
  </div>

  <h2>Easy links</h2>
  <ul>
    <li><a href="/scores"><code>/scores</code></a> — match results &amp; fixtures</li>
    <li><a href="/table"><code>/table</code></a> — league standings</li>
    <li><a href="/teams"><code>/teams</code></a> — clubs</li>
    <li><a href="/seasons/2026-27"><code>/seasons/2026-27</code></a> — one season pack</li>
    <li><a href="/health"><code>/health</code></a> — is the service working?</li>
    <li><a href="/docs"><code>/docs</code></a> — full technical docs</li>
  </ul>

  <p>Examples: <code>/scores?season=2026-27</code> · <code>/table?season=2025-26</code></p>
  <p>Plain-language guide: see the project file <strong>ABOUT.md</strong> (English + Kiswahili).</p>
  <p>Source website: <a href="https://ligikuu.co.tz" rel="noopener">ligikuu.co.tz</a>
     (this API is a helper, not the official league office).</p>

  <div class="sw">
    <h2>Kiswahili (fupi)</h2>
    <p><strong>Sentensi moja:</strong> Tunakusanya matokeo ya NBC Ligi Kuu na kuyashiriki
    kwa waandishi, mashabiki, na programu — bila kuandika tena kwa mkono.</p>
    <ul>
      <li><a href="/scores"><code>/scores</code></a> — matokeo</li>
      <li><a href="/table"><code>/table</code></a> — jedwali</li>
      <li><a href="/teams"><code>/teams</code></a> — timu</li>
    </ul>
  </div>
</body>
</html>
"""


def _load(path: Path) -> Any:
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Data not found ({path.name}). "
                "Run the scraper first, or set DATA_DIR to a folder that contains ligikuu/."
            ),
        )
    return read_json(path)


def _season_id_for_slug(seasons_payload: dict[str, Any], slug: str) -> int | None:
    for item in seasons_payload.get("items") or []:
        if str(item.get("slug") or "") == slug:
            return int(item["id"])
    # allow "2026/27" style
    alt = slug.replace("/", "-")
    for item in seasons_payload.get("items") or []:
        if str(item.get("slug") or "") == alt:
            return int(item["id"])
    return None


def create_app(data_dir: Path | str | None = None) -> FastAPI:
    root = Path(data_dir) if data_dir is not None else Path(
        os.environ.get("DATA_DIR", DEFAULT_DATA_DIR)
    )
    source_dir = root / "ligikuu"
    meta_dir = root / "meta"

    app = FastAPI(
        title="NBC Ligi Kuu Data",
        description=(
            "Simple, free NBC Premier League (Ligi Kuu) scores and tables for Tanzania. "
            "Easy paths: /scores, /table, /teams. "
            "For journalists, students, fans, and developers. "
            "Not the official league office — data is collected from public ligikuu.co.tz."
        ),
        version="0.1.0",
        contact={"name": "Project README / ABOUT.md"},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    def _resource(name: str, *, normalized: bool = True) -> Any:
        if normalized:
            path = source_dir / "normalized" / f"{name}.json"
            if path.is_file():
                return _load(path)
        return _load(source_dir / f"{name}.json")

    def _resolve_season_id(season: str | None, season_id: int | None) -> int | None:
        if season_id is not None:
            return season_id
        if not season:
            return None
        seasons_payload = _resource("seasons")
        resolved = _season_id_for_slug(seasons_payload, season)
        if resolved is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown season '{season}'. Try e.g. 2026-27 or 2025-26.",
            )
        return resolved

    # ── Human-friendly home & shortcuts ──────────────────────────────

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> str:
        return HOME_HTML

    @app.get("/health")
    def health() -> dict[str, Any]:
        index = source_dir / "index.json"
        scraped_at = None
        has_data = index.is_file()
        if has_data:
            scraped_at = _load(index).get("scraped_at")
        return {
            "ok": True,
            "service": "NBC Ligi Kuu Data",
            "has_data": has_data,
            "updated_at": scraped_at,
            "message_en": "Service is running."
            + (" Data is available." if has_data else " No data yet — run the scraper."),
            "message_sw": "Huduma inafanya kazi."
            + (" Data ipo." if has_data else " Bado hakuna data — endesha scraper."),
        }

    @app.get("/scores", tags=["simple"])
    def scores(
        season: str | None = Query(
            None,
            description="Season slug, e.g. 2026-27 or 2025-26",
            examples=["2026-27"],
        ),
        season_id: int | None = Query(None, description="Internal season id (optional)"),
        league_id: int | None = Query(None),
        status: str | None = Query(None, description="publish = played, future = upcoming"),
        limit: int | None = Query(50, ge=1, le=5000, description="Max matches to return"),
    ) -> Any:
        """Match results and fixtures (simple name for /events)."""
        sid = _resolve_season_id(season, season_id)
        payload = _resource("events")
        items = list(payload.get("items") or [])
        if sid is not None:
            items = [e for e in items if sid in (e.get("seasons") or [])]
        if league_id is not None:
            items = [e for e in items if league_id in (e.get("leagues") or [])]
        if status is not None:
            items = [e for e in items if e.get("status") == status]
        if limit is not None:
            items = items[:limit]
        return {
            "what": "Match scores and fixtures — NBC / Ligi Kuu",
            "source": "ligikuu",
            "updated_at": payload.get("scraped_at"),
            "count": len(items),
            "filters": {
                "season": season,
                "season_id": sid,
                "league_id": league_id,
                "status": status,
                "limit": limit,
            },
            "items": items,
        }

    @app.get("/table", tags=["simple"])
    def table(
        season: str | None = Query(None, description="Season slug, e.g. 2026-27"),
        season_id: int | None = Query(None),
        league_id: int | None = Query(None),
    ) -> Any:
        """League standings / jedwali."""
        sid = _resolve_season_id(season, season_id)
        payload = _resource("tables")
        items = list(payload.get("items") or [])
        if sid is not None:
            items = [t for t in items if sid in (t.get("seasons") or [])]
        if league_id is not None:
            items = [t for t in items if league_id in (t.get("leagues") or [])]
        return {
            "what": "League table (standings) — NBC / Ligi Kuu",
            "source": "ligikuu",
            "updated_at": payload.get("scraped_at"),
            "count": len(items),
            "filters": {"season": season, "season_id": sid, "league_id": league_id},
            "items": items,
        }

    @app.get("/teams", tags=["simple"])
    def teams_simple() -> Any:
        """Clubs / timu."""
        payload = _resource("teams")
        return {
            "what": "Teams (clubs) — NBC / Ligi Kuu ecosystem",
            "source": "ligikuu",
            "updated_at": payload.get("scraped_at"),
            "count": payload.get("count", len(payload.get("items") or [])),
            "items": payload.get("items") or [],
        }

    @app.get("/seasons/{slug}", tags=["simple"])
    def season_simple(slug: str) -> Any:
        """One season pack (events + tables + teams when available)."""
        path = source_dir / "seasons" / f"{slug}.json"
        data = _load(path)
        return {
            "what": f"Season pack for {slug}",
            "source": "ligikuu",
            **data,
        }

    # ── Full API (v1) — same data, stable names for apps ─────────────

    @app.get("/api/v1")
    def api_root() -> dict[str, Any]:
        return {
            "name": "NBC Ligi Kuu Data",
            "simple_paths": ["/scores", "/table", "/teams", "/seasons/{slug}", "/health"],
            "docs": "/docs",
            "about": "See ABOUT.md in the repository (English + Kiswahili).",
            "endpoints": [
                "/api/v1/sources/ligikuu",
                "/api/v1/sources/ligikuu/seasons",
                "/api/v1/sources/ligikuu/leagues",
                "/api/v1/sources/ligikuu/teams",
                "/api/v1/sources/ligikuu/events",
                "/api/v1/sources/ligikuu/tables",
                "/api/v1/sources/ligikuu/seasons/{slug}",
                "/api/v1/sources/ligikuu/meta/last-run",
            ],
        }

    @app.get("/api/v1/sources/ligikuu")
    def source_index() -> Any:
        return _load(source_dir / "index.json")

    @app.get("/api/v1/sources/ligikuu/meta/last-run")
    def last_run() -> Any:
        return _load(meta_dir / "last_run.json")

    @app.get("/api/v1/sources/ligikuu/seasons")
    def seasons() -> Any:
        return _resource("seasons")

    @app.get("/api/v1/sources/ligikuu/leagues")
    def leagues() -> Any:
        return _resource("leagues")

    @app.get("/api/v1/sources/ligikuu/teams")
    def teams() -> Any:
        return _resource("teams")

    @app.get("/api/v1/sources/ligikuu/venues")
    def venues() -> Any:
        return _resource("venues")

    @app.get("/api/v1/sources/ligikuu/events")
    def events(
        season_id: int | None = Query(None),
        league_id: int | None = Query(None),
        status: str | None = Query(None),
        limit: int | None = Query(None, ge=1, le=5000),
    ) -> Any:
        payload = _resource("events")
        items = list(payload.get("items") or [])
        if season_id is not None:
            items = [e for e in items if season_id in (e.get("seasons") or [])]
        if league_id is not None:
            items = [e for e in items if league_id in (e.get("leagues") or [])]
        if status is not None:
            items = [e for e in items if e.get("status") == status]
        if limit is not None:
            items = items[:limit]
        return {
            **{k: v for k, v in payload.items() if k != "items"},
            "count": len(items),
            "filters": {
                "season_id": season_id,
                "league_id": league_id,
                "status": status,
                "limit": limit,
            },
            "items": items,
        }

    @app.get("/api/v1/sources/ligikuu/tables")
    def tables(
        season_id: int | None = Query(None),
        league_id: int | None = Query(None),
    ) -> Any:
        payload = _resource("tables")
        items = list(payload.get("items") or [])
        if season_id is not None:
            items = [t for t in items if season_id in (t.get("seasons") or [])]
        if league_id is not None:
            items = [t for t in items if league_id in (t.get("leagues") or [])]
        return {
            **{k: v for k, v in payload.items() if k != "items"},
            "count": len(items),
            "filters": {"season_id": season_id, "league_id": league_id},
            "items": items,
        }

    @app.get("/api/v1/sources/ligikuu/seasons/{slug}")
    def season_bundle(slug: str) -> Any:
        path = source_dir / "seasons" / f"{slug}.json"
        return _load(path)

    @app.get("/api/v1/sources/ligikuu/raw/{resource}")
    def raw_resource(resource: str) -> Any:
        safe = resource.replace("..", "").replace("/", "")
        return _load(source_dir / "raw" / f"{safe}.json")

    return app


app = create_app()
