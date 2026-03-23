import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { applicationsApi } from '../../api/applications'
import { useAuth } from '../../auth/AuthContext'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { formatPercent, STATUS_LABELS } from '../../utils/formatters'

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

export function Dashboard() {
  const { user } = useAuth()
  const { data: stats, isLoading } = useQuery({
    queryKey: ['application-stats'],
    queryFn: applicationsApi.stats,
  })

  const chartData = stats
    ? Object.entries(stats.by_status).map(([status, count]) => ({
        name: STATUS_LABELS[status] ?? status,
        count,
        status,
      }))
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Good day{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}
        </h1>
        <p className="text-sm text-slate-500">Here's your application overview</p>
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : stats ? (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatCard label="Total Applications" value={stats.total} />
            <StatCard label="Applied" value={stats.by_status['APPLIED'] ?? 0} />
            <StatCard label="Interview Rate" value={formatPercent(stats.interview_rate)} />
            <StatCard label="Offer Rate" value={formatPercent(stats.offer_rate)} />
          </div>

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
