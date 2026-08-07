# NBC Ligi Kuu Data

**Free, automatic match scores and league tables for the Tanzania NBC Premier League (Ligi Kuu).**

Built so journalists, fans, students, and app makers can use official-style league data without copying scores by hand.

| | |
|---|---|
| **What it does** | Collects results, fixtures, teams, and standings |
| **Main league** | NBC Premier League (Ligi Kuu) |
| **Also covers** | NBC Championship (and related seasons when available) |
| **Updates** | Automatically every few hours (GitHub Actions) |
| **Source** | Public data from [ligikuu.co.tz](https://ligikuu.co.tz) |
| **For humans** | Read [ABOUT.md](ABOUT.md) (English + Kiswahili) |

---

## In simple words

1. A computer program **reads** the official Ligi Kuu website’s data.
2. It **saves** scores and tables as files.
3. An **API** (simple web address) can **share** that data with websites, apps, or newsrooms.
4. When the **2026/2027** season starts, new matches are picked up **automatically**.

You do **not** need to understand Python to *use* the data once it is published — only to run or host the project yourself.

---

## Quick links

| I want to… | Go here |
|------------|---------|
| Understand the project (non-technical) | [ABOUT.md](ABOUT.md) |
| See how development is phased | [docs/DEV_PHASES.md](docs/DEV_PHASES.md) |
| Technical architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Official league site | [ligikuu.co.tz](https://ligikuu.co.tz) |

---

## For developers (short)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Collect latest data
python -m scraper run

# Open the data API (browser-friendly docs)
python -m scraper serve --data-dir data
# → http://127.0.0.1:8000/
# → http://127.0.0.1:8000/docs
```

### Easy API paths (after `serve`)

| Path | Meaning |
|------|---------|
| `/` | Home — what this service is |
| `/health` | Is the service up? |
| `/scores` | Match results & fixtures |
| `/table` | League standings |
| `/teams` | Clubs |
| `/seasons/2026-27` | One season pack (e.g. NBC 2026/27) |
| `/docs` | Interactive API documentation |

Filters (examples):

```text
/scores?season=2026-27
/table?season=2026-27
```

---

## Public UI (Vercel + TypeScript)

Minimal browser UI lives in [`web/`](web/) — **Vite + React + TypeScript**.
It loads season JSON from GitHub via jsDelivr (no Python server required).

```bash
cd web && npm install && npm run dev
```

**Deploy:** import this repo on [Vercel](https://vercel.com/new), set **Root Directory** to `web`, deploy.
Details: [web/README.md](web/README.md) · consumer URLs: [docs/CONSUMERS.md](docs/CONSUMERS.md)

---

## Deployment

Simplest production deployment:

1. **Scraper** runs on a schedule (already: `.github/workflows/scrape.yml`).
2. **API** serves the saved `data/` folder (or use static JSON + the Vercel UI above).

```bash
# Docker (API + existing data folder)
docker compose up --build
# → http://localhost:8000/
```

Or without Docker:

```bash
pip install -r requirements.txt && pip install -e .
python -m scraper run
DATA_DIR=data uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Set `DATA_DIR` if your JSON lives somewhere else.

---

## Project layout (simple)

```text
ABOUT.md                 ← plain language (EN + SW)
scraper/                 ← collects data
api/                     ← shares data over HTTP
web/                     ← TypeScript UI (Vercel)
data/                    ← saved scores & tables
config/                  ← source/API configuration
.github/workflows/       ← automatic updates
docs/                    ← deeper technical notes
```

---

## Status

Core path works: **collect → save → serve** (including NBC **2026/27** season bundles).
Incremental sync works (`modified_after` + merge-by-id).
Active work: **Phase 6 — dataset publishing** (`web/` UI + public JSON URLs).
See [docs/DEV_PHASES.md](docs/DEV_PHASES.md).

```bash
# Default: incremental when data/ already has a last successful run
python -m scraper run

# Force full re-download (no modified_after; still season-filtered unless --full)
python -m scraper run --no-incremental

# Store every season unfiltered
python -m scraper run --full
```

---

## Credit & fairness

- Data originates from the public Ligi Kuu / TPLB web presence.
- This project is a **helper** for access and reuse — not an official TPLB product.
- Be fair: credit the league where you publish stories; do not overload their website.

## License

See [LICENSE](LICENSE).
