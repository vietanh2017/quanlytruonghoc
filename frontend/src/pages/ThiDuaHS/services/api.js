// frontend/src/pages/ThiDuaHS/services/api.js
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1/thi-dua-hs'
export const api = axios.create({ baseURL: API_BASE })

// ===== METADATA =====
export const metaAPI = {
  getNamHoc: () => api.get('/meta/nam-hoc'),
  getLop: () => api.get('/meta/lop'),
  getHocSinh: (lopId) => api.get(`/meta/hoc-sinh?lop_hoc_id=${lopId}`),
}
export const cauHinhAPI = {
  getSoNgay: () => api.get('/cau-hinh/so-ngay'),           // ✅
  setSoNgay: (soNgay) => api.post(`/cau-hinh/so-ngay?so_ngay=${soNgay}`),  // ✅
}
// ===== LOẠI VI PHẠM =====
export const loaiVpAPI = {
  getAll: (loai) => api.get(`/loai-vi-pham${loai ? `?loai=${loai}` : ''}`),
  create: (data) => api.post('/loai-vi-pham', data),
  update: (id, data) => api.put(`/loai-vi-pham/${id}`, data),
  delete: (id) => api.delete(`/loai-vi-pham/${id}`),
}

// ===== VI PHẠM CÁ NHÂN =====
export const caNhanAPI = {
  get: (lopId, namHocId, tuan) =>
    api.get(`/ca-nhan?lop_hoc_id=${lopId}&nam_hoc_id=${namHocId}&tuan=${tuan}`),
  create: (data) => api.post('/ca-nhan', data),
  update: (id, data) => api.put(`/ca-nhan/${id}`, data),
  delete: (id) => api.delete(`/ca-nhan/${id}`),
}

// ===== VI PHẠM TẬP THỂ =====
export const tapTheAPI = {
  get: (namHocId, tuan, lopId) => {
    let url = `/tap-the?nam_hoc_id=${namHocId}&tuan=${tuan}`
    if (lopId) url += `&lop_hoc_id=${lopId}`
    return api.get(url)
  },
  create: (data) => api.post('/tap-the', data),
  update: (id, data) => api.put(`/tap-the/${id}`, data),
  delete: (id) => api.delete(`/tap-the/${id}`),
}

// ===== ĐIỂM TUẦN =====
export const diemTuanAPI = {
  get: (namHocId, tuan) => api.get(`/diem-tuan?nam_hoc_id=${namHocId}&tuan=${tuan}`),
  save: (data) => api.post('/diem-tuan/luu', data),
}

// ===== QUẢN LÝ THÁNG =====
export const thangAPI = {  // ⭐ THÊM export này
  get: (namHocId) => api.get(`/thang${namHocId ? `?nam_hoc_id=${namHocId}` : ''}`),
  create: (data) => api.post('/thang', data),
  update: (id, data) => api.put(`/thang/${id}`, data),
  delete: (id) => api.delete(`/thang/${id}`),
  baoCao: (id) => api.get(`/bao-cao-thang/${id}`),
  capNhatDiem: (id) => api.post(`/thang/${id}/cap-nhat-diem`),
}

// ===== BÁO CÁO =====
export const baoCaoAPI = {
  thang: (id) => api.get(`/bao-cao-thang/${id}`),
}
// ===== HỌC KỲ =====
export const hocKyAPI = {
  get: (namHocId) => api.get(`/hoc-ky${namHocId ? `?nam_hoc_id=${namHocId}` : ''}`),
  create: (data) => api.post('/hoc-ky', data),
  update: (id, data) => api.put(`/hoc-ky/${id}`, data),
  delete: (id) => api.delete(`/hoc-ky/${id}`),
  baoCao: (id) => api.get(`/bao-cao-hoc-ky/${id}`),
  capNhatDiem: (id) => api.post(`/hoc-ky/${id}/cap-nhat-diem`),
}
// ===== BÁO CÁO NĂM HỌC =====
export const namHocAPI = {
  baoCao: (data) => api.post('/bao-cao-nam-hoc', data),
}