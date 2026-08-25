export type BillingCycle = 'Monthly' | 'Yearly'
export type Status = 'active' | 'paused'

export type Subscription = {
  id: number
  name: string
  cost: number
  billing_cycle: BillingCycle
  renewal_date: string
  status: Status
  monthly_rate: number
  days_to_renewal: number
  renewing_soon: boolean
  overdue: boolean
  created_at: string
  updated_at: string
}

export type Metrics = {
  monthly_burn_rate: number
  upcoming_renewals_count: number
  active_count: number
  paused_count: number
}

export type SubscriptionCreate = {
  name: string
  cost: number
  billing_cycle: BillingCycle
  renewal_date: string
}

export type Insights = {
  categories: { category: string; monthly_spend: number; share: number; names: string[] }[]
  anomalies: { id: number; name: string; monthly_rate: number; category: string; reason: string }[]
  overlaps: { category: string; names: string[]; monthly_spend: number; suggestion: string }[]
  pause_recommendations: {
    id: number
    name: string
    category: string
    monthly_rate: number
    savings_if_paused: number
  }[]
  cashflow: { month: string; amount: number; names: string[] }[]
}
