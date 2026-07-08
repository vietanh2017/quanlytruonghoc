// frontend/src/pages/TKB/components/TabCauHinhNgay.jsx
import React, { useState, useEffect } from 'react'
import { Card, Select, Table, Switch, Button, message, Typography, Row, Col, Tag } from 'antd'
import { SaveOutlined } from '@ant-design/icons'
import { tkbAPI } from '../services/api'

const { Text } = Typography

const THU_LIST = [
  { thu: 2, label: 'Thứ 2' },
  { thu: 3, label: 'Thứ 3' },
  { thu: 4, label: 'Thứ 4' },
  { thu: 5, label: 'Thứ 5' },
  { thu: 6, label: 'Thứ 6' },
  { thu: 7, label: 'Thứ 7' },
]

export default function TabCauHinhNgay({ meta }) {
  const { dsNamHoc, selNamHoc, setSelNamHoc } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const initData = () => THU_LIST.map(t => ({
    thu: t.thu,
    label: t.label,
    co_buoi_sang: true,
    co_buoi_chieu: false,
  }))

  const load = async () => {
    if (!selNamHoc) return
    setLoading(true)
    try {
      const r = await tkbAPI.getCauHinhNgay(selNamHoc)
      if (r.data && r.data.length > 0) {
        const merged = THU_LIST.map(t => {
          const existing = r.data.find(d => d.thu === t.thu)
          return existing
            ? { ...existing, label: t.label }
            : { thu: t.thu, label: t.label, co_buoi_sang: true, co_buoi_chieu: false }
        })
        setData(merged)
      } else {
        setData(initData())
      }
    } catch {
      setData(initData())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [selNamHoc])

  const handleChange = (thu, field, value) => {
    setData(prev => prev.map(d =>
      d.thu === thu ? { ...d, [field]: value } : d
    ))
  }

  const handleSave = async () => {
    if (!selNamHoc) return message.warning('Chọn năm học trước!')
    setSaving(true)
    try {
      await tkbAPI.saveCauHinhNgay({
        nam_hoc_id: selNamHoc,
        items: data.map(d => ({
          thu: d.thu,
          co_buoi_sang: d.co_buoi_sang,
          co_buoi_chieu: d.co_buoi_chieu,
        }))
      })
      message.success('Lưu cấu hình ngày thành công!')
    } catch (err) {
      message.error('Lưu thất bại: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: 'Ngày',
      dataIndex: 'label',
      width: 100,
      render: v => <Text strong>{v}</Text>
    },
    {
      title: 'Buổi sáng',
      dataIndex: 'co_buoi_sang',
      width: 120,
      align: 'center',
      render: (v, r) => (
        <Switch
          checked={v}
          onChange={val => handleChange(r.thu, 'co_buoi_sang', val)}
          checkedChildren="Có"
          unCheckedChildren="Không"
        />
      )
    },
    {
      title: 'Buổi chiều',
      dataIndex: 'co_buoi_chieu',
      width: 120,
      align: 'center',
      render: (v, r) => (
        <Switch
          checked={v}
          onChange={val => handleChange(r.thu, 'co_buoi_chieu', val)}
          checkedChildren="Có"
          unCheckedChildren="Không"
        />
      )
    },
    {
      title: 'Số tiết sáng',
      width: 110,
      align: 'center',
      render: (_, r) => {
        const so_tiet = r.co_buoi_sang ? (r.co_buoi_chieu ? 4 : 5) : 0
        return (
          <Tag color={so_tiet > 0 ? 'orange' : 'default'}>
            ☀️ {so_tiet} tiết
          </Tag>
        )
      }
    },
    {
      title: 'Số tiết chiều',
      width: 110,
      align: 'center',
      render: (_, r) => {
        const so_tiet = r.co_buoi_chieu ? 3 : 0
        return (
          <Tag color={so_tiet > 0 ? 'blue' : 'default'}>
            🌙 {so_tiet} tiết
          </Tag>
        )
      }
    },
    {
      title: 'Tổng tiết/ngày',
      width: 120,
      align: 'center',
      render: (_, r) => {
        const sang = r.co_buoi_sang ? (r.co_buoi_chieu ? 4 : 5) : 0
        const chieu = r.co_buoi_chieu ? 3 : 0
        const tong = sang + chieu
        return (
          <Tag color={tong === 7 ? 'green' : tong === 5 ? 'cyan' : 'default'}>
            <Text strong>Tổng: {tong} tiết</Text>
          </Tag>
        )
      }
    },
  ]

  return (
    <Card
      title="📅 Cấu hình ngày học trong tuần"
      size="small"
      extra={
        <Row gutter={8} align="middle">
          <Col>
            <Select
              placeholder="Chọn năm học"
              value={selNamHoc}
              onChange={setSelNamHoc}
              style={{ width: 150 }}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
            >
              Lưu
            </Button>
          </Col>
        </Row>
      }
    >
      <Table
        rowKey="thu"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={false}
        size="small"
        bordered
      />
    </Card>
  )
}