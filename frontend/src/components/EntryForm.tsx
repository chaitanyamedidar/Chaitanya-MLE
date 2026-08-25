import { useState, type FormEvent } from 'react'
import type { BillingCycle, SubscriptionCreate } from '../types'

type Props = {
  busy: boolean
  onSubmit: (payload: SubscriptionCreate) => Promise<void>
}

export function EntryForm({ busy, onSubmit }: Props) {
  const [name, setName] = useState('')
  const [cost, setCost] = useState('')
  const [cycle, setCycle] = useState<BillingCycle>('Monthly')
  const [renewal, setRenewal] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    const amount = Number(cost)
    if (!name.trim() || !Number.isFinite(amount) || amount <= 0 || !renewal) {
      setError('Fill in a service name, a cost greater than 0, and a renewal date.')
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add subscription')
    }
  }

  return (
    <form className="entry-form" onSubmit={handleSubmit}>
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
            value={renewal}
            onChange={(e) => setRenewal(e.target.value)}
            required
          />
        </label>
      </div>
      {error ? <p className="form-error">{error}</p> : null}
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Add to tracker'}
      </button>
    </form>
  )
}
