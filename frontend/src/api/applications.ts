import { apiClient } from './client'
import type { Application, ApplicationStats, ApplicationStatus } from '../types'

export const applicationsApi = {
  list: () => apiClient.get<Application[]>('/applications').then((r) => r.data),

  create: (data: { job_id: number; cv_id?: number; notes?: string }) =>
    apiClient.post<Application>('/applications', data).then((r) => r.data),

  update: (appId: number, data: { status?: ApplicationStatus; notes?: string; cv_id?: number }) =>
    apiClient.patch<Application>(`/applications/${appId}`, data).then((r) => r.data),

  delete: (appId: number) => apiClient.delete(`/applications/${appId}`),

  stats: () => apiClient.get<ApplicationStats>('/applications/stats').then((r) => r.data),
}
