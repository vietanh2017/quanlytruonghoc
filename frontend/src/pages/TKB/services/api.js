// frontend/src/pages/TKB/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

export const tkbAPI = {
  // Meta
  getNamHoc: () => api.get('/thi-dua-hs/meta/nam-hoc'),
  getMonHoc: () => api.get('/tkb/meta/mon-hoc'),
  getHocKy: (namHocId) => api.get(`/phan-cong/meta/hoc-ky?nam_hoc_id=${namHocId}`),
  getDsLop: (namHocId) => api.get(`/thi-dua-hs/meta/lop?nam_hoc_id=${namHocId}`),
  swapOTKB: (id1, id2) => api.post('/tkb/swap-o-tkb', { id1, id2 }),

  // getDsGV: unwrap and normalize array shape but keep axios-like response shape
  getDsGV: () => api.get('/giao-vien').then(r => {
    const raw = r.data
    const list = Array.isArray(raw) ? raw
      : Array.isArray(raw?.items) ? raw.items
        : Array.isArray(raw?.results) ? raw.results
          : Array.isArray(raw?.data) ? raw.data
            : []
    return { ...r, data: list }
  }),

  getDSLop: (namHocId) => api.get(`/thi-dua-hs/meta/lop?nam_hoc_id=${namHocId}`),

  // Cấu hình ngày
  getCauHinhNgay: (namHocId) => api.get(`/tkb/cau-hinh-ngay?nam_hoc_id=${namHocId}`),
  saveCauHinhNgay: (data) => api.post('/tkb/cau-hinh-ngay', data),

  // Cấu hình tiết
  getCauHinhTiet: () => api.get('/tkb/cau-hinh-tiet'),
  saveCauHinhTiet: (data) => api.post('/tkb/cau-hinh-tiet', data),

  // Cấu hình môn
  getCauHinhMon: (namHocId) => api.get(`/tkb/cau-hinh-mon?nam_hoc_id=${namHocId}`),
  saveCauHinhMon: (data) => api.post('/tkb/cau-hinh-mon', data),

  // Ràng buộc GV
  getRangBuocGV: (namHocId) => api.get(`/tkb/rang-buoc-gv?nam_hoc_id=${namHocId}`),
  saveRangBuocGV: (data) => api.post('/tkb/rang-buoc-gv', data),

  // TKB chính — trả axios response so TabNhapTKB vẫn dùng r.data
  getTKBLop: (lopId, namHocId, hocKyId) => {
    const t = new Date().getTime()
    return api.get(`/tkb/theo-lop/${lopId}?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}&_=${t}`)
  },
  getTKBGV: (gvId, namHocId, hocKyId) => {
    const t = new Date().getTime()
    return api.get(`/tkb/theo-gv/${gvId}?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}&_=${t}`)
  },
  luuOTKB: (data) => api.post('/tkb/o-tkb', data),
  xoaOTKB: (id) => api.delete(`/tkb/o-tkb/${id}`),

  getPhanCongLop: (lopId, namHocId, hocKyId) =>
    api.get(`/tkb/phan-cong-lop/${lopId}?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}`),

  kiemTraXungDot: (namHocId, hocKyId) =>
    api.get(`/tkb/kiem-tra-xung-dot?nam_hoc_id=${namHocId}${hocKyId ? `&hoc_ky_id=${hocKyId}` : ''}`),

  sinhTKBTuDong: (data) => api.post('/tkb/sinh-tu-dong', data),

  getTKBTaiViTri: (namHocId, hocKyId, thu, buoi, tiet) =>
    api.get(`/tkb/tai-vi-tri?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}&thu=${thu}&buoi=${buoi}&tiet=${tiet}`),
  checkMove: (data) => api.post('/tkb/check-move', data),
  confirmMove: (data) => api.post('/tkb/confirm-move', data),
  confirmSwap: (data) => api.post('/tkb/confirm-swap', data),
  resolveConflict: (data) => api.post('/tkb/resolve-conflict', data),

  // exportTKB: keep full response because responseType: 'blob' -> frontend needs response.data (blob)
  exportTKB: (namHocId, hocKyId) => api.get(
    `/tkb/export?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}`,
    { responseType: 'blob' }
  ),
  cascadeConfirm: (body) => api.post('/tkb/cascade-confirm', body),
}