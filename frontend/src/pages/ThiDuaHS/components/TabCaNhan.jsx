// frontend/src/pages/ThiDuaHS/components/TabCaNhan.jsx
import React, { useState, useEffect, useCallback } from 'react'
import { Card, Row, Col, Select, InputNumber, Button, message, Badge, Form } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { caNhanAPI, metaAPI } from '../services/api'
import BangHocSinh from '../tables/BangHocSinh'
import ModalThemVPCaNhan from '../modals/ModalThemVPCaNhan'

export default function TabCaNhan({ meta, onDataChange }) {  // ⭐ Nhận prop onDataChange
  const { dsNamHoc, dsLoaiVP, selNamHoc, dsLop, setSelNamHoc } = meta
  const [tuan, setTuan] = useState(1)
  const [selLop, setSelLop] = useState(null)
  const [dsHS, setDsHS] = useState([])
  const [dsVP, setDsVP] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingHS, setLoadingHS] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const dsLoaiVPCaNhan = dsLoaiVP.filter(item => item.doi_tuong === 'ca_nhan')

  const loadHS = useCallback(async (lopId) => {
    if (!lopId) {
      setDsHS([])
      setDsVP([])
      setSelLop(null)
      return
    }
    setSelLop(lopId)
    setLoadingHS(true)
    try {
      const r = await metaAPI.getHocSinh(lopId)
      setDsHS(r.data || [])
      if (selNamHoc && tuan) {
        await loadVP(lopId)
      }
    } catch (err) {
      console.error('Lỗi load học sinh:', err)
      message.error('Không thể tải danh sách học sinh')
    } finally {
      setLoadingHS(false)
    }
  }, [selNamHoc, tuan])

  const loadVP = useCallback(async (lopId) => {
    if (!selNamHoc || !lopId) return
    setLoading(true)
    try {
      const r = await caNhanAPI.get(lopId, selNamHoc, tuan)
      setDsVP(r.data || [])
    } catch (err) {
      console.error('Lỗi load vi phạm:', err)
    } finally {
      setLoading(false)
    }
  }, [selNamHoc, tuan])

  const refreshData = useCallback(async () => {
    if (selLop) {
      await loadVP(selLop)
    }
  }, [selLop, loadVP])

  const onXoa = async (id) => {
    try {
      await caNhanAPI.delete(id)
      message.success('Đã xóa')
      await refreshData()
      if (onDataChange) onDataChange()  // ⭐ Gọi callback để refresh Tab Tập thể
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  const handleAddSuccess = useCallback(async (values) => {
    await refreshData()
    if (onDataChange) onDataChange()  // ⭐ Gọi callback để refresh Tab Tập thể
  }, [refreshData, onDataChange])

  useEffect(() => {
    if (selLop) {
      loadVP(selLop)
    }
  }, [selLop, tuan, selNamHoc, loadVP])

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
          <Col span={5}>
            <Select
              placeholder="Chọn lớp"
              style={{ width: '100%' }}
              disabled={!selNamHoc}
              value={selLop}
              onChange={loadHS}
              options={dsLop.map(l => ({ value: l.id, label: l.ten_lop }))}
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              disabled={!selLop || !selNamHoc}
              onClick={() => { form.resetFields(); setModalOpen(true) }}
            >
              Thêm
            </Button>
          </Col>
          <Col>
            <Badge count={dsHS.length} showZero />
          </Col>
        </Row>
      </Card>

      <BangHocSinh
        data={dsHS}
        viPham={dsVP}
        loading={loadingHS || loading}
        onAdd={(hsId) => {
          form.setFieldsValue({ hoc_sinh_id: hsId })
          setModalOpen(true)
        }}
        onDelete={onXoa}
      />

      <ModalThemVPCaNhan
        open={modalOpen}
        onClose={() => {
          setModalOpen(false)
          form.resetFields()
        }}
        onSuccess={handleAddSuccess}
        dsHS={dsHS}
        dsLoaiVPCaNhan={dsLoaiVPCaNhan}
        selNamHoc={selNamHoc}
        tuan={tuan}
        form={form}
      />
    </div>
  )
}