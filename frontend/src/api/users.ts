import type { AxiosResponse } from 'axios'
import { apiClient } from './client'
import type { User } from '../types'

export interface AIQuota {
  used: number
  limit: number
  remaining: number
  resets_at: string
}

export const usersApi = {
  me: () => apiClient.get<User>('/users/me').then((r: AxiosResponse<User>) => r.data),
  update: (data: { full_name?: string | null }) =>
    apiClient.patch<User>('/users/me', data).then((r: AxiosResponse<User>) => r.data),
  quota: () => apiClient.get<AIQuota>('/ai/quota').then((r: AxiosResponse<AIQuota>) => r.data),
}
