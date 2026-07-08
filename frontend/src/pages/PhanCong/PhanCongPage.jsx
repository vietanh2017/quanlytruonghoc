// frontend/src/pages/PhanCong/PhanCongPage.jsx
import React, { useEffect, useState, useCallback } from 'react'
import {
  Table, Button, Space, Select, message, Popconfirm,
  Typography, Card, Row, Col, Tag, Modal,
  Checkbox, Badge, Upload, Tooltip
} from 'antd'
import {
  PlusOutlined, DeleteOutlined, ReloadOutlined,
  SaveOutlined, ClearOutlined,
  FileExcelOutlined, CheckOutlined, EditOutlined
} from '@ant-design/icons'
import axios from 'axios'
import * as XLSX from 'xlsx'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_URL + '/api/v1/phan-cong' })
const apiPhanMon = axios.create({ baseURL: API_URL + '/api/v1/phan-cong' })
const apiCH = axios.create({ baseURL: API_URL + '/api/v1/cau-hinh' })
const { Title, Text } = Typography

export default function PhanCongPage() {
  // ── Metadata ───────────────────────────────────────────────
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsHocKy, setDsHocKy] = useState([])
  const [dsGiaoVien, setDsGiaoVien] = useState([])
  const [dsMonHoc, setDsMonHoc] = useState([])
  const [dsLopHoc, setDsLopHoc] = useState([])
  const [dsPhanMon, setDsPhanMon] = useState([])

  // ── Sửa phân công (theo dòng GV trong bảng Tổng hợp) ────────
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editGV, setEditGV] = useState(null) // { giao_vien_id, ho_ten }
  const [editNamHoc, setEditNamHoc] = useState(null)
  const [editHocKy, setEditHocKy] = useState(null)
  const [dsHocKyEdit, setDsHocKyEdit] = useState([])
  const [editDsPhanCong, setEditDsPhanCong] = useState([])
  const [editLoading, setEditLoading] = useState(false)
  const [editSelMon, setEditSelMon] = useState(null)
  const [editSelLop, setEditSelLop] = useState(null)
  const [editPendingList, setEditPendingList] = useState([])

  // ── Filter ────────────────────────────────────────────────
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [selHocKy, setSelHocKy] = useState(null)
  const [selGiaoVien, setSelGiaoVien] = useState(null)

  // ── Dữ liệu ───────────────────────────────────────────────
  const [dsPhanCong, setDsPhanCong] = useState([])
  const [tongHop, setTongHop] = useState([])
  const [loading, setLoading] = useState(false)

  // ── Modal ─────────────────────────────────────────────────
  const [modalOpen, setModalOpen] = useState(false)
  const [selMon, setSelMon] = useState(null)
  const [selPhanMon, setSelPhanMon] = useState(null)
  const [selLop, setSelLop] = useState(null)
  const [clearOld, setClearOld] = useState(false)
  const [pendingList, setPendingList] = useState([])

  // ── Import Excel ──────────────────────────────────────────
  const [importModalOpen, setImportModalOpen] = useState(false)
  const [importData, setImportData] = useState([])
  const [importLoading, setImportLoading] = useState(false)

  // ── Xóa hàng loạt ──────────────────────────────────────────
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [selectedGiaoVienIds, setSelectedGiaoVienIds] = useState([])

  // ── Load metadata ──────────────────────────────────────────
  const loadMeta = useCallback(async () => {
    try {
      const [nh, gv, lop] = await Promise.all([
        api.get('/meta/nam-hoc'),
        api.get('/meta/giao-vien'),
        api.get('/meta/lop-hoc'),
      ])
      setDsNamHoc(nh.data || [])
      setDsGiaoVien(gv.data || [])
      setDsLopHoc(lop.data || [])

      const monRes = await apiCH.get('/mon-hoc')
      setDsMonHoc(monRes.data || [])
    } catch (error) {
      console.error('Lỗi load meta:', error)
      message.error('Không thể tải dữ liệu')
    }
  }, [])

  // ── Load tổng hợp ─────────────────────────────────────────
  const loadTongHop = useCallback(async () => {
    try {
      const res = await api.get('/tong-hop')
      setTongHop(res.data || [])
      setSelectedRowKeys([])
      setSelectedGiaoVienIds([])
    } catch (error) {
      console.error('Lỗi load tổng hợp:', error)
      setTongHop([])
    }
  }, [])

  // ── Load phân công theo GV + học kỳ ──────────────────────
  const loadPhanCong = useCallback(async () => {
    if (!selGiaoVien || !selNamHoc || !selHocKy) {
      setDsPhanCong([])
      return
    }

    setLoading(true)
    try {
      const res = await api.get(
        `/giao-vien/${selGiaoVien}?nam_hoc_id=${selNamHoc}&hoc_ky_id=${selHocKy}`
      )
      setDsPhanCong(res.data || [])
    } catch (error) {
      console.error('Lỗi load phân công:', error)
      message.error('Không thể tải phân công')
      setDsPhanCong([])
    } finally {
      setLoading(false)
    }
  }, [selGiaoVien, selNamHoc, selHocKy])

  // ── Load học kỳ theo năm học ─────────────────────────────
  const loadHocKy = useCallback(async (namHocId) => {
    if (!namHocId) {
      setDsHocKy([])
      return
    }
    try {
      const res = await api.get(`/meta/hoc-ky?nam_hoc_id=${namHocId}`)
      setDsHocKy(res.data || [])
    } catch (error) {
      console.error('Lỗi load học kỳ:', error)
      setDsHocKy([])
    }
  }, [])

  // ── Khởi tạo ──────────────────────────────────────────────
  useEffect(() => {
    loadMeta()
    loadTongHop()
  }, [loadMeta, loadTongHop])

  // ── Load lại khi filter thay đổi ──────────────────────────
  useEffect(() => {
    if (selGiaoVien && selNamHoc && selHocKy) {
      loadPhanCong()
    }
  }, [selGiaoVien, selNamHoc, selHocKy, loadPhanCong])

  // ── Xử lý chọn môn ────────────────────────────────────────
  const onSelectMon = useCallback(async (monId) => {
    setSelMon(monId)
    setSelPhanMon(null)
    setDsPhanMon([])

    const mon = dsMonHoc.find(m => m.id === monId)
    if (mon?.co_phan_mon) {
      try {
        const res = await apiCH.get(`/phan-mon/mon-hoc/${monId}`)
        setDsPhanMon(res.data || [])
      } catch (error) {
        console.error('Lỗi load phân môn:', error)
        message.warning('Không tải được danh sách phân môn')
      }
    }
  }, [dsMonHoc])

  // ── Load học kỳ theo năm học (dùng riêng cho modal Sửa) ────
  const loadHocKyEdit = async (namHocId) => {
    if (!namHocId) {
      setDsHocKyEdit([])
      return []
    }
    try {
      const res = await api.get(`/meta/hoc-ky?nam_hoc_id=${namHocId}`)
      const data = res.data || []
      setDsHocKyEdit(data)
      return data
    } catch (error) {
      console.error('Lỗi load học kỳ:', error)
      setDsHocKyEdit([])
      return []
    }
  }

  // ── Load danh sách phân công hiện có của 1 GV (cho modal Sửa) ──
  const loadEditDsPhanCong = async (gvId, namHocId, hocKyId) => {
    if (!gvId || !namHocId || !hocKyId) {
      setEditDsPhanCong([])
      return
    }
    setEditLoading(true)
    try {
      const res = await api.get(`/giao-vien/${gvId}?nam_hoc_id=${namHocId}&hoc_ky_id=${hocKyId}`)
      setEditDsPhanCong(res.data || [])
    } catch (error) {
      console.error('Lỗi load phân công:', error)
      message.error('Không tải được phân công của giáo viên')
      setEditDsPhanCong([])
    } finally {
      setEditLoading(false)
    }
  }

  // ── Mở modal Sửa trực tiếp từ dòng trong bảng Tổng hợp ──────
  const handleOpenEdit = async (r) => {
    const namHocId = selNamHoc || dsNamHoc[0]?.id
    const hocKyId = selHocKy || dsHocKy[0]?.id

    if (!namHocId) {
      message.warning('Chưa có năm học nào trong hệ thống')
      return
    }

    setEditGV(r)
    setEditNamHoc(namHocId)
    setEditPendingList([])
    setEditSelMon(null)
    setEditSelLop(null)

    const hocKyList = await loadHocKyEdit(namHocId)
    const resolvedHocKyId = hocKyId || hocKyList[0]?.id
    setEditHocKy(resolvedHocKyId)

    setEditModalOpen(true)
    await loadEditDsPhanCong(r.giao_vien_id, namHocId, resolvedHocKyId)
  }

  const handleChangeEditNamHoc = async (v) => {
    setEditNamHoc(v)
    setEditHocKy(null)
    setEditDsPhanCong([])
    const hocKyList = await loadHocKyEdit(v)
    const resolvedHocKyId = hocKyList[0]?.id || null
    setEditHocKy(resolvedHocKyId)
    if (editGV && resolvedHocKyId) {
      await loadEditDsPhanCong(editGV.giao_vien_id, v, resolvedHocKyId)
    }
  }

  const handleChangeEditHocKy = async (v) => {
    setEditHocKy(v)
    if (editGV && editNamHoc) {
      await loadEditDsPhanCong(editGV.giao_vien_id, editNamHoc, v)
    }
  }

  // ── Xóa 1 phân công đã có (áp dụng ngay) ───────────────────
  const handleXoaEditItem = async (pc) => {
    try {
      await api.delete(`/${pc.id}`)
      message.success('Đã xóa phân công')
      await Promise.all([
        loadEditDsPhanCong(editGV.giao_vien_id, editNamHoc, editHocKy),
        loadTongHop(),
        loadPhanCong(),
      ])
    } catch (err) {
      console.error('Lỗi xóa:', err)
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ── Thêm môn/lớp mới vào danh sách chờ lưu ─────────────────
  const handleThemEditPending = () => {
    if (!editSelMon) {
      message.warning('Vui lòng chọn môn học')
      return
    }
    if (!editSelLop) {
      message.warning('Vui lòng chọn lớp')
      return
    }

    const daCo = editDsPhanCong.some(
      pc => pc.mon_hoc_id === editSelMon && pc.lop_hoc_id === editSelLop
    )
    const dangCho = editPendingList.some(
      p => p.mon_hoc_id === editSelMon && p.lop_hoc_id === editSelLop
    )
    if (daCo || dangCho) {
      message.warning('Đã có trong danh sách')
      return
    }

    const mon = dsMonHoc.find(m => m.id === editSelMon)
    const lop = dsLopHoc.find(l => l.id === editSelLop)
    setEditPendingList(prev => [...prev, {
      mon_hoc_id: editSelMon,
      lop_hoc_id: editSelLop,
      ten_mon: mon?.ten_mon || '',
      ten_lop: lop?.ten_lop || '',
    }])
    setEditSelMon(null)
    setEditSelLop(null)
  }

  const handleXoaEditPending = (idx) => {
    setEditPendingList(prev => prev.filter((_, i) => i !== idx))
  }

  // ── Lưu các môn/lớp mới thêm ────────────────────────────────
  const handleLuuEdit = async () => {
    if (editPendingList.length === 0) {
      message.warning('Chưa có mục mới nào để lưu')
      return
    }
    try {
      await api.post('/', {
        giao_vien_id: editGV.giao_vien_id,
        nam_hoc_id: editNamHoc,
        hoc_ky_id: editHocKy,
        phan_cong_list: editPendingList.map(p => ({
          mon_hoc_id: p.mon_hoc_id,
          lop_hoc_id: p.lop_hoc_id,
        })),
        clear_old: false,
      })
      message.success('Đã lưu phân công')
      setEditPendingList([])
      await Promise.all([
        loadEditDsPhanCong(editGV.giao_vien_id, editNamHoc, editHocKy),
        loadTongHop(),
        loadPhanCong(),
      ])
    } catch (err) {
      console.error('Lỗi lưu:', err)
      message.error(err.response?.data?.detail || 'Lưu thất bại')
    }
  }

  const handleOpenModal = useCallback(() => {
    setPendingList([])
    setSelMon(null)
    setSelPhanMon(null)
    setSelLop(null)
    setClearOld(false)
    setModalOpen(true)
  }, [])

  const handleThemVaoPending = useCallback(() => {
    if (!selMon) {
      message.warning('Vui lòng chọn môn học')
      return
    }
    if (!selLop) {
      message.warning('Vui lòng chọn lớp')
      return
    }

    const mon = dsMonHoc.find(m => m.id === selMon)
    if (mon?.co_phan_mon && !selPhanMon) {
      message.warning('Môn này có phân môn, vui lòng chọn phân môn')
      return
    }

    const tenMonHienThi = mon?.co_phan_mon
      ? dsPhanMon.find(pm => pm.id === selPhanMon)?.ten_phan_mon || mon.ten_mon
      : mon?.ten_mon

    const dup = pendingList.find(
      p => p.mon_hoc_id === selMon && p.lop_hoc_id === selLop
    )
    if (dup) {
      message.warning('Đã có trong danh sách')
      return
    }

    const lop = dsLopHoc.find(l => l.id === selLop)
    const newItem = {
      mon_hoc_id: selMon,
      lop_hoc_id: selLop,
      ten_mon: tenMonHienThi,
      ten_lop: lop?.ten_lop || '',
      phan_mon_id: selPhanMon,
      co_phan_mon: mon?.co_phan_mon || false,
    }

    setPendingList(prev => [...prev, newItem])
    setSelMon(null)
    setSelPhanMon(null)
    setSelLop(null)
    setDsPhanMon([])

    message.success(`Đã thêm "${tenMonHienThi} - ${lop?.ten_lop}" vào danh sách`)
  }, [selMon, selPhanMon, selLop, dsMonHoc, dsPhanMon, dsLopHoc, pendingList])

  const handleXoaPending = useCallback((idx) => {
    setPendingList(prev => prev.filter((_, i) => i !== idx))
  }, [])

  const handleLuu = useCallback(async () => {
    if (!selGiaoVien) {
      message.warning('Vui lòng chọn giáo viên')
      return
    }
    if (!selNamHoc) {
      message.warning('Vui lòng chọn năm học')
      return
    }
    if (!selHocKy) {
      message.warning('Vui lòng chọn học kỳ')
      return
    }

    if (pendingList.length === 0) {
      message.warning('Chưa có phân công nào để lưu')
      return
    }

    try {
      const data = {
        giao_vien_id: selGiaoVien,
        nam_hoc_id: selNamHoc,
        hoc_ky_id: selHocKy,
        phan_cong_list: pendingList.map(p => ({
          mon_hoc_id: p.mon_hoc_id,
          lop_hoc_id: p.lop_hoc_id,
        })),
        clear_old: clearOld,
      }

      await api.post('/', data)
      message.success('Lưu phân công thành công!')
      setPendingList([])
      setModalOpen(false)

      await Promise.all([
        loadPhanCong(),
        loadTongHop()
      ])
    } catch (err) {
      console.error('Lỗi lưu:', err)
      message.error(err.response?.data?.detail || 'Lỗi khi lưu phân công')
    }
  }, [selGiaoVien, selNamHoc, selHocKy, pendingList, clearOld, loadPhanCong, loadTongHop])

  const handleXoa = useCallback(async (pc) => {
    try {
      await api.delete(`/${pc.id}`)
      message.success('Đã xóa phân công')
      await Promise.all([
        loadPhanCong(),
        loadTongHop()
      ])
    } catch (err) {
      console.error('Lỗi xóa:', err)
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }, [loadPhanCong, loadTongHop])

  const handleXoaTatCa = useCallback(async () => {
    try {
      await api.delete('/tat-ca/xoa', {
        data: {
          giao_vien_id: selGiaoVien,
          nam_hoc_id: selNamHoc,
          hoc_ky_id: selHocKy,
        }
      })
      message.success('Đã xóa tất cả phân công')
      await Promise.all([
        loadPhanCong(),
        loadTongHop()
      ])
    } catch (err) {
      console.error('Lỗi xóa tất cả:', err)
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }, [selGiaoVien, selNamHoc, selHocKy, loadPhanCong, loadTongHop])

  const handleXoaNhieuGiaoVien = useCallback(async () => {
    if (selectedGiaoVienIds.length === 0) {
      message.warning('Vui lòng chọn giáo viên cần xóa')
      return
    }

    const namHocId = selNamHoc || dsNamHoc[0]?.id
    const hocKyId = selHocKy || dsHocKy[0]?.id

    if (!namHocId || !hocKyId) {
      message.warning('Vui lòng chọn năm học và học kỳ')
      return
    }

    try {
      const response = await api.delete('/nhieu-giao-vien', {
        data: {
          giao_vien_ids: selectedGiaoVienIds,
          nam_hoc_id: namHocId,
          hoc_ky_id: hocKyId,
        }
      })

      const deletedCount = response.data?.deleted || 0
      message.success(
        response.data?.message ||
        `Đã xóa ${deletedCount} phân công của ${selectedGiaoVienIds.length} giáo viên`
      )

      setSelectedGiaoVienIds([])
      setSelectedRowKeys([])

      await Promise.all([
        loadTongHop(),
        loadPhanCong()
      ])

    } catch (error) {
      console.error('Lỗi xóa nhiều:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Xóa thất bại'
      message.error(errorMsg)
    }
  }, [selectedGiaoVienIds, selNamHoc, selHocKy, dsNamHoc, dsHocKy, loadTongHop, loadPhanCong])

  const handleImportExcel = useCallback(async (file) => {
    setImportLoading(true)
    try {
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const worksheet = workbook.Sheets[workbook.SheetNames[0]]
          const jsonData = XLSX.utils.sheet_to_json(worksheet)

          const importList = []

          jsonData.forEach((row, rowIndex) => {
            const hoTen = String(row['Họ tên'] || '').trim()
            const phanCongStr = String(row['Phân công chuyên môn'] || '').trim()

            if (!hoTen || !phanCongStr) return

            const giaoVien = dsGiaoVien.find(gv =>
              gv.ho_ten?.toLowerCase() === hoTen.toLowerCase()
            )

            const monParts = phanCongStr.split('+').map(s => s.trim())

            monParts.forEach(part => {
              const match = part.match(/^(.+?)\s*\(([^)]+)\)$/)
              if (!match) return

              const tenMon = match[1].trim()
              const lopStr = match[2].trim()
              const tenLops = lopStr.split(',').map(l => l.trim())

              const monHoc = dsMonHoc.find(m =>
                m.ten_mon?.toLowerCase() === tenMon.toLowerCase()
              )
              tenLops.forEach(tenLop => {
                const lopHoc = dsLopHoc.find(l =>
                  l.ten_lop?.toLowerCase() === tenLop.toLowerCase()
                )

                const errors = [
                  !giaoVien ? `Không tìm thấy GV "${hoTen}"` : null,
                  !monHoc ? `Không tìm thấy môn "${tenMon}"` : null,
                  !lopHoc ? `Không tìm thấy lớp "${tenLop}"` : null,
                ].filter(Boolean).join(', ')

                importList.push({
                  index: importList.length + 1,
                  giao_vien_id: giaoVien?.id || null,
                  giao_vien_ten: hoTen,
                  mon_hoc_id: monHoc?.id || null,
                  mon_hoc_ten: tenMon,
                  lop_hoc_id: lopHoc?.id || null,
                  lop_hoc_ten: tenLop,
                  status: giaoVien && monHoc && lopHoc ? 'valid' : 'invalid',
                  errors,
                })
              })
            })
          })

          setImportData(importList)
          setImportModalOpen(true)

          const validCount = importList.filter(i => i.status === 'valid').length
          message.success(`Đọc file thành công! ${validCount}/${importList.length} dòng hợp lệ`)
        } catch (err) {
          message.error('Lỗi đọc file: ' + err.message)
        } finally {
          setImportLoading(false)
        }
      }
      reader.readAsArrayBuffer(file)
    } catch (err) {
      message.error('Lỗi xử lý file: ' + err.message)
      setImportLoading(false)
    }
    return false
  }, [dsGiaoVien, dsMonHoc, dsLopHoc])

  const handleSaveImport = useCallback(async () => {
    const validData = importData.filter(item => item.status === 'valid')
    if (validData.length === 0) {
      message.warning('Không có dữ liệu hợp lệ để import')
      return
    }

    const groupedByGiaoVien = validData.reduce((acc, item) => {
      const key = item.giao_vien_id
      if (!acc[key]) {
        acc[key] = {
          giao_vien_id: item.giao_vien_id,
          mon_hoc_lop: []
        }
      }
      acc[key].mon_hoc_lop.push({
        mon_hoc_id: item.mon_hoc_id,
        lop_hoc_id: item.lop_hoc_id
      })
      return acc
    }, {})

    try {
      const namHocId = selNamHoc || dsNamHoc[0]?.id
      const hocKyId = selHocKy || dsHocKy[0]?.id

      if (!namHocId || !hocKyId) {
        message.warning('Vui lòng chọn năm học và học kỳ trước khi import')
        return
      }

      const promises = Object.values(groupedByGiaoVien).map(async (gv) => {
        const data = {
          giao_vien_id: gv.giao_vien_id,
          nam_hoc_id: namHocId,
          hoc_ky_id: hocKyId,
          phan_cong_list: gv.mon_hoc_lop,
          clear_old: false
        }
        console.log('Data gửi lên:', JSON.stringify(data, null, 2))
        await api.post('/', data)
      })

      await Promise.all(promises)
      message.success(`Import thành công ${validData.length} phân công`)
      setImportModalOpen(false)
      setImportData([])

      await Promise.all([
        loadTongHop(),
        loadPhanCong()
      ])
    } catch (error) {
      console.error('Lỗi import:', error)
      message.error('Lỗi import: ' + (error.response?.data?.detail || error.message))
    }
  }, [importData, selNamHoc, selHocKy, dsNamHoc, dsHocKy, loadTongHop, loadPhanCong])

  const handleTaiFileMau = useCallback(async () => {
    try {
      const res = await api.get('/tong-hop')
      const data = res.data || []

      const lopRes = await api.get('/meta/lop-hoc')
      const dsLop = lopRes.data || []

      const gvRes = await api.get('/meta/giao-vien')
      const dsGVFull = gvRes.data || []

      const cnMap = {}
      dsLop.forEach(lop => {
        if (lop.giao_vien_cn_id) {
          cnMap[lop.giao_vien_cn_id] = lop.ten_lop
        }
      })

      const kiemNhiemMap = {}
      dsGVFull.forEach(gv => {
        kiemNhiemMap[gv.id] = gv.kiem_nhiem || ''
      })

      const rows = data.map((gv, idx) => {
        const phanCongStr = gv.phan_cong?.map(pc => {
          const lops = pc.lops?.join(',') || ''
          return `${pc.mon_hoc} (${lops})`
        }).join(' + ') || ''

        return {
          'TT': idx + 1,
          'Họ tên': gv.ho_ten || '',
          'Kiêm nhiệm': kiemNhiemMap[gv.giao_vien_id] || '',
          'CN': cnMap[gv.giao_vien_id] || '',
          'Phân công chuyên môn': phanCongStr,
          'Số tiết': gv.tong_tiet || 0,
        }
      })

      for (let i = 0; i < 5; i++) {
        rows.push({
          'TT': data.length + i + 1,
          'Họ tên': '',
          'Kiêm nhiệm': '',
          'CN': '',
          'Phân công chuyên môn': '',
          'Số tiết': 0,
        })
      }

      const ws = XLSX.utils.json_to_sheet(rows)
      ws['!cols'] = [
        { wch: 5 },   // TT
        { wch: 25 },  // Họ tên
        { wch: 20 },  // Kiêm nhiệm
        { wch: 10 },  // CN
        { wch: 60 },  // Phân công
        { wch: 10 },  // Số tiết
      ]

      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Phân công')

      const hdRows = [
        { 'Hướng dẫn': 'FORMAT PHÂN CÔNG GIẢNG DẠY' },
        { 'Hướng dẫn': '─────────────────────────────────────' },
        { 'Hướng dẫn': 'Cột "Phân công chuyên môn" theo format:' },
        { 'Hướng dẫn': 'TenMon1 (LopA,LopB) + TenMon2 (LopC)' },
        { 'Hướng dẫn': '' },
        { 'Hướng dẫn': 'Ví dụ:' },
        { 'Hướng dẫn': 'Tin học (6A,6B,6C) + Công nghệ (7A,7B)' },
        { 'Hướng dẫn': '' },
        { 'Hướng dẫn': 'LƯU Ý:' },
        { 'Hướng dẫn': '- Tên môn phải khớp chính xác với hệ thống' },
        { 'Hướng dẫn': '- Tên lớp phải khớp chính xác với hệ thống' },
        { 'Hướng dẫn': '- Họ tên GV phải khớp với hệ thống' },
        { 'Hướng dẫn': '- Cột Kiêm nhiệm và CN chỉ để tham khảo, không import' },
        { 'Hướng dẫn': '- Cột Số tiết tính tự động khi import' },
      ]
      const wsHD = XLSX.utils.json_to_sheet(hdRows)
      wsHD['!cols'] = [{ wch: 60 }]
      XLSX.utils.book_append_sheet(wb, wsHD, 'Hướng dẫn')

      XLSX.writeFile(wb, 'mau_phan_cong.xlsx')
      message.success('Đã tải file mẫu!')
    } catch (err) {
      message.error('Lỗi tạo file mẫu: ' + err.message)
    }
  }, [])

  // ── Cột bảng ──────────────────────────────────────────────
  const colPhanCong = [
    { title: 'Môn học', render: (_, r) => r.mon_hoc?.ten_mon || '—' },
    { title: 'Lớp', render: (_, r) => r.lop_hoc?.ten_lop || '—' },
    { title: 'Khối', render: (_, r) => r.lop_hoc?.khoi || '—', width: 70 },
    {
      title: '', width: 60,
      render: (_, r) => (
        <Popconfirm
          title="Xóa phân công này?"
          onConfirm={() => handleXoa(r)}
          okText="Xóa"
          cancelText="Hủy"
          okButtonProps={{ danger: true }}
        >
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    }
  ]

  const colTongHop = [
    {
      title: 'Giáo viên',
      dataIndex: 'ho_ten',
      sorter: (a, b) => a.ho_ten?.localeCompare(b.ho_ten) || 0,
    },
    {
      title: 'Phân công',
      render: (_, r) => (
        <Space wrap size={4}>
          {r.phan_cong?.map((pc, i) => (
            <Tag key={i} color="blue">{pc.mon_hoc}: {pc.lops?.join(', ')}</Tag>
          ))}
          {r.lop_chu_nhiem?.length > 0 && (
            <Tag color="gold">
              Chủ nhiệm: {r.lop_chu_nhiem.join(', ')}
            </Tag>
          )}
        </Space>
      )
    },
    {
      title: '',
      width: 80,
      render: (_, r) => (
        <Button
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleOpenEdit(r)}
        >
          Sửa
        </Button>
      )
    },
    {
      title: 'Tổng tiết',
      dataIndex: 'tong_tiet',
      width: 130,
      align: 'center',
      render: (v, r) => (
        <Tooltip
          title={
            r.tiet_cn > 0
              ? `Dạy: ${r.tiet_day} tiết + Chủ nhiệm: ${r.tiet_cn} tiết = ${v} tiết`
              : `Dạy: ${r.tiet_day} tiết`
          }
        >
          <Space direction="vertical" size={0}>
            <Tag color={v > 18 ? 'red' : v > 12 ? 'orange' : 'green'}>
              {v || 0} tiết
            </Tag>
            {r.tiet_cn > 0 && (
              <Text type="secondary" style={{ fontSize: 11 }}>
                (Thực dạy {r.tiet_day} + CN {r.tiet_cn})
              </Text>
            )}
          </Space>
        </Tooltip>
      ),
      sorter: (a, b) => (a.tong_tiet || 0) - (b.tong_tiet || 0),
    },
  ]
  // ── RowSelection cho bảng tổng hợp ──────────────────────────
  const rowSelection = {
    selectedRowKeys: selectedGiaoVienIds,
    onChange: (selectedRowKeys, selectedRows) => {
      setSelectedGiaoVienIds(selectedRowKeys)
      setSelectedRowKeys(selectedRowKeys)
    },
    getCheckboxProps: (record) => ({
      disabled: record.phan_cong?.length === 0,
    }),
  }
  const monDangChon = dsMonHoc.find(m => m.id === selMon)
  const cooPhanMon = !!monDangChon?.co_phan_mon

  const uploadProps = {
    beforeUpload: handleImportExcel,
    showUploadList: false,
    accept: '.xlsx,.xls',
  }

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>📋 Phân Công Giảng Dạy</Title>

      {/* ═══ PHÂN CÔNG THEO GIÁO VIÊN - LÊN TRÊN ═══ */}
      <Card
        title="Phân công theo giáo viên"
        size="small"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Tooltip title="Tải file mẫu Excel">
              <Button
                icon={<FileExcelOutlined />}
                onClick={handleTaiFileMau}
                style={{ color: '#52c41a', borderColor: '#52c41a' }}
              >
                File mẫu
              </Button>
            </Tooltip>
            <Tooltip title="Import từ file Excel">
              <Upload {...uploadProps}>
                <Button
                  icon={<FileExcelOutlined />}
                  disabled={!selNamHoc || !selHocKy}
                >
                  Import Excel
                </Button>
              </Upload>
            </Tooltip>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleOpenModal}
              disabled={!selGiaoVien || !selNamHoc || !selHocKy}
            >
              Thêm phân công
            </Button>
          </Space>
        }
      >
        <Row gutter={16} style={{ marginBottom: 12 }}>
          <Col span={8}>
            <Select
              placeholder="Chọn năm học"
              style={{ width: '100%' }}
              value={selNamHoc}
              onChange={v => {
                setSelNamHoc(v)
                setSelHocKy(null)
                setSelGiaoVien(null)
                loadHocKy(v)
              }}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
              allowClear
            />
          </Col>
          <Col span={8}>
            <Select
              placeholder="Chọn học kỳ"
              style={{ width: '100%' }}
              value={selHocKy}
              onChange={setSelHocKy}
              disabled={!selNamHoc}
              options={dsHocKy.map(h => ({ value: h.id, label: h.ten_hoc_ky }))}
              allowClear
            />
          </Col>
          <Col span={8}>
            <Select
              placeholder="Chọn giáo viên"
              style={{ width: '100%' }}
              showSearch
              optionFilterProp="label"
              value={selGiaoVien}
              onChange={setSelGiaoVien}
              options={dsGiaoVien.map(gv => ({
                value: gv.id,
                label: `${gv.ho_ten} (${gv.ma_giao_vien})`,
              }))}
              allowClear
            />
          </Col>
        </Row>

        {dsPhanCong.length > 0 && (
          <div style={{ marginBottom: 8, textAlign: 'right' }}>
            <Popconfirm
              title="Xóa tất cả phân công của GV này trong học kỳ?"
              onConfirm={handleXoaTatCa}
              okText="Xóa tất cả"
              cancelText="Hủy"
              okButtonProps={{ danger: true }}
            >
              <Button danger icon={<ClearOutlined />} size="small">
                Xóa tất cả
              </Button>
            </Popconfirm>
          </div>
        )}

        <Table
          rowKey="id"
          columns={colPhanCong}
          dataSource={dsPhanCong}
          loading={loading}
          size="small"
          bordered
          pagination={{ pageSize: 8, size: 'small' }}
          locale={{
            emptyText: selGiaoVien ? 'Chưa có phân công' : 'Chọn giáo viên để xem'
          }}
        />
      </Card>

      {/* ═══ TỔNG HỢP PHÂN CÔNG - XUỐNG DƯỚI ═══ */}
      <Card
        title={
          <Space>
            <span>Tổng hợp phân công</span>
            <Badge count={tongHop.length} />
          </Space>
        }
        size="small"
        extra={
          <Space>
            {selectedGiaoVienIds.length > 0 && (
              <Popconfirm
                title={`Xóa phân công của ${selectedGiaoVienIds.length} giáo viên?`}
                onConfirm={handleXoaNhieuGiaoVien}
                okText="Xóa"
                cancelText="Hủy"
                okButtonProps={{ danger: true }}
              >
                <Button danger icon={<DeleteOutlined />} size="small">
                  Xóa đã chọn ({selectedGiaoVienIds.length})
                </Button>
              </Popconfirm>
            )}
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={loadTongHop}
            />
          </Space>
        }
      >
        <Table
          rowKey="giao_vien_id"
          columns={colTongHop}
          dataSource={tongHop}
          rowSelection={rowSelection}
          size="small"
          bordered
          pagination={{ pageSize: 8, size: 'small' }}
          loading={loading}
        />
        {selectedGiaoVienIds.length > 0 && (
          <div style={{ marginTop: 8, color: '#1890ff' }}>
            Đã chọn {selectedGiaoVienIds.length} giáo viên
          </div>
        )}
      </Card>

      {/* ── Modal thêm phân công ── */}
      <Modal
        title="➕ Thêm phân công"
        open={modalOpen}
        centered
        width={580}
        onCancel={() => {
          setModalOpen(false)
          setPendingList([])
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setModalOpen(false)
            setPendingList([])
          }}>Hủy</Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleLuu}
            disabled={pendingList.length === 0}
          >
            Lưu phân công ({pendingList.length})
          </Button>
        ]}
      >
        <Space direction="vertical" style={{ width: '100%', marginTop: 12 }} size={10}>
          <Row gutter={8} align="bottom">
            <Col span={9}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: 12 }}>Môn học</Text>
              </div>
              <Select
                placeholder="Chọn môn"
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="label"
                value={selMon}
                onChange={onSelectMon}
                options={dsMonHoc.map(m => ({
                  value: m.id,
                  label: m.co_phan_mon ? `${m.ten_mon} ★` : m.ten_mon,
                }))}
              />
            </Col>

            {cooPhanMon && (
              <Col span={8}>
                <div style={{ marginBottom: 4 }}>
                  <Text style={{ fontSize: 12, color: '#1677ff' }}>Phân môn</Text>
                </div>
                <Select
                  placeholder="Chọn phân môn"
                  style={{ width: '100%' }}
                  value={selPhanMon}
                  onChange={setSelPhanMon}
                  options={dsPhanMon.map(pm => ({
                    value: pm.id,
                    label: pm.ten_phan_mon,
                  }))}
                />
              </Col>
            )}

            <Col span={cooPhanMon ? 5 : 11}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: 12 }}>Lớp</Text>
              </div>
              <Select
                placeholder="Chọn lớp"
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="label"
                value={selLop}
                onChange={setSelLop}
                options={dsLopHoc.map(l => ({ value: l.id, label: l.ten_lop }))}
              />
            </Col>

            <Col span={2}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleThemVaoPending}
                style={{ width: '100%', marginTop: 22 }}
              />
            </Col>
          </Row>

          {cooPhanMon && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              ★ Môn này có phân môn — vui lòng chọn phân môn cụ thể
            </Text>
          )}

          <div style={{
            background: pendingList.length > 0 ? '#f6ffed' : '#f5f5f5',
            border: `1px solid ${pendingList.length > 0 ? '#b7eb8f' : '#d9d9d9'}`,
            borderRadius: 6,
            padding: 10,
            minHeight: 60
          }}>
            <Text strong style={{ fontSize: 12 }}>
              Danh sách sẽ thêm ({pendingList.length} mục):
            </Text>
            {pendingList.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '10px 0' }}>
                <Text type="secondary">Chưa có mục nào. Hãy chọn môn và lớp để thêm.</Text>
              </div>
            ) : (
              <div style={{ marginTop: 8 }}>
                {pendingList.map((p, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between',
                    alignItems: 'center', padding: '4px 0',
                    borderBottom: i < pendingList.length - 1 ? '1px solid #e8e8e8' : 'none'
                  }}>
                    <Text style={{ fontSize: 13 }}>
                      <Tag color="blue">{p.ten_mon}</Tag> → <Tag>{p.ten_lop}</Tag>
                    </Text>
                    <Button
                      size="small"
                      danger
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={() => handleXoaPending(i)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          <Checkbox checked={clearOld} onChange={e => setClearOld(e.target.checked)}>
            <Text type="warning">Xóa phân công cũ trước khi thêm mới</Text>
          </Checkbox>
        </Space>
      </Modal>

      {/* ── Modal Import Excel ── */}
      <Modal
        title="📥 Import phân công từ Excel"
        open={importModalOpen}
        onCancel={() => {
          setImportModalOpen(false)
          setImportData([])
        }}
        width={900}
        footer={[
          <Button key="cancel" onClick={() => {
            setImportModalOpen(false)
            setImportData([])
          }}>Hủy</Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSaveImport}
            loading={importLoading}
            disabled={importData.filter(item => item.status === 'valid').length === 0}
          >
            Import ({importData.filter(item => item.status === 'valid').length} hợp lệ)
          </Button>
        ]}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            File Excel cần có các cột: <strong>Mã GV</strong>, <strong>Tên GV</strong>, <strong>Môn học</strong>, <strong>Lớp</strong>
          </Text>
        </div>

        <Table
          rowKey="index"
          dataSource={importData}
          pagination={{ pageSize: 10 }}
          size="small"
          bordered
          columns={[
            {
              title: 'STT',
              dataIndex: 'index',
              width: 60,
            },
            {
              title: 'Trạng thái',
              width: 140,
              render: (_, record) => (
                record.status === 'valid'
                  ? <Tag color="green"><CheckOutlined /> Hợp lệ</Tag>
                  : <Tooltip title={record.errors}>
                    <Tag color="red">✖ Không hợp lệ</Tag>
                  </Tooltip>
              )
            },
            { title: 'Mã GV', dataIndex: 'giao_vien_ma', width: 100 },
            { title: 'Tên GV', dataIndex: 'giao_vien_ten', width: 150 },
            { title: 'Môn học', dataIndex: 'mon_hoc_ten', width: 150 },
            { title: 'Lớp', dataIndex: 'lop_hoc_ten', width: 100 },
            {
              title: 'Ghi chú',
              dataIndex: 'errors',
              render: (errors) => errors || '-',
              width: 150,
            },
          ]}
        />
      </Modal>

      {/* ── Modal Sửa phân công (mở trực tiếp từ dòng GV, không cần chọn bộ lọc trước) ── */}
      <Modal
        title={`✏️ Sửa phân công — ${editGV?.ho_ten || ''}`}
        open={editModalOpen}
        onCancel={() => {
          setEditModalOpen(false)
          setEditPendingList([])
        }}
        width={640}
        footer={[
          <Button key="close" onClick={() => {
            setEditModalOpen(false)
            setEditPendingList([])
          }}>Đóng</Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleLuuEdit}
            disabled={editPendingList.length === 0}
          >
            Lưu mục mới ({editPendingList.length})
          </Button>
        ]}
      >
        <Row gutter={8} style={{ marginBottom: 12 }}>
          <Col span={12}>
            <div style={{ marginBottom: 4 }}><Text style={{ fontSize: 12 }}>Năm học</Text></div>
            <Select
              style={{ width: '100%' }}
              value={editNamHoc}
              onChange={handleChangeEditNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={12}>
            <div style={{ marginBottom: 4 }}><Text style={{ fontSize: 12 }}>Học kỳ</Text></div>
            <Select
              style={{ width: '100%' }}
              value={editHocKy}
              onChange={handleChangeEditHocKy}
              options={dsHocKyEdit.map(h => ({ value: h.id, label: h.ten_hoc_ky }))}
            />
          </Col>
        </Row>

        <Text strong style={{ fontSize: 12 }}>Phân công hiện tại:</Text>
        <Table
          rowKey="id"
          size="small"
          bordered
          style={{ marginTop: 6, marginBottom: 14 }}
          loading={editLoading}
          pagination={false}
          dataSource={editDsPhanCong}
          locale={{ emptyText: 'Chưa có phân công nào' }}
          columns={[
            { title: 'Môn học', render: (_, pc) => pc.mon_hoc?.ten_mon || '—' },
            { title: 'Lớp', render: (_, pc) => pc.lop_hoc?.ten_lop || '—' },
            {
              title: '', width: 50,
              render: (_, pc) => (
                <Popconfirm
                  title="Xóa phân công này?"
                  onConfirm={() => handleXoaEditItem(pc)}
                  okText="Xóa"
                  cancelText="Hủy"
                  okButtonProps={{ danger: true }}
                >
                  <Button size="small" danger icon={<DeleteOutlined />} />
                </Popconfirm>
              )
            },
          ]}
        />

        <Text strong style={{ fontSize: 12 }}>Thêm môn/lớp mới:</Text>
        <Row gutter={8} align="bottom" style={{ marginTop: 6 }}>
          <Col span={11}>
            <Select
              placeholder="Chọn môn"
              style={{ width: '100%' }}
              showSearch
              optionFilterProp="label"
              value={editSelMon}
              onChange={setEditSelMon}
              options={dsMonHoc.map(m => ({ value: m.id, label: m.ten_mon }))}
            />
          </Col>
          <Col span={11}>
            <Select
              placeholder="Chọn lớp"
              style={{ width: '100%' }}
              showSearch
              optionFilterProp="label"
              value={editSelLop}
              onChange={setEditSelLop}
              options={dsLopHoc.map(l => ({ value: l.id, label: l.ten_lop }))}
            />
          </Col>
          <Col span={2}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleThemEditPending}
              style={{ width: '100%' }}
            />
          </Col>
        </Row>

        {editPendingList.length > 0 && (
          <div style={{
            background: '#f6ffed',
            border: '1px solid #b7eb8f',
            borderRadius: 6,
            padding: 10,
            marginTop: 10,
          }}>
            <Text strong style={{ fontSize: 12 }}>
              Mục mới sẽ thêm ({editPendingList.length}):
            </Text>
            <div style={{ marginTop: 6 }}>
              {editPendingList.map((p, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'center', padding: '4px 0',
                  borderBottom: i < editPendingList.length - 1 ? '1px solid #e8e8e8' : 'none'
                }}>
                  <Text style={{ fontSize: 13 }}>
                    <Tag color="blue">{p.ten_mon}</Tag> → <Tag>{p.ten_lop}</Tag>
                  </Text>
                  <Button
                    size="small"
                    danger
                    type="text"
                    icon={<DeleteOutlined />}
                    onClick={() => handleXoaEditPending(i)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
