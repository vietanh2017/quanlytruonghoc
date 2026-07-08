// frontend/src/pages/ThiDuaHS/components/TabDanhMuc.jsx
import axios from 'axios'
import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Popconfirm, message, Tag, Typography, Select, Modal, Form, Input, InputNumber, Row, Col } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { loaiVpAPI, cauHinhAPI } from '../services/api'
const { Text } = Typography

export default function TabDanhMuc({ meta }) {
  const { setDsLoaiVP } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()
  const [soNgayTrongTuan, setSoNgayTrongTuan] = useState(() => {
    return parseInt(localStorage.getItem('soNgayTrongTuan')) || 6
  })

  const load = async () => {
    setLoading(true)
    try {
      console.log('🔍 Đang tải danh mục...')
      const r = await loaiVpAPI.getAll()
      console.log('✅ Dữ liệu nhận được:', r.data)
      setData(r.data || [])
      setDsLoaiVP(r.data || [])
    } catch (err) {
      console.error('❌ Lỗi load chi tiết:', err)
      console.error('❌ Response:', err.response)
      message.error('Không thể tải danh mục: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])
  const handleChangeSoNgay = async (value) => {
    setSoNgayTrongTuan(value)
    localStorage.setItem('soNgayTrongTuan', String(value))

    try {
      await cauHinhAPI.setSoNgay(value)  // ✅ Dùng API đã có axios
      message.success(`Đã cập nhật số ngày trong tuần: ${value} ngày`)
    } catch (err) {
      message.error('Lưu cấu hình thất bại: ' + (err.response?.data?.detail || err.message))
    }

    setTimeout(() => window.location.reload(), 500)
  }
  const onSave = async () => {
    try {
      const v = await form.validateFields()
      console.log('📤 Dữ liệu gửi lên:', v)

      const submitData = {
        ma_loi: v.ma_loi,
        ten_loi: v.ten_loi,
        loai: v.loai,
        doi_tuong: v.doi_tuong,
        loai_diem: v.loai_diem,
        so_diem: Math.abs(v.so_diem),
        nhom: v.nhom || '',
        mo_ta: v.mo_ta || '',
        thu_tu: v.thu_tu || 0,
      }

      let response
      if (edit) {
        console.log('🔄 Cập nhật ID:', edit.id)
        response = await loaiVpAPI.update(edit.id, submitData)
        message.success('Cập nhật thành công')
      } else {
        console.log('➕ Thêm mới')
        response = await loaiVpAPI.create(submitData)
        message.success('Thêm thành công')
      }
      console.log('✅ Response:', response.data)

      setOpen(false)
      form.resetFields()
      load()
      setOpen(false)
      load()  // ⭐ Tải lại danh sách, tự động sắp xếp theo thu_tu
    } catch (err) {
      console.error('❌ Lỗi lưu chi tiết:', err)
      console.error('❌ Response:', err.response)
      message.error(err.response?.data?.detail || 'Lỗi khi lưu')
    }
  }

  const onXoa = async (id) => {
    try {
      console.log('🗑️ Xóa ID:', id)
      await loaiVpAPI.delete(id)
      message.success('Đã xóa')
      load()
    } catch (err) {
      console.error('❌ Lỗi xóa chi tiết:', err)
      console.error('❌ Response:', err.response)
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  const columns = [
    { title: 'Mã', dataIndex: 'ma_loi', width: 80 },
    { title: 'Tên', dataIndex: 'ten_loi' },
    {
      title: 'Đối tượng',
      dataIndex: 'doi_tuong',
      width: 100,
      render: v => {
        if (v === 'ca_nhan') return <Tag color="blue">👤 Cá nhân</Tag>
        if (v === 'tap_the') return <Tag color="green">🏫 Tập thể</Tag>
        return <Tag>—</Tag>
      }
    },
    {
      title: 'Loại',
      dataIndex: 'loai',
      width: 100,
      render: v => <Tag color={v === 'vi_pham' ? 'red' : 'green'}>
        {v === 'vi_pham' ? '⚠ Vi phạm' : '⭐ Thành tích'}
      </Tag>
    },
    {
      title: 'Loại điểm',
      dataIndex: 'loai_diem',
      width: 100,
      render: v => <Tag color={v === 'cong' ? 'green' : 'red'}>
        {v === 'cong' ? '➕ Cộng' : '➖ Trừ'}
      </Tag>
    },
    {
      title: 'Điểm tối đa',
      dataIndex: 'so_diem',
      width: 100,
      align: 'center',
      render: v => <Text strong>{Math.abs(v)}</Text>
    },
    { title: 'Nhóm', dataIndex: 'nhom', width: 120, render: v => v || '—' },
    { title: 'Thứ tự', dataIndex: 'thu_tu', width: 70, align: 'center' },
    {
      title: 'Thao tác',
      width: 100,
      render: (_, r) => (
        <Space size={4}>
          <Button size="small" onClick={() => {
            setEdit(r)
            form.setFieldsValue({
              ...r,
              so_diem: Math.abs(r.so_diem),
              loai_diem: r.so_diem < 0 ? 'tru' : 'cong',
              doi_tuong: r.doi_tuong || 'tap_the',
            })
            setOpen(true)
          }}>Sửa</Button>
          <Popconfirm title="Xóa?" onConfirm={() => onXoa(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <>
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Text strong style={{ marginRight: 8 }}>📅 Số ngày trong tuần:</Text>
          <Select
            value={soNgayTrongTuan}
            onChange={handleChangeSoNgay}
            style={{ width: 120 }}
            options={[
              { value: 5, label: '5 ngày' },
              { value: 6, label: '6 ngày' },
            ]}
          />
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
            (Áp dụng cho tất cả lớp trong tuần)
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { setEdit(null); form.resetFields(); setOpen(true) }}>
          Thêm danh mục
        </Button>
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="small"
        bordered
        pagination={{ pageSize: 15 }}
      />

      <Modal
        title={edit ? 'Sửa danh mục' : 'Thêm danh mục'}
        open={open}
        onOk={onSave}
        onCancel={() => {
          setOpen(false)
          form.resetFields()
        }}
        okText="Lưu"
        cancelText="Hủy"
        width={700}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Row gutter={8}>
            <Col span={8}>
              <Form.Item name="ma_loi" label="Mã" rules={[{ required: true }]}>
                <Input placeholder="VP001" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="loai" label="Loại" rules={[{ required: true }]}>
                <Select options={[
                  { value: 'vi_pham', label: '⚠ Vi phạm' },
                  { value: 'thanh_tich', label: '⭐ Thành tích' },
                ]} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="doi_tuong" label="Đối tượng" rules={[{ required: true }]} initialValue="tap_the">
                <Select options={[
                  { value: 'ca_nhan', label: '👤 Cá nhân' },
                  { value: 'tap_the', label: '🏫 Tập thể' },
                ]} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="ten_loi" label="Tên" rules={[{ required: true }]}>
            <Input placeholder="VD: Đi học muộn" />
          </Form.Item>

          <Row gutter={8}>
            <Col span={8}>
              <Form.Item name="loai_diem" label="Loại điểm" rules={[{ required: true }]} initialValue="tru">
                <Select options={[
                  { value: 'cong', label: '➕ Cộng điểm' },
                  { value: 'tru', label: '➖ Trừ điểm' },
                ]} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="so_diem" label="Điểm tối đa" rules={[{ required: true }]}>
                <InputNumber min={0} max={20} step={0.5} style={{ width: '100%' }} placeholder="VD: 2" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="nhom" label="Nhóm">
                <Input placeholder="VD: Nề nếp" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={8}>
            <Col span={12}>
              <Form.Item name="thu_tu" label="Thứ tự" initialValue={0}>
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="mo_ta" label="Mô tả">
                <Input placeholder="Mô tả chi tiết..." />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </>
  )
}