import { money } from '../format'
import type { Insights, Metrics, Subscription } from '../types'

const PALETTE = ['#0f766e', '#d97706', '#be123c', '#1d4ed8', '#7c3aed', '#0f766e']

type Props = {
  metrics: Metrics | null
  insights: Insights | null
  rows: Subscription[]
}

function Donut({ shares }: { shares: { label: string; share: number; color: string }[] }) {
  const r = 42
  const c = 2 * Math.PI * r
  let offset = 0
  const slices = shares.filter((s) => s.share > 0)
  return (
    <svg className="donut" viewBox="0 0 120 120" aria-hidden="true">
      <circle cx="60" cy="60" r={r} fill="none" stroke="#e7e2d6" strokeWidth="14" />
      {slices.map((slice) => {
        const len = c * slice.share
        const dash = `${len} ${c - len}`
        const el = (
          <circle
            key={slice.label}
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke={slice.color}
            strokeWidth="14"
            strokeDasharray={dash}
            strokeDashoffset={-offset}
            transform="rotate(-90 60 60)"
          />
        )
        offset += len
        return el
      })}
    </svg>
  )
}

export function MetricsRow({ metrics, insights, rows }: Props) {
  const categories = insights?.categories ?? []
  const shares = categories.map((row, i) => ({
    label: row.category,
    share: row.share,
    color: PALETTE[i % PALETTE.length],
  }))
  const week = [0, 1, 2, 3, 4, 5, 6].map((day) => ({
    day,
    count: rows.filter((row) => row.renewing_soon && row.days_to_renewal === day).length,
  }))
  const weekMax = Math.max(1, ...week.map((d) => d.count))
  const active = metrics?.active_count ?? 0
  const paused = metrics?.paused_count ?? 0
  const totalRows = Math.max(1, active + paused)

  return (
    <section className="metrics" aria-label="Dashboard metrics">
      <article className="metric-card metric-burn">
        <div className="metric-copy">
          <p className="metric-label">Total Monthly Burn Rate</p>
          <p className="metric-value">{metrics ? money(metrics.monthly_burn_rate) : '—'}</p>
          <p className="metric-hint">
            {metrics ? `${metrics.active_count} active · paused costs excluded` : 'Waiting for API'}
          </p>
          {shares.length > 0 ? (
            <ul className="legend">
              {shares.map((s) => (
                <li key={s.label}>
                  <span className="swatch" style={{ background: s.color }} />
                  {s.label} {Math.round(s.share * 100)}%
                </li>
              ))}
            </ul>
          ) : null}
        </div>
        <Donut shares={shares} />
      </article>

      <article className="metric-card metric-card-alert">
        <p className="metric-label">Upcoming Renewals Alert Count</p>
        <p className="metric-value">{metrics ? metrics.upcoming_renewals_count : '—'}</p>
        <p className="metric-hint">Next 7 days · each column is a day</p>
        <div className="week-strip" aria-hidden="true">
          {week.map((cell) => (
            <div key={cell.day} className="week-col">
              <div
                className="week-bar"
                style={{ height: `${12 + (cell.count / weekMax) * 36}px` }}
                data-hot={cell.count > 0 ? '1' : '0'}
              />
              <span>D+{cell.day}</span>
            </div>
          ))}
        </div>
      </article>

      <article className="metric-card">
        <p className="metric-label">Active vs paused</p>
        <p className="metric-value">
          {active}
          <span className="metric-sub"> / {paused} paused</span>
        </p>
        <p className="metric-hint">Pause is a savings simulation, not a delete</p>
        <div className="split-track">
          <span className="split-active" style={{ width: `${(active / totalRows) * 100}%` }} />
          <span className="split-paused" style={{ width: `${(paused / totalRows) * 100}%` }} />
        </div>
      </article>
    </section>
  )
}
