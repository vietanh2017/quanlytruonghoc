// frontend/src/pages/CauHinh/CauHinhPage.jsx
import React, { useEffect, useState } from 'react'
import {
  Tabs, Table, Button, Space, Modal, Form, Input,
  InputNumber, Switch, message, Popconfirm, Tooltip,
  Typography, Tag, Select, Badge, Avatar, Card, Row, Col, Divider
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined, KeyOutlined,
  UserOutlined, CrownOutlined, UnorderedListOutlined, SettingOutlined
} from '@ant-design/icons'
import axios from 'axios'
import TabPhanQuyen from './components/TabPhanQuyen'
// ⭐ Thêm import API
import { monHocAPI, phanMonAPI, soTietAPI } from '../../api/cauHinh'

const { Title, Text } = Typography
const api = axios.create({ baseURL: 'http://localhost:8000/api/v1/cau-hinh' })
const apiGV = axios.create({ baseURL: 'http://localhost:8000/api/v1/giao-vien' })

// ── Hook chung cho mọi tab ────────────────────────────────────
function useCRUD(endpoint, baseApi = api) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const res = await baseApi.get(endpoint)
      setData(Array.isArray(res.data) ? res.data : (res.data.items || []))
    } catch { message.error('Không thể tải dữ liệu') }
    finally { setLoading(false) }
  }

  const create = async (body) => { await baseApi.post(endpoint, body); await load() }
  const update = async (id, body) => { await baseApi.put(`${endpoint}/${id}`, body); await load() }
  const remove = async (id) => { await baseApi.delete(`${endpoint}/${id}`); await load() }

  useEffect(() => { load() }, [])
  return { data, loading, load, create, update, remove }
}

// ── Component bảng đơn giản ──────────────────────────────────
function SimpleTable({ columns, data, loading, onAdd, onEdit, onDelete, addLabel, extraActions }) {
  const cols = [
    ...columns,
    {
      title: 'Thao tác', width: extraActions ? 140 : 100, align: 'center',
      render: (_, r) => (
        <Space size={4}>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => onEdit(r)} />
          </Tooltip>
          {extraActions && extraActions(r)}
          <Tooltip title="Xóa">
            <Popconfirm title="Xác nhận xóa?" onConfirm={() => onDelete(r.id)}
              okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={onAdd}>{addLabel}</Button>
      </div>
      <Table rowKey="id" columns={cols} dataSource={data} loading={loading}
        size="small" bordered pagination={{ pageSize: 10 }} />
    </div>
  )
}

// ════════════════════════════════════════════════════
//  TAB NĂM HỌC
// ════════════════════════════════════════════════════
function TabNamHoc() {
  const { data, loading, create, update, remove } = useCRUD('/nam-hoc')
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const onAdd = () => { setEdit(null); form.resetFields(); setOpen(true) }
  const onEdit = (r) => { setEdit(r); form.setFieldsValue(r); setOpen(true) }
  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await update(edit.id, v); else await create(v)
      setOpen(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const cols = [
    { title: 'Tên năm học', dataIndex: 'ten_nam_hoc' },
    {
      title: 'Trạng thái', dataIndex: 'active', width: 110,
      render: v => <Tag color={v ? 'green' : 'red'}>{v ? 'Hoạt động' : 'Vô hiệu'}</Tag>
    },
  ]

  return (
    <>
      <SimpleTable columns={cols} data={data} loading={loading}
        onAdd={onAdd} onEdit={onEdit} onDelete={remove} addLabel="Thêm năm học" />
      <Modal title={edit ? 'Sửa năm học' : 'Thêm năm học'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="ten_nam_hoc" label="Tên năm học"
            rules={[{ required: true, message: 'Nhập tên năm học' }]}>
            <Input placeholder="VD: 2024-2025" />
          </Form.Item>
          <Form.Item name="active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB HỌC KỲ
// ════════════════════════════════════════════════════
function TabHocKy() {
  const { data, loading, create, update, remove } = useCRUD('/hoc-ky')
  const { data: dsNamHoc } = useCRUD('/nam-hoc')
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const onAdd = () => { setEdit(null); form.resetFields(); setOpen(true) }
  const onEdit = (r) => { setEdit(r); form.setFieldsValue(r); setOpen(true) }
  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await update(edit.id, v); else await create(v)
      setOpen(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const namHocMap = Object.fromEntries(dsNamHoc.map(n => [n.id, n.ten_nam_hoc]))

  const cols = [
    {
      title: 'Năm học', dataIndex: 'nam_hoc_id', width: 180, align: 'center',
      render: v => <Tag color="blue">{namHocMap[v] || v}</Tag>
    },
    { title: 'Tên học kỳ', dataIndex: 'ten_hoc_ky', width: 180, align: 'center', },
    { title: 'Thứ tự', dataIndex: 'so_thu_tu', width: 80, align: 'center' },
    {
      title: 'Trạng thái', dataIndex: 'active', width: 110,
      render: v => <Tag color={v ? 'green' : 'red'}>{v ? 'Hoạt động' : 'Vô hiệu'}</Tag>
    },
  ]

  return (
    <>
      <SimpleTable columns={cols} data={data} loading={loading}
        onAdd={onAdd} onEdit={onEdit} onDelete={remove} addLabel="Thêm học kỳ" />
      <Modal title={edit ? 'Sửa học kỳ' : 'Thêm học kỳ'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="nam_hoc_id" label="Năm học"
            rules={[{ required: true, message: 'Chọn năm học' }]}>
            <Select placeholder="-- Chọn năm học --">
              {dsNamHoc.filter(n => n.active).map(n => (
                <Select.Option key={n.id} value={n.id}>{n.ten_nam_hoc}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="ten_hoc_ky" label="Tên học kỳ"
            rules={[{ required: true, message: 'Nhập tên học kỳ' }]}>
            <Input placeholder="VD: Học kỳ 1" />
          </Form.Item>
          <Form.Item name="so_thu_tu" label="Thứ tự"
            rules={[{ required: true, message: 'Nhập thứ tự' }]}>
            <InputNumber min={1} max={3} style={{ width: '100%' }} placeholder="1 hoặc 2" />
          </Form.Item>
          <Form.Item name="active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB TỔ CHUYÊN MÔN
// ════════════════════════════════════════════════════
function TabToChuyenMon() {
  const { data, loading, create, update, remove } = useCRUD('/to-chuyen-mon')
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const onAdd = () => { setEdit(null); form.resetFields(); setOpen(true) }
  const onEdit = (r) => { setEdit(r); form.setFieldsValue(r); setOpen(true) }
  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await update(edit.id, v); else await create(v)
      setOpen(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const cols = [
    { title: 'Mã tổ', dataIndex: 'ma_to', width: 100 },
    { title: 'Tên tổ', dataIndex: 'ten_to' },
    { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
    {
      title: 'Trạng thái', dataIndex: 'active', width: 110,
      render: v => <Tag color={v ? 'green' : 'red'}>{v ? 'Hoạt động' : 'Vô hiệu'}</Tag>
    },
  ]

  return (
    <>
      <SimpleTable columns={cols} data={data} loading={loading}
        onAdd={onAdd} onEdit={onEdit} onDelete={remove} addLabel="Thêm tổ" />
      <Modal title={edit ? 'Sửa tổ chuyên môn' : 'Thêm tổ chuyên môn'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="ma_to" label="Mã tổ" rules={[{ required: true }]}>
            <Input placeholder="VD: TOAN" />
          </Form.Item>
          <Form.Item name="ten_to" label="Tên tổ" rules={[{ required: true }]}>
            <Input placeholder="VD: Tổ Toán - Lý" />
          </Form.Item>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB MÔN HỌC (ĐÃ SỬA)
// ════════════════════════════════════════════════════
// frontend/src/pages/CauHinh/CauHinhPage.jsx
// Thay thế hoàn toàn TabMonHoc bằng code này

function TabMonHoc() {
  const { data, loading, create, update, remove, load } = useCRUD('/mon-hoc')
  const { data: dsTo } = useCRUD('/to-chuyen-mon')
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const [phanMonList, setPhanMonList] = useState([])
  const [khoiTietList, setKhoiTietList] = useState([])
  const [openPhanMonModal, setOpenPhanMonModal] = useState(false)
  const [openKhoiTietModal, setOpenKhoiTietModal] = useState(false)
  const [currentMonHocId, setCurrentMonHocId] = useState(null)
  const [currentMonHocData, setCurrentMonHocData] = useState(null)

  const KHOI_LIST = [6, 7, 8, 9]

  const tenTo = (to_id) => dsTo.find(t => t.id === to_id)?.ten_to || '—'

  const filterKhoiList = (list) => {
    if (!list) return []
    return list.filter(item => KHOI_LIST.includes(item.khoi))
  }

  const cols = [
    {
      title: 'Mã môn', dataIndex: 'ma_mon', width: 100,
      align: 'center',
      render: (v) => <Text strong>{v}</Text>
    },
    {
      title: 'Tên môn', dataIndex: 'ten_mon', align: 'center',
      render: (v) => <Text>{v}</Text>
    },
    {
      title: 'Tổ CM', dataIndex: 'to_id', width: 150, align: 'center',
      render: (v) => <Tag color="blue">{tenTo(v)}</Tag>
    },
    {
      title: 'Phân môn', dataIndex: 'phan_mon_list', width: 230, align: 'center',
      render: (list) => {
        if (!list || list.length === 0) return <Tag>—</Tag>
        return (
          <Space size={4} wrap>
            {list.map(pm => (
              <Tag key={pm.id} color="green" style={{ margin: 2 }}>
                {pm.ten_phan_mon}
              </Tag>
            ))}
          </Space>
        )
      }
    },
    {
      title: 'Số tiết theo khối', dataIndex: 'khoi_list', width: 240, align: 'center',
      render: (list) => {
        const filtered = filterKhoiList(list)
        if (!filtered || filtered.length === 0) return <Tag>—</Tag>
        return (
          <Space size={4} wrap>
            {filtered.map(k => (
              <Tag key={k.khoi} color="purple" style={{ margin: 2 }}>
                K{k.khoi}: {k.so_tiet}
              </Tag>
            ))}
          </Space>
        )
      }
    },
    {
      title: 'Thứ tự', dataIndex: 'thu_tu', width: 60, align: 'center'
    },
    {
      title: 'Trạng thái', dataIndex: 'active', width: 110, align: 'center',
      render: v => <Tag color={v ? 'green' : 'red'}>{v ? 'Hoạt động' : 'Vô hiệu'}</Tag>
    },
  ]

  const onAdd = () => {
    setEdit(null)
    form.resetFields()
    form.setFieldsValue({ co_phan_mon: false, thu_tu: 0, active: true })
    setPhanMonList([])
    setKhoiTietList(KHOI_LIST.map(k => ({ khoi: k, so_tiet: 0 })))
    setCurrentMonHocId(null)
    setCurrentMonHocData(null)
    setOpen(true)
  }

  const onEdit = (r) => {
    setEdit(r)
    setCurrentMonHocId(r.id)
    setCurrentMonHocData(r)
    form.setFieldsValue({
      ma_mon: r.ma_mon,
      ten_mon: r.ten_mon,
      to_id: r.to_id,
      co_phan_mon: r.co_phan_mon,
      thu_tu: r.thu_tu,
      active: r.active,
    })
    setPhanMonList(r.phan_mon_list || [])
    if (r.khoi_list && r.khoi_list.length > 0) {
      const filtered = r.khoi_list.filter(k => KHOI_LIST.includes(k.khoi))
      setKhoiTietList(filtered)
    } else {
      setKhoiTietList(KHOI_LIST.map(k => ({ khoi: k, so_tiet: 0 })))
    }
    setOpen(true)
  }

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) {
        await update(edit.id, v)
      } else {
        await create(v)
      }
      setOpen(false)
      message.success('Lưu thành công!')
      await load()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  // ⭐ Xử lý thêm phân môn
  const handleAddPhanMon = () => {
    const newPhanMon = {
      id: Date.now(),
      ma_phan_mon: '',
      ten_phan_mon: '',
      thu_tu: phanMonList.length + 1,
      active: true,
      isNew: true
    }
    setPhanMonList([...phanMonList, newPhanMon])
  }

  const handleRemovePhanMon = (index) => {
    const newList = phanMonList.filter((_, i) => i !== index)
    setPhanMonList(newList)
  }

  const handleUpdatePhanMon = (index, field, value) => {
    const newList = [...phanMonList]
    newList[index][field] = value
    setPhanMonList(newList)
  }

  // ⭐ Lưu phân môn - DÙNG API TỪ cauHinh.js
  const handleSavePhanMon = async () => {
    try {
      const invalid = phanMonList.some(pm => !pm.ma_phan_mon.trim() || !pm.ten_phan_mon.trim())
      if (invalid) {
        message.warning('Vui lòng nhập đầy đủ mã và tên phân môn')
        return
      }

      if (!currentMonHocId) {
        message.info('Vui lòng lưu môn học trước khi thêm phân môn')
        return
      }

      // ⭐ Lấy danh sách phân môn hiện có
      const oldPhanMons = await phanMonAPI.getByMonHoc(currentMonHocId)

      // ⭐ Xóa TẤT CẢ phân môn cũ (chỉ gọi 1 lần)
      if (oldPhanMons.data && oldPhanMons.data.length > 0) {
        await phanMonAPI.deleteByMonHoc(currentMonHocId)
      }

      // ⭐ Thêm phân môn mới
      for (const pm of phanMonList) {
        if (pm.ma_phan_mon.trim() && pm.ten_phan_mon.trim()) {
          await phanMonAPI.create({
            ma_phan_mon: pm.ma_phan_mon.trim(),
            ten_phan_mon: pm.ten_phan_mon.trim(),
            mon_hoc_id: currentMonHocId,
            thu_tu: pm.thu_tu || 0,
            active: true
          })
        }
      }

      message.success('Lưu phân môn thành công!')
      setOpenPhanMonModal(false)
      await load()

      const updated = await monHocAPI.getById(currentMonHocId)
      setCurrentMonHocData(updated.data)

    } catch (err) {
      console.error('❌ Lỗi lưu phân môn:', err)
      message.error(err.response?.data?.detail || 'Lỗi lưu phân môn')
    }
  }

  // ⭐ Cập nhật số tiết theo khối
  const handleUpdateKhoiTiet = (khoi, value) => {
    const newList = khoiTietList.map(item =>
      item.khoi === khoi ? { ...item, so_tiet: parseInt(value) || 0 } : item
    )
    setKhoiTietList(newList)
  }

  // ⭐ Lưu số tiết theo khối - DÙNG API TỪ cauHinh.js
  const handleSaveKhoiTiet = async () => {
    try {
      if (!currentMonHocId) {
        message.info('Vui lòng lưu môn học trước khi cấu hình số tiết')
        return
      }

      // ⭐ Xóa số tiết cũ
      await soTietAPI.deleteByMonHoc(currentMonHocId)

      // ⭐ Thêm số tiết mới
      let count = 0
      for (const item of khoiTietList) {
        if (item.so_tiet > 0) {
          await soTietAPI.create({
            mon_hoc_id: currentMonHocId,
            khoi: item.khoi,
            so_tiet: item.so_tiet
          })
          count++
        }
      }

      message.success(`Lưu số tiết thành công! (${count} khối)`)
      setOpenKhoiTietModal(false)
      await load()

      const updated = await monHocAPI.getById(currentMonHocId)
      setCurrentMonHocData(updated.data)

    } catch (err) {
      console.error('❌ Lỗi lưu số tiết:', err)
      message.error(err.response?.data?.detail || 'Lỗi lưu số tiết')
    }
  }

  // ⭐ Mở modal quản lý phân môn
  const handleOpenPhanMonModal = () => {
    if (!currentMonHocId && !edit) {
      message.warning('Vui lòng lưu môn học trước khi thêm phân môn')
      return
    }
    setOpenPhanMonModal(true)
  }

  // ⭐ Mở modal cấu hình số tiết
  const handleOpenKhoiTietModal = () => {
    if (!currentMonHocId && !edit) {
      message.warning('Vui lòng lưu môn học trước khi cấu hình số tiết')
      return
    }
    setOpenKhoiTietModal(true)
  }

  return (
    <>
      <SimpleTable
        columns={cols}
        data={data}
        loading={loading}
        onAdd={onAdd}
        onEdit={onEdit}
        onDelete={remove}
        addLabel="Thêm môn học"
      />

      {/* Modal thêm/sửa môn học */}
      <Modal
        title={edit ? '✏️ Sửa môn học' : '➕ Thêm môn học'}
        open={open}
        onOk={onSave}
        onCancel={() => setOpen(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={700}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8, marginBottom: 16 }}>
            <Title level={5}>Thông tin cơ bản</Title>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="ma_mon" label="Mã môn" rules={[{ required: true }]}>
                  <Input placeholder="VD: TOAN" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="ten_mon" label="Tên môn" rules={[{ required: true }]}>
                  <Input placeholder="VD: Toán" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="to_id" label="Tổ chuyên môn">
                  <Select allowClear placeholder="-- Chọn tổ --">
                    {dsTo.map(t => (
                      <Select.Option key={t.id} value={t.id}>{t.ten_to}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="thu_tu" label="Thứ tự hiển thị" initialValue={0}>
                  <InputNumber min={0} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="co_phan_mon" label="Có phân môn" valuePropName="checked" initialValue={false}>
              <Switch checkedChildren="Có" unCheckedChildren="Không" />
            </Form.Item>
            <Form.Item name="active" label="Trạng thái" valuePropName="checked" initialValue={true}>
              <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
            </Form.Item>
          </div>

          <Divider />
          <Row gutter={16}>
            <Col span={12}>
              <Button
                type="default"
                icon={<UnorderedListOutlined />}
                onClick={handleOpenPhanMonModal}
                style={{ width: '100%' }}
              >
                Quản lý phân môn
              </Button>
            </Col>
            <Col span={12}>
              <Button
                type="default"
                icon={<SettingOutlined />}
                onClick={handleOpenKhoiTietModal}
                style={{ width: '100%' }}
              >
                Cấu hình số tiết
              </Button>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Modal quản lý phân môn */}
      <Modal
        title="📋 Quản lý phân môn"
        open={openPhanMonModal}
        onOk={handleSavePhanMon}
        onCancel={() => setOpenPhanMonModal(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={700}
      >
        <div style={{ padding: '16px 0' }}>
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={handleAddPhanMon}
            style={{ marginBottom: 16 }}
          >
            Thêm phân môn
          </Button>
          {phanMonList.length === 0 ? (
            <Text type="secondary">Chưa có phân môn nào</Text>
          ) : (
            phanMonList.map((pm, index) => (
              <Row key={pm.id || index} gutter={8} style={{ marginBottom: 8 }}>
                <Col span={7}>
                  <Input
                    placeholder="Mã phân môn"
                    value={pm.ma_phan_mon}
                    onChange={(e) => handleUpdatePhanMon(index, 'ma_phan_mon', e.target.value)}
                  />
                </Col>
                <Col span={10}>
                  <Input
                    placeholder="Tên phân môn"
                    value={pm.ten_phan_mon}
                    onChange={(e) => handleUpdatePhanMon(index, 'ten_phan_mon', e.target.value)}
                  />
                </Col>
                <Col span={4}>
                  <InputNumber
                    placeholder="TT"
                    min={0}
                    value={pm.thu_tu}
                    onChange={(value) => handleUpdatePhanMon(index, 'thu_tu', value)}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={3}>
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemovePhanMon(index)}
                  />
                </Col>
              </Row>
            ))
          )}
        </div>
      </Modal>

      {/* Modal cấu hình số tiết theo khối */}
      <Modal
        title="📊 Cấu hình số tiết theo khối"
        open={openKhoiTietModal}
        onOk={handleSaveKhoiTiet}
        onCancel={() => setOpenKhoiTietModal(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={500}
      >
        <div style={{ padding: '16px 0' }}>
          <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
            Cấu hình số tiết cho từng khối (6,7,8,9)
          </Text>
          <Row gutter={[16, 8]}>
            {KHOI_LIST.map(khoi => {
              const item = khoiTietList.find(k => k.khoi === khoi) || { khoi, so_tiet: 0 }
              return (
                <Col key={khoi} span={12}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Text strong style={{ minWidth: 40 }}>K{khoi}:</Text>
                    <InputNumber
                      min={0}
                      max={10}
                      value={item.so_tiet}
                      onChange={(value) => handleUpdateKhoiTiet(khoi, value)}
                      style={{ width: 80 }}
                    />
                    <Text type="secondary" style={{ fontSize: 12 }}>tiết</Text>
                  </div>
                </Col>
              )
            })}
          </Row>
        </div>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB TIẾT HỌC
// ════════════════════════════════════════════════════
function TabTietHoc() {
  const { data, loading, create, update, remove } = useCRUD('/tiet-hoc')
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  const onAdd = () => { setEdit(null); form.resetFields(); setOpen(true) }
  const onEdit = (r) => { setEdit(r); form.setFieldsValue(r); setOpen(true) }
  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await update(edit.id, v); else await create(v)
      setOpen(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const cols = [
    { title: 'STT', dataIndex: 'so_thu_tu', width: 60, align: 'center', },
    { title: 'Tên tiết', dataIndex: 'ten_tiet', width: 180, align: 'center', },
    { title: 'Bắt đầu', dataIndex: 'thoi_gian_bat_dau', width: 100, align: 'center', render: v => v || '—' },
    { title: 'Kết thúc', dataIndex: 'thoi_gian_ket_thuc', width: 100, align: 'center', render: v => v || '—' },
  ]

  return (
    <>
      <SimpleTable columns={cols} data={data} loading={loading}
        onAdd={onAdd} onEdit={onEdit} onDelete={remove} addLabel="Thêm tiết" />
      <Modal title={edit ? 'Sửa tiết học' : 'Thêm tiết học'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="so_thu_tu" label="Số thứ tự" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="ten_tiet" label="Tên tiết" rules={[{ required: true }]}>
            <Input placeholder="VD: Tiết 1" />
          </Form.Item>
          <Form.Item name="thoi_gian_bat_dau" label="Giờ bắt đầu">
            <Input placeholder="VD: 07:00" />
          </Form.Item>
          <Form.Item name="thoi_gian_ket_thuc" label="Giờ kết thúc">
            <Input placeholder="VD: 07:45" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TAB TÀI KHOẢN
// ════════════════════════════════════════════════════

const ROLE_CONFIG = {
  ADMIN: { label: 'Admin', color: 'red', icon: <CrownOutlined /> },
  TO_TRUONG: { label: 'Tổ trưởng', color: 'orange', icon: <UserOutlined /> },
  PHO_TO_TRUONG: { label: 'Phó tổ trưởng', color: 'gold', icon: <UserOutlined /> },
  TONG_PHU_TRACH: { label: 'Tổng phụ trách', color: 'purple', icon: <UserOutlined /> },
  GIAO_VIEN: { label: 'Giáo viên', color: 'blue', icon: <UserOutlined /> },
  NHAN_VIEN: { label: 'Nhân viên', color: 'cyan', icon: <UserOutlined /> },
}

function RoleTag({ role }) {
  const cfg = ROLE_CONFIG[role] || { label: role, color: 'default' }
  return <Tag color={cfg.color}>{cfg.label}</Tag>
}

function TabTaiKhoan() {
  const { data, loading, create, update, remove } = useCRUD('/tai-khoan')
  const { data: dsGiaoVien } = useCRUD('/', apiGV)

  const [open, setOpen] = useState(false)
  const [openReset, setOpenReset] = useState(false)
  const [edit, setEdit] = useState(null)
  const [resetId, setResetId] = useState(null)
  const [matKhauMoi, setMatKhauMoi] = useState('eduschool@123')
  const [form] = Form.useForm()

  const onSelectGV = (gvId) => {
    const gv = dsGiaoVien.find(g => g.id === gvId)
    if (gv) form.setFieldsValue({ email: gv.email, ho_ten: gv.ho_ten })
  }

  const onAdd = () => {
    setEdit(null)
    form.resetFields()
    setOpen(true)
  }

  const onEdit = (r) => {
    setEdit(r)
    form.setFieldsValue({ ho_ten: r.ho_ten, email: r.email, role: r.role, active: r.active })
    setOpen(true)
  }

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      const { gv_id, ...body } = v
      if (edit) await update(edit.id, body)
      else await create(body)
      setOpen(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const onResetMatKhau = async () => {
    try {
      await api.patch(`/tai-khoan/${resetId}/mat-khau`, { mat_khau_moi: matKhauMoi })
      message.success('Đặt lại mật khẩu thành công')
      setOpenReset(false)
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const cols = [
    {
      title: 'Họ tên', dataIndex: 'ho_ten',
      render: (v, r) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />}
            style={{ backgroundColor: ROLE_CONFIG[r.role]?.color === 'red' ? '#ff4d4f' : '#1677ff' }} />
          <Text strong={r.role === 'ADMIN'}>{v}</Text>
        </Space>
      )
    },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Vai trò', dataIndex: 'role', width: 140, align: 'center', render: v => <RoleTag role={v} /> },
    {
      title: 'Trạng thái', dataIndex: 'active', width: 110, align: 'center',
      render: v => <Badge status={v ? 'success' : 'error'} text={v ? 'Hoạt động' : 'Vô hiệu'} />
    },
  ]

  const extraActions = (r) => (
    <Tooltip title="Đặt lại mật khẩu">
      <Button size="small" icon={<KeyOutlined />}
        onClick={() => { setResetId(r.id); setMatKhauMoi('eduschool@123'); setOpenReset(true) }} />
    </Tooltip>
  )

  return (
    <>
      <SimpleTable columns={cols} data={data} loading={loading}
        onAdd={onAdd} onEdit={onEdit} onDelete={remove}
        addLabel="Thêm tài khoản" extraActions={extraActions} />

      <Modal title={edit ? 'Sửa tài khoản' : 'Thêm tài khoản'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          {!edit && (
            <Form.Item name="gv_id" label="Chọn giáo viên">
              <Select
                showSearch allowClear
                placeholder="-- Tìm và chọn giáo viên --"
                optionFilterProp="label"
                onChange={onSelectGV}
                options={dsGiaoVien.map(g => ({
                  value: g.id,
                  label: `${g.ho_ten} — ${g.email}`,
                }))}
              />
            </Form.Item>
          )}
          <Form.Item name="ho_ten" label="Họ tên" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="Email"
            rules={[{ required: true }, { type: 'email', message: 'Email không hợp lệ' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="Vai trò" rules={[{ required: true }]}>
            <Select placeholder="-- Chọn vai trò --">
              {Object.entries(ROLE_CONFIG).map(([val, cfg]) => (
                <Select.Option key={val} value={val}>
                  <Tag color={cfg.color}>{cfg.label}</Tag>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          {!edit && (
            <Form.Item name="mat_khau" label="Mật khẩu khởi tạo" initialValue="eduschool@123">
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Đặt lại mật khẩu" open={openReset}
        onOk={onResetMatKhau} onCancel={() => setOpenReset(false)}
        okText="Xác nhận" cancelText="Hủy" okButtonProps={{ danger: true }}>
        <div style={{ marginTop: 16 }}>
          <Text>Mật khẩu mới:</Text>
          <Input.Password
            style={{ marginTop: 8 }}
            value={matKhauMoi}
            onChange={e => setMatKhauMoi(e.target.value)}
          />
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 6 }}>
            Để trống sẽ dùng mật khẩu mặc định: <code>eduschool@123</code>
          </Text>
        </div>
      </Modal>
    </>
  )
}

// ════════════════════════════════════════════════════
//  TRANG CHÍNH
// ════════════════════════════════════════════════════
export default function CauHinhPage() {
  const tabs = [
    { key: 'nam-hoc', label: '📅 Năm học', children: <TabNamHoc /> },
    { key: 'hoc-ky', label: '🗓 Học kỳ', children: <TabHocKy /> },
    { key: 'to-chuyen-mon', label: '👥 Tổ chuyên môn', children: <TabToChuyenMon /> },
    { key: 'mon-hoc', label: '📚 Môn học', children: <TabMonHoc /> },
    { key: 'tiet-hoc', label: '⏰ Tiết học', children: <TabTietHoc /> },
    { key: 'tai-khoan', label: '🔐 Tài khoản', children: <TabTaiKhoan /> },
    { key: 'phan-quyen', label: '🛡 Phân quyền', children: <TabPhanQuyen /> },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>⚙️ Cấu Hình Hệ Thống</Title>
      <Tabs items={tabs} type="card" />
    </div>
  )
}