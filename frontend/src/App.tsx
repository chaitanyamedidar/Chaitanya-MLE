import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import { EntryForm } from './components/EntryForm'
import { InsightsPanel } from './components/InsightsPanel'
import { MetricsRow } from './components/MetricsRow'
import { SubscriptionTable } from './components/SubscriptionTable'
import type { Insights, Metrics, Status, Subscription, SubscriptionCreate } from './types'
import './App.css'

export default function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [insights, setInsights] = useState<Insights | null>(null)
  const [rows, setRows] = useState<Subscription[]>([])
  const [health, setHealth] = useState<'checking' | 'ok' | 'down'>('checking')
  const [busy, setBusy] = useState(false)
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [banner, setBanner] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const [nextMetrics, nextRows, nextInsights] = await Promise.all([
      api.metrics(),
      api.list(),
      api.insights(),
    ])
    setMetrics(nextMetrics)
    setRows(nextRows)
    setInsights(nextInsights)
  }, [])

  useEffect(() => {
    api
      .health()
      .then(() => setHealth('ok'))
      .catch(() => setHealth('down'))
    refresh().catch(() => {
      setHealth('down')
      setBanner('Could not load subscriptions from the API.')
    })
  }, [refresh])

  async function handleCreate(payload: SubscriptionCreate) {
    setBusy(true)
    setBanner(null)
    try {
      await api.create(payload)
      await refresh()
    } finally {
      setBusy(false)
    }
  }

  async function handleToggle(id: number, status: Status) {
    setPendingId(id)
    setBanner(null)
    try {
      await api.setStatus(id, status)
      await refresh()
    } catch (err) {
      setBanner(err instanceof Error ? err.message : 'Could not update status')
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Subscription Tracker & Renewal Dashboard</p>
          <h1>Monthly cash-flow, at a glance</h1>
          <p className="lede">
            Add SaaS and streaming bills. Yearly plans are normalized on the server.
            Pause a row to simulate savings without deleting it.
          </p>
        </div>
        <p className={`health health-${health}`}>
          API {health === 'checking' ? 'checking…' : health === 'ok' ? 'connected' : 'offline'}
        </p>
      </header>

      <MetricsRow metrics={metrics} />
      {banner ? <p className="banner">{banner}</p> : null}
      <EntryForm busy={busy} onSubmit={handleCreate} />
      <section>
        <h2>Subscriptions</h2>
        <SubscriptionTable rows={rows} pendingId={pendingId} onToggle={handleToggle} />
      </section>
      <InsightsPanel insights={insights} />
    </div>
  )
}
