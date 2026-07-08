// frontend/src/pages/Reports/services/api.js
import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = API_URL + '/api/v1/reports'
const api = axios.create({ baseURL: API_BASE })

// ════════════════════════════════════════════════════════════
// ══ REPORTS API ════════════════════════════════════════════
// ════════════════════════════════════════════════════════════

export const reportsAPI = {
  /**
   * Lấy báo cáo theo loại và bộ lọc
   * @param {Object} params - Tham số lọc
   * @param {string} params.loai - tuan, thang, hoc_ky, nam_hoc, ca_nhan, giao_vien
   * @param {number} params.nam_hoc_id - ID năm học
   * @param {number} params.hoc_ky_id - ID học kỳ
   * @param {number} params.thang_id - ID tháng
   * @param {number} params.tuan - Số tuần
   * @param {number} params.lop_hoc_id - ID lớp học
   * @param {number} params.khoi - Khối lớp
   */
  getReport: (params) => api.get('/report', { params }),

  exportExcel: (data) => api.post('/export-excel', data),
}