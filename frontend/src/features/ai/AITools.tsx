import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react'
import { aiApi } from '../../api/ai'
import { cvsApi } from '../../api/cvs'
import { jobsApi } from '../../api/jobs'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import type { CoverLetterResult, CVTailoringResult, JobMatchResult } from '../../types'

type Tool = 'job-match' | 'cv-tailoring' | 'cover-letter'

function MatchScore({ score }: { score: number }) {
  const color = score >= 70 ? 'text-green-600' : score >= 45 ? 'text-yellow-600' : 'text-red-600'
  return (
    <div className="flex items-center gap-2">
      <span className={`text-4xl font-bold ${color}`}>{score}</span>
      <span className="text-slate-400">/100</span>
    </div>
  )
}

function TagList({ items, color }: { items: string[]; color: string }) {
  if (!items.length) return <p className="text-xs text-slate-400">None</p>
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span key={item} className={`rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
          {item}
        </span>
      ))}
    </div>
  )
}

export function AITools() {
  const [activeTool, setActiveTool] = useState<Tool>('job-match')
  const [cvId, setCvId] = useState<number | ''>('')
  const [jobId, setJobId] = useState<number | ''>('')

  const { data: cvs } = useQuery({ queryKey: ['cvs'], queryFn: cvsApi.list })
  const { data: jobs } = useQuery({ queryKey: ['jobs'], queryFn: jobsApi.list })

  const matchMut = useMutation({ mutationFn: () => aiApi.jobMatch(Number(cvId), Number(jobId)) })
  const tailorMut = useMutation({ mutationFn: () => aiApi.cvTailoring(Number(cvId), Number(jobId)) })
  const coverMut = useMutation({ mutationFn: () => aiApi.coverLetter(Number(cvId), Number(jobId)) })

  const canRun = cvId !== '' && jobId !== ''

  const handleRun = () => {
    if (!canRun) return
    if (activeTool === 'job-match') matchMut.mutate()
    if (activeTool === 'cv-tailoring') tailorMut.mutate()
    if (activeTool === 'cover-letter') coverMut.mutate()
  }

  const activeMut =
    activeTool === 'job-match' ? matchMut : activeTool === 'cv-tailoring' ? tailorMut : coverMut

  const tools: { id: Tool; label: string }[] = [
    { id: 'job-match', label: 'Job Match Analysis' },
    { id: 'cv-tailoring', label: 'CV Tailoring' },
    { id: 'cover-letter', label: 'Cover Letter' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">AI Tools</h1>
        <p className="text-sm text-slate-500">
          AI-powered tools to improve your applications. Outputs are drafts — always review before use.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
        <div className="flex flex-wrap gap-2">
          {tools.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTool(t.id)}
              className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                activeTool === t.id
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Select CV</label>
            <select
              value={cvId}
              onChange={(e) => setCvId(e.target.value ? Number(e.target.value) : '')}
              className="input w-full"
            >
              <option value="">Choose a CV…</option>
              {cvs?.map((cv) => (
                <option key={cv.id} value={cv.id}>
                  {cv.original_filename}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Select Job</label>
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value ? Number(e.target.value) : '')}
              className="input w-full"
            >
              <option value="">Choose a job…</option>
              {jobs?.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} — {job.company_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={!canRun || activeMut.isPending}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
        >
          <Sparkles className="h-4 w-4" />
          {activeMut.isPending ? 'Analysing…' : 'Run Analysis'}
        </button>

        {activeMut.isError && (
          <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="h-4 w-4 shrink-0" />
            AI service error. Check your API key or try again.
          </div>
        )}
      </div>

      {activeMut.isPending && <LoadingSpinner size="lg" />}

      {activeTool === 'job-match' && matchMut.data && (
        <JobMatchOutput result={matchMut.data} />
      )}
      {activeTool === 'cv-tailoring' && tailorMut.data && (
        <TailoringOutput result={tailorMut.data} />
      )}
      {activeTool === 'cover-letter' && coverMut.data && (
        <CoverLetterOutput result={coverMut.data} />
      )}
    </div>
  )
}

function JobMatchOutput({ result }: { result: JobMatchResult }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
      <h2 className="font-semibold text-slate-900">Job Match Analysis</h2>
      <div className="flex items-center gap-4">
        <MatchScore score={result.match_score} />
        <p className="flex-1 text-sm text-slate-600">{result.summary}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-green-700">Matched Skills</p>
          <TagList items={result.matched_skills} color="bg-green-100 text-green-700" />
        </div>
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-red-700">Missing Skills</p>
          <TagList items={result.missing_skills} color="bg-red-100 text-red-700" />
        </div>
      </div>
      {result.suggested_improvements.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Suggested Improvements</p>
          <ul className="space-y-1">
            {result.suggested_improvements.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-brand-500" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function TailoringOutput({ result }: { result: CVTailoringResult }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
      <h2 className="font-semibold text-slate-900">CV Tailoring Suggestions</h2>
      <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-700">{result.disclaimer}</p>

      {[
        { label: 'Summary Suggestions', items: result.summary_suggestions },
        { label: 'Experience Improvements', items: result.experience_improvements },
        { label: 'Skills Suggestions', items: result.skills_suggestions },
      ].map(({ label, items }) =>
        items.length ? (
          <div key={label}>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
            <ul className="space-y-2">
              {items.map((s, i) => (
                <li key={i} className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{s}</li>
              ))}
            </ul>
          </div>
        ) : null
      )}

      {result.keywords_to_emphasize.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Keywords to Emphasize</p>
          <TagList items={result.keywords_to_emphasize} color="bg-brand-100 text-brand-700" />
        </div>
      )}
    </div>
  )
}

function CoverLetterOutput({ result }: { result: CoverLetterResult }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(result.cover_letter)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-900">Cover Letter Draft</h2>
        <button
          onClick={copy}
          className="rounded-lg px-3 py-1.5 text-xs font-medium text-brand-600 hover:bg-brand-50 transition-colors"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-700">{result.disclaimer}</p>
      <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700 leading-relaxed">
        {result.cover_letter}
      </pre>
    </div>
  )
}
