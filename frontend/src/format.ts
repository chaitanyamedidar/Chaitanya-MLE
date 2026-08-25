const inr = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
})

export function money(value: number): string {
  return inr.format(value)
}

export function daysLabel(days: number): string {
  if (days === 0) return 'Today'
  if (days === 1) return '1 day'
  if (days === -1) return '1 day overdue'
  if (days < 0) return `${Math.abs(days)} days overdue`
  return `${days} days`
}
