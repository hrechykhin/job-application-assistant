import { apiClient } from './client'
import type { CoverLetterResult, CVTailoringResult, JobMatchResult } from '../types'

export const aiApi = {
  jobMatch: (cv_id: number, job_id: number) =>
    apiClient.post<JobMatchResult>('/ai/job-match', { cv_id, job_id }).then((r) => r.data),

  cvTailoring: (cv_id: number, job_id: number) =>
    apiClient.post<CVTailoringResult>('/ai/cv-tailoring', { cv_id, job_id }).then((r) => r.data),

  coverLetter: (cv_id: number, job_id: number, tone = 'professional') =>
    apiClient.post<CoverLetterResult>('/ai/cover-letter', { cv_id, job_id, tone }).then((r) => r.data),
}
