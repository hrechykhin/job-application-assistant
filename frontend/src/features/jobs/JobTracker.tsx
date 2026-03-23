import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Briefcase, Trash2, ExternalLink } from 'lucide-react'
import { jobsApi, type JobCreatePayload } from '../../api/jobs'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { ErrorMessage } from '../../components/ErrorMessage'
import { formatDate } from '../../utils/formatters'

function JobForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState<JobCreatePayload>({
    company_name: '',
    title: '',
    location: '',
    job_url: '',
    description: '',
  })
  const [error, setError] = useState('')

  const mut = useMutation({
    mutationFn: jobsApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      onClose()
    },
    onError: () => setError('Failed to save job.'),
  })

  const set = (field: keyof JobCreatePayload) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => setForm((f) => ({ ...f, [field]: e.target.value }))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Add Job</h2>
        {error && <ErrorMessage message={error} />}
        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault()
            mut.mutate(form)
          }}
        >
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Company *</label>
              <input required value={form.company_name} onChange={set('company_name')}
                className="input w-full" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Job Title *</label>
              <input required value={form.title} onChange={set('title')}
                className="input w-full" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Location</label>
              <input value={form.location} onChange={set('location')} className="input w-full" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Job URL</label>
              <input type="url" value={form.job_url} onChange={set('job_url')} className="input w-full" />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Job Description *</label>
            <textarea required rows={5} value={form.description} onChange={set('description')}
              className="input w-full resize-none" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={mut.isPending}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60 transition-colors">
              {mut.isPending ? 'Saving…' : 'Save Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export function JobTracker() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const { data: jobs, isLoading, error } = useQuery({ queryKey: ['jobs'], queryFn: jobsApi.list })
  const deleteMut = useMutation({
    mutationFn: jobsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Job Tracker</h1>
          <p className="text-sm text-slate-500">Jobs you're targeting</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Job
        </button>
      </div>

      {showForm && <JobForm onClose={() => setShowForm(false)} />}

      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message="Failed to load jobs." />
      ) : jobs?.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <Briefcase className="mx-auto mb-3 h-8 w-8 text-slate-400" />
          <p className="text-slate-500">No jobs yet. Add a job to start applying.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs?.map((job) => (
            <div key={job.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm hover:border-brand-300 transition-colors">
              <Link to={`/jobs/${job.id}`} className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 truncate">{job.title}</p>
                <p className="text-sm text-slate-500">
                  {job.company_name}
                  {job.location && ` · ${job.location}`}
                  {' · '}
                  {formatDate(job.created_at)}
                </p>
              </Link>
              <div className="flex items-center gap-2 ml-4">
                {job.job_url && (
                  <a href={job.job_url} target="_blank" rel="noopener noreferrer"
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
                <button
                  onClick={() => { if (confirm('Delete this job?')) deleteMut.mutate(job.id) }}
                  className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
