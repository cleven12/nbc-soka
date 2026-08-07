import { DATA_BASE, rawGithubUrl, seasonUrl } from '../lib/data'

type Props = {
  seasonSlug: string
}

export function DevLinks({ seasonSlug }: Props) {
  const links = [
    {
      label: 'Season pack (recommended)',
      url: seasonUrl(seasonSlug),
      note: 'Events + tables + teams for one season',
    },
    {
      label: 'Index / catalog',
      url: `${DATA_BASE}/index.json`,
      note: 'Resource counts and season plan',
    },
    {
      label: 'All events (large)',
      url: `${DATA_BASE}/normalized/events.json`,
      note: 'Full corpus — prefer season packs in apps',
    },
    {
      label: 'Raw GitHub (same file)',
      url: rawGithubUrl(`seasons/${seasonSlug}.json`),
      note: 'Direct from main branch',
    },
  ]

  return (
    <section className="panel" aria-labelledby="dev-heading">
      <header className="panel-head">
        <h2 id="dev-heading">For developers</h2>
        <p className="panel-sub">
          Free public JSON. No API key. Not the official league office.
        </p>
      </header>
      <ul className="dev-list">
        {links.map((l) => (
          <li key={l.url}>
            <a href={l.url} target="_blank" rel="noopener noreferrer">
              {l.label}
            </a>
            <code className="url">{l.url}</code>
            <span className="note">{l.note}</span>
          </li>
        ))}
      </ul>
      <pre className="curl" tabIndex={0}>
        {`curl -sL "${seasonUrl(seasonSlug)}" | head`}
      </pre>
    </section>
  )
}
