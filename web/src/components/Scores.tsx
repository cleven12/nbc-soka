import {
  formatMatchDate,
  splitMatchName,
  teamNameMap,
} from '../lib/data'
import type { Event, SeasonPack } from '../types'

type Props = {
  pack: SeasonPack
  filter: 'results' | 'fixtures' | 'all'
}

function resolveSides(
  e: Event,
  names: Map<number, string>,
): { home: string; away: string } {
  const fromName = splitMatchName(e.name)
  const home =
    (e.home_team_id != null && names.get(e.home_team_id)) || fromName.home
  const away =
    (e.away_team_id != null && names.get(e.away_team_id)) || fromName.away
  return { home, away }
}

export function Scores({ pack, filter }: Props) {
  const names = teamNameMap(pack)
  let events = [...(pack.events || [])]

  if (filter === 'results') {
    events = events.filter((e) => e.status === 'publish')
  } else if (filter === 'fixtures') {
    events = events.filter((e) => e.status === 'future')
  }

  events.sort((a, b) => {
    const da = a.date ? new Date(a.date).getTime() : 0
    const db = b.date ? new Date(b.date).getTime() : 0
    // results: newest first; fixtures: soonest first
    return filter === 'fixtures' ? da - db : db - da
  })

  // Keep UI light
  const limit = filter === 'all' ? 40 : 30
  events = events.slice(0, limit)

  if (events.length === 0) {
    return (
      <p className="empty">
        {filter === 'results'
          ? 'No played matches in this pack yet.'
          : filter === 'fixtures'
            ? 'No upcoming fixtures listed yet.'
            : 'No matches found.'}
      </p>
    )
  }

  return (
    <section className="panel" aria-labelledby="scores-heading">
      <header className="panel-head">
        <h2 id="scores-heading">
          {filter === 'fixtures'
            ? 'Fixtures'
            : filter === 'results'
              ? 'Results'
              : 'Matches'}
        </h2>
        <p className="panel-sub">Showing {events.length} matches</p>
      </header>
      <ul className="scoreboard" role="list">
        {events.map((e) => {
          const { home, away } = resolveSides(e, names)
          const played = e.status === 'publish'
          const hs = e.home_score
          const as = e.away_score
          return (
            <li key={e.id} className="match-card">
              <time className="match-date" dateTime={e.date ?? undefined}>
                {formatMatchDate(e.date)}
              </time>
              <div className="match-line">
                <span className="side home">{home}</span>
                <span
                  className={`score ${played ? 'played' : 'tbd'}`}
                  aria-label={
                    played
                      ? `${hs} to ${as}`
                      : 'Kick-off time only, score not available'
                  }
                >
                  {played ? (
                    <>
                      <span>{hs ?? '—'}</span>
                      <span className="sep">–</span>
                      <span>{as ?? '—'}</span>
                    </>
                  ) : (
                    <span className="vs">vs</span>
                  )}
                </span>
                <span className="side away">{away}</span>
              </div>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
