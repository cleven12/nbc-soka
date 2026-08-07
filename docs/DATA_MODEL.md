# Data model

## Artifact envelope

Every stored resource uses:

```json
{
  "source": "ligikuu",
  "resource": "events",
  "scraped_at": "2026-07-24T12:00:00+00:00",
  "api_root": "https://ligikuu.co.tz/wp-json/sportspress/v2",
  "count": 0,
  "filters": {},
  "items": []
}
```

## Normalized event

| Field | Type | Notes |
|-------|------|--------|
| id | int | SportsPress event id |
| name | string | e.g. `Simba SC vs KMC FC` |
| date | string | Local kickoff |
| status | string | `publish`, `future`, … |
| home_team_id / away_team_id | int? | `teams[0]` / `teams[1]` |
| home_score / away_score | int? | from `main_results` |
| outcome | object | team_id → win/loss/draw |
| leagues / seasons | int[] | taxonomy ids |
| is_placeholder | bool | TBD fixtures (`teams: [-1,-1]`) |

## Normalized table

| Field | Type | Notes |
|-------|------|--------|
| id | int | |
| name / slug | string | |
| leagues / seasons | int[] | |
| standings[] | rows | pos, played, won, drawn, lost, gf, ga, gd, pts |

## Season bundle (`seasons/{slug}.json`)

```json
{
  "season": { "id": 431, "slug": "2026-27", "name": "2026/27" },
  "competitions": [],
  "counts": { "events": 0, "tables": 0, "teams": 0 },
  "events": [],
  "tables": [],
  "teams": []
}
```

## Known season ids (Ligi Kuu)

| Season | id | NBC Premier league id |
|--------|---:|----------------------:|
| 2026/27 | 431 | 432 |
| 2025/26 | 417 | 418 |
| 2024/25 | 288 | 287 |
