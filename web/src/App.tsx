import { useEffect, useMemo, useState } from 'react'
import { DevLinks } from './components/DevLinks'
import { Scores } from './components/Scores'
import { Standings } from './components/Standings'
import {
  SEASON_OPTIONS,
  fetchIndex,
  fetchSeasonPack,
  formatUpdated,
  pickPremierTable,
} from './lib/data'
import type { SeasonPack } from './types'

type Tab = 'table' | 'results' | 'fixtures' | 'dev'
type Lang = 'en' | 'sw'

const copy = {
  en: {
    title: 'NBC Ligi Kuu',
    tag: 'Public scores & tables for Tanzania’s top flight',
    notOfficial: 'Helper data — not the official league office',
    updated: 'Data updated',
    season: 'Season',
    table: 'Table',
    results: 'Results',
    fixtures: 'Fixtures',
    dev: 'JSON',
    loading: 'Loading season data…',
    retry: 'Try again',
    source: 'Source data from',
    about: 'Free open collector. Built for journalists, fans, and apps.',
  },
  sw: {
    title: 'NBC Ligi Kuu',
    tag: 'Matokeo na jedwali la ligi kuu ya Tanzania',
    notOfficial: 'Data ya msaada — si ofisi rasmi ya ligi',
    updated: 'Imesasishwa',
    season: 'Msimu',
    table: 'Jedwali',
    results: 'Matokeo',
    fixtures: 'Mechi zijazo',
    dev: 'JSON',
    loading: 'Inapakia data ya msimu…',
    retry: 'Jaribu tena',
    source: 'Data inatoka',
    about: 'Mkusanyaji huru. Kwa waandishi, mashabiki, na programu.',
  },
} as const

export default function App() {
  const [lang, setLang] = useState<Lang>('en')
  const [season, setSeason] = useState<string>('2025-26')
  const [tab, setTab] = useState<Tab>('table')
  const [pack, setPack] = useState<SeasonPack | null>(null)
  const [updatedAt, setUpdatedAt] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [reloadToken, setReloadToken] = useState(0)

  const t = copy[lang]

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.all([fetchSeasonPack(season), fetchIndex().catch(() => null)])
      .then(([seasonPack, index]) => {
        if (cancelled) return
        setPack(seasonPack)
        setUpdatedAt(seasonPack.scraped_at || index?.scraped_at || null)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setPack(null)
        setError(err instanceof Error ? err.message : 'Failed to load data')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [season, reloadToken])

  const premierTable = useMemo(
    () => (pack ? pickPremierTable(pack) : null),
    [pack],
  )

  return (
    <div className="app">
      <a className="skip" href="#main">
        Skip to content
      </a>

      <header className="top">
        <div className="brand">
          <p className="eyebrow">Tanzania · open football data</p>
          <h1>{t.title}</h1>
          <p className="tag">{t.tag}</p>
        </div>
        <div className="top-actions">
          <div className="lang" role="group" aria-label="Language">
            <button
              type="button"
              className={lang === 'en' ? 'active' : ''}
              onClick={() => setLang('en')}
            >
              EN
            </button>
            <button
              type="button"
              className={lang === 'sw' ? 'active' : ''}
              onClick={() => setLang('sw')}
            >
              SW
            </button>
          </div>
          <label className="season-pick">
            <span>{t.season}</span>
            <select
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              aria-label={t.season}
            >
              {SEASON_OPTIONS.map((s) => (
                <option key={s.slug} value={s.slug}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <p className="meta-bar">
        <span>{t.notOfficial}</span>
        <span className="dot" aria-hidden />
        <span>
          {t.updated}: <strong>{formatUpdated(updatedAt)}</strong>
        </span>
      </p>

      <nav className="tabs" aria-label="Sections">
        {(
          [
            ['table', t.table],
            ['results', t.results],
            ['fixtures', t.fixtures],
            ['dev', t.dev],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? 'tab active' : 'tab'}
            onClick={() => setTab(id)}
            aria-current={tab === id ? 'page' : undefined}
          >
            {label}
          </button>
        ))}
      </nav>

      <main id="main">
        {loading && <p className="status">{t.loading}</p>}
        {error && (
          <div className="error" role="alert">
            <p>{error}</p>
            <button type="button" onClick={() => setReloadToken((n) => n + 1)}>
              {t.retry}
            </button>
          </div>
        )}
        {!loading && !error && pack && tab === 'table' && (
          <Standings table={premierTable} />
        )}
        {!loading && !error && pack && tab === 'results' && (
          <Scores pack={pack} filter="results" />
        )}
        {!loading && !error && pack && tab === 'fixtures' && (
          <Scores pack={pack} filter="fixtures" />
        )}
        {!loading && !error && tab === 'dev' && (
          <DevLinks seasonSlug={season} />
        )}
      </main>

      <footer className="foot">
        <p>{t.about}</p>
        <p>
          {t.source}{' '}
          <a href="https://ligikuu.co.tz" rel="noopener noreferrer">
            ligikuu.co.tz
          </a>
          {' · '}
          <a
            href="https://github.com/cleven12/nbc-soka"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}
