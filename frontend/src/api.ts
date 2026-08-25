import type { Insights, Metrics, Status, Subscription, SubscriptionCreate } from './types'

const TOKEN_KEY = 'st_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item) =>
          typeof item === 'object' && item && 'msg' in item ? String(item.msg) : JSON.stringify(item),
        )
        .join('; ')
    }
  } catch {
    /* ignore */
  }
  return `Request failed (${res.status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  const isForm = init?.body instanceof FormData
  if (!isForm && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const res = await fetch(`/api${path}`, { ...init, headers })
  if (res.status === 401) {
    setToken(null)
  }
  if (!res.ok) throw new Error(await parseError(res))
  return (await res.json()) as T
}

export type InvoiceDraft = {
  name: string
  cost: number
  billing_cycle: 'Monthly' | 'Yearly'
  next_renewal_date: string | null
  currency: string
  notes: string
  confidence: number
}

export const api = {
  health: () => request<{ status: string; gemini: boolean }>('/health'),
  login: (email: string, password: string) =>
    request<{ access_token: string; email: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string) =>
    request<{ access_token: string; email: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<{ id: number; email: string; gemini_enabled: boolean }>('/auth/me'),
  metrics: () => request<Metrics>('/metrics'),
  list: () => request<Subscription[]>('/subscriptions'),
  create: (payload: SubscriptionCreate) =>
    request<Subscription>('/subscriptions', { method: 'POST', body: JSON.stringify(payload) }),
  setStatus: (id: number, status: Status) =>
    request<Subscription>(`/subscriptions/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  insights: () => request<Insights>('/insights'),
  extractInvoice: (file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<{ draft: InvoiceDraft; saved: boolean }>('/extract/invoice', {
      method: 'POST',
      body,
    })
  },
  chat: (message: string) =>
    request<{ reply: string; source: string }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),
}
