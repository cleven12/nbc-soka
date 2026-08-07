import type { Table } from '../types'

type Props = {
  table: Table | null
}

export function Standings({ table }: Props) {
  if (!table) {
    return (
      <p className="empty">
        No league table in this season pack yet. Fixtures may still be loading.
      </p>
    )
  }

  const rows = [...(table.standings || [])].sort((a, b) => a.pos - b.pos)

  return (
    <section className="panel" aria-labelledby="table-heading">
      <header className="panel-head">
        <h2 id="table-heading">Table</h2>
        <p className="panel-sub">{table.name}</p>
      </header>
      <div className="table-wrap">
        <table className="standings">
          <thead>
            <tr>
              <th scope="col" className="num">
                #
              </th>
              <th scope="col">Club</th>
              <th scope="col" className="num">
                P
              </th>
              <th scope="col" className="num hide-sm">
                W
              </th>
              <th scope="col" className="num hide-sm">
                D
              </th>
              <th scope="col" className="num hide-sm">
                L
              </th>
              <th scope="col" className="num hide-sm">
                GD
              </th>
              <th scope="col" className="num">
                Pts
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.team_id || r.pos}>
                <td className="num pos">{r.pos}</td>
                <td className="club">{r.name}</td>
                <td className="num">{r.played}</td>
                <td className="num hide-sm">{r.won}</td>
                <td className="num hide-sm">{r.drawn}</td>
                <td className="num hide-sm">{r.lost}</td>
                <td className="num hide-sm">
                  {r.goal_diff > 0 ? `+${r.goal_diff}` : r.goal_diff}
                </td>
                <td className="num pts">{r.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
