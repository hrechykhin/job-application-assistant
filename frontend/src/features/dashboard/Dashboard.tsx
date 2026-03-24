import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Calendar } from 'lucide-react'
import { applicationsApi } from '../../api/applications'
import { useAuth } from '../../auth/AuthContext'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { formatDate, STATUS_LABELS, STATUS_COLORS } from '../../utils/formatters'
import type { Application } from '../../types'

const STATUS_CHART_COLORS: Record<string, string> = {
  SAVED: '#94a3b8',
  APPLIED: '#3b82f6',
  INTERVIEW: '#f59e0b',
  OFFER: '#22c55e',
  REJECTED: '#ef4444',
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-slate-900">{value}</p>
    </div>
  )
}

function UpcomingItem({ app, label, date }: { app: Application; label: string; date: string }) {
  return (
    <Link
      to={`/applications/${app.id}`}
      className="flex items-center justify-between rounded-lg border border-slate-100 bg-white px-4 py-3 hover:border-brand-300 transition-colors"
    >
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-slate-900">{app.job?.title ?? 'Application'}</p>
        <p className="text-xs text-slate-500">{app.job?.company_name}</p>
      </div>
      <div className="ml-4 shrink-0 text-right">
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[app.status]}`}>
          {label}
        </span>
        <p className="mt-0.5 text-xs text-slate-400">{formatDate(date)}</p>
      </div>
    </Link>
  )
}

function getUpcoming(applications: Application[]): { app: Application; label: string; date: string }[] {
  const now = new Date()
  const cutoff = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  const items: { app: Application; label: string; date: string; ts: number }[] = []

  for (const app of applications) {
    if (app.interview_at) {
      const d = new Date(app.interview_at)
      if (d >= now && d <= cutoff) items.push({ app, label: 'Interview', date: app.interview_at, ts: d.getTime() })
    }
    if (app.deadline) {
      const d = new Date(app.deadline)
      if (d >= now && d <= cutoff) items.push({ app, label: 'Deadline', date: app.deadline, ts: d.getTime() })
    }
    if (app.follow_up_date) {
      const d = new Date(app.follow_up_date)
      if (d >= now && d <= cutoff) items.push({ app, label: 'Follow up', date: app.follow_up_date, ts: d.getTime() })
    }
  }

  return items.sort((a, b) => a.ts - b.ts).map(({ app, label, date }) => ({ app, label, date }))
}

export function Dashboard() {
  const { user } = useAuth()
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['application-stats'],
    queryFn: applicationsApi.stats,
  })
  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: applicationsApi.list,
  })

  const chartData = stats
    ? Object.entries(stats.by_status).map(([status, count]) => ({
        name: STATUS_LABELS[status] ?? status,
        count,
        status,
      }))
    : []

  const upcoming = applications ? getUpcoming(applications) : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Good day{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}
        </h1>
        <p className="text-sm text-slate-500">Here's your application overview</p>
      </div>

      {statsLoading ? (
        <LoadingSpinner />
      ) : stats ? (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatCard label="Total Applications" value={stats.total} />
            <StatCard label="Applied" value={stats.by_status['APPLIED'] ?? 0} />
            <StatCard label="Interview Rate" value={`${Math.round(stats.interview_rate * 100)}%`} />
            <StatCard label="Offer Rate" value={`${Math.round(stats.offer_rate * 100)}%`} />
          </div>

          {upcoming.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Calendar className="h-4 w-4 text-slate-500" />
                <h2 className="text-sm font-semibold text-slate-700">Upcoming (next 7 days)</h2>
              </div>
              <div className="space-y-2">
                {upcoming.map(({ app, label, date }) => (
                  <UpcomingItem key={`${app.id}-${label}`} app={app} label={label} date={date} />
                ))}
              </div>
            </div>
          )}

          {chartData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-sm font-semibold text-slate-700">Applications by Status</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry) => (
                      <Cell key={entry.status} fill={STATUS_CHART_COLORS[entry.status] ?? '#94a3b8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {stats.total === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
              <p className="text-slate-500">No applications yet. Start by adding a job and creating an application.</p>
            </div>
          )}
        </>
      ) : null}
    </div>
  )
}
