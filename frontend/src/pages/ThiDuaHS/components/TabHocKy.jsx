// frontend/src/pages/ThiDuaHS/components/TabHocKy.jsx
import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Popconfirm, message, Tag, Badge, Modal, Form, Input, Select, Switch, Row, Col, Tooltip } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons'
import { hocKyAPI, thangAPI } from '../services/api'
import ModalBaoCaoHocKy from '../modals/ModalBaoCaoHocKy'

export default function TabHocKy({ meta, refreshKey }) {
  const { dsNamHoc } = meta
  const [data, setData] = useState([])
  const [dsThang, setDsThang] = useState([])
  const [loading, setLoading] = useState(false)
  const [openModal, setOpenModal] = useState(false)
  const [openBaoCao, setOpenBaoCao] = useState(false)
  const [editItem, setEditItem] = useState(null)
  const [baoCaoData, setBaoCaoData] = useState(null)
  const [filterNamHoc, setFilterNamHoc] = useState(null)
  const [form] = Form.useForm()

  const loadData = async () => {
    setLoading(true)
    try {
      const r = await hocKyAPI.get(filterNamHoc)
      setData(r.data || [])
    } catch (err) {
      message.error('Không thể tải dữ liệu')
    } finally {
      setLoading(false)
    }
  }

  const loadThang = async () => {
    try {
      const r = await thangAPI.get(filterNamHoc)
      setDsThang(r.data || [])
    } catch (err) {
      console.error('Lỗi load tháng:', err)
    }
  }

  useEffect(() => {
    loadData()
    loadThang()
  }, [filterNamHoc, refreshKey])

  // ⭐ Hàm cập nhật điểm học kỳ
  const capNhatDiemHocKy = async (id) => {
    try {
      console.log('🔄 Cập nhật điểm học kỳ ID:', id)
      await hocKyAPI.capNhatDiem(id)
      message.success('Đã cập nhật lại điểm học kỳ')
      loadData()
    } catch (err) {
      console.error('❌ Lỗi cập nhật điểm học kỳ:', err)
      message.error(err.response?.data?.detail || 'Cập nhật thất bại')
    }
  }

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      const dataSubmit = {
        ...v,
        thang_list: v.thang_list || [],
      }
      if (editItem) {
        await hocKyAPI.update(editItem.id, dataSubmit)
        message.success('Cập nhật thành công')
      } else {
        await hocKyAPI.create(dataSubmit)
        message.success('Thêm thành công')
      }
      setOpenModal(false)
      loadData()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  const onXoa = async (id) => {
    await hocKyAPI.delete(id)
    message.success('Đã xóa')
    loadData()
  }

  const xemBaoCao = async (id) => {
    try {
      console.log('🔍 Đang tải báo cáo học kỳ ID:', id)
      const r = await hocKyAPI.baoCao(id)
      console.log('✅ Dữ liệu báo cáo học kỳ:', r.data)
      setBaoCaoData(r.data)
      setOpenBaoCao(true)
    } catch (err) {
      console.error('❌ Lỗi tải báo cáo học kỳ:', err)
      message.error(err.response?.data?.detail || 'Không thể tải báo cáo')
    }
  }

  const columns = [
    { title: 'STT', key: 'stt', width: 50, render: (_, __, i) => i + 1 },
    { title: 'Tên học kỳ', dataIndex: 'ten_hoc_ky' },
    {
      title: 'Năm học',
      dataIndex: 'ten_nam_hoc',
      render: v => <Tag color="blue">{v}</Tag>
    },
    {
      title: 'Tháng áp dụng',
      dataIndex: 'thang_list',
      render: list => (
        <Space size={4} wrap>
          {list?.map(t => {
            const thang = dsThang.find(th => th.id === t)
            return <Tag key={t} color="purple">{thang?.ten_thang || `Tháng ${t}`}</Tag>
          })}
        </Space>
      )
    },
    {
      title: 'Số tháng',
      dataIndex: 'so_thang',
      align: 'center',
      render: v => <Tag color="green">{v}</Tag>
    },
    {
      title: 'Trạng thái',
      dataIndex: 'is_active',
      render: v => <Tag color={v ? 'green' : 'red'}>{v ? 'Đang áp dụng' : 'Đã kết thúc'}</Tag>
    },
    {
      title: 'Thao tác',
      width: 200,  // ⭐ Tăng width để chứa nút
      render: (_, r) => (
        <Space size={4}>
          <Tooltip title="Cập nhật lại điểm học kỳ">
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => capNhatDiemHocKy(r.id)}
            />
          </Tooltip>
          <Tooltip title="Xem báo cáo">
            <Button size="small" icon={<EyeOutlined />} onClick={() => xemBaoCao(r.id)} />
          </Tooltip>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => {
              setEditItem(r)
              form.setFieldsValue({
                ten_hoc_ky: r.ten_hoc_ky,
                nam_hoc_id: r.nam_hoc_id,
                thang_list: r.thang_list,
                is_active: r.is_active,
              })
              setOpenModal(true)
            }} />
          </Tooltip>
          <Popconfirm title="Xóa học kỳ này?" onConfirm={() => onXoa(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Lọc theo năm học"
              style={{ width: '100%' }}
              allowClear
              value={filterNamHoc}
              onChange={setFilterNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => {
              setEditItem(null)
              form.resetFields()
              form.setFieldsValue({ is_active: true })
              setOpenModal(true)
            }}>
              Tạo học kỳ mới
            </Button>
          </Col>
          <Col>
            <Badge count={data.length} showZero>
              <span style={{ marginLeft: 8 }}>Tổng số học kỳ</span>
            </Badge>
          </Col>
        </Row>
      </Card>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="small"
        bordered
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editItem ? '✏️ Sửa học kỳ' : '➕ Thêm học kỳ mới'}
        open={openModal}
        onOk={onSave}
        onCancel={() => setOpenModal(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={600}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="ten_hoc_ky" label="Tên học kỳ" rules={[{ required: true }]}>
            <Input placeholder="VD: Học kỳ I, Học kỳ II..." />
          </Form.Item>
          <Form.Item name="nam_hoc_id" label="Năm học" rules={[{ required: true }]}>
            <Select options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))} />
          </Form.Item>
          <Form.Item name="thang_list" label="Chọn tháng" rules={[{ required: true }]}>
            <Select
              mode="multiple"
              placeholder="Chọn các tháng"
              style={{ width: '100%' }}
              options={dsThang.map(t => ({ value: t.id, label: t.ten_thang }))}
            />
          </Form.Item>
          <Form.Item name="is_active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Đang áp dụng" unCheckedChildren="Đã kết thúc" />
          </Form.Item>
        </Form>
      </Modal>

      <ModalBaoCaoHocKy
        open={openBaoCao}
        onClose={() => setOpenBaoCao(false)}
        data={baoCaoData}
      />
    </div>
  )
}