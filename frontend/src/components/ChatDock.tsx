import { useState, type FormEvent } from 'react'
import { api } from '../api'

type Msg = { role: 'user' | 'bot'; text: string; source?: string }

const QUICK = [
  "What's my monthly burn?",
  'What renews this week?',
  'What should I pause?',
]

export function ChatDock() {
  const [open, setOpen] = useState(true)
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: 'bot',
      text: 'Ask about burn, upcoming renewals, pause advice, categories, or cash-flow. Numbers come from the ledger.',
    },
  ])

  async function ask(text: string) {
    const trimmed = text.trim()
    if (!trimmed || busy) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text: trimmed }])
    setBusy(true)
    try {
      const res = await api.chat(trimmed)
      setMessages((m) => [...m, { role: 'bot', text: res.reply, source: res.source }])
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'bot', text: err instanceof Error ? err.message : 'Chat failed' },
      ])
    } finally {
      setBusy(false)
    }
  }

  function send(event: FormEvent) {
    event.preventDefault()
    void ask(input)
  }

  return (
    <div className={`chat-dock ${open ? 'open' : ''}`}>
      {open ? (
        <div className="chat-panel">
          <div className="chat-head">
            <strong>Assistant</strong>
            <button type="button" className="chat-x" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </div>
          <div className="chat-log">
            {messages.map((msg, idx) => (
              <p key={idx} className={`bubble ${msg.role}`}>
                {msg.text}
                {msg.source ? <span className="muted"> · {msg.source}</span> : null}
              </p>
            ))}
          </div>
          <div className="quick-row">
            {QUICK.map((q) => (
              <button key={q} type="button" className="quick" onClick={() => void ask(q)}>
                {q}
              </button>
            ))}
          </div>
          <form onSubmit={send} className="chat-form">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your subscriptions…"
            />
            <button type="submit" disabled={busy}>
              Send
            </button>
          </form>
        </div>
      ) : null}
      <button
        id="chat-fab"
        type="button"
        className="chat-fab"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Close assistant' : 'Open assistant'}
      >
        {open ? 'Close chat' : 'Chat'}
      </button>
    </div>
  )
}
