import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, ExternalLink, Sparkles } from 'lucide-react'
import { applicationsApi } from '../../api/applications'
import { cvsApi } from '../../api/cvs'
import { aiApi } from '../../api/ai'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { ErrorMessage } from '../../components/ErrorMessage'
import { STATUS_LABELS } from '../../utils/formatters'
import type { ApplicationStatus, JobMatchResult, CVTailoringResult, CoverLetterResult } from '../../types'

const STATUSES: ApplicationStatus[] = ['SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED']
const AI_TABS = ['Job Match', 'CV Tailoring', 'Cover Letter'] as const
type AiTab = typeof AI_TABS[number]

function DateField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-slate-600">{label}</label>
      <input
        type="datetime-local"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input w-full text-sm"
      />
    </div>
  )
}

function JobMatchPanel({ cvId, jobId }: { cvId: number | null; jobId: number }) {
  const [result, setResult] = useState<JobMatchResult | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!cvId) { setError('Select a CV first.'); return }
    setRunning(true); setError('')
    try { setResult(await aiApi.jobMatch(cvId, jobId)) }
    catch { setError('AI request failed.') }
    finally { setRunning(false) }
  }

  return (
    <div className="space-y-3">
      <button onClick={run} disabled={running || !cvId}
        className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50 transition-colors">
        <Sparkles className="h-3 w-3" />
        {running ? 'Analysing…' : 'Run Job Match'}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {result && (
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-brand-600">{result.match_score}</span>
            <span className="text-slate-500">/ 100 match score</span>
          </div>
          {result.matched_skills.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Matched skills</p>
              <div className="flex flex-wrap gap-1">
                {result.matched_skills.map((s) => (
                  <span key={s} className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">{s}</span>
                ))}
              </div>
            </div>
          )}
          {result.missing_skills.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Missing skills</p>
              <div className="flex flex-wrap gap-1">
                {result.missing_skills.map((s) => (
                  <span key={s} className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700">{s}</span>
                ))}
              </div>
            </div>
          )}
          {result.summary && <p className="text-slate-600 italic">{result.summary}</p>}
          {result.suggested_improvements.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Improvements</p>
              <ul className="list-disc pl-4 space-y-1 text-slate-600">
                {result.suggested_improvements.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
      {!result && !running && (
        <p className="text-xs text-slate-400">Run to see how well your CV matches this job.</p>
      )}
    </div>
  )
}

function CVTailoringPanel({ cvId, jobId }: { cvId: number | null; jobId: number }) {
  const [result, setResult] = useState<CVTailoringResult | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!cvId) { setError('Select a CV first.'); return }
    setRunning(true); setError('')
    try { setResult(await aiApi.cvTailoring(cvId, jobId)) }
    catch { setError('AI request failed.') }
    finally { setRunning(false) }
  }

  return (
    <div className="space-y-3">
      <button onClick={run} disabled={running || !cvId}
        className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50 transition-colors">
        <Sparkles className="h-3 w-3" />
        {running ? 'Analysing…' : 'Run CV Tailoring'}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {result && (
        <div className="space-y-3 text-sm">
          {result.keywords_to_emphasize.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Keywords to emphasise</p>
              <div className="flex flex-wrap gap-1">
                {result.keywords_to_emphasize.map((k) => (
                  <span key={k} className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">{k}</span>
                ))}
              </div>
            </div>
          )}
          {result.summary_suggestions.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Summary suggestions</p>
              <ul className="list-disc pl-4 space-y-1 text-slate-600">
                {result.summary_suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          {result.experience_improvements.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold text-slate-600">Experience improvements</p>
              <ul className="list-disc pl-4 space-y-1 text-slate-600">
                {result.experience_improvements.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          {result.disclaimer && <p className="text-xs text-slate-400 italic">{result.disclaimer}</p>}
        </div>
      )}
      {!result && !running && (
        <p className="text-xs text-slate-400">Run to get tailoring suggestions for your CV.</p>
      )}
    </div>
  )
}

function CoverLetterPanel({ cvId, jobId }: { cvId: number | null; jobId: number }) {
  const [result, setResult] = useState<CoverLetterResult | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [tone, setTone] = useState('professional')

  const run = async () => {
    if (!cvId) { setError('Select a CV first.'); return }
    setRunning(true); setError('')
    try { setResult(await aiApi.coverLetter(cvId, jobId, tone)) }
    catch { setError('AI request failed.') }
    finally { setRunning(false) }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <select value={tone} onChange={(e) => setTone(e.target.value)} className="input text-xs py-1">
          <option value="professional">Professional</option>
          <option value="enthusiastic">Enthusiastic</option>
          <option value="concise">Concise</option>
        </select>
        <button onClick={run} disabled={running || !cvId}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50 transition-colors">
          <Sparkles className="h-3 w-3" />
          {running ? 'Writing…' : 'Generate'}
        </button>
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {result && (
        <div className="space-y-2">
          <textarea
            readOnly
            value={result.cover_letter}
            rows={14}
            className="input w-full resize-none text-sm leading-relaxed"
          />
          {result.disclaimer && <p className="text-xs text-slate-400 italic">{result.disclaimer}</p>}
        </div>
      )}
      {!result && !running && (
        <p className="text-xs text-slate-400">Generate a cover letter tailored to this job.</p>
      )}
    </div>
  )
}

export function ApplicationWorkspace() {
  const { appId } = useParams<{ appId: string }>()
  const id = Number(appId)
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: app, isLoading, error } = useQuery({
    queryKey: ['application', id],
    queryFn: () => applicationsApi.get(id),
  })
  const { data: cvs } = useQuery({ queryKey: ['cvs'], queryFn: cvsApi.list })

  const [activeTab, setActiveTab] = useState<AiTab>('Job Match')
  const [form, setForm] = useState<{
    status: ApplicationStatus
    notes: string
    cv_id: number | ''
    applied_at: string
    deadline: string
    follow_up_date: string
    interview_at: string
  } | null>(null)
  const [saveMsg, setSaveMsg] = useState('')

  // Initialise form once app loads
  if (app && form === null) {
    setForm({
      status: app.status,
      notes: app.notes ?? '',
      cv_id: app.cv_id ?? '',
      applied_at: app.applied_at ? app.applied_at.slice(0, 16) : '',
      deadline: app.deadline ? app.deadline.slice(0, 16) : '',
      follow_up_date: app.follow_up_date ? app.follow_up_date.slice(0, 16) : '',
      interview_at: app.interview_at ? app.interview_at.slice(0, 16) : '',
    })
  }

  const saveMut = useMutation({
    mutationFn: () =>
      applicationsApi.update(id, {
        status: form!.status,
        notes: form!.notes || null,
        cv_id: form!.cv_id !== '' ? Number(form!.cv_id) : null,
        applied_at: form!.applied_at || null,
        deadline: form!.deadline || null,
        follow_up_date: form!.follow_up_date || null,
        interview_at: form!.interview_at || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      qc.invalidateQueries({ queryKey: ['application', id] })
      qc.invalidateQueries({ queryKey: ['application-stats'] })
      setSaveMsg('Saved')
      setTimeout(() => setSaveMsg(''), 2000)
    },
  })

  if (isLoading) return <LoadingSpinner />
  if (error || !app) return <ErrorMessage message="Application not found." />
  if (!form) return <LoadingSpinner />

  const job = app.job
  const cvId = form.cv_id !== '' ? Number(form.cv_id) : null

  return (
    <div className="space-y-4">
      <button
        onClick={() => navigate('/applications')}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Board
      </button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{job?.title ?? 'Application'}</h1>
          <p className="text-sm text-slate-500">
            {job?.company_name}
            {job?.location && ` · ${job.location}`}
          </p>
        </div>
        {job?.job_url && (
          <a href={job.job_url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-brand-600 hover:underline">
            <ExternalLink className="h-4 w-4" />
            View posting
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Left: Application details */}
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <h2 className="text-sm font-semibold text-slate-700">Application Details</h2>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Status</label>
              <select
                value={form.status}
                onChange={(e) => setForm((f) => f && ({ ...f, status: e.target.value as ApplicationStatus }))}
                className="input w-full"
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">CV</label>
              <select
                value={form.cv_id}
                onChange={(e) => setForm((f) => f && ({ ...f, cv_id: e.target.value ? Number(e.target.value) : '' }))}
                className="input w-full"
              >
                <option value="">No CV selected</option>
                {cvs?.map((cv) => (
                  <option key={cv.id} value={cv.id}>{cv.original_filename}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Notes</label>
              <textarea
                rows={3}
                value={form.notes}
                onChange={(e) => setForm((f) => f && ({ ...f, notes: e.target.value }))}
                className="input w-full resize-none"
                placeholder="Add notes…"
              />
            </div>

            <DateField label="Applied on" value={form.applied_at}
              onChange={(v) => setForm((f) => f && ({ ...f, applied_at: v }))} />
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <h2 className="text-sm font-semibold text-slate-700">Reminders</h2>
            <DateField label="Application deadline" value={form.deadline}
              onChange={(v) => setForm((f) => f && ({ ...f, deadline: v }))} />
            <DateField label="Follow-up date" value={form.follow_up_date}
              onChange={(v) => setForm((f) => f && ({ ...f, follow_up_date: v }))} />
            <DateField label="Interview date & time" value={form.interview_at}
              onChange={(v) => setForm((f) => f && ({ ...f, interview_at: v }))} />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => saveMut.mutate()}
              disabled={saveMut.isPending}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
            >
              {saveMut.isPending ? 'Saving…' : 'Save Changes'}
            </button>
            {saveMsg && <span className="text-sm text-green-600">{saveMsg}</span>}
          </div>

          {job && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-slate-700">Job Description</h2>
              <pre className="whitespace-pre-wrap text-sm text-slate-600 font-sans leading-relaxed max-h-64 overflow-y-auto">
                {job.description}
              </pre>
            </div>
          )}
        </div>

        {/* Right: AI tools */}
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex border-b border-slate-200">
            {AI_TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-3 py-3 text-xs font-medium transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-brand-600 text-brand-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="p-5">
            {!cvId && (
              <p className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
                Select a CV on the left to enable AI analysis.
              </p>
            )}
            {activeTab === 'Job Match' && <JobMatchPanel cvId={cvId} jobId={app.job_id} />}
            {activeTab === 'CV Tailoring' && <CVTailoringPanel cvId={cvId} jobId={app.job_id} />}
            {activeTab === 'Cover Letter' && <CoverLetterPanel cvId={cvId} jobId={app.job_id} />}
          </div>
        </div>
      </div>
    </div>
  )
}
