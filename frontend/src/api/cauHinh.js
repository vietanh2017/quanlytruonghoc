// frontend/src/api/cauHinh.js
import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

// ============ THÔNG TIN TRƯỜNG ============
export const thongTinTruongAPI = {
  get: () => axios.get(`${API_URL}/cau-hinh/thong-tin-truong`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/thong-tin-truong`, data),
  update: (data) => axios.put(`${API_URL}/cau-hinh/thong-tin-truong`, data),
};

// ============ CẤU HÌNH CHUNG (KEY-VALUE) ============
export const cauHinhChungAPI = {
  get: (key) => axios.get(`${API_URL}/cau-hinh/cau-hinh?key=${key}`),
  getAll: () => axios.get(`${API_URL}/cau-hinh/cau-hinh/tat-ca`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/cau-hinh`, data),
  update: (key, data) => axios.put(`${API_URL}/cau-hinh/cau-hinh/${key}`, data),
  delete: (key) => axios.delete(`${API_URL}/cau-hinh/cau-hinh/${key}`),
};

// ============ NĂM HỌC ============
export const namHocAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/nam-hoc`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/nam-hoc/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/nam-hoc`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/nam-hoc/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/nam-hoc/${id}`),
};

// ============ HỌC KỲ ============
export const hocKyAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/hoc-ky`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/hoc-ky/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/hoc-ky`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/hoc-ky/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/hoc-ky/${id}`),
};

// ============ MÔN HỌC ============
export const monHocAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/mon-hoc`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/mon-hoc/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/mon-hoc`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/mon-hoc/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/mon-hoc/${id}`),
};

// ============ PHÂN MÔN ============
export const phanMonAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/phan-mon`),
  getByMonHoc: (monHocId) => axios.get(`${API_URL}/cau-hinh/phan-mon/mon-hoc/${monHocId}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/phan-mon`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/phan-mon/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/phan-mon/${id}`),
  deleteByMonHoc: (monHocId) => axios.delete(`${API_URL}/cau-hinh/phan-mon/mon-hoc/${monHocId}`),
};

// ============ SỐ TIẾT THEO KHỐI ============
export const soTietAPI = {
  getByMonHoc: (monHocId) => axios.get(`${API_URL}/cau-hinh/mon-hoc/${monHocId}/so-tiet`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/mon-hoc/so-tiet`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/mon-hoc/so-tiet/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/mon-hoc/so-tiet/${id}`),
  deleteByMonHoc: (monHocId) => axios.delete(`${API_URL}/cau-hinh/mon-hoc/${monHocId}/so-tiet`),
};

// ============ TIẾT HỌC ============
export const tietHocAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/tiet-hoc`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/tiet-hoc/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/tiet-hoc`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/tiet-hoc/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/tiet-hoc/${id}`),
};

// ============ TỔ CHUYÊN MÔN ============
export const toChuyenMonAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/to-chuyen-mon`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/to-chuyen-mon/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/to-chuyen-mon`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/to-chuyen-mon/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/to-chuyen-mon/${id}`),
};

// ============ NGƯỜI DÙNG ============
export const nguoiDungAPI = {
  getAll: () => axios.get(`${API_URL}/cau-hinh/tai-khoan`),
  getById: (id) => axios.get(`${API_URL}/cau-hinh/tai-khoan/${id}`),
  create: (data) => axios.post(`${API_URL}/cau-hinh/tai-khoan`, data),
  update: (id, data) => axios.put(`${API_URL}/cau-hinh/tai-khoan/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/cau-hinh/tai-khoan/${id}`),
  resetPassword: (id, mat_khau_moi) =>
    axios.patch(`${API_URL}/cau-hinh/tai-khoan/${id}/mat-khau`, { mat_khau_moi }),
};

// ============ PHÂN QUYỀN ============
export const phanQuyenAPI = {
  getAllQuyen: () => axios.get(`${API_URL}/cau-hinh/phan-quyen/tat-ca-quyen`),
  getQuyenByVaiTro: (vaiTro) => axios.get(`${API_URL}/cau-hinh/phan-quyen/${vaiTro}`),
  save: (vaiTro, data) => axios.post(`${API_URL}/cau-hinh/phan-quyen/${vaiTro}`, data),
};