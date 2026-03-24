import { apiClient } from './client'
import type { CV } from '../types'

export const cvsApi = {
  list: () => apiClient.get<CV[]>('/cvs').then((r) => r.data),

  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<CV>('/cvs', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  download: (cvId: number) =>
    apiClient.get(`/cvs/download/${cvId}`, { responseType: 'blob' }).then((r) => r.data as Blob),

  delete: (cvId: number) => apiClient.delete(`/cvs/${cvId}`),
}
