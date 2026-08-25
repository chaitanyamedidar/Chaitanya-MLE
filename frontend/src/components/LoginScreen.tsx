import { useState, type FormEvent } from 'react'
import { api, setToken } from '../api'

type Props = {
  onAuthed: (email: string) => void
}

export function LoginScreen({ onAuthed }: Props) {
  const [email, setEmail] = useState('demo@quantiphi.dev')
  const [password, setPassword] = useState('Demo@123')
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const res =
        mode === 'login' ? await api.login(email, password) : await api.register(email, password)
      setToken(res.access_token)
      onAuthed(res.email)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Auth failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <p className="eyebrow">Subscription Tracker</p>
        <h1>Sign in</h1>
        <p className="lede">Demo account is pre-filled. Reviewers can enter immediately.</p>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        </label>
        <label>
          Password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            minLength={6}
            required
          />
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" disabled={busy}>
          {busy ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
        </button>
        <button
          type="button"
          className="linkish"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? 'Need an account? Register' : 'Have an account? Log in'}
        </button>
      </form>
    </div>
  )
}
