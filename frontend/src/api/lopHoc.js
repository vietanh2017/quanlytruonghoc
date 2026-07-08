// frontend/src/api/lopHoc.js
import axios from 'axios'

const api = axios.create({ baseURL: `${import.meta.env.VITE_API_URL}/api/v1` })

export const lopHocApi = {
  // Lớp học
  getAll: (includeInactive = false) => api.get(`/lop-hoc/?include_inactive=${includeInactive}`),
  getById: (id) => api.get(`/lop-hoc/${id}`),
  create: (data) => api.post('/lop-hoc/', data),
  update: (id, data) => api.put(`/lop-hoc/${id}`, data),
  delete: (id) => api.delete(`/lop-hoc/${id}`),
  toggleActive: (id) => api.patch(`/lop-hoc/${id}/trang-thai`),

  // Học sinh
  getHocSinh: (lopId) => api.get(`/lop-hoc/${lopId}/hoc-sinh`),
  themHocSinh: (lopId, data) => api.post(`/lop-hoc/${lopId}/hoc-sinh`, { ...data, lop_hoc_id: lopId }),
  suaHocSinh: (hsId, data) => api.put(`/lop-hoc/hoc-sinh/${hsId}`, data),
  xoaHocSinh: (hsId) => api.delete(`/lop-hoc/hoc-sinh/${hsId}`),
  toggleHocSinh: (hsId) => api.patch(`/lop-hoc/hoc-sinh/${hsId}/trang-thai`),
  xoaToanBoHocSinh: (lopId) => api.delete(`/lop-hoc/${lopId}/hoc-sinh`),
}
