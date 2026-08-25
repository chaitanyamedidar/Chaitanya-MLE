import { money } from '../format'
import type { Insights } from '../types'

const PALETTE = ['#0f766e', '#d97706', '#be123c', '#1d4ed8', '#7c3aed']

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

  const cashMax = Math.max(1, ...insights.cashflow.map((row) => row.amount))
  const pauseMax = Math.max(1, ...insights.pause_recommendations.map((row) => row.savings_if_paused))

  return (
    <section className="insights">
      <h2>Insights</h2>
      <div className="insight-grid">
        <article className="insight-card">
          <h3>Spend by category</h3>
          {insights.categories.length === 0 ? (
            <p className="empty">No active spend.</p>
          ) : (
            <ul className="bar-list">
              {insights.categories.map((row, i) => (
                <li key={row.category}>
                  <div className="bar-head">
                    <strong>{row.category}</strong>
                    <span>
                      {money(row.monthly_spend)} · {Math.round(row.share * 100)}%
                    </span>
                  </div>
                  <div className="bar-track">
                    <span
                      style={{
                        width: `${Math.max(6, row.share * 100)}%`,
                        background: PALETTE[i % PALETTE.length],
                      }}
                    />
                  </div>
                  <p className="muted">{row.names.join(', ')}</p>
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
            <ul className="bar-list">
              {insights.pause_recommendations.map((row) => (
                <li key={row.id}>
                  <div className="bar-head">
                    <strong>{row.name}</strong>
                    <span>{money(row.savings_if_paused)}/mo</span>
                  </div>
                  <div className="bar-track">
                    <span
                      style={{
                        width: `${(row.savings_if_paused / pauseMax) * 100}%`,
                        background: '#0f766e',
                      }}
                    />
                  </div>
                  <p className="muted">{row.category}</p>
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
            <ul className="chip-stack">
              {insights.overlaps.map((row) => (
                <li key={row.category}>
                  <p>{row.suggestion}</p>
                  <div className="chips">
                    {row.names.map((name) => (
                      <span key={name} className="chip">
                        {name}
                      </span>
                    ))}
                  </div>
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
            <ul className="chip-stack">
              {insights.anomalies.map((row) => (
                <li key={row.id}>
                  <strong>{row.name}</strong> {money(row.monthly_rate)}/mo
                  <p className="muted">{row.reason}</p>
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
            <div className="cash-bars">
              {insights.cashflow.map((row) => (
                <div key={row.month} className="cash-col">
                  <div
                    className="cash-bar"
                    style={{ height: `${24 + (row.amount / cashMax) * 88}px` }}
                    title={row.names.join(', ')}
                  />
                  <strong>{money(row.amount)}</strong>
                  <span>{row.month}</span>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  )
}
