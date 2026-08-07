# Roadmap

Development is **phased**. See **[DEV_PHASES.md](./DEV_PHASES.md)** for the full module order, exit criteria, and status board.

**Rule:** finish and ship one phase before starting the next.

## Status (short)

| Phase | Name | Status |
|------:|------|--------|
| 0 | Source discovery | done |
| 1 | Core scraper | done |
| 2 | GitHub Action automation | done |
| 3 | Local data API | done |
| 4 | Harden + first production dataset (NBC 2026/27) | done |
| 5 | Incremental sync | done |
| **6** | **Dataset publishing (data repo / pages)** | **active** |
| 7 | API deploy (public URL) | later |
| 8 | Expand (championship, players, exports…) | later |

## Active phase checklist (Phase 6)

- [x] Choose publish target: **static JSON on `main` + Vercel TS UI** (`web/`)
- [x] Stable public paths for scores / table / seasons ([CONSUMERS.md](./CONSUMERS.md))
- [x] Repo public (CDN/raw 200 for season packs)
- [ ] Deploy `web/` to Vercel (Root Directory = `web`) — manual once
- [x] Short consumer docs (curl examples for journalists/devs)
- [x] Thin bots: Dependabot + PR CI (`pytest` + `web` build)
- [x] Scheduled scrape soft-fails when ligikuu is down/blocked
