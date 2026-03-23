export interface User {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

export interface CV {
  id: number
  user_id: number
  original_filename: string
  s3_key: string
  has_text: boolean
  created_at: string
}

export interface Job {
  id: number
  user_id: number
  company_name: string
  title: string
  location: string | null
  job_url: string | null
  description: string
  created_at: string
  updated_at: string
}

export type ApplicationStatus = 'SAVED' | 'APPLIED' | 'INTERVIEW' | 'OFFER' | 'REJECTED'

export interface Application {
  id: number
  user_id: number
  job_id: number
  cv_id: number | null
  status: ApplicationStatus
  notes: string | null
  applied_at: string | null
  created_at: string
  updated_at: string
  job?: Job
}

export interface ApplicationStats {
  total: number
  by_status: Record<string, number>
  interview_rate: number
  offer_rate: number
}

export interface JobMatchResult {
  match_score: number
  matched_skills: string[]
  missing_skills: string[]
  suggested_improvements: string[]
  summary: string
}

export interface CVTailoringResult {
  summary_suggestions: string[]
  experience_improvements: string[]
  skills_suggestions: string[]
  keywords_to_emphasize: string[]
  disclaimer: string
}

export interface CoverLetterResult {
  cover_letter: string
  disclaimer: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
