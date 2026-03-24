import { apiClient } from './client'
import type { Job, JobImportPreview } from '../types'

export interface JobCreatePayload {
  company_name: string
  title: string
  location?: string
  job_url?: string
  description: string
}

export const jobsApi = {
  list: () => apiClient.get<Job[]>('/jobs').then((r) => r.data),

  get: (jobId: number) => apiClient.get<Job>(`/jobs/${jobId}`).then((r) => r.data),

  create: (data: JobCreatePayload) => apiClient.post<Job>('/jobs', data).then((r) => r.data),

  update: (jobId: number, data: Partial<JobCreatePayload>) =>
    apiClient.patch<Job>(`/jobs/${jobId}`, data).then((r) => r.data),

  delete: (jobId: number) => apiClient.delete(`/jobs/${jobId}`),

  importFromUrl: (url: string) =>
    apiClient.post<JobImportPreview>('/jobs/import-url', { url }).then((r) => r.data),
}
