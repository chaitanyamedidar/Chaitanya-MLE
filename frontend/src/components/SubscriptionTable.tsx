import { daysLabel, money } from '../format'
import type { Status, Subscription } from '../types'

type Props = {
  rows: Subscription[]
  pendingId: number | null
  onToggle: (id: number, status: Status) => void
}

export function SubscriptionTable({ rows, pendingId, onToggle }: Props) {
  if (rows.length === 0) {
    return <p className="empty">No subscriptions yet. Add one above.</p>
  }

  return (
    <div className="table-wrap">
      <table className="grid">
        <thead>
          <tr>
            <th>Service</th>
            <th>Cost</th>
            <th>Cycle</th>
            <th>Monthly</th>
            <th>Next renewal</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const paused = row.status === 'paused'
            return (
              <tr key={row.id} className={paused ? 'row-paused' : undefined}>
                <td>
                  <span className="svc">{row.name}</span>
                  {row.renewing_soon ? (
                    <span className="badge-soon">Renewing Soon</span>
                  ) : null}
                </td>
                <td>{money(row.cost)}</td>
                <td>{row.billing_cycle}</td>
                <td>{money(row.monthly_rate)}</td>
                <td>
                  {row.renewal_date}
                  <span className="muted"> · {daysLabel(row.days_to_renewal)}</span>
                </td>
                <td>
                  <label className="switch">
                    <input
                      type="checkbox"
                      role="switch"
                      aria-label={`${row.name} ${paused ? 'paused' : 'active'}`}
                      checked={!paused}
                      disabled={pendingId === row.id}
                      onChange={() => onToggle(row.id, paused ? 'active' : 'paused')}
                    />
                    <span>{paused ? 'Paused' : 'Active'}</span>
                  </label>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
