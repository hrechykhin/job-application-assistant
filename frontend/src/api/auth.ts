import { apiClient } from './client'
import type { TokenResponse, User } from '../types'

export const authApi = {
  register: (email: string, password: string, full_name?: string) =>
    apiClient.post<User>('/auth/register', { email, password, full_name }).then((r) => r.data),

  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),
}
