# Consumer guide — public NBC Ligi Kuu JSON

Free static JSON collected from [ligikuu.co.tz](https://ligikuu.co.tz).
**Not** the official league office. No API key. Read-only.

> **Requires a public GitHub repo.** jsDelivr and `raw.githubusercontent.com` only serve files from public repositories.

## Preferred files (season packs)

One file per season: events + tables + teams.

| Season | jsDelivr | Raw GitHub |
|--------|----------|------------|
| 2026/27 | [seasons/2026-27.json](https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/seasons/2026-27.json) | [raw](https://raw.githubusercontent.com/cleven12/nbc-soka/main/data/ligikuu/seasons/2026-27.json) |
| 2025/26 | [seasons/2025-26.json](https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/seasons/2025-26.json) | [raw](https://raw.githubusercontent.com/cleven12/nbc-soka/main/data/ligikuu/seasons/2025-26.json) |
| 2024/25 | [seasons/2024-25.json](https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/seasons/2024-25.json) | [raw](https://raw.githubusercontent.com/cleven12/nbc-soka/main/data/ligikuu/seasons/2024-25.json) |

```bash
curl -sL \
  "https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/seasons/2025-26.json" \
  | head -c 400
```

## Other useful paths

Base (jsDelivr):

```text
https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/
```

| Path | Use |
|------|-----|
| `index.json` | Catalog, counts, last scrape time |
| `normalized/events.json` | All events (large) |
| `normalized/tables.json` | All tables |
| `normalized/teams.json` | Clubs |
| `meta` sibling: `../meta/last_run.json` under `data/` | Scraper run metadata |

## Browser UI

TypeScript app in [`web/`](../web/) — deploy to **Vercel** with root directory `web`.
It fetches the season packs above (no backend).

## Local API (developers)

```bash
python -m scraper serve --data-dir data
# /scores /table /teams /seasons/2026-27
```

## Update cadence

GitHub Action refreshes `data/` about every **6 hours** when the source is reachable.
CDN caches may lag a few minutes after a commit.
