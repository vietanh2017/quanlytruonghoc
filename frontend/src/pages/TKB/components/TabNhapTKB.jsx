// frontend/src/pages/TKB/components/TabNhapTKB.jsx
import React, { useState, useEffect, useRef } from 'react'
import {
  Card, Row, Col, Select, Table, Modal, Button, Tag,
  Typography, Tooltip, Popconfirm, message, Spin, Radio,
  Checkbox, Space
} from 'antd'
import { DeleteOutlined, PlusOutlined, ThunderboltOutlined, SwapOutlined } from '@ant-design/icons'
import { tkbAPI } from '../services/api'
import { DownloadOutlined } from '@ant-design/icons'
const { Text } = Typography

const THU_LIST = [2, 3, 4, 5, 6, 7]
const THU_LABEL = { 2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5', 6: 'Thứ 6', 7: 'Thứ 7' }

export default function TabNhapTKB({ meta }) {
  const { dsNamHoc, selNamHoc, setSelNamHoc } = meta

  const [dsHocKy, setDsHocKy] = useState([])
  const [selHocKy, setSelHocKy] = useState(null)
  const [dsLop, setDsLop] = useState([])
  const [dsGV, setDsGV] = useState([])
  const [selLop, setSelLop] = useState(null)
  const [selGV, setSelGV] = useState(null)
  const [xemTheo, setXemTheo] = useState('lop')
  const [tkbData, setTkbData] = useState([])
  const [cauHinhNgay, setCauHinhNgay] = useState([])
  const [loading, setLoading] = useState(false)
  const [rangBuocGV, setRangBuocGV] = useState({})

  const [popupOpen, setPopupOpen] = useState(false)
  const [selectedCell, setSelectedCell] = useState(null)
  const [dsPhanCong, setDsPhanCong] = useState([])
  const [selPhanCong, setSelPhanCong] = useState(null)

  const [sinhModalOpen, setSinhModalOpen] = useState(false)
  const [clearOld, setClearOld] = useState(true)
  const [sinhing, setSinhing] = useState(false)
  const [sinhResult, setSinhResult] = useState(null)

  const [dragSource, setDragSource] = useState(null)
  const [dragOver, setDragOver] = useState(null)
  const [swapModal, setSwapModal] = useState(null)

  const [tableKey, setTableKey] = useState(0)
  const [refreshKey, setRefreshKey] = useState(0)
  const tkbDataRef = useRef([])

  // ⭐ Context Menu và các state liên quan
  const [contextMenu, setContextMenu] = useState({
    visible: false,
    x: 0,
    y: 0,
    thu: null,
    buoi: null,
    tiet: null,
    lop_id: null,
    oTKB: null
  })
  const [fixedSlots, setFixedSlots] = useState({})
  const [offSlots, setOffSlots] = useState({})

  useEffect(() => {
    if (!selNamHoc) return
    tkbAPI.getHocKy(selNamHoc)
      .then(r => {
        const data = r.data || []
        setDsHocKy(data)
        if (data.length > 0) setSelHocKy(data[0].id)
      }).catch(console.error)

    tkbAPI.getDsLop(selNamHoc)
      .then(r => {
        const data = r.data || []
        setDsLop(data)
        if (data.length > 0) setSelLop(data[0].id)
      }).catch(console.error)

    tkbAPI.getDsGV()
      .then(r => {
        const data = r.data || []
        setDsGV(data)
        if (data.length > 0) setSelGV(data[0].id)
      }).catch(console.error)

    tkbAPI.getCauHinhNgay(selNamHoc)
      .then(r => setCauHinhNgay(r.data || []))
      .catch(console.error)

    tkbAPI.getRangBuocGV(selNamHoc)
      .then(r => {
        const data = r.data || []
        const map = {}
        data.forEach(item => {
          map[item.giao_vien_id] = {
            ngay_nghi_list: item.ngay_nghi_list || []
          }
        })
        setRangBuocGV(map)
      })
      .catch(console.error)
  }, [selNamHoc])

  useEffect(() => {
    if (!selNamHoc || !selHocKy) return
    if (xemTheo === 'lop' && !selLop) return
    if (xemTheo === 'gv' && !selGV) return
    loadTKB()
  }, [selNamHoc, selHocKy, selLop, selGV, xemTheo])

  // ⭐ Đóng context menu khi click ra ngoài

  useEffect(() => {
    const handleClickOutside = () => {
      if (contextMenu.visible) {
        setContextMenu({ visible: false, x: 0, y: 0, thu: null, buoi: null, tiet: null, lop_id: null, oTKB: null })
      }
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [contextMenu.visible])

  useEffect(() => {
    console.log('🔄 tkbData CHANGED:', tkbData.map(t => ({
      id: t.id,
      lop: t.ten_lop,
      thu: t.thu,
      tiet: t.tiet
    })))
  }, [tkbData])

  // ═══ LOCAL STORAGE CHO OFF SLOTS ═══
  const saveOffSlotsToStorage = (slots) => {
    try {
      const key = `offSlots_${selNamHoc}_${selHocKy}`
      localStorage.setItem(key, JSON.stringify(slots))
    } catch (e) {
      console.error('Lưu offSlots thất bại:', e)
    }
  }

  const loadOffSlotsFromStorage = () => {
    try {
      const key = `offSlots_${selNamHoc}_${selHocKy}`
      const data = localStorage.getItem(key)
      if (data) {
        return JSON.parse(data)
      }
    } catch (e) {
      console.error('Load offSlots thất bại:', e)
    }
    return {}
  }

  // ⭐ Load offSlots từ localStorage khi chọn năm học/học kỳ
  useEffect(() => {
    if (selNamHoc && selHocKy) {
      const saved = loadOffSlotsFromStorage()
      if (Object.keys(saved).length > 0) {
        setOffSlots(saved)
        console.log('📋 Đã load offSlots từ localStorage:', Object.keys(saved).length, 'ô')
      }
    }
  }, [selNamHoc, selHocKy])

  // ⭐ Lưu offSlots vào localStorage mỗi khi thay đổi
  useEffect(() => {
    if (selNamHoc && selHocKy && Object.keys(offSlots).length > 0) {
      saveOffSlotsToStorage(offSlots)
    }
  }, [offSlots, selNamHoc, selHocKy])

  // ═══ LOCAL STORAGE CHO FIXED SLOTS ═══
  const saveFixedSlotsToStorage = (slots) => {
    try {
      const key = `fixedSlots_${selNamHoc}_${selHocKy}`
      localStorage.setItem(key, JSON.stringify(slots))
    } catch (e) {
      console.error('Lưu fixedSlots thất bại:', e)
    }
  }

  const loadFixedSlotsFromStorage = () => {
    try {
      const key = `fixedSlots_${selNamHoc}_${selHocKy}`
      const data = localStorage.getItem(key)
      if (data) {
        return JSON.parse(data)
      }
    } catch (e) {
      console.error('Load fixedSlots thất bại:', e)
    }
    return {}
  }

  // ⭐ Load fixedSlots từ localStorage
  useEffect(() => {
    if (selNamHoc && selHocKy) {
      const saved = loadFixedSlotsFromStorage()
      if (Object.keys(saved).length > 0) {
        setFixedSlots(saved)
        console.log('📋 Đã load fixedSlots từ localStorage:', Object.keys(saved).length, 'ô')
      }
    }
  }, [selNamHoc, selHocKy])

  // ⭐ Lưu fixedSlots vào localStorage
  useEffect(() => {
    if (selNamHoc && selHocKy && Object.keys(fixedSlots).length > 0) {
      saveFixedSlotsToStorage(fixedSlots)
    }
  }, [fixedSlots, selNamHoc, selHocKy])

  const loadTKB = async () => {
    setLoading(true)
    try {
      const timestamp = new Date().getTime()

      const r = xemTheo === 'lop'
        ? await tkbAPI.getTKBLop(selLop, selNamHoc, selHocKy)
        : await tkbAPI.getTKBGV(selGV, selNamHoc, selHocKy)

      const data = r.data || []
      console.log('📥 loadTKB received:', data.map(t => ({
        id: t.id,
        lop: t.ten_lop,
        thu: t.thu,
        tiet: t.tiet
      })))
      // ⭐ LOG CHI TIẾT
      console.log('📥 loadTKB data:', data)
      console.log('📥 ID 49:', data.find(t => t.id === 49))
      console.log('📥 ID 44:', data.find(t => t.id === 44))
      setTkbData(data)
      setTableKey(prev => prev + 1)
      // ⭐ LOG SAU KHI SET STATE (dùng setTimeout để đảm bảo state đã update)
      setTimeout(() => {
        console.log('📥 tkbData state sau khi set:', tkbData)
      }, 100)
    } catch (error) {
      console.error('❌ loadTKB error:', error)
      message.error('Không tải được TKB')
    } finally {
      setLoading(false)
    }
  }

  // ══ CONTEXT MENU HANDLERS ════════════════════════════════

  const handleContextMenu = (e, thu, buoi, tiet, oTKB, forcedLopId = null) => {
    e.preventDefault()
    e.stopPropagation()

    // Xác định lop_id
    let lop_id = forcedLopId

    if (!lop_id) {
      if (xemTheo === 'lop') {
        lop_id = selLop
      } else if (oTKB) {
        lop_id = oTKB.lop_hoc_id
      } else if (xemTheo === 'gv' && selGV) {
        // Ở chế độ GV, ô trống dùng gv_id làm key
        lop_id = `gv_${selGV}`
      }
    }

    if (!lop_id) return

    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      thu,
      buoi,
      tiet,
      lop_id,
      oTKB
    })
  }

  const handleCloseContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, thu: null, buoi: null, tiet: null, lop_id: null, oTKB: null })
  }
  const getSlotKey = (thu, buoi, tiet, lop_id) => {
    if (!lop_id) return null
    return `${thu}-${buoi}-${tiet}-${lop_id}`
  }

  const isSlotOff = (thu, buoi, tiet, lop_id) => {
    if (!lop_id) return false
    const key = getSlotKey(thu, buoi, tiet, lop_id)
    return !!offSlots[key]
  }

  const isSlotFixed = (thu, buoi, tiet, lop_id) => {
    if (!lop_id) return false
    const key = getSlotKey(thu, buoi, tiet, lop_id)
    return !!fixedSlots[key]
  }

  const toggleOffSlot = () => {
    const { thu, buoi, tiet, lop_id } = contextMenu
    if (!lop_id) return
    const key = getSlotKey(thu, buoi, tiet, lop_id)

    setOffSlots(prev => {
      const newOff = { ...prev }
      if (newOff[key]) {
        delete newOff[key]
      } else {
        newOff[key] = true
        // Nếu đánh dấu nghỉ thì bỏ cố định
        const fixedKey = getSlotKey(thu, buoi, tiet, lop_id)
        setFixedSlots(prevFixed => {
          const newFixed = { ...prevFixed }
          if (newFixed[fixedKey]) {
            delete newFixed[fixedKey]
          }
          return newFixed
        })
      }
      return newOff
    })
    handleCloseContextMenu()
  }

  const toggleFixedSlot = () => {
    const { thu, buoi, tiet, lop_id } = contextMenu
    if (!lop_id) return
    const key = getSlotKey(thu, buoi, tiet, lop_id)

    // Nếu ô đang nghỉ thì không cho cố định
    if (offSlots[key]) {
      message.warning('Ô này đang nghỉ, không thể cố định')
      handleCloseContextMenu()
      return
    }

    setFixedSlots(prev => {
      const newFixed = { ...prev }
      if (newFixed[key]) {
        delete newFixed[key]
      } else {
        newFixed[key] = true
      }
      return newFixed
    })
    handleCloseContextMenu()
  }

  // Helper: chuyển map offSlots/fixedSlots -> array payload
  const mapToSlotList = (slotsMap) => {
    return Object.keys(slotsMap || {}).map(key => {
      const parts = key.split('-')
      return {
        thu: parseInt(parts[0]),
        buoi: parts[1],
        tiet: parseInt(parts[2]),
        lop_id: parts[3]?.startsWith('gv_') ? null : (parts[3] ? parseInt(parts[3]) : null),
        gv_id: parts[3]?.startsWith('gv_') ? parseInt(parts[3].replace('gv_', '')) : null
      }
    })
  }

  // ══ CÁC HÀM XỬ LÝ KHÁC ══════════════════════════════════

  const openPopup = async (thu, buoi, tiet) => {
    if (!selLop || !selHocKy) return message.warning('Vui lòng chọn lớp và học kỳ!')
    setSelectedCell({ thu, buoi, tiet })
    setSelPhanCong(null)
    try {
      const r = await tkbAPI.getPhanCongLop(selLop, selNamHoc, selHocKy)
      setDsPhanCong(r.data || [])
      setPopupOpen(true)
    } catch {
      message.error('Không tải được danh sách phân công')
    }
  }

  const handleLuuOTKB = async () => {
    if (!selPhanCong) return message.warning('Chọn môn học trước!')
    try {
      await tkbAPI.luuOTKB({
        nam_hoc_id: selNamHoc,
        hoc_ky_id: selHocKy,
        lop_hoc_id: selLop,
        giao_vien_id: selPhanCong.giao_vien_id,
        mon_hoc_id: selPhanCong.mon_hoc_id,
        phan_mon_id: selPhanCong.phan_mon_id,
        thu: selectedCell.thu,
        buoi: selectedCell.buoi,
        tiet: selectedCell.tiet,
      })
      message.success('Đã lưu!')
      setPopupOpen(false)
      loadTKB()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lưu thất bại')
    }
  }

  const handleXoaOTKB = async (id) => {
    try {
      await tkbAPI.xoaOTKB(id)
      message.success('Đã xóa!')
      loadTKB()
    } catch {
      message.error('Xóa thất bại')
    }
  }

  // TabNhapTKB.jsx - hàm handleSinhTKB
  const handleSinhTKB = async () => {
    if (!selNamHoc || !selHocKy) return message.warning('Vui lòng chọn năm học và học kỳ!')
    setSinhing(true)
    setSinhResult(null)
    try {
      // ⭐ Chuyển đổi offSlots và fixedSlots thành mảng gửi lên server
      const offSlotList = mapToSlotList(offSlots)
      const fixedSlotList = mapToSlotList(fixedSlots)

      const r = await tkbAPI.sinhTKBTuDong({
        nam_hoc_id: selNamHoc,
        hoc_ky_id: selHocKy,
        clear_old: clearOld,
        off_slots: offSlotList,      // ⭐ Gửi danh sách ô nghỉ
        fixed_slots: fixedSlotList,  // ⭐ Gửi danh sách ô cố định
      })
      setSinhResult(r.data)
      message.success(`Sinh TKB xong! ${r.data.success}/${r.data.total_jobs} tiết`)
      loadTKB()
    } catch (err) {
      message.error('Lỗi: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSinhing(false)
    }
  }

  const handleCloseSinhModal = () => {
    setSinhModalOpen(false)
    setSinhResult(null)
    setSinhing(false)
  }
  // TabNhapTKB.jsx - handleExportExcel
  const handleExportExcel = async () => {
    if (!selNamHoc || !selHocKy) {
      message.warning('Vui lòng chọn năm học và học kỳ!')
      return
    }

    try {
      setLoading(true)
      const response = await tkbAPI.exportTKB(selNamHoc, selHocKy)

      // ⭐ LOG để kiểm tra
      console.log('📥 Response status:', response.status)
      console.log('📥 Response headers:', response.headers)
      console.log('📥 Response data type:', typeof response.data)
      console.log('📥 Response data size:', response.data?.size || response.data?.length)

      // Kiểm tra nếu response.data là string (lỗi)
      if (typeof response.data === 'string') {
        console.error('❌ Response là string, có thể bị lỗi:', response.data.substring(0, 200))
        message.error('File bị lỗi, vui lòng thử lại')
        return
      }

      const url = window.URL.createObjectURL(new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `TKB_${selNamHoc}_${selHocKy}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      message.success('Xuất Excel thành công!')
    } catch (error) {
      console.error('❌ Export error:', error)
      message.error('Xuất Excel thất bại: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }


  // ══ DRAG & DROP ═══════════════════════════════════════════

  const handleDragStart = (e, oTKB) => {
    // Kiểm tra ô nguồn có bị cố định không
    const sourceKey = getSlotKey(oTKB.thu, oTKB.buoi, oTKB.tiet, oTKB.lop_hoc_id)
    if (fixedSlots[sourceKey]) {
      message.warning('Tiết này đã bị cố định, không thể di chuyển!')
      e.preventDefault()
      return
    }
    setDragSource(oTKB)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(oTKB.id))
  }

  const handleDragOver = (e, thu, buoi, tiet) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOver({ thu, buoi, tiet })
  }

  const handleDragLeave = () => setDragOver(null)

  const handleDragEnd = () => {
    setDragOver(null)
  }

  const handleDrop = async (e, thu, buoi, tiet) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(null)

    if (!dragSource) {
      console.warn('⚠️ Không có dragSource')
      return
    }

    if (dragSource.thu === thu && dragSource.buoi === buoi && dragSource.tiet === tiet) {
      setDragSource(null)
      return
    }

    const source = { ...dragSource }

    // --- NEW: determine targetLopId from occupant if exists ---
    const targetOccupant = getOTKB(thu, buoi, tiet) // gets occupant or undefined
    const targetLopId = targetOccupant
      ? targetOccupant.lop_hoc_id
      : (xemTheo === 'lop' ? selLop : source.lop_hoc_id)
    // --------------------------------------------------------

    // ⭐ KIỂM TRA Ô ĐÍCH CÓ BỊ NGHỈ KHÔNG
    const offKey = getSlotKey(thu, buoi, tiet, targetLopId)
    if (offSlots[offKey]) {
      message.warning('Ô này đang nghỉ, không thể xếp tiết!')
      setDragSource(null)
      return
    }

    // ⭐ KIỂM TRA Ô ĐÍCH CÓ BỊ CỐ ĐỊNH KHÔNG
    const fixedKey = getSlotKey(thu, buoi, tiet, targetLopId)
    if (fixedSlots[fixedKey]) {
      message.warning('Ô này đã bị cố định, không thể kéo thả vào!')
      setDragSource(null)
      return
    }

    console.log('📤 Drop:', { source, thu, buoi, tiet, targetLopId })

    try {
      // Gửi cả off_slots và fixed_slots để backend có thể dùng (nếu backend hỗ trợ)
      const offSlotList = mapToSlotList(offSlots)
      const fixedSlotList = mapToSlotList(fixedSlots)

      const r = await tkbAPI.checkMove({
        source_id: source.id,
        target_thu: thu,
        target_buoi: buoi,
        target_tiet: tiet,
        target_lop_hoc_id: targetLopId,
        off_slots: offSlotList,
        fixed_slots: fixedSlotList,
      })

      console.log('📥 Response:', r)

      if (!r || !r.data) {
        message.error('Không nhận được phản hồi từ server')
        setDragSource(null)
        return
      }

      if (r.data.ok === false) {
        message.error(r.data.error || 'Lỗi không xác định')
        setDragSource(null)
        return
      }

      const data = r.data

      if (data.status === 'empty') {
        await tkbAPI.confirmMove({
          source_id: data.source_id,
          target_thu: data.target_thu,
          target_buoi: data.target_buoi,
          target_tiet: data.target_tiet,
          target_lop_hoc_id: data.target_lop_hoc_id,
        })
        message.success('Đã di chuyển tiết học!')
        await loadTKB()
        setDragSource(null)

      } else if (data.status === 'can_swap') {
        setSwapModal({ type: 'swap', data })

      } else if (data.status === 'cascade') {
        setSwapModal({ type: 'cascade', data })

      } else if (data.status === 'conflict') {
        setSwapModal({ type: 'conflict', data })

      } else {
        message.error(`Trạng thái không xác định: ${data.status}`)
        setDragSource(null)
      }
    } catch (err) {
      console.error('❌ Drop error:', err)
      console.error('Response:', err.response)
      const detail = err.response?.data?.detail || err.message || 'Di chuyển thất bại'
      message.error(detail)
      setDragSource(null)
    }
  }
  // ══ XÁC NHẬN CASCADE (đổi chỗ dây chuyền) ════════════════

  const handleConfirmCascade = async () => {
    if (!swapModal?.data?.moves) return
    try {
      const r = await tkbAPI.cascadeConfirm({ moves: swapModal.data.moves })
      message.success(`Đã đổi chỗ dây chuyền: ${r.data.so_tiet_da_doi} tiết`)
      await loadTKB()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Đổi chỗ thất bại')
    } finally {
      setSwapModal(null)
      setDragSource(null)
    }
  }

  // ══ CONFIRM SWAP + REFRESH UI (NEW) ═══════════════════════════════
  const confirmSwapAndRefresh = async (itemAId, itemBId) => {
    try {
      console.log('📤 /confirm-swap body:', { item_a_id: itemAId, item_b_id: itemBId })
      const res = await tkbAPI.confirmSwap({
        item_a_id: itemAId,
        item_b_id: itemBId,
      })
      console.log('📥 /confirm-swap result:', res)

      if (res && res.ok) {
        message.success('Đã đổi chỗ thành công')

        // Reload main TKB view (this respects xemTheo)
        try {
          await loadTKB()
        } catch (err) {
          console.warn('loadTKB failed after swap', err)
        }

        // As a fallback, force a small re-render by bumping tableKey if needed
        setTableKey(prev => prev + 1)
      } else {
        message.error(res?.error || 'Đổi chỗ thất bại')
      }
    } catch (err) {
      console.error('confirmSwap error', err)
      message.error(err?.response?.data?.detail || err?.message || 'Lỗi khi gọi confirm-swap')
    } finally {
      setSwapModal(null)
      setDragSource(null)
    }
  }

  // ══ XÁC NHẬN SWAP (kết nối với hàm refresh) ═══════════════════════════════
  const handleConfirmSwap = async () => {
    if (!swapModal?.data) return
    const d = swapModal.data

    try {
      const r = await tkbAPI.confirmSwap({
        item_a_id: d.item_a_id,
        item_b_id: d.item_b_id,
      })
      console.log('📥 confirmSwap response:', r)
      message.success('Đã đổi chỗ 2 tiết!')

      setSwapModal(null)
      setDragSource(null)

      // ⭐ Load lại dữ liệu
      await loadTKB()

      // ⭐ Force re-render Table
      setRefreshKey(prev => prev + 1)

      console.log('✅ Reload TKB thành công!')

    } catch (err) {
      console.error('❌ Lỗi swap:', err)
      message.error(err.response?.data?.detail || 'Đổi chỗ thất bại')
      setSwapModal(null)
      setDragSource(null)
    }
  }

  // ══ XỬ LÝ CONFLICT ═══════════════════════════════════════

  const handleResolveConflict = async () => {
    const d = swapModal?.data
    if (!d) return
    try {
      // Gọi API resolve conflict: dùng source_id (item A) và conflict_item.id (item B đang chiếm)
      const payload = {
        item_a_id: d.source_id,                     // chính là item A (nguồn)
        item_b_id: d.conflict_item?.id || d.item_b_id, // chính là item B (gây conflict)
        target_thu: d.target_thu,
        target_buoi: d.target_buoi,
        target_tiet: d.target_tiet,
        target_lop_hoc_id: d.target_lop_hoc_id,
        // gửi cả off_slots/fixed_slots nếu bạn muốn backend tôn trọng chúng
        off_slots: mapToSlotList(offSlots),
        fixed_slots: mapToSlotList(fixedSlots),
      }
      console.log('🔁 Resolve payload', payload)
      const r = await tkbAPI.resolveConflict(payload)
      console.log('🔁 Resolve response', r)
      message.success('Đã thay thế và tự động sắp xếp lại!')
      await loadTKB()
    } catch (err) {
      console.error('Resolve error', err, err.response?.data)
      message.error(err.response?.data?.detail || err.response?.data?.error || 'Không thể tự động sắp xếp. Đã hủy thao tác.')
    } finally {
      setSwapModal(null)
      setDragSource(null)
    }
  }

  // ══ HELPER ═══════════════════════════════════════════════

  const getCauHinhNgay = (thu) => cauHinhNgay.find(n => n.thu === thu)

  const ngayCoHoc = (thu) => {
    const cfg = getCauHinhNgay(thu)
    return cfg ? cfg.co_buoi_sang || cfg.co_buoi_chieu : true
  }

  const buoiCoHoc = (thu, buoi) => {
    const cfg = getCauHinhNgay(thu)
    if (!cfg) return true

    if (xemTheo === 'gv' && selGV) {
      const gvConfig = rangBuocGV[selGV]
      if (gvConfig && gvConfig.ngay_nghi_list && gvConfig.ngay_nghi_list.includes(thu)) {
        return false
      }
    }

    return buoi === 'sang' ? cfg.co_buoi_sang : cfg.co_buoi_chieu
  }

  const soTietSangNgay = (thu) => {
    const cfg = getCauHinhNgay(thu)
    if (!cfg || !cfg.co_buoi_sang) return 0
    return cfg.co_buoi_chieu ? 4 : 5
  }

  const getOTKB = (thu, buoi, tiet) => {
    return tkbData.find(t =>
      t.thu === thu && t.buoi === buoi && t.tiet === tiet
    )
    // ⭐ LOG CHI TIẾT
    if (found && (found.id === 49 || found.id === 44)) {
      console.log(`🔍 getOTKB(${thu}, ${buoi}, ${tiet}) =`, found)
    }
    return found
  }

  const isSlotDragOver = (thu, buoi, tiet) =>
    dragOver?.thu === thu && dragOver?.buoi === buoi && dragOver?.tiet === tiet

  const isSlotBeingDragged = (oTKB) =>
    dragSource?.id === oTKB?.id

  // ══ BUILD ROWS ═══════════════════════════════════════════

  // ⭐ SỬA: Không dùng hàm buildRows, dùng useMemo trực tiếp
  const rows = React.useMemo(() => {
    const result = []
    const maxTietSang = cauHinhNgay.reduce((max, n) => {
      const so = n.co_buoi_sang ? (n.co_buoi_chieu ? 4 : 5) : 0
      return Math.max(max, so)
    }, 5)
    const maxTietChieu = cauHinhNgay.some(n => n.co_buoi_chieu) ? 3 : 0

    for (let t = 1; t <= maxTietSang; t++) {
      result.push({ buoi: 'sang', tiet: t, label: `Sáng T${t}` })
    }
    for (let t = 1; t <= maxTietChieu; t++) {
      result.push({ buoi: 'chieu', tiet: t, label: `Chiều T${t}` })
    }
    return result
  }, [cauHinhNgay, tkbData])  // ⭐ PHỤ THUỘC vào tkbData

  // ══ BUILD COLUMNS ═══════════════════════════════════════

  const columns = [
    {
      title: 'Tiết',
      dataIndex: 'label',
      width: 80,
      fixed: 'left',
      render: v => <Text style={{ fontSize: 12 }}>{v}</Text>
    },
    ...THU_LIST.map(thu => ({
      title: (
        <div style={{ textAlign: 'center' }}>
          <Text strong style={{ fontSize: 12 }}>{THU_LABEL[thu]}</Text>
          {!ngayCoHoc(thu) && <div><Tag color="default" style={{ fontSize: 10 }}>Nghỉ</Tag></div>}
        </div>
      ),
      key: `thu_${thu}`,
      width: 130,
      align: 'center',
      render: (_, row) => {
        // ⭐ KIỂM TRA GV NGHỈ NGÀY NÀY
        if (xemTheo === 'gv' && selGV) {
          const gvConfig = rangBuocGV[selGV]
          if (gvConfig && gvConfig.ngay_nghi_list && gvConfig.ngay_nghi_list.includes(thu)) {
            return (
              <div style={{
                background: '#f5f5f5',
                borderRadius: 4,
                minHeight: 48,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ccc',
                fontSize: 11,
                border: '1px dashed #d9d9d9'
              }}>
                🚫 Nghỉ
              </div>
            )
          }
        }

        // Kiểm tra buổi học theo cấu hình ngày
        if (!buoiCoHoc(thu, row.buoi)) {
          return <div style={{ background: '#f5f5f5', borderRadius: 4, minHeight: 48 }} />
        }
        if (row.buoi === 'sang' && row.tiet > soTietSangNgay(thu)) {
          return <div style={{ background: '#f5f5f5', borderRadius: 4, minHeight: 48 }} />
        }

        const oTKB = getOTKB(thu, row.buoi, row.tiet)
        const isOver = isSlotDragOver(thu, row.buoi, row.tiet)
        const isDragged = isSlotBeingDragged(oTKB)

        // ⭐ QUAN TRỌNG: Xác định lop_id cho ô này
        let lop_id = null
        if (xemTheo === 'lop') {
          // Chế độ lớp: dùng ID lớp đang chọn
          lop_id = selLop
        } else if (xemTheo === 'gv' && selGV) {
          // Chế độ GV: dùng ID GV làm key (vì ô trống không thuộc lớp nào)
          lop_id = `gv_${selGV}`
        }

        // Nếu có tiết thì dùng lop_hoc_id của tiết đó
        const finalLopId = oTKB ? oTKB.lop_hoc_id : lop_id

        // ⭐ Kiểm tra trạng thái của ô
        const isOff = isSlotOff(thu, row.buoi, row.tiet, finalLopId)
        const isFixed = isSlotFixed(thu, row.buoi, row.tiet, finalLopId)

        // ══ Ô CÓ TIẾT ═══════════════════════════════════════
        if (oTKB) {
          return (
            <div
              draggable={xemTheo === 'gv' && !isFixed}
              onDragStart={xemTheo === 'gv' ? e => handleDragStart(e, oTKB) : undefined}
              onDragEnd={xemTheo === 'gv' ? handleDragEnd : undefined}
              onDragOver={xemTheo === 'gv' ? e => handleDragOver(e, thu, row.buoi, row.tiet) : undefined}
              onDragLeave={xemTheo === 'gv' ? handleDragLeave : undefined}
              onDrop={xemTheo === 'gv' ? e => handleDrop(e, thu, row.buoi, row.tiet) : undefined}
              onContextMenu={e => handleContextMenu(e, thu, row.buoi, row.tiet, oTKB, finalLopId)}
              style={{
                background: isDragged ? '#fff7e6' : isOver ? '#f6ffed' : isOff ? '#f5f5f5' : isFixed ? '#fff7e6' : '#e6f4ff',
                border: isDragged ? '2px dashed #fa8c16' : isOver ? '2px dashed #52c41a' : isFixed ? '2px solid #fa8c16' : '1px solid #91caff',
                borderRadius: 4, padding: '3px 4px', minHeight: 48,
                position: 'relative',
                cursor: isFixed ? 'not-allowed' : (xemTheo === 'gv' ? 'grab' : 'pointer'),
                opacity: isDragged ? 0.5 : (isOff ? 0.4 : 1),
                transition: 'all 0.15s',
              }}
            >
              {isOff && (
                <div style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  background: '#ff4d4f',
                  color: 'white',
                  fontSize: 8,
                  padding: '1px 4px',
                  borderRadius: '0 4px 0 4px'
                }}>
                  NGHỈ
                </div>
              )}
              {isFixed && (
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  background: '#fa8c16',
                  color: 'white',
                  fontSize: 8,
                  padding: '1px 4px',
                  borderRadius: '4px 0 4px 0'
                }}>
                  🔒
                </div>
              )}
              <Text strong style={{ fontSize: 12, color: isOff ? '#999' : '#1677ff', display: 'block' }}>
                {oTKB.ten_mon}
              </Text>
              <Text style={{ fontSize: 11, color: isOff ? '#999' : '#555' }}>
                {xemTheo === 'lop' ? oTKB.ten_giao_vien : oTKB.ten_lop}
              </Text>
              {xemTheo === 'gv' && !isFixed && (
                <Tooltip title="Kéo để di chuyển tiết này">
                  <SwapOutlined style={{ position: 'absolute', top: 3, right: 20, color: '#aaa', fontSize: 10 }} />
                </Tooltip>
              )}
              {!isFixed && (
                <Popconfirm title="Xóa tiết này?" onConfirm={() => handleXoaOTKB(oTKB.id)} okText="Xóa" cancelText="Hủy">
                  <DeleteOutlined style={{ position: 'absolute', top: 3, right: 4, color: '#ff4d4f', fontSize: 11 }} />
                </Popconfirm>
              )}
            </div>
          )
        }

        // ══ Ô TRỐNG ══════════════════════════════════════════
        return (
          <div
            onDragOver={xemTheo === 'gv' ? e => handleDragOver(e, thu, row.buoi, row.tiet) : undefined}
            onDragLeave={xemTheo === 'gv' ? handleDragLeave : undefined}
            onDrop={xemTheo === 'gv' ? e => handleDrop(e, thu, row.buoi, row.tiet) : undefined}
            onClick={() => {
              if (!isOff && !isFixed && xemTheo === 'lop') {
                openPopup(thu, row.buoi, row.tiet)
              }
            }}
            onContextMenu={(e) => {
              e.preventDefault()
              e.stopPropagation()
              // ⭐ Dùng finalLopId đã xác định ở trên
              if (finalLopId) {
                handleContextMenu(e, thu, row.buoi, row.tiet, null, finalLopId)
              }
            }}
            style={{
              minHeight: 48,
              borderRadius: 4,
              border: isOff ? '1px solid #d9d9d9' : (isOver ? '2px dashed #52c41a' : (isFixed ? '2px solid #fa8c16' : '1px dashed #d9d9d9')),
              background: isOff ? '#f5f5f5' : (isOver ? '#f6ffed' : (isFixed ? '#fff7e6' : 'transparent')),
              cursor: isFixed ? 'not-allowed' : (xemTheo === 'lop' ? 'pointer' : 'default'),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: isOff ? '#bfbfbf' : (isOver ? '#52c41a' : (isFixed ? '#fa8c16' : '#ccc')),
              transition: 'all 0.15s',
              position: 'relative'
            }}
            onMouseEnter={e => {
              if (xemTheo === 'lop' && !isFixed && !isOff) {
                e.currentTarget.style.background = '#f0f9ff'
              }
            }}
            onMouseLeave={e => {
              if (!isOver && !isFixed && !isOff) {
                e.currentTarget.style.background = 'transparent'
              }
            }}
          >
            {isOff ? (
              <Text style={{ fontSize: 11, color: '#bfbfbf' }}>🚫 Nghỉ</Text>
            ) : (
              <>
                {isFixed && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    background: '#fa8c16',
                    color: 'white',
                    fontSize: 8,
                    padding: '1px 4px',
                    borderRadius: '4px 0 4px 0'
                  }}>
                    🔒
                  </div>
                )}
                {xemTheo === 'lop' && !isFixed && <PlusOutlined style={{ fontSize: 12 }} />}
                {xemTheo === 'gv' && isOver && !isFixed && !isOff && <Text style={{ fontSize: 11, color: '#52c41a' }}>Thả vào đây</Text>}
              </>
            )}
          </div>
        )
      }
    }))
  ]
  // ══ RENDER ════════════════════════════════════════════════

  return (
    <>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle" wrap>
          <Col>
            <Select
              placeholder="Năm học"
              value={selNamHoc}
              onChange={setSelNamHoc}
              style={{ width: 130 }}
              options={(dsNamHoc || []).map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col>
            <Select
              placeholder="Học kỳ"
              value={selHocKy}
              onChange={setSelHocKy}
              style={{ width: 130 }}
              options={dsHocKy.map(h => ({ value: h.id, label: h.ten_hoc_ky }))}
            />
          </Col>
          <Col>
            <Radio.Group
              value={xemTheo}
              onChange={e => setXemTheo(e.target.value)}
              buttonStyle="solid"
              size="small"
            >
              <Radio.Button value="lop">📚 Theo lớp</Radio.Button>
              <Radio.Button value="gv">👨‍🏫 Theo GV</Radio.Button>
            </Radio.Group>
          </Col>
          <Col>
            {xemTheo === 'lop' ? (
              <Select
                placeholder="Chọn lớp"
                value={selLop}
                onChange={setSelLop}
                style={{ width: 120 }}
                options={dsLop.map(l => ({ value: l.id, label: l.ten_lop }))}
                showSearch
                optionFilterProp="label"
              />
            ) : (
              <Select
                placeholder="Chọn giáo viên"
                value={selGV}
                onChange={setSelGV}
                style={{ width: 180 }}
                options={(dsGV || []).map(g => ({
                  value: g.id,
                  label: g.nguoi_dung?.ho_ten || `GV #${g.id}`
                }))}
                showSearch
                optionFilterProp="label"
              />
            )}
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={() => { setSinhModalOpen(true); setSinhResult(null) }}
              disabled={!selNamHoc || !selHocKy}
              style={{ background: '#722ed1', borderColor: '#722ed1' }}
            >
              Sinh TKB tự động
            </Button>
          </Col>
          {/* ⭐ THÊM BUTTON XUẤT EXCEL VÀO ĐÂY - CÙNG HÀNG */}
          <Col>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExportExcel}
              disabled={!selNamHoc || !selHocKy}
              style={{ color: '#1D9E75', borderColor: '#1D9E75' }}
            >
              📥 Xuất Excel
            </Button>
          </Col>
        </Row>
      </Card >

      <Spin spinning={loading}>
        <Table
          key={tableKey + refreshKey}
          rowKey={r => `${r.buoi}-${r.tiet}`}
          columns={columns}
          dataSource={[...rows]}
          pagination={false}
          size="small"
          bordered
          scroll={{ x: 900 }}
        />
      </Spin>

      {/* ══ CONTEXT MENU ═══════════════════════════════════════ */}

      {
        contextMenu.visible && contextMenu.lop_id && (
          <div
            style={{
              position: 'fixed',
              top: contextMenu.y,
              left: contextMenu.x,
              background: 'white',
              borderRadius: 8,
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              padding: '4px 0',
              zIndex: 1000,
              minWidth: 200,
              border: '1px solid #e8e8e8'
            }}
            onMouseLeave={handleCloseContextMenu}
            onClick={e => e.stopPropagation()}
          >
            <div
              style={{
                padding: '8px 16px',
                cursor: 'default',
                borderBottom: '1px solid #f0f0f0',
                display: 'flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <Text strong style={{ fontSize: 12 }}>
                {contextMenu.oTKB ? `📚 ${contextMenu.oTKB.ten_mon}` : '📌 Ô trống'}
              </Text>
              <Text type="secondary" style={{ fontSize: 11 }}>
                {THU_LABEL[contextMenu.thu]} - T{contextMenu.tiet}
              </Text>
            </div>

            {/* ⭐ LUÔN HIỂN THỊ TÙY CHỌN TIẾT NGHỈ CHO MỌI Ô */}
            <div
              style={{
                padding: '8px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: offSlots[getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)] ? '#f6ffed' : 'transparent'
              }}
              onClick={toggleOffSlot}
              onMouseEnter={e => e.currentTarget.style.background = '#f5f5f5'}
              onMouseLeave={e => {
                const key = getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)
                if (!offSlots[key]) {
                  e.currentTarget.style.background = 'transparent'
                }
              }}
            >
              <Checkbox
                checked={!!offSlots[getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)]}
                onChange={() => { }}
              />
              <Text>🚫 Tiết nghỉ</Text>
              <Text type="secondary" style={{ fontSize: 11, marginLeft: 'auto' }}>
                (không xếp tiết)
              </Text>
            </div>

            {/* ⭐ CHỈ HIỂN THỊ CỐ ĐỊNH KHI CÓ TIẾT HOẶC Ở CHẾ ĐỘ LỚP */}
            {(contextMenu.oTKB || xemTheo === 'lop') && (
              <div
                style={{
                  padding: '8px 16px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: fixedSlots[getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)] ? '#fff7e6' : 'transparent'
                }}
                onClick={toggleFixedSlot}
                onMouseEnter={e => e.currentTarget.style.background = '#f5f5f5'}
                onMouseLeave={e => {
                  const key = getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)
                  if (!fixedSlots[key]) {
                    e.currentTarget.style.background = 'transparent'
                  }
                }}
              >
                <Checkbox
                  checked={!!fixedSlots[getSlotKey(contextMenu.thu, contextMenu.buoi, contextMenu.tiet, contextMenu.lop_id)]}
                  onChange={() => { }}
                />
                <Text>🔒 Cố định tiết</Text>
              </div>
            )}

            {/* ⭐ CHỈ HIỂN THỊ XÓA KHI CÓ TIẾT */}
            {contextMenu.oTKB && (
              <div
                style={{
                  padding: '8px 16px',
                  cursor: 'pointer',
                  color: '#ff4d4f',
                  borderTop: '1px solid #f0f0f0'
                }}
                onClick={() => {
                  handleXoaOTKB(contextMenu.oTKB.id)
                  handleCloseContextMenu()
                }}
                onMouseEnter={e => e.currentTarget.style.background = '#fff1f0'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                🗑️ Xóa tiết này
              </div>
            )}
          </div>
        )
      }

      {/* ══ MODAL CHỌN MÔN ═══════════════════════════════════ */}
      <Modal
        title={selectedCell
          ? `Chọn môn — ${THU_LABEL[selectedCell?.thu]} | ${selectedCell?.buoi === 'sang' ? '☀️ Sáng' : '🌙 Chiều'} Tiết ${selectedCell?.tiet}`
          : 'Chọn môn học'}
        open={popupOpen}
        onOk={handleLuuOTKB}
        onCancel={() => setPopupOpen(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={500}
      >
        {dsPhanCong.length === 0 ? (
          <Text type="secondary">Lớp này chưa có phân công môn học</Text>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {dsPhanCong.map((pc, idx) => (
              <div
                key={idx}
                onClick={() => setSelPhanCong(pc)}
                style={{
                  padding: '10px 14px',
                  border: `2px solid ${selPhanCong?.mon_hoc_id === pc.mon_hoc_id && selPhanCong?.giao_vien_id === pc.giao_vien_id ? '#1677ff' : '#d9d9d9'}`,
                  borderRadius: 8, cursor: 'pointer',
                  background: selPhanCong?.mon_hoc_id === pc.mon_hoc_id && selPhanCong?.giao_vien_id === pc.giao_vien_id ? '#e6f4ff' : '#fff',
                  transition: 'all 0.2s',
                }}
              >
                <Text strong style={{ color: '#1677ff' }}>{pc.ten_mon}</Text>
                {pc.ten_phan_mon && (
                  <Text style={{ marginLeft: 6, fontSize: 12, color: '#fa8c16' }}>
                    ({pc.ten_phan_mon})
                  </Text>
                )}
                <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>({pc.ma_mon})</Text>
                <br />
                <Text style={{ fontSize: 12 }}>👨‍🏫 {pc.ten_giao_vien}</Text>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* ══ MODAL SINH TKB ═══════════════════════════════════ */}
      <Modal
        title="⚡ Sinh TKB tự động"
        open={sinhModalOpen}
        onOk={() => {
          if (sinhResult) {
            handleCloseSinhModal()
          } else {
            handleSinhTKB()
          }
        }}
        onCancel={handleCloseSinhModal}
        okText={sinhing ? 'Đang sinh...' : (sinhResult ? '✅ Đồng ý' : '⚡ Bắt đầu sinh')}
        okButtonProps={{
          loading: sinhing,
          style: {
            background: sinhResult ? '#52c41a' : '#722ed1',
            borderColor: sinhResult ? '#52c41a' : '#722ed1'
          }
        }}
        cancelText={sinhResult ? 'Đóng' : 'Hủy'}
        width={500}
      >
        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          <Text>Hệ thống sẽ tự động xếp TKB cho toàn trường dựa trên:</Text>
          <ul style={{ paddingLeft: 20, color: '#555', margin: 0 }}>
            <li>Phân công giảng dạy đã cấu hình</li>
            <li>Số tiết/tuần theo khối</li>
            <li>Ràng buộc môn học</li>
            <li>Ràng buộc giáo viên</li>
            <li>Cấu hình ngày học</li>
          </ul>
          <Checkbox
            checked={clearOld}
            onChange={e => setClearOld(e.target.checked)}
            disabled={sinhing || !!sinhResult}
          >
            <Text type="warning">Xóa TKB cũ trước khi sinh mới</Text>
          </Checkbox>
          {sinhResult && (
            <Card size="small" style={{ background: '#f6ffed', borderColor: '#b7eb8f' }}>
              <Text strong style={{ color: '#52c41a' }}>
                ✅ Đã xếp: {sinhResult.success}/{sinhResult.total_jobs} tiết
              </Text>
              {sinhResult.errors?.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <Text type="danger" strong>⚠️ {sinhResult.errors.length} tiết không xếp được:</Text>
                  <ul style={{ paddingLeft: 20, marginTop: 4 }}>
                    {sinhResult.errors.slice(0, 10).map((e, i) => (
                      <li key={i} style={{ fontSize: 12, color: '#ff4d4f' }}>{e}</li>
                    ))}
                    {sinhResult.errors.length > 10 && (
                      <li style={{ fontSize: 12, color: '#888' }}>... và {sinhResult.errors.length - 10} tiết khác</li>
                    )}
                  </ul>
                </div>
              )}
            </Card>
          )}
        </Space>
      </Modal>

      {/* ══ MODAL XÁC NHẬN SWAP ══════════════════════════════ */}
      <Modal
        title="🔗 Xác nhận đổi chỗ dây chuyền"
        open={swapModal?.type === 'cascade'}
        onOk={handleConfirmCascade}
        onCancel={() => { setSwapModal(null); setDragSource(null) }}
        okText={`Đồng ý đổi ${swapModal?.data?.moves?.length || 0} tiết`}
        cancelText="Hủy"
        width={560}
        centered
        destroyOnClose
      >
        {swapModal?.data?.moves && (
          <Space direction="vertical" style={{ width: '100%' }} size={8}>
            <Text type="secondary">
              Hệ thống cần đổi chỗ dây chuyền {swapModal.data.moves.length} tiết học sau:
            </Text>
            {swapModal.data.moves.map((mv, idx) => (
              <div key={idx} style={{
                background: '#f0f5ff', border: '1px solid #adc6ff',
                borderRadius: 8, padding: '8px 12px',
              }}>
                <Text strong>{mv.ten_mon}</Text>
                <Text style={{ fontSize: 12, color: '#555', marginLeft: 8 }}>
                  👨‍🏫 {mv.ten_gv} — {mv.ten_lop}
                </Text>
                <div style={{ fontSize: 12, marginTop: 2 }}>
                  {THU_LABEL[mv.tu_thu]} {mv.tu_buoi === 'sang' ? 'Sáng' : 'Chiều'} T{mv.tu_tiet}
                  {' → '}
                  <Text strong style={{ color: '#1677ff' }}>
                    {THU_LABEL[mv.den_thu]} {mv.den_buoi === 'sang' ? 'Sáng' : 'Chiều'} T{mv.den_tiet}
                  </Text>
                </div>
              </div>
            ))}
          </Space>
        )}
      </Modal>
      <Modal
        title="🔄 Xác nhận đổi chỗ"
        open={swapModal?.type === 'swap'}
        onOk={handleConfirmSwap}
        onCancel={() => { setSwapModal(null); setDragSource(null) }}
        okText="Đồng ý đổi chỗ"
        cancelText="Hủy"
        width={500}
        centered
        destroyOnClose
      >
        {swapModal?.data && (
          <Space direction="vertical" style={{ width: '100%' }} size={12}>
            <div style={{
              background: '#e6f4ff', border: '1px solid #91caff',
              borderRadius: 8, padding: '12px 16px'
            }}>
              <Text strong style={{ color: '#1677ff' }}>📤 Tiết A:</Text>
              <div style={{ marginTop: 4 }}>
                <Text>{swapModal.data.ten_mon_a}</Text>
                <Text style={{ fontSize: 12, color: '#555', marginLeft: 8 }}>
                  👨‍🏫 {swapModal.data.ten_gv_a} — {swapModal.data.ten_lop_a}
                </Text>
              </div>
            </div>

            <div style={{ textAlign: 'center', color: '#fa8c16', fontSize: 18 }}>🔄</div>

            <div style={{
              background: '#fff7e6', border: '1px solid #ffd591',
              borderRadius: 8, padding: '12px 16px'
            }}>
              <Text strong style={{ color: '#fa8c16' }}>📥 Tiết B:</Text>
              <div style={{ marginTop: 4 }}>
                <Text>{swapModal.data.ten_mon_b}</Text>
                <Text style={{ fontSize: 12, color: '#555', marginLeft: 8 }}>
                  👨‍🏫 {swapModal.data.ten_gv_b} — {swapModal.data.ten_lop_b}
                </Text>
              </div>
            </div>

            <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
              Bạn có chắc chắn muốn đổi chỗ 2 tiết học này?
            </Text>
          </Space>
        )}
      </Modal>

      {/* ══ MODAL XỬ LÝ CONFLICT ══════════════════════════════ */}
      <Modal
        title="⚠️ Không thể đổi chỗ"
        open={swapModal?.type === 'conflict'}
        onCancel={() => { setSwapModal(null); setDragSource(null) }}
        footer={[
          <Button key="close" onClick={() => { setSwapModal(null); setDragSource(null) }}>Đóng</Button>
        ]}
        width={480}
        centered
        destroyOnClose
      >
        {swapModal?.data && (
          <Text type="danger">{swapModal.data.ly_do}</Text>
        )}
      </Modal>
    </>
  )
}