// frontend/src/pages/ThiDuaHS/components/TabTapThe.jsx
import React, { useState, useEffect, useCallback } from 'react'
import { Card, Row, Col, Select, InputNumber, Button, message, Badge, Modal, Form, DatePicker, Input, Space, Tag, Typography, Tooltip, Popconfirm, Table, Tabs } from 'antd'
import { PlusOutlined, SaveOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { tapTheAPI, caNhanAPI, diemTuanAPI } from '../services/api'
import BangTongHopLop from '../tables/BangTongHopLop'
import BangDiemTuan from '../tables/BangDiemTuan'
import ModalThemVPTapThe from '../modals/ModalThemVPTapThe'
import ModalSuaVPTapThe from '../modals/ModalSuaVPTapThe'
import ModalSuaVPCaNhan from '../modals/ModalSuaVPCaNhan'
import ModalChiTietViPham from '../modals/ModalChiTietViPham'  // ⭐ Import modal mới

const { Text } = Typography

export default function TabTapThe({ meta, refreshKey, onDataChange }) {
  const { dsNamHoc, dsLoaiVP, selNamHoc, dsLop, setSelNamHoc } = meta
  const [tuan, setTuan] = useState(1)
  const [dsVPTapThe, setDsVPTapThe] = useState([])
  const [dsVPCaNhan, setDsVPCaNhan] = useState([])
  const [diemTuan, setDiemTuan] = useState([])
  const [tongHopLop, setTongHopLop] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingCaNhan, setLoadingCaNhan] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saved, setSaved] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [form] = Form.useForm()

  const dsLoaiTapThe = dsLoaiVP.filter(item => item.doi_tuong === 'tap_the')
  const dsLoaiVPCaNhan = dsLoaiVP.filter(item => item.doi_tuong === 'ca_nhan')
  const soTieuChi = dsLoaiVP.filter(l => l.is_active !== false).length || 8
  const soNgayTrongTuan = parseInt(localStorage.getItem('soNgayTrongTuan')) || 5

  const [editTapTheModal, setEditTapTheModal] = useState(false)
  const [editingTapThe, setEditingTapThe] = useState(null)
  const [editTapTheForm] = Form.useForm()

  const [editCaNhanModal, setEditCaNhanModal] = useState(false)
  const [editingCaNhan, setEditingCaNhan] = useState(null)
  const [editCaNhanForm] = Form.useForm()

  // ⭐ State cho ModalChiTietViPham
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState(null)

  // ⭐ Hàm mở modal chi tiết
  const openDetailModal = (record) => {
    setSelectedRecord(record)
    setDetailModalOpen(true)
  }

  // ⭐ Hàm đóng modal chi tiết
  const closeDetailModal = () => {
    setDetailModalOpen(false)
    setSelectedRecord(null)
  }

  // ⭐ Hàm refresh sau khi xóa trong modal chi tiết
  const handleRefreshAfterDelete = async () => {
    await loadVPTapThe()
    await loadVPCaNhan()
    await loadDiemTuan()
    await tinhTongHopLop()
  }

  // Load vi phạm tập thể
  const loadVPTapThe = useCallback(async () => {
    if (!selNamHoc || !tuan) return
    setLoading(true)
    try {
      const r = await tapTheAPI.get(selNamHoc, tuan)
      setDsVPTapThe(r.data || [])
    } catch (err) {
      console.error('Lỗi load vi phạm tập thể:', err)
    } finally {
      setLoading(false)
    }
  }, [selNamHoc, tuan])

  // Load vi phạm cá nhân
  const loadVPCaNhan = useCallback(async () => {
    if (!selNamHoc || !tuan || !dsLop.length) return
    setLoadingCaNhan(true)
    try {
      let allViPham = []
      for (const lop of dsLop) {
        try {
          const r = await caNhanAPI.get(lop.id, selNamHoc, tuan)
          const viPhamWithLop = (r.data || []).map(vp => ({
            ...vp,
            lop_hoc_id: lop.id,
            ten_lop: lop.ten_lop,
          }))
          allViPham = [...allViPham, ...viPhamWithLop]
        } catch (err) {
          console.error(`Lỗi load vi phạm lớp ${lop.ten_lop}:`, err)
        }
      }
      setDsVPCaNhan(allViPham)
    } catch (err) {
      console.error('Lỗi load vi phạm cá nhân:', err)
    } finally {
      setLoadingCaNhan(false)
    }
  }, [selNamHoc, tuan, dsLop])

  // Load điểm tuần
  const loadDiemTuan = useCallback(async () => {
    if (!selNamHoc || !tuan) return
    try {
      const r = await diemTuanAPI.get(selNamHoc, tuan)
      const data = r.data || []
      const fullData = dsLop.map(lop => {
        const existing = data.find(d => d.lop_hoc_id === lop.id)
        return {
          lop_hoc_id: lop.id,
          ten_lop: lop.ten_lop,
          khoi: lop.khoi,
          diem_doi: existing?.diem_doi || 0,
          diem_doi_tb: existing?.diem_doi || 0,
          diem_hoc_tap: existing?.diem_hoc_tap || 0,
          tong_diem: existing?.tong_diem || 0,
          trung_binh: existing?.trung_binh || 0,
          ghi_chu: existing?.ghi_chu || '',
        }
      })
      setDiemTuan(fullData)
      setSaved(true)
    } catch (err) {
      console.error('Lỗi load điểm tuần:', err)
    }
  }, [selNamHoc, tuan, dsLop])

  // Hàm tính tổng hợp điểm đội

  const tinhTongHopLop = useCallback(() => {
    if (!dsLop.length) return

    const soDanhMuc = dsLoaiVP.filter(l => l.is_active !== false).length
    const soNgayTrongTuan = parseInt(localStorage.getItem('soNgayTrongTuan')) || 5
    const tongDiemToiDa = soDanhMuc * 10 * soNgayTrongTuan

    const lopMap = {}
    dsLop.forEach(lop => {
      lopMap[lop.id] = {
        lop_hoc_id: lop.id,
        ten_lop: lop.ten_lop,
        khoi: lop.khoi,
        tong_vi_pham: 0,
        tong_thanh_tich: 0,
        tong_diem_doi: tongDiemToiDa,
        diem_doi_tb: 0,
      }
    })

    dsVPTapThe.forEach(vp => {
      const lopId = vp.lop_hoc_id
      if (lopMap[lopId]) {
        if (vp.so_diem < 0) lopMap[lopId].tong_vi_pham += vp.so_diem
        else lopMap[lopId].tong_thanh_tich += vp.so_diem
      }
    })

    dsVPCaNhan.forEach(vp => {
      const lopId = vp.lop_hoc_id
      if (lopId && lopMap[lopId]) {
        if (vp.so_diem < 0) lopMap[lopId].tong_vi_pham += vp.so_diem
        else lopMap[lopId].tong_thanh_tich += vp.so_diem
      }
    })

    const result = Object.values(lopMap).map(item => {
      const tongDiem = tongDiemToiDa + item.tong_thanh_tich + item.tong_vi_pham
      const diemTB = parseFloat((tongDiem / soDanhMuc / soNgayTrongTuan).toFixed(3))
      return { ...item, tong_diem_doi: tongDiem, diem_doi_tb: diemTB }
    })

    result.sort((a, b) => b.diem_doi_tb - a.diem_doi_tb)
    result.forEach((item, index) => { item.xep_hang = index + 1 })

    setTongHopLop(result)

    // ✅ Đồng bộ diem_doi sang bảng phải ngay tại đây
    setDiemTuan(prev => prev.map(item => {
      const lopTongHop = result.find(t => t.lop_hoc_id === item.lop_hoc_id)
      if (!lopTongHop) return item
      return {
        ...item,
        diem_doi: lopTongHop.diem_doi_tb,
        diem_doi_tb: lopTongHop.diem_doi_tb,
      }
    }))

  }, [dsLop, dsVPTapThe, dsVPCaNhan, dsLoaiVP])
  // Hàm lưu điểm học tập
  const onLuuDiemHocTap = async () => {
    if (isSaving) {
      console.log('⏳ Đang lưu, bỏ qua lần gọi trùng')
      return
    }
    setIsSaving(true)
    try {
      const dataToSave = diemTuan.map(d => ({
        lop_hoc_id: d.lop_hoc_id,
        diem_hoc_tap: parseFloat(d.diem_hoc_tap) || 0,
        diem_doi: parseFloat(d.diem_doi_tb) || 0,
        ghi_chu: d.ghi_chu || '',
      }))
      await diemTuanAPI.save({
        nam_hoc_id: selNamHoc,
        tuan: tuan,
        nguoi_nhap: 'Admin',
        data: dataToSave
      })
      setSaved(true)
      message.success('Đã lưu điểm học tập!')

      if (onDataChange) {
        console.log('🔄 Gọi onDataChange từ TabTapThe')
        onDataChange()
      }
    } catch (err) {
      console.error('Lỗi lưu điểm HT:', err)
      message.error('Lỗi khi lưu điểm học tập')
    } finally {
      setIsSaving(false)
    }
  }

  // Xóa vi phạm tập thể (dùng khi xóa từ bên ngoài modal)
  const onXoaTapThe = async (id) => {
    try {
      await tapTheAPI.delete(id)
      message.success('Đã xóa')
      await loadVPTapThe()
      await loadDiemTuan()
      await tinhTongHopLop()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // Xóa vi phạm cá nhân (dùng khi xóa từ bên ngoài modal)
  const onXoaCaNhan = async (id) => {
    try {
      await caNhanAPI.delete(id)
      message.success('Đã xóa')
      await loadVPCaNhan()
      await loadDiemTuan()
      await tinhTongHopLop()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // Auto-save điểm học tập
  useEffect(() => {
    if (selNamHoc && tuan && diemTuan.length > 0 && !saved) {
      const timer = setTimeout(() => {
        onLuuDiemHocTap()
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [diemTuan, saved])

  // Load dữ liệu ban đầu
  useEffect(() => {
    if (selNamHoc && tuan) {
      loadVPTapThe()
      loadVPCaNhan()
      loadDiemTuan()
    }
  }, [selNamHoc, tuan])

  // Reload khi refreshKey thay đổi
  useEffect(() => {
    if (selNamHoc && tuan) {
      console.log('🔄 Refresh Tab Tập thể do refreshKey thay đổi:', refreshKey)
      loadVPTapThe()
      loadVPCaNhan()
      loadDiemTuan()
    }
  }, [refreshKey, selNamHoc, tuan])

  // Tính tổng hợp
  useEffect(() => {
    if (dsLop.length > 0) {
      tinhTongHopLop()
    }
  }, [dsVPTapThe, dsVPCaNhan, dsLop])

  // Cập nhật điểm đội vào diemTuan
  /*  useEffect(() => {
      if (tongHopLop.length > 0 && diemTuan.length > 0) {
        setDiemTuan(prev => prev.map(item => {
          const lopTongHop = tongHopLop.find(t => t.lop_hoc_id === item.lop_hoc_id)
          return {
            ...item,
            diem_doi: lopTongHop?.diem_doi_tb || 0,
            diem_doi_tb: lopTongHop?.diem_doi_tb || 0,
          }
        }))
      }
    }, [tongHopLop])
  */
  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}
              onChange={setSelNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={4}>
            <InputNumber
              placeholder="Tuần"
              min={1}
              max={52}
              style={{ width: '100%' }}
              value={tuan}
              onChange={setTuan}
              addonBefore="Tuần"
            />
          </Col>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalOpen(true) }}>
              Thêm vi phạm
            </Button>
          </Col>
          <Col>
            <Badge count={dsVPTapThe.length + dsVPCaNhan.length} showZero />
          </Col>
        </Row>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <BangTongHopLop
            data={tongHopLop}
            loading={loading || loadingCaNhan}
            onViewDetail={openDetailModal}  // ⭐ Truyền hàm mở modal mới
          />
        </Col>
        <Col span={12}>
          <BangDiemTuan
            data={diemTuan}
            loading={loading || loadingCaNhan}
            onSave={onLuuDiemHocTap}
            setData={setDiemTuan}
            setSaved={setSaved}
            tuan={tuan}
            namHoc={selNamHoc}
            saving={isSaving}
          />
        </Col>
      </Row>

      {/* ⭐ Modal chi tiết vi phạm - Component riêng */}
      <ModalChiTietViPham
        open={detailModalOpen}
        onClose={closeDetailModal}
        record={selectedRecord}
        dsVPTapThe={dsVPTapThe}
        dsVPCaNhan={dsVPCaNhan}
        onRefresh={handleRefreshAfterDelete}
        onEditTapThe={(vp) => {
          setEditingTapThe(vp)
          editTapTheForm.setFieldsValue({
            loai_vi_pham_id: vp.loai_vi_pham_id,
            so_diem: Math.abs(vp.so_diem),
            ngay_xay_ra: dayjs(vp.ngay_xay_ra),
            tiet: vp.tiet,
            mo_ta: vp.mo_ta || '',
          })
          setEditTapTheModal(true)
        }}
        onEditCaNhan={(vp) => {
          setEditingCaNhan(vp)
          editCaNhanForm.setFieldsValue({
            loai_vi_pham_id: vp.loai_vi_pham_id,
            so_diem: Math.abs(vp.so_diem),
            ngay_xay_ra: dayjs(vp.ngay_xay_ra),
            tiet: vp.tiet,
            mo_ta: vp.mo_ta || '',
          })
          setEditCaNhanModal(true)
        }}
      />

      <ModalThemVPTapThe
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => { loadVPTapThe(); loadDiemTuan() }}
        dsLop={dsLop}
        dsLoaiTapThe={dsLoaiTapThe}
        selNamHoc={selNamHoc}
        tuan={tuan}
      />

      <ModalSuaVPTapThe
        open={editTapTheModal}
        onClose={() => setEditTapTheModal(false)}
        onSuccess={() => { loadVPTapThe(); loadDiemTuan(); tinhTongHopLop() }}
        editing={editingTapThe}
        dsLoaiTapThe={dsLoaiTapThe}
        form={editTapTheForm}
      />

      <ModalSuaVPCaNhan
        open={editCaNhanModal}
        onClose={() => setEditCaNhanModal(false)}
        onSuccess={() => { loadVPCaNhan(); loadDiemTuan(); tinhTongHopLop() }}
        editing={editingCaNhan}
        dsLoaiVPCaNhan={dsLoaiVPCaNhan}
        form={editCaNhanForm}
      />
    </div>
  )
}