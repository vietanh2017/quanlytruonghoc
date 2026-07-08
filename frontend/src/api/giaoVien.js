// frontend/src/api/giaoVien.js
import axios from 'axios'

const BASE = 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: BASE })

export const giaoVienApi = {
  // Lấy danh sách
  getAll: (includeInactive = true) =>
    api.get(`/giao-vien/?include_inactive=${includeInactive}`),
  // ⭐ THÊM API TÍNH TỔNG TIẾT
  getTongTiet: (id) => api.get(`/giao-vien/${id}/tong-tiet`),
  // Chi tiết
  getById: (id) => api.get(`/giao-vien/${id}`),

  // Thêm mới
  create: (data) => api.post('/giao-vien/', data),

  // Cập nhật
  update: (id, data) => api.put(`/giao-vien/${id}`, data),

  // Xóa
  delete: (id) => api.delete(`/giao-vien/${id}`),

  // Bật/tắt trạng thái
  toggleActive: (id) => api.patch(`/giao-vien/${id}/trang-thai`),

  // Đặt lại mật khẩu
  resetPassword: (id, matKhauMoi = 'eduschool@123') =>
    api.patch(`/giao-vien/${id}/mat-khau`, { mat_khau_moi: matKhauMoi }),

  importExcel: async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      '/giao-vien/import-excel',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      }
    )
    return response.data
  }
}