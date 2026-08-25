import { money } from '../format'
import type { Insights } from '../types'

type Props = {
  insights: Insights | null
}

export function InsightsPanel({ insights }: Props) {
  if (!insights) {
    return (
      <section className="insights">
        <h2>Insights</h2>
        <p className="empty">Insights load with your subscriptions.</p>
      </section>
    )
  }

  return (
    <section className="insights">
      <h2>Insights</h2>
      <div className="insight-grid">
        <article className="insight-card">
          <h3>Spend by category</h3>
          {insights.categories.length === 0 ? (
            <p className="empty">No active spend.</p>
          ) : (
            <ul>
              {insights.categories.map((row) => (
                <li key={row.category}>
                  <strong>{row.category}</strong> {money(row.monthly_spend)}{' '}
                  <span className="muted">({Math.round(row.share * 100)}%)</span>
                  <div className="muted">{row.names.join(', ')}</div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="insight-card">
          <h3>Pause to save</h3>
          {insights.pause_recommendations.length === 0 ? (
            <p className="empty">Nothing to pause.</p>
          ) : (
            <ul>
              {insights.pause_recommendations.map((row) => (
                <li key={row.id}>
                  <strong>{row.name}</strong> · {row.category}
                  <div>Save {money(row.savings_if_paused)}/mo if paused</div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="insight-card">
          <h3>Redundant stack</h3>
          {insights.overlaps.length === 0 ? (
            <p className="empty">No overlapping categories.</p>
          ) : (
            <ul>
              {insights.overlaps.map((row) => (
                <li key={row.category}>
                  {row.suggestion}
                  <div className="muted">{row.names.join(', ')}</div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="insight-card">
          <h3>Cost outliers</h3>
          {insights.anomalies.length === 0 ? (
            <p className="empty">No unusual prices.</p>
          ) : (
            <ul>
              {insights.anomalies.map((row) => (
                <li key={row.id}>
                  <strong>{row.name}</strong> {money(row.monthly_rate)}/mo
                  <div className="muted">{row.reason}</div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="insight-card insight-wide">
          <h3>Next 90 days cash-flow</h3>
          {insights.cashflow.length === 0 ? (
            <p className="empty">No upcoming charges.</p>
          ) : (
            <ul className="cashflow">
              {insights.cashflow.map((row) => (
                <li key={row.month}>
                  <strong>{row.month}</strong> {money(row.amount)}
                  <div className="muted">{row.names.join(', ')}</div>
                </li>
              ))}
            </ul>
          )}
        </article>
      </div>
    </section>
  )
}
