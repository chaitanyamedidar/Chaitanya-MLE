import { useState, type FormEvent } from 'react'
import { api } from '../api'

type Msg = { role: 'user' | 'bot'; text: string; source?: string }

export function ChatDock() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: 'bot',
      text: 'Ask about burn, upcoming renewals, pause advice, categories, or cash-flow. Numbers come from the ledger, not a guess.',
    },
  ])

  async function send(event: FormEvent) {
    event.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text }])
    setBusy(true)
    try {
      const res = await api.chat(text)
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

  return (
    <div className={`chat-dock ${open ? 'open' : ''}`}>
      <button type="button" className="chat-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? 'Close assistant' : 'Ask the assistant'}
      </button>
      {open ? (
        <div className="chat-panel">
          <div className="chat-log">
            {messages.map((msg, idx) => (
              <p key={idx} className={`bubble ${msg.role}`}>
                {msg.text}
                {msg.source ? <span className="muted"> · {msg.source}</span> : null}
              </p>
            ))}
          </div>
          <form onSubmit={send} className="chat-form">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="What's my monthly burn?"
            />
            <button type="submit" disabled={busy}>
              Send
            </button>
          </form>
        </div>
      ) : null}
    </div>
  )
}
