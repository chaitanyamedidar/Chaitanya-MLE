import { useCallback, useEffect, useState } from 'react'
import { api, getToken, setToken } from './api'
import { ChatDock } from './components/ChatDock'
import { EntryForm } from './components/EntryForm'
import { InsightsPanel } from './components/InsightsPanel'
import { LoginScreen } from './components/LoginScreen'
import { MetricsRow } from './components/MetricsRow'
import { SubscriptionTable } from './components/SubscriptionTable'
import type { Insights, Metrics, Status, Subscription, SubscriptionCreate } from './types'
import './App.css'

export default function App() {
  const [email, setEmail] = useState<string | null>(null)
  const [geminiEnabled, setGeminiEnabled] = useState(false)
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
      .then((h) => {
        setHealth('ok')
        setGeminiEnabled(Boolean(h.gemini))
      })
      .catch(() => setHealth('down'))

    if (!getToken()) return
    api
      .me()
      .then(async (me) => {
        setEmail(me.email)
        setGeminiEnabled(me.gemini_enabled)
        await refresh()
      })
      .catch(() => {
        setToken(null)
        setEmail(null)
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

  async function handleExtract(file: File): Promise<SubscriptionCreate> {
    const { draft } = await api.extractInvoice(file)
    return {
      name: draft.name,
      cost: draft.cost,
      billing_cycle: draft.billing_cycle,
      renewal_date: draft.next_renewal_date ?? '',
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

  if (!email) {
    return (
      <LoginScreen
        onAuthed={async (nextEmail) => {
          setEmail(nextEmail)
          const me = await api.me()
          setGeminiEnabled(me.gemini_enabled)
          await refresh()
        }}
      />
    )
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Subscription Tracker & Renewal Dashboard</p>
          <h1>Monthly cash-flow, at a glance</h1>
          <p className="lede">
            Signed in as {email}. Yearly plans are normalized on the server. Pause a row to
            simulate savings without deleting it.
          </p>
        </div>
        <div className="hero-actions">
          <p className={`health health-${health}`}>
            API {health === 'checking' ? 'checking…' : health === 'ok' ? 'connected' : 'offline'}
            {geminiEnabled ? ' · Gemini on' : ' · Gemini off'}
          </p>
          <button
            type="button"
            className="linkish"
            onClick={() => {
              setToken(null)
              setEmail(null)
            }}
          >
            Log out
          </button>
        </div>
      </header>

      <MetricsRow metrics={metrics} insights={insights} rows={rows} />
      {banner ? <p className="banner">{banner}</p> : null}
      <EntryForm
        busy={busy}
        geminiEnabled={geminiEnabled}
        onSubmit={handleCreate}
        onExtract={handleExtract}
      />
      <section>
        <h2>Subscriptions</h2>
        <SubscriptionTable rows={rows} pendingId={pendingId} onToggle={handleToggle} />
      </section>
      <InsightsPanel insights={insights} />
      <ChatDock />
    </div>
  )
}
