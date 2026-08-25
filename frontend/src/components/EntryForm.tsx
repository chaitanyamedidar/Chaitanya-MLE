import { useState, type FormEvent } from 'react'
import type { BillingCycle, SubscriptionCreate } from '../types'

type Props = {
  busy: boolean
  geminiEnabled: boolean
  onSubmit: (payload: SubscriptionCreate) => Promise<void>
  onExtract: (file: File) => Promise<SubscriptionCreate>
}

function todayIso(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

export function EntryForm({ busy, geminiEnabled, onSubmit, onExtract }: Props) {
  const [name, setName] = useState('')
  const [cost, setCost] = useState('')
  const [cycle, setCycle] = useState<BillingCycle>('Monthly')
  const [renewal, setRenewal] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [note, setNote] = useState<string | null>(null)
  const minDate = todayIso()

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    const amount = Number(cost)
    if (!name.trim() || !Number.isFinite(amount) || amount <= 0 || !renewal) {
      setError('Fill in a service name, a cost greater than 0, and a renewal date.')
      return
    }
    if (renewal < minDate) {
      setError('Next renewal date cannot be in the past.')
      return
    }
    try {
      await onSubmit({
        name: name.trim(),
        cost: amount,
        billing_cycle: cycle,
        renewal_date: renewal,
      })
      setName('')
      setCost('')
      setCycle('Monthly')
      setRenewal('')
      setNote(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add subscription')
    }
  }

  async function handleFile(file: File | undefined) {
    if (!file) return
    setError(null)
    setNote('Reading invoice… confirm the fields before saving.')
    try {
      const draft = await onExtract(file)
      setName(draft.name)
      setCost(String(draft.cost))
      setCycle(draft.billing_cycle)
      if (draft.renewal_date && draft.renewal_date >= todayIso()) {
        setRenewal(draft.renewal_date)
      } else if (draft.renewal_date) {
        setRenewal('')
        setNote('Invoice date is in the past. Pick the next renewal (today or later), then confirm.')
      }
    } catch (err) {
      setNote(null)
      setError(err instanceof Error ? err.message : 'Could not read invoice')
    }
  }

  return (
    <form id="entry-form" className="entry-form" onSubmit={handleSubmit}>
      <h2>Add subscription</h2>
      <div className="form-grid">
        <label>
          Service name
          <input
            type="text"
            name="name"
            maxLength={80}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Netflix"
            required
          />
        </label>
        <label>
          Cost
          <input
            type="number"
            name="cost"
            inputMode="decimal"
            min="0.01"
            step="0.01"
            value={cost}
            onChange={(e) => setCost(e.target.value)}
            placeholder="649.00"
            required
          />
        </label>
        <label>
          Billing cycle
          <select
            name="billing_cycle"
            value={cycle}
            onChange={(e) => setCycle(e.target.value as BillingCycle)}
          >
            <option value="Monthly">Monthly</option>
            <option value="Yearly">Yearly</option>
          </select>
        </label>
        <label>
          Next renewal date
          <input
            type="date"
            name="renewal_date"
            min={minDate}
            value={renewal}
            onChange={(e) => setRenewal(e.target.value)}
            required
          />
        </label>
      </div>
      {note ? <p className="form-note">{note}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}
      <div className="form-actions">
        <label className="btn-secondary upload-btn">
          Upload invoice
          <input
            id="invoice-upload"
            type="file"
            accept="image/*,application/pdf"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (!file) return
              if (!geminiEnabled) {
                setError('Gemini is off — add GEMINI_API_KEY and restart the API.')
                return
              }
              void handleFile(file)
            }}
          />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? 'Saving…' : 'Add to tracker'}
        </button>
      </div>
    </form>
  )
}
