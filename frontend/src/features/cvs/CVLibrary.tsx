import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileText, Trash2, Upload, Download } from 'lucide-react'
import { cvsApi } from '../../api/cvs'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { ErrorMessage } from '../../components/ErrorMessage'
import { formatDate } from '../../utils/formatters'

export function CVLibrary() {
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const { data: cvs, isLoading, error } = useQuery({ queryKey: ['cvs'], queryFn: cvsApi.list })

  const deleteMut = useMutation({
    mutationFn: cvsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cvs'] }),
  })

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadError('')
    try {
      await cvsApi.upload(file)
      qc.invalidateQueries({ queryKey: ['cvs'] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setUploadError(msg ?? 'Upload failed.')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleDownload = async (cvId: number, filename: string) => {
    const url = await cvsApi.getDownloadUrl(cvId)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">CV Library</h1>
          <p className="text-sm text-slate-500">Upload and manage your CV files</p>
        </div>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60 transition-colors"
        >
          <Upload className="h-4 w-4" />
          {uploading ? 'Uploading…' : 'Upload CV'}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {uploadError && <ErrorMessage message={uploadError} />}

      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message="Failed to load CVs." />
      ) : cvs?.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <FileText className="mx-auto mb-3 h-8 w-8 text-slate-400" />
          <p className="text-slate-500">No CVs uploaded yet. Upload a PDF or DOCX file to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {cvs?.map((cv) => (
            <div
              key={cv.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-brand-500" />
                <div>
                  <p className="text-sm font-medium text-slate-900">{cv.original_filename}</p>
                  <p className="text-xs text-slate-400">
                    {formatDate(cv.created_at)} · {cv.has_text ? 'Text extracted' : 'No text extracted'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(cv.id, cv.original_filename)}
                  className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                  title="Download"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={() => {
                    if (confirm('Delete this CV?')) deleteMut.mutate(cv.id)
                  }}
                  className="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors"
                  title="Delete"
                >
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
