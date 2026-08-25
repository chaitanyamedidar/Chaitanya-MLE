import { useEffect, useState } from 'react'
import './App.css'

type Health = 'checking' | 'ok' | 'down'

function App() {
  const [health, setHealth] = useState<Health>('checking')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? setHealth('ok') : setHealth('down')))
      .catch(() => setHealth('down'))
  }, [])

  return (
    <div className="shell">
      <header className="top">
        <p className="eyebrow">Quantiphi MLE · vibe coding</p>
        <h1>Subscription Tracker</h1>
        <p className="lede">
          Recurring SaaS and streaming spend, renewal alerts, and a pause-to-save
          simulation. Dashboard ships in the next commits.
        </p>
        <p className={`health health-${health}`}>
          API {health === 'checking' ? 'checking…' : health === 'ok' ? 'connected' : 'offline'}
        </p>
      </header>
    </div>
  )
}

export default App
