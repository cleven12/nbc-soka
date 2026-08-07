# NBC Ligi Kuu — public web UI

Minimal **TypeScript + React (Vite)** front end for Vercel.

Reads season JSON published by the scraper on GitHub (`main` → jsDelivr). No backend.

## Stack

| Piece | Choice |
|-------|--------|
| Language | TypeScript |
| UI | React 19 |
| Build | Vite |
| Host | Vercel (static) |
| Data | `cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu/…` |

## Local

```bash
cd web
npm install
npm run dev
```

Optional env (`.env.local`):

```bash
# Point at raw GitHub or a local mirror instead of jsDelivr
VITE_DATA_BASE=https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu
```

## Deploy on Vercel

1. Push this repo (or only `web/`) to GitHub.
2. [vercel.com/new](https://vercel.com/new) → import the repo.
3. **Root Directory:** `web`
4. Framework preset: Vite (auto from `vercel.json`)
5. Deploy.

Every scraper Action commit to `data/` becomes visible after jsDelivr/GitHub cache refreshes (usually minutes; pin `@main` may lag briefly).

## What users see

- Season switcher (2024/25–2026/27)
- NBC Premier **table**
- **Results** / **fixtures** scoreboard
- EN / SW labels
- **JSON** tab with stable URLs + `curl` example

## Not in scope (yet)

- Live FastAPI host (Phase 7)
- Auth, accounts, write paths
- Championship UI polish (Premier first)
