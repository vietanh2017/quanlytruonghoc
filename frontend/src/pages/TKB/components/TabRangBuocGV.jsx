// frontend/src/pages/TKB/components/TabRangBuocGV.jsx
import React, { useState, useEffect } from 'react'
import {
  Card, Select, Table, Checkbox, InputNumber,
  Button, message, Typography, Row, Col, Tag, Tooltip
} from 'antd'
import { SaveOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { tkbAPI } from '../services/api'

const { Text } = Typography

const THU_OPTIONS = [
  { label: 'Thứ 2', value: 2 },
  { label: 'Thứ 3', value: 3 },
  { label: 'Thứ 4', value: 4 },
  { label: 'Thứ 5', value: 5 },
  { label: 'Thứ 6', value: 6 },
  { label: 'Thứ 7', value: 7 },
]

export default function TabRangBuocGV({ meta }) {
  const { dsNamHoc, selNamHoc, setSelNamHoc } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    if (!selNamHoc) return
    setLoading(true)
    try {
      const r = await tkbAPI.getRangBuocGV(selNamHoc)
      setData(r.data || [])
    } catch (err) {
      message.error('Không tải được dữ liệu')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [selNamHoc])

  const handleChange = (giao_vien_id, field, value) => {
    setData(prev => prev.map(d =>
      d.giao_vien_id === giao_vien_id
        ? {
            ...d,
            [field]: value,
            ...(field === 'chi_buoi_sang' && value ? { chi_buoi_chieu: false } : {}),
            ...(field === 'chi_buoi_chieu' && value ? { chi_buoi_sang: false } : {}),
          }
        : d
    ))
  }

  const handleSave = async () => {
    if (!selNamHoc) return message.warning('Chọn năm học trước!')
    setSaving(true)
    try {
      await tkbAPI.saveRangBuocGV({
        nam_hoc_id: selNamHoc,
        items: data.map(d => ({
          giao_vien_id: d.giao_vien_id,
          chi_buoi_sang: d.chi_buoi_sang || false,
          chi_buoi_chieu: d.chi_buoi_chieu || false,
          so_tiet_toi_da_ngay: d.so_tiet_toi_da_ngay || 0,
          so_tiet_toi_thieu_ngay: d.so_tiet_toi_thieu_ngay || 0,
          gom_tiet: d.gom_tiet || false,
          so_ngay_nghi: d.ngay_nghi_list?.length || 0,
          ngay_nghi_list: d.ngay_nghi_list || [],
        }))
      })
      message.success('Lưu ràng buộc giáo viên thành công!')
    } catch (err) {
      message.error('Lưu thất bại: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: 'Giáo viên',
      dataIndex: 'ho_ten',
      width: 180,
      fixed: 'left',
      render: (v, r) => (
        <Text strong>
          {v} <Text type="secondary" style={{ fontSize: 11 }}>({r.ma_giao_vien})</Text>
        </Text>
      )
    },
    {
      title: (
        <Tooltip title="GV chỉ dạy buổi sáng">
          ☀️ Chỉ sáng <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'chi_buoi_sang',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.giao_vien_id, 'chi_buoi_sang', e.target.checked)}
        />
      )
    },
    {
      title: (
        <Tooltip title="GV chỉ dạy buổi chiều">
          🌙 Chỉ chiều <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'chi_buoi_chieu',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.giao_vien_id, 'chi_buoi_chieu', e.target.checked)}
        />
      )
    },
    {
      title: (
        <Tooltip title="Số tiết tối đa GV dạy trong 1 ngày. 0 = không giới hạn">
          Max tiết/ngày <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'so_tiet_toi_da_ngay',
      width: 110,
      align: 'center',
      render: (v, r) => (
        <InputNumber
          size="small"
          min={0} max={7}
          value={v || 0}
          style={{ width: 60 }}
          placeholder="0=∞"
          onChange={val => handleChange(r.giao_vien_id, 'so_tiet_toi_da_ngay', val || 0)}
        />
      )
    },
    {
      title: (
        <Tooltip title="GV ở xa: số tiết tối thiểu mỗi ngày đi dạy (để gom tiết)">
          Min tiết/ngày <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'so_tiet_toi_thieu_ngay',
      width: 110,
      align: 'center',
      render: (v, r) => (
        <InputNumber
          size="small"
          min={0} max={7}
          value={v || 0}
          style={{ width: 60 }}
          placeholder="0"
          onChange={val => handleChange(r.giao_vien_id, 'so_tiet_toi_thieu_ngay', val || 0)}
        />
      )
    },
    {
      title: (
        <Tooltip title="Ưu tiên gom tiết vào ít ngày (GV ở xa)">
          📦 Gom tiết <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'gom_tiet',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.giao_vien_id, 'gom_tiet', e.target.checked)}
        />
      )
    },
    {
      title: (
        <Tooltip title="Các ngày GV không thể dạy trong tuần">
          🚫 Ngày nghỉ <InfoCircleOutlined style={{ fontSize: 11 }} />
        </Tooltip>
      ),
      dataIndex: 'ngay_nghi_list',
      width: 220,
      render: (v, r) => (
        <Select
          mode="multiple"
          size="small"
          style={{ width: '100%' }}
          placeholder="Chọn ngày nghỉ..."
          value={v || []}
          options={THU_OPTIONS}
          onChange={val => handleChange(r.giao_vien_id, 'ngay_nghi_list', val)}
          maxTagCount={3}
        />
      )
    },
    {
      title: 'Tóm tắt',
      width: 180,
      render: (_, r) => {
        const tags = []
        if (r.chi_buoi_sang) tags.push(<Tag color="orange" key="s">☀️ Chỉ sáng</Tag>)
        if (r.chi_buoi_chieu) tags.push(<Tag color="blue" key="c">🌙 Chỉ chiều</Tag>)
        if (r.gom_tiet) tags.push(<Tag color="green" key="g">📦 Gom tiết</Tag>)
        if (r.ngay_nghi_list?.length > 0)
          tags.push(
            <Tag color="red" key="n">
              🚫 Nghỉ {r.ngay_nghi_list.map(t => `T${t}`).join(', ')}
            </Tag>
          )
        return tags.length > 0
          ? <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>{tags}</div>
          : <Text type="secondary" style={{ fontSize: 11 }}>Không giới hạn</Text>
      }
    },
  ]

  return (
    <Card
      title="👨‍🏫 Ràng buộc giáo viên"
      size="small"
      extra={
        <Row gutter={8} align="middle">
          <Col>
            <Select
              placeholder="Chọn năm học"
              value={selNamHoc}
              onChange={setSelNamHoc}
              style={{ width: 150 }}
              options={(dsNamHoc || []).map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
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
        rowKey="giao_vien_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={false}
        size="small"
        bordered
        scroll={{ x: 1100 }}
        locale={{ emptyText: 'Không có dữ liệu giáo viên' }}
      />
    </Card>
  )
}