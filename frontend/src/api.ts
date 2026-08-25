import type { Insights, Metrics, Status, Subscription, SubscriptionCreate } from './types'

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item) => (typeof item === 'object' && item && 'msg' in item ? String(item.msg) : JSON.stringify(item)))
        .join('; ')
    }
  } catch {
    /* ignore */
  }
  return `Request failed (${res.status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })
  if (!res.ok) throw new Error(await parseError(res))
  return (await res.json()) as T
}

export const api = {
  health: () => request<{ status: string }>('/health'),
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
}
