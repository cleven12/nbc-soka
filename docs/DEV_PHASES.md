# Development phases — NBC Ligi Kuu Data

Ship **one phase at a time**. Update this board when a phase ships.

**Rule:** finish and mark a phase **done** before starting the next.

## Status board

| Phase | Name | Status | Exit criteria (short) |
|------:|------|--------|------------------------|
| 0 | Source discovery | **done** | `config/ligikuu.json` + docs; SportsPress REST mapped |
| 1 | Core scraper | **done** | `python -m scraper run` writes `data/ligikuu/` JSON |
| 2 | GitHub Action automation | **done** | Cron + `workflow_dispatch` commits `data/` |
| 3 | Local data API | **done** | FastAPI `/scores`, `/table`, `/teams`, `/seasons/{slug}` |
| 4 | Harden + first production dataset (NBC 2026/27) | **done** | Season bundles present; Action refresh commits; tests green |
| **5** | **Incremental sync** | **done** | `modified_after` + merge-by-id; live smoke OK |
| **6** | **Dataset publishing (data repo / pages)** | **active** | Public static dump or separate data repo |
| 7 | API deploy (public URL) | later | Live URL for newsrooms / bots |
| 8 | Expand (championship polish, players, CSV/SQLite…) | later | Extra leagues & export formats |

---

## Phase details

### Phase 0 — Source discovery (done)

- Human docs: `ABOUT.md`, `docs/SOURCE_LIGIKUU.md`, `docs/ARCHITECTURE.md`
- Machine config: `config/ligikuu.json`
- Prefer official REST over HTML

### Phase 1 — Core scraper (done)

- Adapter + pagination (`X-WP-TotalPages`)
- Season auto-plan from live `/seasons` + `/leagues`
- Normalize → `raw/` + `normalized/` + top-level artifacts

### Phase 2 — GitHub Action (done)

- `.github/workflows/scrape.yml` every 6 hours + manual run
- Commits refreshed `data/`

### Phase 3 — Local data API (done)

- `python -m scraper serve`
- Easy paths + `/api/v1/sources/ligikuu/...`

### Phase 4 — Harden + NBC 2026/27 dataset (done)

Checklist:

- [x] Full scrape path produces usable artifacts under `data/`
- [x] `data/ligikuu/seasons/2026-27.json` present (and sibling seasons)
- [x] GitHub Action green (recurring `data: refresh NBC Ligi Kuu scores …` commits)
- [x] Season plan tracks NBC Premier + Championship including 2026/27
- [x] Unit tests for normalize / season / API
- [x] This status board created and linked from README / ROADMAP

### Phase 5 — Incremental sync (**done**)

Goal: scheduled runs only pull **changed** post-like resources when possible, then **merge** into existing JSON by id.

Exit criteria:

- [x] CLI supports incremental mode (default when not `--full`) and `--full` force refresh
- [x] Events/tables/teams/… use `modified_after` from `meta/last_run.json` when corpus exists
- [x] Merge-by-id preserves items not returned in the delta (`scraper/core/merge.py`)
- [x] Taxonomies (seasons/leagues/venues) still full-fetched (small)
- [x] Tests cover merge + “no corpus → no modified_after”
- [x] Live smoke: `python -m scraper run` → `mode=incremental`, delta merges (e.g. events delta=0 kept)
- [x] Docs / Action notes updated

### Phase 6 — Dataset publishing (**active**)

Goal: make JSON easy to consume without cloning the whole scraper repo.

Exit criteria:

- [x] Decide publish shape: **committed `data/ligikuu/` on `main`** + **Vercel UI** (`web/`, TypeScript)
- [x] Document stable URLs ([CONSUMERS.md](./CONSUMERS.md)) — season packs preferred
- [x] Minimal public UI: table / results / fixtures / JSON links (EN+SW)
- [x] Repo **public** so raw/jsDelivr season packs return 200
- [x] Scheduled scrape soft-fails when source is down/blocked (manual runs stay strict)
- [ ] Deploy once on Vercel (Root Directory = `web`) — manual once in Vercel dashboard
- [ ] Optional: CSV or SQLite snapshot for analysts

### Phase 7 — API deploy

- Docker / small host; public base URL; CORS as needed

### Phase 8 — Expand

- Championship polish, players/lists, CSV/SQLite/Parquet exports

---
