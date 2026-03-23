import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Plus, ExternalLink } from 'lucide-react'
import { jobsApi } from '../../api/jobs'
import { applicationsApi } from '../../api/applications'
import { cvsApi } from '../../api/cvs'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { ErrorMessage } from '../../components/ErrorMessage'
import { formatDate, STATUS_LABELS, STATUS_COLORS } from '../../utils/formatters'

export function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>()
  const id = Number(jobId)
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [applying, setApplying] = useState(false)
  const [selectedCv, setSelectedCv] = useState<number | ''>('')

  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.get(id),
  })

  const { data: cvs } = useQuery({ queryKey: ['cvs'], queryFn: cvsApi.list })
  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: applicationsApi.list,
  })

  const jobApplications = applications?.filter((a) => a.job_id === id) ?? []

  const createAppMut = useMutation({
    mutationFn: () =>
      applicationsApi.create({ job_id: id, cv_id: selectedCv !== '' ? selectedCv : undefined }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      setApplying(false)
    },
  })

  if (isLoading) return <LoadingSpinner />
  if (error || !job) return <ErrorMessage message="Job not found." />

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">{job.title}</h1>
            <p className="mt-1 text-slate-500">
              {job.company_name}
              {job.location && ` · ${job.location}`}
            </p>
            <p className="mt-1 text-xs text-slate-400">Added {formatDate(job.created_at)}</p>
          </div>
          {job.job_url && (
            <a
              href={job.job_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-brand-600 hover:underline"
            >
              <ExternalLink className="h-4 w-4" />
              View posting
            </a>
          )}
        </div>
        <div className="mt-4 border-t border-slate-100 pt-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Job Description</h2>
          <pre className="whitespace-pre-wrap text-sm text-slate-600 font-sans leading-relaxed">
            {job.description}
          </pre>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-slate-700">
            Applications ({jobApplications.length})
          </h2>
          {!applying && (
            <button
              onClick={() => setApplying(true)}
              className="flex items-center gap-1 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 transition-colors"
            >
              <Plus className="h-3 w-3" />
              Create Application
            </button>
          )}
        </div>

        {applying && (
          <div className="mb-4 rounded-lg bg-slate-50 p-4 space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Select CV (optional)</label>
              <select
                value={selectedCv}
                onChange={(e) => setSelectedCv(e.target.value ? Number(e.target.value) : '')}
                className="input w-full"
              >
                <option value="">No CV</option>
                {cvs?.map((cv) => (
                  <option key={cv.id} value={cv.id}>
                    {cv.original_filename}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => createAppMut.mutate()}
                disabled={createAppMut.isPending}
                className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
              >
                {createAppMut.isPending ? 'Creating…' : 'Confirm'}
              </button>
              <button
                onClick={() => setApplying(false)}
                className="rounded-lg px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {jobApplications.length === 0 ? (
          <p className="text-sm text-slate-400">No applications for this job yet.</p>
        ) : (
          <div className="space-y-2">
            {jobApplications.map((app) => (
              <div key={app.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-2">
                <span className="text-sm text-slate-700">
                  {app.applied_at ? `Applied ${formatDate(app.applied_at)}` : 'Not applied yet'}
                </span>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[app.status]}`}>
                  {STATUS_LABELS[app.status]}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
