# Architecture

## Goals

1. **Scrape** official Tanzanian football data (NBC Premier League / Ligi Kuu).
2. **Store** versioned JSON under `data/` automatically (GitHub Actions).
3. **Serve** that data via a small read-only HTTP API.
4. **Auto-track new seasons** (e.g. NBC **2026/2027**) without hard-coding a single league id forever.

## Components

```
config/ligikuu.json          ← source map (endpoints, focus, HTTP policy)
        │
        ▼
scraper/                     ← CLI + pipeline
  adapters/ligikuu.py        ← SportsPress client
  core/season.py             ← detect active / upcoming seasons
  core/pipeline.py           ← fetch → normalize → write
  core/storage.py            ← data/ layout
        │
        ▼
data/
  meta/last_run.json
  ligikuu/
    index.json
    *.json                   ← top-level artifacts
    raw/                     ← source-shaped dumps
    normalized/              ← clean models for API
    seasons/2026-27.json     ← per-season bundles
        │
        ▼
api/app.py                   ← FastAPI read API over data/
```

## Season auto-tracking

Upstream Ligi Kuu creates a **new league taxonomy term per season**
(`nbc-premier-league-2025-2026`, `nbc-premier-league-2026-2027`, …).

On every run the pipeline:

1. Fetches `/seasons` and `/leagues`.
2. Builds a `SeasonPlan` keeping the **N most recent seasons** (default 3).
3. Classifies competitions (`nbc_premier`, `nbc_championship`, …).
4. Filters events/tables to those seasons/leagues (unless `--full`).
5. Writes `data/ligikuu/seasons/{slug}.json` bundles for API consumers.

When NBC 2026/27 fixtures/results appear on ligikuu.co.tz, the next Action run stores them without code changes.

## Automation

`.github/workflows/scrape.yml`:

- Cron every 6 hours + manual `workflow_dispatch`
- `python -m scraper run` (default **incremental**: `modified_after` from `data/meta/last_run.json`, merge-by-id)
- `workflow_dispatch` input `full=true` → `python -m scraper run --full`
- Commits updated `data/` to the repo

## Incremental sync

1. Read `data/meta/last_run.json` → `scraped_at` (minus overlap window, default 60 minutes).
2. For post-like resources (`events`, `tables`, `teams`, …), request `?modified_after=…`.
3. Merge delta into previous `raw/*_all.json` / `raw/*.json` by `id`.
4. Re-apply season filters and rewrite normalized + season bundles.
5. Always full-fetch small taxonomies (`seasons`, `leagues`, `venues`).

If there is no prior corpus, the run falls back to a full collection refresh.

## API

```bash
python -m scraper serve --data-dir data
# open http://127.0.0.1:8000/docs
```

Key routes:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + whether data exists |
| GET | `/api/v1/sources/ligikuu` | Scrape index |
| GET | `/api/v1/sources/ligikuu/events` | Events (`season_id`, `league_id` filters) |
| GET | `/api/v1/sources/ligikuu/tables` | Standings tables |
| GET | `/api/v1/sources/ligikuu/seasons/{slug}` | Season bundle (e.g. `2026-27`) |
