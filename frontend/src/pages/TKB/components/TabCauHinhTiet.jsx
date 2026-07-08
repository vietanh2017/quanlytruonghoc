// frontend/src/pages/TKB/components/TabCauHinhTiet.jsx
import React, { useState, useEffect } from 'react'
import { Card, Table, Input, Button, message, Typography, Tag, Space } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import { tkbAPI } from '../services/api'

const { Text } = Typography

const DEFAULT_TIET = [
  { buoi: 'sang', tiet_so: 1, gio_bat_dau: '07:00', gio_ket_thuc: '07:45' },
  { buoi: 'sang', tiet_so: 2, gio_bat_dau: '07:50', gio_ket_thuc: '08:35' },
  { buoi: 'sang', tiet_so: 3, gio_bat_dau: '08:45', gio_ket_thuc: '09:30' },
  { buoi: 'sang', tiet_so: 4, gio_bat_dau: '09:40', gio_ket_thuc: '10:25' },
  { buoi: 'sang', tiet_so: 5, gio_bat_dau: '10:30', gio_ket_thuc: '11:15' },
  { buoi: 'chieu', tiet_so: 1, gio_bat_dau: '13:00', gio_ket_thuc: '13:45' },
  { buoi: 'chieu', tiet_so: 2, gio_bat_dau: '13:50', gio_ket_thuc: '14:35' },
  { buoi: 'chieu', tiet_so: 3, gio_bat_dau: '14:45', gio_ket_thuc: '15:30' },
]

export default function TabCauHinhTiet() {
  const [data, setData] = useState(DEFAULT_TIET)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await tkbAPI.getCauHinhTiet()
      if (r.data && r.data.length > 0) {
        setData(r.data)
      } else {
        setData(DEFAULT_TIET)
      }
    } catch {
      setData(DEFAULT_TIET)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleChange = (buoi, tiet_so, field, value) => {
    setData(prev => prev.map(d =>
      d.buoi === buoi && d.tiet_so === tiet_so
        ? { ...d, [field]: value }
        : d
    ))
  }

  const handleReset = () => {
    setData(DEFAULT_TIET)
    message.info('Đã khôi phục về mặc định')
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await tkbAPI.saveCauHinhTiet({ items: data })
      message.success('Lưu cấu hình tiết thành công!')
    } catch (err) {
      message.error('Lưu thất bại: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: 'Buổi',
      dataIndex: 'buoi',
      width: 100,
      render: v => (
        <Tag color={v === 'sang' ? 'orange' : 'blue'}>
          {v === 'sang' ? '☀️ Sáng' : '🌙 Chiều'}
        </Tag>
      )
    },
    {
      title: 'Tiết',
      dataIndex: 'tiet_so',
      width: 80,
      align: 'center',
      render: v => <Text strong>Tiết {v}</Text>
    },
    {
      title: 'Giờ bắt đầu',
      dataIndex: 'gio_bat_dau',
      width: 150,
      align: 'center',
      render: (v, r) => (
        <Input
          size="small"
          value={v}
          style={{ width: 90, textAlign: 'center' }}
          placeholder="07:00"
          onChange={e => handleChange(r.buoi, r.tiet_so, 'gio_bat_dau', e.target.value)}
        />
      )
    },
    {
      title: 'Giờ kết thúc',
      dataIndex: 'gio_ket_thuc',
      width: 150,
      align: 'center',
      render: (v, r) => (
        <Input
          size="small"
          value={v}
          style={{ width: 90, textAlign: 'center' }}
          placeholder="07:45"
          onChange={e => handleChange(r.buoi, r.tiet_so, 'gio_ket_thuc', e.target.value)}
        />
      )
    },
    {
      title: 'Thời lượng',
      width: 120,
      align: 'center',
      render: (_, r) => {
        if (!r.gio_bat_dau || !r.gio_ket_thuc) return '—'
        try {
          const [h1, m1] = r.gio_bat_dau.split(':').map(Number)
          const [h2, m2] = r.gio_ket_thuc.split(':').map(Number)
          const phut = (h2 * 60 + m2) - (h1 * 60 + m1)
          return <Tag color="green">{phut} phút</Tag>
        } catch {
          return '—'
        }
      }
    },
  ]

  return (
    <Card
      title="⏰ Cấu hình giờ học từng tiết"
      size="small"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            Mặc định
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            Lưu
          </Button>
        </Space>
      }
    >
      <Table
        rowKey={r => `${r.buoi}-${r.tiet_so}`}
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