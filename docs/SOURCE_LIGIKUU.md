# Source: Ligi Kuu (ligikuu.co.tz)

Machine config for the runner: [`../config/ligikuu.json`](../config/ligikuu.json)

## Discovery

| Field | Value |
|-------|--------|
| Name | LIGI KUU |
| Description | Tanzania Premier League Board |
| Site URL | https://ligikuu.co.tz |
| WP REST index | https://ligikuu.co.tz/wp-json/ |
| SportsPress namespace | `sportspress/v2` |
| SportsPress root | https://ligikuu.co.tz/wp-json/sportspress/v2 |
| Timezone | Africa/Nairobi (GMT+3) |
| Auth (public scrape) | None — public `GET` only |

### Relevant WP namespaces

From `https://ligikuu.co.tz/wp-json/` `namespaces`:

- **`sportspress/v2`** — primary sports data (use this)
- `wp/v2` — generic WordPress posts/media (secondary)
- Others (Elementor, Yoast, Site Kit, …) — ignore for scraping

## SportsPress resources (GET)

Base: `https://ligikuu.co.tz/wp-json/sportspress/v2/{resource}`

| Resource | Path | Approx. size (observed) | Notes |
|----------|------|-------------------------|--------|
| calendars | `/calendars` | ~45 | Match bundles; `data` embeds events |
| events | `/events` | ~2580 | Fixtures + results; core scores source |
| teams | `/teams` | ~71 | Clubs |
| tables | `/tables` | ~24 | Standings; `data` keyed by team id |
| leagues | `/leagues` | ~29 | Competition taxonomy |
| seasons | `/seasons` | ~7 | Season taxonomy |
| players | `/players` | ~1368 | Optional / heavy |
| lists | `/lists` | ~31 | Player stats lists (goals, etc.) |
| venues | `/venues` | ~47 | Stadiums taxonomy |
| staff | `/staff` | small | Coaches etc. |
| officials | `/officials` | — | Referees |
| positions | `/positions` | — | Player positions |
| roles | `/roles` | — | Staff roles |
| duties | `/duties` | — | Official duties |

Single item: `/{resource}/{id}`

### Common query args (collections)

| Arg | Default | Notes |
|-----|---------|--------|
| `page` | 1 | 1-based |
| `per_page` | 10 | Use **100** (max) for bulk |
| `search` | — | Free text |
| `after` / `before` | — | ISO8601 publish date filter |
| `modified_after` / `modified_before` | — | Incremental sync |
| `include` / `exclude` | — | ID arrays |
| `slug` | — | Filter by slug(s) |
| `order` | desc | `asc` \| `desc` |
| `orderby` | date | `date`, `id`, `modified`, `slug`, `title`, … |
| `status` | — | e.g. `publish` for finished/public posts |
| `context` | view | `view` \| `embed` \| `edit` |

Pagination headers: `X-WP-Total`, `X-WP-TotalPages`, `Link`.

## Priority IDs (NBC focus)

### Seasons

| id | slug | name |
|---:|------|------|
| 431 | 2026-27 | 2026/27 |
| 417 | 2025-26 | 2025/26 |
| 288 | 2024-25 | 2024/25 |
| 235 | 2023-24 | 2023/24 |
| 135 | 2022-23 | 2022/23 |
| 87 | 2021-22 | 2021/22 |
| 23 | 2020-21 | 2020/21 |

### Key leagues (Premier)

| id | slug | name |
|---:|------|------|
| 432 | nbc-premier-league-2026-2027 | NBC PREMIER LEAGUE 2026/2027 |
| 418 | nbc-premier-league-2025-2026 | NBC PREMIER LEAGUE 2025/2026 |
| 287 | nbc-premier-league-2024-25 | NBC PREMIER LEAGUE 2024/2025 |
| 236 | nbc-premier-league-2023-2024 | NBC PREMIER LEAGUE 2023/2024 |
| 134 | nbc-premier-league-2022-23 | NBC PREMIER LEAGUE 2022/23 |

### Key leagues (Championship / First)

| id | slug | name |
|---:|------|------|
| 419 | nbc-championship-2025-2026 | NBC CHAMPIONSHIP LEAGUE 2025/2026 |
| 290 | nbc-championship-league-2024-2025 | NBC CHAMPIONSHIP LEAGUE 2024/2025 |
| 421 | first-league-group-a-2025-2026 | FIRST LEAGUE GROUP A 2025/2026 |
| 422 | first-league-group-b-2025-2026 | FIRST LEAGUE GROUP B 2025/2026 |

## Field cheat-sheet (what the runner cares about)

### Event (`sp_event`)

```json
{
  "id": 16613,
  "status": "publish",
  "date": "2026-06-30T16:00:00",
  "title": { "rendered": "JKT Tanzania vs Young Africans" },
  "teams": [268, 292],
  "main_results": ["0", "3"],
  "outcome": { "268": "loss", "292": "win" },
  "results": { "...": "per-team detail" },
  "leagues": [418],
  "seasons": [417],
  "venues": [],
  "winner": "...",
  "format": "league"
}
```

- `teams[0]` = home, `teams[1]` = away (SportsPress convention)  
- `main_results` parallel to `teams` (string goals)  
- Placeholder / TBD fixtures may use `teams: [-1, -1]` and empty titles  

### Table (`sp_table`)

```json
{
  "id": 13247,
  "title": { "rendered": "NBC PREMIER LEAGUE 2025/2026 STANDING" },
  "leagues": [418],
  "seasons": [417],
  "data": {
    "294": {
      "name": "Azam",
      "pos": 1,
      "p": "0", "w": "0", "d": "0", "l": "0",
      "f": "0", "a": "0", "gd": "0", "pts": "0"
    }
  }
}
```

Keys in `data` are **team IDs** (as strings).

### Team (`sp_team`)

Useful: `id`, `title.rendered`, `slug`, `abbreviation`, `leagues`, `seasons`, `venues`, `url`.

### League / season / venue

Taxonomies: `id`, `name`, `slug`, `parent`, `count`.

## Example requests for the runner

```bash
# Index
curl -sS https://ligikuu.co.tz/wp-json/ | jq '.namespaces, .timezone_string'

# Current NBC PL standings table
curl -sS 'https://ligikuu.co.tz/wp-json/sportspress/v2/tables?slug=nbc-premier-league-2025-2026&per_page=10'

# Published events (page 1, max page size)
curl -sS 'https://ligikuu.co.tz/wp-json/sportspress/v2/events?status=publish&per_page=100&page=1'

# Teams
curl -sS 'https://ligikuu.co.tz/wp-json/sportspress/v2/teams?per_page=100&page=1'
```

## Do not use

- Authenticated write endpoints (POST/PUT/PATCH/DELETE)  
- Elementor / Yoast / Site Kit / Statistics namespaces  
- Scraping HTML when the SportsPress JSON already has the field
