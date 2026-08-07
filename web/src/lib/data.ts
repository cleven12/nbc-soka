import type { DataIndex, SeasonPack } from '../types'

/**
 * Public JSON lives on the scraper repo `main` branch.
 * jsDelivr is CORS-friendly and caches; override with VITE_DATA_BASE.
 */
const DEFAULT_BASE =
  'https://cdn.jsdelivr.net/gh/cleven12/nbc-soka@main/data/ligikuu'

export const DATA_BASE = (
  import.meta.env.VITE_DATA_BASE as string | undefined
)?.replace(/\/$/, '') || DEFAULT_BASE

export const SEASON_OPTIONS = [
  { slug: '2026-27', label: '2026/27' },
  { slug: '2025-26', label: '2025/26' },
  { slug: '2024-25', label: '2024/25' },
] as const

export function seasonUrl(slug: string): string {
  return `${DATA_BASE}/seasons/${slug}.json`
}

export function indexUrl(): string {
  return `${DATA_BASE}/index.json`
}

export function rawGithubUrl(pathFromLigikuu: string): string {
  return `https://raw.githubusercontent.com/cleven12/nbc-soka/main/data/ligikuu/${pathFromLigikuu}`
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) {
    throw new Error(`Could not load data (${res.status}). Try again in a moment.`)
  }
  return res.json() as Promise<T>
}

export function fetchSeasonPack(slug: string): Promise<SeasonPack> {
  return fetchJson<SeasonPack>(seasonUrl(slug))
}

export function fetchIndex(): Promise<DataIndex> {
  return fetchJson<DataIndex>(indexUrl())
}

/** Prefer NBC Premier table when several exist for a season. */
export function pickPremierTable(pack: SeasonPack) {
  const tables = pack.tables || []
  const premier = tables.find((t) =>
    /premier/i.test(t.name) && !/relegation|promotion|play/i.test(t.name),
  )
  return premier ?? tables[0] ?? null
}

export function teamNameMap(pack: SeasonPack): Map<number, string> {
  const m = new Map<number, string>()
  for (const t of pack.teams || []) {
    m.set(t.id, t.name)
  }
  return m
}

export function splitMatchName(name: string): { home: string; away: string } {
  const parts = name.split(/\s+vs\.?\s+/i)
  if (parts.length >= 2) {
    return { home: parts[0].trim(), away: parts.slice(1).join(' vs ').trim() }
  }
  return { home: name, away: '' }
}

export function formatMatchDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatUpdated(iso: string | null | undefined): string {
  if (!iso) return 'unknown'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}
