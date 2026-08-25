import { money } from '../format'
import type { Metrics } from '../types'

type Props = {
  metrics: Metrics | null
}

export function MetricsRow({ metrics }: Props) {
  return (
    <section className="metrics" aria-label="Dashboard metrics">
      <article className="metric-card">
        <p className="metric-label">Total Monthly Burn Rate</p>
        <p className="metric-value">{metrics ? money(metrics.monthly_burn_rate) : '—'}</p>
        <p className="metric-hint">
          {metrics
            ? `${metrics.active_count} active · paused costs excluded`
            : 'Waiting for API'}
        </p>
      </article>
      <article className="metric-card metric-card-alert">
        <p className="metric-label">Upcoming Renewals Alert Count</p>
        <p className="metric-value">{metrics ? metrics.upcoming_renewals_count : '—'}</p>
        <p className="metric-hint">Renewal within 7 days of today</p>
      </article>
    </section>
  )
}
