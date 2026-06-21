// frontend/src/pages/ThiDuaGV/ThiDuaGVPage.jsx
import React, { useEffect, useState, useCallback } from 'react'
import {
  Tabs, Table, Button, Space, Select, Modal, Form, Input,
  InputNumber, message, Popconfirm, Tooltip, Typography,
  Tag, Card, Row, Col, Badge,
} from 'antd'
import {
  PlusOutlined, DeleteOutlined, EditOutlined, SaveOutlined, CopyOutlined,
} from '@ant-design/icons'
import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1/thi-dua-gv' })
const { Title, Text } = Typography

const THANG_NAM_HOC = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5]

const XEP_LOAI_COLOR = (xep_loai) => {
  if (xep_loai?.includes('xuất sắc')) return 'gold'
  if (xep_loai?.includes('tốt')) return 'green'
  if (xep_loai?.includes('Hoàn thành')) return 'orange'
  return 'red'
}

const HANG_LABEL = (hang) => {
  if (hang === 1) return '🥇'
  if (hang === 2) return '🥈'
  if (hang === 3) return '🥉'
  return `#${hang}`
}

// ── Hook load metadata ────────────────────────────────────────
function useMeta() {
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsTo, setDsTo] = useState([])
  const [dsGiaoVien, setDsGiaoVien] = useState([])
  const [dsTieuChi, setDsTieuChi] = useState([])
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [selTo, setSelTo] = useState(null)

  useEffect(() => {
    api.get('/meta/nam-hoc')
      .then(r => {
        setDsNamHoc(r.data)
        // ⭐ Tự động chọn năm học
        if (r.data && r.data.length > 0) {
          const savedId = localStorage.getItem('selectedNamHocIdGV')
          const exists = r.data.some(n => n.id === parseInt(savedId))
          const selectedId = exists ? parseInt(savedId) : r.data[0].id
          setSelNamHoc(selectedId)
          localStorage.setItem('selectedNamHocIdGV', selectedId)
        }
      })
      .catch(() => { })

    api.get('/meta/to').then(r => setDsTo(r.data)).catch(() => { })
    api.get('/tieu-chi').then(r => setDsTieuChi(r.data)).catch(() => { })
  }, [])

  const handleSelectNamHoc = (id) => {
    setSelNamHoc(id)
    localStorage.setItem('selectedNamHocIdGV', id)
  }

  const onSelectTo = async (toId) => {
    setSelTo(toId)
    try {
      const q = toId ? `?to_id=${toId}` : ''
      const r = await api.get(`/meta/giao-vien${q}`)
      setDsGiaoVien(r.data)
    } catch { }
  }

  useEffect(() => {
    if (selNamHoc) {
      const q = selTo ? `?to_id=${selTo}` : ''
      api.get(`/meta/giao-vien${q}`).then(r => setDsGiaoVien(r.data)).catch(() => { })
    }
  }, [selNamHoc])

  return {
    dsNamHoc, dsTo, dsGiaoVien, dsTieuChi, setDsTieuChi,
    selNamHoc, setSelNamHoc: handleSelectNamHoc, selTo, setSelTo, onSelectTo,
  }
}

// ════════════════════════════════════════════════════
//  TAB TIÊU CHÍ
// ════════════════════════════════════════════════════
function TabTieuChi({ meta }) {
  const { dsTieuChi, setDsTieuChi } = meta
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const r = await api.get('/tieu-chi')
      setDsTieuChi(r.data)
    } catch { } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await api.put(`/tieu-chi/${edit.id}`, v)
      else await api.post('/tieu-chi', v)
      message.success('Lưu thành công')
      setOpen(false)
      load()
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const onXoa = async (id) => {
    await api.delete(`/tieu-chi/${id}`)
    message.success('Đã xóa')
    load()
  }

  const cols = [
    { title: 'Mã', dataIndex: 'ma_tieu_chi', width: 80, align: 'center' },
    { title: 'Tên tiêu chí', dataIndex: 'ten_tieu_chi' },
    {
      title: 'Loại', dataIndex: 'loai', width: 100, align: 'center',
      render: v => <Tag color={v === 'cong' ? 'green' : 'red'}>
        {v === 'cong' ? '✅ Cộng' : '❌ Trừ'}
      </Tag>
    },
    { title: 'Điểm tối đa', dataIndex: 'diem_toi_da', width: 110, align: 'center' },
    { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
    {
      title: 'Thao tác', width: 100,
      render: (_, r) => (
        <Space size={4}>
          <Button size="small" icon={<EditOutlined />}
            onClick={() => { setEdit(r); form.setFieldsValue(r); setOpen(true) }} />
          <Popconfirm title="Xóa tiêu chí?" onConfirm={() => onXoa(r.id)}
            okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <>
      <div style={{ marginBottom: 12, textAlign: 'right' }}>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { setEdit(null); form.resetFields(); setOpen(true) }}>
          Thêm tiêu chí
        </Button>
      </div>
      <Table rowKey="id" columns={cols} dataSource={dsTieuChi}
        loading={loading} size="small" bordered pagination={{ pageSize: 15 }} />

      <Modal title={edit ? 'Sửa tiêu chí' : 'Thêm tiêu chí'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="ten_tieu_chi" label="Tên tiêu chí" rules={[{ required: true }]}>
            <Input placeholder="VD: Soạn bài đầy đủ, đúng phân phối" />
          </Form.Item>
          <Row gutter={8}>
            <Col span={12}>
              <Form.Item name="loai" label="Loại" rules={[{ required: true }]}>
                <Select options={[
                  { value: 'cong', label: '✅ Tiêu chí cộng' },
                  { value: 'tru', label: '❌ Tiêu chí trừ' },
                ]} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="diem_toi_da" label="Điểm tối đa" rules={[{ required: true }]}>
                <InputNumber min={0} max={100} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB CHẤM ĐIỂM
// ════════════════════════════════════════════════════
function TabChamDiem({ meta }) {
  const { dsNamHoc, dsTo, dsGiaoVien, dsTieuChi, selNamHoc, setSelNamHoc, onSelectTo } = meta
  const [selGV, setSelGV] = useState(null)
  const [thang, setThang] = useState(9)
  const [diemMap, setDiemMap] = useState({})
  const [ghiChuMap, setGhiChuMap] = useState({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const diemHienTai = (() => {
    let tong = 100
    dsTieuChi.forEach(tc => {
      const d = parseFloat(diemMap[tc.id]) || 0
      if (tc.loai === 'cong') tong += d
      else tong -= d
    })
    return Math.max(0, tong)
  })()

  const xepLoai = (d) => {
    if (d >= 90) return { text: 'Hoàn thành xuất sắc nhiệm vụ', color: '#2E7D32', bg: '#E8F5E9' }
    if (d >= 80) return { text: 'Hoàn thành tốt nhiệm vụ', color: '#1565C0', bg: '#E3F2FD' }
    if (d >= 70) return { text: 'Hoàn thành nhiệm vụ', color: '#E65100', bg: '#FFF3E0' }
    return { text: 'Không hoàn thành nhiệm vụ', color: '#C62828', bg: '#FFEBEE' }
  }
  const xl = xepLoai(diemHienTai)

  const loadDiem = useCallback(async () => {
    if (!selGV || !selNamHoc) return
    setLoading(true)
    try {
      const r = await api.get(`/diem?giao_vien_id=${selGV}&thang=${thang}&nam_hoc_id=${selNamHoc}`)
      const dm = {}, gc = {}
      r.data.forEach(d => {
        dm[d.tieu_chi_id] = d.diem
        gc[d.tieu_chi_id] = d.ghi_chu
      })
      setDiemMap(dm)
      setGhiChuMap(gc)
    } catch { } finally { setLoading(false) }
  }, [selGV, thang, selNamHoc])

  useEffect(() => { loadDiem() }, [selGV, thang, selNamHoc])

  const onLuu = async () => {
    if (!selGV || !selNamHoc) { message.warning('Chọn GV và năm học'); return }
    setSaving(true)
    try {
      const diem_list = Object.entries(diemMap)
        .filter(([, d]) => d !== '' && d !== undefined)
        .map(([tc_id, d]) => ({
          tieu_chi_id: parseInt(tc_id),
          diem: parseFloat(d),
          ghi_chu: ghiChuMap[tc_id] || '',
        }))
      await api.post('/diem', {
        giao_vien_id: selGV,
        thang, nam_hoc_id: selNamHoc,
        nguoi_cham_id: 1,
        diem_list,
      })
      message.success('Đã lưu điểm!')
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi khi lưu')
    } finally { setSaving(false) }
  }

  const onCopyThangTruoc = async () => {
    const thangTruoc = thang === 8 ? null : thang === 1 ? 12 : thang - 1
    if (!thangTruoc) { message.warning('Không có tháng trước'); return }
    try {
      const r = await api.get(`/diem?giao_vien_id=${selGV}&thang=${thangTruoc}&nam_hoc_id=${selNamHoc}`)
      if (!r.data.length) { message.warning('Tháng trước chưa có điểm'); return }
      const dm = {}, gc = {}
      r.data.forEach(d => { dm[d.tieu_chi_id] = d.diem; gc[d.tieu_chi_id] = d.ghi_chu })
      setDiemMap(dm); setGhiChuMap(gc)
      message.success('Đã copy điểm từ tháng trước!')
    } catch { }
  }

  const renderBangTieuChi = (loai) => {
    const ds = dsTieuChi.filter(tc => tc.loai === loai)
    if (!ds.length) return <Text type="secondary">Chưa có tiêu chí</Text>
    return (
      <Table rowKey="id" size="small" bordered pagination={false}
        dataSource={ds}
        columns={[
          { title: 'Tên tiêu chí', dataIndex: 'ten_tieu_chi' },
          { title: 'Điểm tối đa', dataIndex: 'diem_toi_da', width: 100, align: 'center' },
          {
            title: 'Nhập điểm', width: 110, align: 'center',
            render: (_, r) => (
              <InputNumber size="small" min={0} max={r.diem_toi_da}
                style={{ width: 90 }}
                value={diemMap[r.id] ?? ''}
                onChange={val => setDiemMap(prev => ({ ...prev, [r.id]: val }))}
              />
            )
          },
          {
            title: 'Ghi chú', width: 140,
            render: (_, r) => (
              <Input size="small" value={ghiChuMap[r.id] || ''}
                onChange={e => setGhiChuMap(prev => ({ ...prev, [r.id]: e.target.value }))} />
            )
          },
        ]}
      />
    )
  }

  return (
    <div>
      {/* Filter */}
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}  // ⭐ Thêm value
              onChange={setSelNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={5}>
            <Select placeholder="Tổ chuyên môn" style={{ width: '100%' }}
              allowClear onChange={onSelectTo}
              options={dsTo.map(t => ({ value: t.id, label: t.ten_to }))} />
          </Col>
          <Col span={6}>
            <Select placeholder="Giáo viên" style={{ width: '100%' }}
              showSearch optionFilterProp="label"
              onChange={setSelGV}
              options={dsGiaoVien.map(gv => ({
                value: gv.id,
                label: `${gv.ho_ten} (${gv.ma_giao_vien})`,
              }))} />
          </Col>
          <Col span={4}>
            <Select style={{ width: '100%' }} value={thang} onChange={setThang}
              options={THANG_NAM_HOC.map(t => ({ value: t, label: `Tháng ${t}` }))} />
          </Col>
        </Row>
      </Card>

      {/* Điểm hiện tại */}
      {selGV && (
        <Card size="small" style={{ marginBottom: 12 }}>
          <Row align="middle" gutter={16}>
            <Col>
              <Text strong>📊 ĐIỂM HIỆN TẠI:</Text>
              <Text strong style={{ fontSize: 20, color: '#1D9E75', marginLeft: 8 }}>
                [{diemHienTai.toFixed(1)}]
              </Text>
            </Col>
            <Col>
              <Tag color={XEP_LOAI_COLOR(xl.text)} style={{ fontSize: 13, padding: '4px 10px' }}>
                {xl.text}
              </Tag>
            </Col>
            <Col flex="auto" style={{ textAlign: 'right' }}>
              <Space>
                <Button icon={<CopyOutlined />} onClick={onCopyThangTruoc}>
                  Copy tháng trước
                </Button>
                <Button type="primary" icon={<SaveOutlined />}
                  loading={saving} onClick={onLuu}>
                  Lưu điểm
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>
      )}

      {/* Bảng tiêu chí cộng */}
      <Card title="✅ Tiêu chí cộng" size="small" style={{ marginBottom: 12 }}>
        {renderBangTieuChi('cong')}
      </Card>

      {/* Bảng tiêu chí trừ */}
      <Card title="❌ Tiêu chí trừ" size="small">
        {renderBangTieuChi('tru')}
      </Card>
    </div>
  )
}

// ════════════════════════════════════════════════════
//  COMPONENT BẢNG XẾP HẠNG (dùng chung 3 tab)
// ════════════════════════════════════════════════════
function BangXepHang({ data, loading, tieuDe }) {
  // ⭐ Thêm state để quản lý pageSize
  const [pageSize, setPageSize] = useState(20)

  const cols = [
    {
      title: 'Hạng', dataIndex: 'hang', width: 70, align: 'center',
      render: v => <Text strong style={{ fontSize: 16 }}>{HANG_LABEL(v)}</Text>
    },
    { title: 'Mã GV', dataIndex: 'ma_giao_vien', width: 90, align: 'center' },
    { title: 'Họ tên', dataIndex: 'ho_ten' },
    {
      title: 'Điểm', dataIndex: 'diem', width: 90, align: 'center',
      render: (v, r) => (
        <Tag color={v >= 90 ? 'green' : v >= 80 ? 'blue' : v >= 70 ? 'orange' : 'red'}
          style={{ fontSize: 14, fontWeight: 'bold' }}>
          {v?.toFixed(1)}
        </Tag>
      )
    },
    {
      title: 'Xếp loại', dataIndex: 'xep_loai', width: 220,
      render: v => <Tag color={XEP_LOAI_COLOR(v)}>{v}</Tag>
    },
  ]

  // Thêm cột HK1/HK2 nếu có
  if (data.length && data[0].diem_hk1 !== undefined) {
    cols.splice(3, 0,
      {
        title: 'HK1', dataIndex: 'diem_hk1', width: 80, align: 'center',
        render: v => v?.toFixed(1)
      },
      {
        title: 'HK2', dataIndex: 'diem_hk2', width: 80, align: 'center',
        render: v => v?.toFixed(1)
      },
    )
  }

  return (
    <Table
      rowKey="giao_vien_id"
      columns={cols}
      dataSource={data}
      loading={loading}
      size="small"
      bordered
      pagination={{
        pageSize: pageSize,  // ⭐ Dùng state
        showSizeChanger: true,
        showQuickJumper: true,
        pageSizeOptions: ['10', '20', '50', '100'],
        showTotal: (total) => `Tổng: ${total} giáo viên`,
        onShowSizeChange: (current, size) => setPageSize(size),  // ⭐ Cập nhật state
      }}
      locale={{ emptyText: tieuDe ? 'Chưa có dữ liệu' : 'Chọn bộ lọc để xem' }}
      rowClassName={(r) =>
        r.hang === 1 ? 'row-gold' : r.hang === 2 ? 'row-silver' : r.hang === 3 ? 'row-bronze' : ''
      }
    />
  )
}
// ════════════════════════════════════════════════════
//  TAB THEO THÁNG
// ════════════════════════════════════════════════════
function TabTheoThang({ meta }) {
  const { dsNamHoc, dsTo, selNamHoc, setSelNamHoc, selTo, onSelectTo } = meta
  const [thang, setThang] = useState(9)
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  const onLoad = async () => {
    if (!selNamHoc) { message.warning('Chọn năm học'); return }
    setLoading(true)
    try {
      const q = `thang=${thang}&nam_hoc_id=${selNamHoc}${selTo ? `&to_id=${selTo}` : ''}`
      const r = await api.get(`/xep-hang/thang?${q}`)
      setData(r.data)
    } catch { message.error('Lỗi tải dữ liệu') } finally { setLoading(false) }
  }

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}  // ⭐ Thêm value
              onChange={setSelNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={5}>
            <Select placeholder="Tổ (tùy chọn)" style={{ width: '100%' }}
              allowClear onChange={onSelectTo}
              options={dsTo.map(t => ({ value: t.id, label: t.ten_to }))} />
          </Col>
          <Col span={4}>
            <Select style={{ width: '100%' }} value={thang} onChange={setThang}
              options={THANG_NAM_HOC.map(t => ({ value: t, label: `Tháng ${t}` }))} />
          </Col>
          <Col>
            <Button type="primary" onClick={onLoad} loading={loading}>🔍 Hiển thị</Button>
          </Col>
          {data.length > 0 && (
            <Col>
              <Badge count={data.length} style={{ backgroundColor: '#1D9E75' }}>
                <Text type="secondary">giáo viên</Text>
              </Badge>
            </Col>
          )}
        </Row>
      </Card>
      <BangXepHang data={data} loading={loading} tieuDe={!!selNamHoc} />
    </div>
  )
}

// ════════════════════════════════════════════════════
//  TAB HỌC KỲ
// ════════════════════════════════════════════════════
function TabHocKy({ meta }) {
  const { dsNamHoc, dsTo, selNamHoc, setSelNamHoc, selTo, onSelectTo } = meta
  const [hocKy, setHocKy] = useState(1)
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  const onLoad = async () => {
    if (!selNamHoc) { message.warning('Chọn năm học'); return }
    setLoading(true)
    try {
      const q = `hoc_ky_so_thu_tu=${hocKy}&nam_hoc_id=${selNamHoc}${selTo ? `&to_id=${selTo}` : ''}`
      const r = await api.get(`/xep-hang/hoc-ky?${q}`)
      setData(r.data)
    } catch { message.error('Lỗi tải dữ liệu') } finally { setLoading(false) }
  }

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}  // ⭐ Thêm value
              onChange={setSelNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={5}>
            <Select placeholder="Tổ (tùy chọn)" style={{ width: '100%' }}
              allowClear onChange={onSelectTo}
              options={dsTo.map(t => ({ value: t.id, label: t.ten_to }))} />
          </Col>
          <Col span={4}>
            <Select style={{ width: '100%' }} value={hocKy} onChange={setHocKy}
              options={[
                { value: 1, label: 'Học kỳ 1 (T8-T12)' },
                { value: 2, label: 'Học kỳ 2 (T1-T5)' },
              ]} />
          </Col>
          <Col>
            <Button type="primary" onClick={onLoad} loading={loading}>🔍 Hiển thị</Button>
          </Col>
        </Row>
      </Card>
      <BangXepHang data={data} loading={loading} tieuDe={!!selNamHoc} />
    </div>
  )
}

// ════════════════════════════════════════════════════
//  TAB CẢ NĂM
// ════════════════════════════════════════════════════
function TabCaNam({ meta }) {
  const { dsNamHoc, dsTo, selNamHoc, setSelNamHoc, selTo, onSelectTo } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  const onLoad = async () => {
    if (!selNamHoc) { message.warning('Chọn năm học'); return }
    setLoading(true)
    try {
      const q = `nam_hoc_id=${selNamHoc}${selTo ? `&to_id=${selTo}` : ''}`
      const r = await api.get(`/xep-hang/ca-nam?${q}`)
      setData(r.data)
    } catch { message.error('Lỗi tải dữ liệu') } finally { setLoading(false) }
  }

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}  // ⭐ Thêm value
              onChange={setSelNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={5}>
            <Select placeholder="Tổ (tùy chọn)" style={{ width: '100%' }}
              allowClear onChange={onSelectTo}
              options={dsTo.map(t => ({ value: t.id, label: t.ten_to }))} />
          </Col>
          <Col>
            <Button type="primary" onClick={onLoad} loading={loading}>🔍 Hiển thị</Button>
          </Col>
        </Row>
      </Card>
      <BangXepHang data={data} loading={loading} tieuDe={!!selNamHoc} />
    </div>
  )
}

// ════════════════════════════════════════════════════
//  TRANG CHÍNH
// ════════════════════════════════════════════════════
export default function ThiDuaGVPage() {
  const meta = useMeta()

  const tabs = [
    { key: 'tieu-chi', label: '⚙️ Tiêu chí', children: <TabTieuChi meta={meta} /> },
    { key: 'cham-diem', label: '📝 Chấm điểm', children: <TabChamDiem meta={meta} /> },
    { key: 'theo-thang', label: '📊 Theo tháng', children: <TabTheoThang meta={meta} /> },
    { key: 'hoc-ky', label: '📚 Học kỳ', children: <TabHocKy meta={meta} /> },
    { key: 'ca-nam', label: '🎯 Cả năm', children: <TabCaNam meta={meta} /> },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>🏆 Thi Đua Giáo Viên</Title>
      <Tabs items={tabs} type="card" />
      <style>{`
        .row-gold  td { background: #FFFDE7 !important; }
        .row-silver td { background: #FAFAFA !important; }
        .row-bronze td { background: #FFF8F0 !important; }
      `}</style>
    </div>
  )
}