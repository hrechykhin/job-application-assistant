export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function formatPercent(rate: number): string {
  return `${Math.round(rate * 100)}%`
}

export const STATUS_LABELS: Record<string, string> = {
  SAVED: 'Saved',
  APPLIED: 'Applied',
  SCREENING: 'Screening',
  TEST_TASK: 'Test Task',
  TECHNICAL_INTERVIEW: 'Tech Interview',
  TEAM_INTERVIEW: 'Team Interview',
  OFFER: 'Offer',
  REJECTED: 'Rejected',
}

export const STATUS_COLORS: Record<string, string> = {
  SAVED: 'bg-slate-100 text-slate-700',
  APPLIED: 'bg-blue-100 text-blue-700',
  SCREENING: 'bg-purple-100 text-purple-700',
  TEST_TASK: 'bg-orange-100 text-orange-700',
  TECHNICAL_INTERVIEW: 'bg-cyan-100 text-cyan-700',
  TEAM_INTERVIEW: 'bg-yellow-100 text-yellow-700',
  OFFER: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}
