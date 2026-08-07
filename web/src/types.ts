/** Shapes from data/ligikuu season packs (normalized). */

export type StandingRow = {
  pos: number
  name: string
  team_id: number
  played: number
  won: number
  drawn: number
  lost: number
  goals_for: number
  goals_against: number
  goal_diff: number
  points: number
}

export type Table = {
  id: number
  name: string
  slug: string
  leagues: number[]
  seasons: number[]
  standings: StandingRow[]
}

export type Event = {
  id: number
  name: string
  date: string | null
  status: string
  home_team_id: number | null
  away_team_id: number | null
  home_score: number | null
  away_score: number | null
  leagues: number[]
  seasons: number[]
  venues: number[]
}

export type Team = {
  id: number
  name: string
  slug: string
  abbreviation?: string | null
}

export type Competition = {
  id: number
  name: string
  slug: string
  kind: string
}

export type SeasonMeta = {
  id: number
  name: string
  slug: string
}

export type SeasonPack = {
  source: string
  scraped_at?: string
  season: SeasonMeta
  competitions: Competition[]
  counts: Record<string, number>
  events: Event[]
  tables: Table[]
  teams: Team[]
}

export type DataIndex = {
  scraped_at?: string
  resources?: Record<string, number>
  season_plan?: {
    seasons?: SeasonMeta[]
  }
}
