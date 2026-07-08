// frontend/src/pages/ThiDuaHS/components/TabThang.jsx
import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Popconfirm, message, Tag, Badge, Modal, Form, Input, Select, Switch, Row, Col, Tooltip } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons'  // ⭐ Thêm ReloadOutlined
import { thangAPI } from '../services/api'
import { TUAN_OPTIONS } from '../utils/constants'
import ModalBaoCaoThang from '../modals/ModalBaoCaoThang'

export default function TabThang({ meta, refreshKey }) {
  const { dsNamHoc } = meta
  const [data, setData] = useState([])
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
      console.log('🔄 Load dữ liệu tháng, refreshKey:', refreshKey)
      const r = await thangAPI.get(filterNamHoc)
      setData(r.data || [])
    } catch (err) {
      console.error('❌ Lỗi load dữ liệu tháng:', err)
      message.error('Không thể tải dữ liệu')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [filterNamHoc, refreshKey])

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      const dataSubmit = {
        ...v,
        tuan_list: v.tuan_list || [],
      }
      if (editItem) {
        await thangAPI.update(editItem.id, dataSubmit)
        message.success('Cập nhật thành công')
      } else {
        await thangAPI.create(dataSubmit)
        message.success('Thêm thành công')
      }
      setOpenModal(false)
      loadData()
    } catch (err) {
      console.error('❌ Lỗi lưu tháng:', err)
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  const onXoa = async (id) => {
    try {
      await thangAPI.delete(id)
      message.success('Đã xóa')
      loadData()
    } catch (err) {
      console.error('❌ Lỗi xóa tháng:', err)
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  const xemBaoCao = async (id) => {
    try {
      console.log('🔍 Đang tải báo cáo tháng ID:', id)
      const r = await thangAPI.baoCao(id)
      console.log('✅ Dữ liệu báo cáo:', r.data)
      setBaoCaoData(r.data)
      setOpenBaoCao(true)
    } catch (err) {
      console.error('❌ Lỗi tải báo cáo:', err)
      message.error(err.response?.data?.detail || 'Không thể tải báo cáo')
    }
  }

  // ⭐ Hàm cập nhật lại điểm tháng
  const capNhatDiemThang = async (thangId) => {
    try {
      console.log('🔄 Cập nhật điểm tháng ID:', thangId)
      // Gọi API cập nhật điểm (cần thêm trong service)
      await thangAPI.capNhatDiem(thangId)
      message.success('Đã cập nhật lại điểm tháng')
      loadData()
    } catch (err) {
      console.error('❌ Lỗi cập nhật điểm tháng:', err)
      message.error(err.response?.data?.detail || 'Cập nhật thất bại')
    }
  }

  const columns = [
    { title: 'STT', key: 'stt', width: 50, render: (_, __, i) => i + 1 },
    { title: 'Tên tháng', dataIndex: 'ten_thang' },
    {
      title: 'Năm học',
      dataIndex: 'ten_nam_hoc',
      render: v => <Tag color="blue">{v}</Tag>
    },
    {
      title: 'Tuần áp dụng',
      dataIndex: 'tuan_list',
      render: list => (
        <Space size={4} wrap>
          {list?.map(t => <Tag key={t} color="purple">{`Tuần ${t}`}</Tag>)}
        </Space>
      )
    },
    {
      title: 'Số tuần',
      dataIndex: 'so_tuan',
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
          <Tooltip title="Cập nhật lại điểm tháng">
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => capNhatDiemThang(r.id)}
            />
          </Tooltip>
          <Tooltip title="Xem báo cáo">
            <Button size="small" icon={<EyeOutlined />} onClick={() => xemBaoCao(r.id)} />
          </Tooltip>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => {
              setEditItem(r)
              form.setFieldsValue({
                ten_thang: r.ten_thang,
                nam_hoc_id: r.nam_hoc_id,
                tuan_list: r.tuan_list,
                is_active: r.is_active,
              })
              setOpenModal(true)
            }} />
          </Tooltip>
          <Popconfirm title="Xóa tháng này?" onConfirm={() => onXoa(r.id)}>
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
              Tạo tháng mới
            </Button>
          </Col>
          <Col>
            <Badge count={data.length} showZero>
              <span style={{ marginLeft: 8 }}>Tổng số tháng</span>
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
        title={editItem ? '✏️ Sửa tháng thi đua' : '➕ Thêm tháng thi đua'}
        open={openModal}
        onOk={onSave}
        onCancel={() => setOpenModal(false)}
        okText="Lưu"
        cancelText="Hủy"
        width={600}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="ten_thang" label="Tên tháng" rules={[{ required: true }]}>
            <Input placeholder="VD: Tháng 9, Chào mừng 20/11..." />
          </Form.Item>
          <Form.Item name="nam_hoc_id" label="Năm học" rules={[{ required: true }]}>
            <Select options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))} />
          </Form.Item>
          <Form.Item name="tuan_list" label="Tuần áp dụng" rules={[{ required: true }]}>
            <Select
              mode="multiple"
              placeholder="Chọn các tuần"
              options={TUAN_OPTIONS}
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item name="is_active" label="Trạng thái" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren="Đang áp dụng" unCheckedChildren="Đã kết thúc" />
          </Form.Item>
        </Form>
      </Modal>

      <ModalBaoCaoThang
        open={openBaoCao}
        onClose={() => setOpenBaoCao(false)}
        data={baoCaoData}
      />
    </div>
  )
}