import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../../auth/AuthContext'
import { usersApi } from '../../api/users'
import { authApi } from '../../api/auth'
import { LoadingSpinner } from '../../components/LoadingSpinner'

function ProgressBar({ used, limit }: { used: number; limit: number }) {
  const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0
  const colour =
    pct >= 80 ? 'bg-red-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-green-500'
  return (
    <div className="h-2 w-full rounded-full bg-slate-200">
      <div
        className={`h-2 rounded-full transition-all ${colour}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function formatResetTime(iso: string): string {
  const d = new Date(iso)
  const hh = d.getUTCHours().toString().padStart(2, '0')
  const mm = d.getUTCMinutes().toString().padStart(2, '0')
  return `${hh}:${mm} UTC`
}

function formatMemberSince(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function ProfilePage() {
  const { user } = useAuth()
  const qc = useQueryClient()
  const [name, setName] = useState(user?.full_name ?? '')
  const [saved, setSaved] = useState(false)

  const { data: quota, isLoading: quotaLoading } = useQuery({
    queryKey: ['ai-quota'],
    queryFn: usersApi.quota,
  })

  const updateMut = useMutation({
    mutationFn: (full_name: string | null) => usersApi.update({ full_name }),
    onSuccess: async () => {
      // Re-fetch /users/me to refresh auth context
      const updated = await authApi.me()
      qc.setQueryData(['me'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (!user) return <LoadingSpinner />

  return (
    <div className="space-y-4 max-w-xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Profile</h1>
        <p className="text-sm text-slate-500">Your account details and AI usage</p>
      </div>

      {/* Account card */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Account</h2>

        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-500">Email</label>
          <p className="text-sm text-slate-700">{user.email}</p>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-500">Full name</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              className="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              onClick={() => updateMut.mutate(name || null)}
              disabled={updateMut.isPending}
              className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50 transition-colors"
            >
              {updateMut.isPending ? 'Saving…' : saved ? 'Saved!' : 'Save'}
            </button>
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-500">Member since</label>
          <p className="text-sm text-slate-700">{formatMemberSince(user.created_at)}</p>
        </div>
      </div>

      {/* AI Quota card */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          AI Requests Today
        </h2>

        {quotaLoading ? (
          <LoadingSpinner />
        ) : quota ? (
          <div className="space-y-3">
            <ProgressBar used={quota.used} limit={quota.limit} />
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-700">
                <span className="font-semibold">{quota.used}</span>
                <span className="text-slate-400"> of {quota.limit} used</span>
                {' · '}
                <span className={quota.remaining === 0 ? 'text-red-600 font-medium' : 'text-slate-600'}>
                  {quota.remaining} remaining
                </span>
              </span>
              <span className="text-xs text-slate-400">
                Resets at {formatResetTime(quota.resets_at)}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Could not load quota.</p>
        )}
      </div>
    </div>
  )
}
