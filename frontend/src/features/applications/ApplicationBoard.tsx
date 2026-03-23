import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { applicationsApi } from '../../api/applications'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { ErrorMessage } from '../../components/ErrorMessage'
import { formatDate, STATUS_LABELS } from '../../utils/formatters'
import type { Application, ApplicationStatus } from '../../types'
import { Trash2, ChevronRight } from 'lucide-react'

const COLUMNS: ApplicationStatus[] = ['SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED']

const COLUMN_STYLES: Record<ApplicationStatus, string> = {
  SAVED: 'border-slate-300 bg-slate-50',
  APPLIED: 'border-blue-300 bg-blue-50',
  INTERVIEW: 'border-yellow-300 bg-yellow-50',
  OFFER: 'border-green-300 bg-green-50',
  REJECTED: 'border-red-300 bg-red-50',
}

const COLUMN_DRAG_OVER_STYLES: Record<ApplicationStatus, string> = {
  SAVED: 'border-slate-400 bg-slate-100 ring-2 ring-slate-300',
  APPLIED: 'border-blue-400 bg-blue-100 ring-2 ring-blue-300',
  INTERVIEW: 'border-yellow-400 bg-yellow-100 ring-2 ring-yellow-300',
  OFFER: 'border-green-400 bg-green-100 ring-2 ring-green-300',
  REJECTED: 'border-red-400 bg-red-100 ring-2 ring-red-300',
}

const HEADER_STYLES: Record<ApplicationStatus, string> = {
  SAVED: 'text-slate-700',
  APPLIED: 'text-blue-700',
  INTERVIEW: 'text-yellow-700',
  OFFER: 'text-green-700',
  REJECTED: 'text-red-700',
}

const NEXT_STATUS: Partial<Record<ApplicationStatus, ApplicationStatus>> = {
  SAVED: 'APPLIED',
  APPLIED: 'INTERVIEW',
  INTERVIEW: 'OFFER',
}

function AppCard({
  app,
  onAdvance,
  onDelete,
  onDragStart,
  onDragEnd,
  isDragging,
}: {
  app: Application
  onAdvance?: () => void
  onDelete: () => void
  onDragStart: () => void
  onDragEnd: () => void
  isDragging: boolean
}) {
  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className={`rounded-lg border border-white bg-white p-3 shadow-sm space-y-1 cursor-grab active:cursor-grabbing transition-opacity ${
        isDragging ? 'opacity-40' : 'opacity-100'
      }`}
    >
      <p className="text-sm font-medium text-slate-900 truncate">{app.job?.title ?? 'Unknown role'}</p>
      <p className="text-xs text-slate-500 truncate">{app.job?.company_name}</p>
      {app.job?.location && <p className="text-xs text-slate-400">{app.job.location}</p>}
      <p className="text-xs text-slate-400">{formatDate(app.updated_at)}</p>
      {app.notes && <p className="text-xs text-slate-500 italic line-clamp-2">{app.notes}</p>}
      <div className="flex items-center justify-between pt-1">
        {onAdvance ? (
          <button
            onClick={onAdvance}
            className="flex items-center gap-0.5 text-xs text-brand-600 hover:underline"
          >
            <ChevronRight className="h-3 w-3" />
            {STATUS_LABELS[NEXT_STATUS[app.status]!]}
          </button>
        ) : (
          <span />
        )}
        <button
          onClick={onDelete}
          className="rounded p-1 text-slate-300 hover:bg-red-50 hover:text-red-500 transition-colors"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    </div>
  )
}

export function ApplicationBoard() {
  const qc = useQueryClient()
  const [draggedId, setDraggedId] = useState<number | null>(null)
  const [overColumn, setOverColumn] = useState<ApplicationStatus | null>(null)
  const dragCounter = useRef<Record<string, number>>({})

  const { data: applications, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: applicationsApi.list,
  })

  const updateMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ApplicationStatus }) =>
      applicationsApi.update(id, { status }),
    onMutate: async ({ id, status }) => {
      await qc.cancelQueries({ queryKey: ['applications'] })
      const prev = qc.getQueryData<Application[]>(['applications'])
      qc.setQueryData<Application[]>(['applications'], (old) =>
        old?.map((a) => (a.id === id ? { ...a, status } : a)) ?? []
      )
      return { prev }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) qc.setQueryData(['applications'], ctx.prev)
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      qc.invalidateQueries({ queryKey: ['application-stats'] })
    },
  })

  const deleteMut = useMutation({
    mutationFn: applicationsApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      qc.invalidateQueries({ queryKey: ['application-stats'] })
    },
  })

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load applications." />

  const byStatus = COLUMNS.reduce<Record<string, Application[]>>(
    (acc, status) => {
      acc[status] = applications?.filter((a) => a.status === status) ?? []
      return acc
    },
    {}
  )

  const handleDrop = (targetStatus: ApplicationStatus) => {
    if (draggedId !== null) {
      const app = applications?.find((a) => a.id === draggedId)
      if (app && app.status !== targetStatus) {
        updateMut.mutate({ id: draggedId, status: targetStatus })
      }
    }
    setDraggedId(null)
    setOverColumn(null)
    dragCounter.current = {}
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Application Board</h1>
        <p className="text-sm text-slate-500">Track your applications through the pipeline</p>
      </div>

      {(!applications || applications.length === 0) && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <p className="text-slate-500">No applications yet. Create applications from the Job Tracker.</p>
        </div>
      )}

      <div className="grid grid-cols-5 gap-3 overflow-x-auto pb-4">
        {COLUMNS.map((status) => {
          const isOver = overColumn === status
          return (
            <div
              key={status}
              className={`rounded-xl border p-3 transition-all ${
                isOver ? COLUMN_DRAG_OVER_STYLES[status] : COLUMN_STYLES[status]
              }`}
              onDragOver={(e) => {
                e.preventDefault()
                e.dataTransfer.dropEffect = 'move'
              }}
              onDragEnter={(e) => {
                e.preventDefault()
                dragCounter.current[status] = (dragCounter.current[status] ?? 0) + 1
                setOverColumn(status)
              }}
              onDragLeave={() => {
                dragCounter.current[status] = (dragCounter.current[status] ?? 1) - 1
                if (dragCounter.current[status] <= 0) {
                  dragCounter.current[status] = 0
                  setOverColumn((prev) => (prev === status ? null : prev))
                }
              }}
              onDrop={() => handleDrop(status)}
            >
              <div className="mb-3 flex items-center justify-between">
                <span className={`text-xs font-semibold uppercase tracking-wide ${HEADER_STYLES[status]}`}>
                  {STATUS_LABELS[status]}
                </span>
                <span className="rounded-full bg-white/70 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {byStatus[status].length}
                </span>
              </div>
              <div className="space-y-2 min-h-[2rem]">
                {byStatus[status].map((app) => (
                  <AppCard
                    key={app.id}
                    app={app}
                    isDragging={draggedId === app.id}
                    onDragStart={() => setDraggedId(app.id)}
                    onDragEnd={() => {
                      setDraggedId(null)
                      setOverColumn(null)
                      dragCounter.current = {}
                    }}
                    onAdvance={
                      NEXT_STATUS[status]
                        ? () => updateMut.mutate({ id: app.id, status: NEXT_STATUS[status]! })
                        : undefined
                    }
                    onDelete={() => {
                      if (confirm('Delete this application?')) deleteMut.mutate(app.id)
                    }}
                  />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
