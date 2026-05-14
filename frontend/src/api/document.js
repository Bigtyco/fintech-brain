import request from './request'

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getDocuments() {
  return request.get('/documents')
}

export function getDocument(id) {
  return request.get(`/documents/${id}`)
}
