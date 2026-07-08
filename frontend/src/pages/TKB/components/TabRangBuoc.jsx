// frontend/src/pages/TKB/components/TabRangBuoc.jsx
import React, { useState, useEffect } from 'react'
import {
  Card, Select, Table, Checkbox, InputNumber,
  Button, message, Typography, Row, Col, Tag, Tooltip
} from 'antd'
import { SaveOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { tkbAPI } from '../services/api'

const { Text } = Typography

export default function TabRangBuoc({ meta }) {
  const { dsNamHoc, selNamHoc, setSelNamHoc } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    if (!selNamHoc) return
    setLoading(true)
    try {
      const r = await tkbAPI.getCauHinhMon(selNamHoc)
      setData(r.data || [])
    } catch (err) {
      message.error('Không tải được dữ liệu: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [selNamHoc])

  const handleChange = (mon_hoc_id, field, value) => {
    console.log('handleChange:', mon_hoc_id, field, value)  // 👈 thêm dòng này
    setData(prev => prev.map(d =>
      d.mon_hoc_id === mon_hoc_id
        ? {
          ...d,
          [field]: value,
          // Nếu bật chỉ sáng thì tắt chỉ chiều và ngược lại
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
      await tkbAPI.saveCauHinhMon({
        nam_hoc_id: selNamHoc,
        items: data.map(d => ({
          mon_hoc_id: d.mon_hoc_id,
          chi_buoi_sang: d.chi_buoi_sang || false,
          chi_buoi_chieu: d.chi_buoi_chieu || false,
          khong_lien_tiet: d.khong_lien_tiet || false,
          so_tiet_toi_da_ngay: d.so_tiet_toi_da_ngay || 0,
          cho_phep_tiet_doi: d.cho_phep_tiet_doi || false,  // ✅ thêm
        }))
      })
      message.success('Lưu ràng buộc thành công!')
    } catch (err) {
      message.error('Lưu thất bại: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: 'Môn học',
      dataIndex: 'ten_mon',
      width: 150,
      fixed: 'left',
      render: (v, r) => (
        <Text strong>
          {v}{' '}
          <Text type="secondary" style={{ fontSize: 11 }}>({r.ma_mon})</Text>
        </Text>
      )
    },
    {
      title: 'Số tiết/tuần theo khối',
      width: 250,
      render: (_, r) => {
        const map = r.so_tiet_theo_khoi || {}
        const khois = Object.keys(map).sort((a, b) => a - b)
        if (khois.length === 0)
          return <Text type="secondary" style={{ fontSize: 11 }}>Chưa cấu hình</Text>
        return (
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {khois.map(k => (
              <Tag key={k} color="geekblue" style={{ fontSize: 11 }}>
                K{k}: <strong>{map[k]}</strong>t
              </Tag>
            ))}
          </div>
        )
      }
    },
    {
      title: (
        <Tooltip title="Môn này chỉ được xếp vào buổi sáng">
          <span>☀️ Chỉ sáng <InfoCircleOutlined style={{ fontSize: 11 }} /></span>
        </Tooltip>
      ),
      dataIndex: 'chi_buoi_sang',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.mon_hoc_id, 'chi_buoi_sang', e.target.checked)}
        />
      )
    },
    {
      title: (
        <Tooltip title="Môn này chỉ được xếp vào buổi chiều">
          <span>🌙 Chỉ chiều <InfoCircleOutlined style={{ fontSize: 11 }} /></span>
        </Tooltip>
      ),
      dataIndex: 'chi_buoi_chieu',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.mon_hoc_id, 'chi_buoi_chieu', e.target.checked)}
        />
      )
    },
    {
      title: (
        <Tooltip title="Môn này không được xếp 2 tiết liền nhau trong cùng 1 ngày">
          <span>⛔ Không liên tiết <InfoCircleOutlined style={{ fontSize: 11 }} /></span>
        </Tooltip>
      ),
      dataIndex: 'khong_lien_tiet',
      width: 120,
      align: 'center',
      render: (v, r) => (
        <Checkbox
          checked={!!v}
          onChange={e => handleChange(r.mon_hoc_id, 'khong_lien_tiet', e.target.checked)}
        />
      )
    },

    {
      title: (
        <Tooltip title="Số tiết tối đa môn này được xếp trong 1 ngày. 0 = không giới hạn">
          <span>📊 Tối đa/ngày <InfoCircleOutlined style={{ fontSize: 11 }} /></span>
        </Tooltip>
      ),
      dataIndex: 'so_tiet_toi_da_ngay',
      width: 110,
      align: 'center',
      render: (v, r) => (
        <InputNumber
          size="small"
          min={0}
          max={7}
          value={v || 0}
          style={{ width: 65 }}
          placeholder="0=∞"
          onChange={val => handleChange(r.mon_hoc_id, 'so_tiet_toi_da_ngay', val || 0)}
        />
      )
    },
    {
      title: 'Tóm tắt',
      render: (_, r) => {
        const tags = []
        if (r.chi_buoi_sang)
          tags.push(<Tag color="orange" key="s">☀️ Chỉ sáng</Tag>)
        if (r.chi_buoi_chieu)
          tags.push(<Tag color="blue" key="c">🌙 Chỉ chiều</Tag>)
        if (r.khong_lien_tiet)
          tags.push(<Tag color="red" key="l">⛔ Không liên tiết</Tag>)
        if (r.so_tiet_toi_da_ngay > 0)
          tags.push(<Tag color="purple" key="m">Max {r.so_tiet_toi_da_ngay}/ngày</Tag>)

        return tags.length > 0
          ? <>{tags}</>
          : <Text type="secondary" style={{ fontSize: 11 }}>Không giới hạn</Text>
      }
    },
  ]

  return (
    <Card
      title="📋 Ràng buộc môn học"
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
              Lưu ràng buộc
            </Button>
          </Col>
        </Row>
      }
    >
      <Table
        rowKey="mon_hoc_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={false}
        size="small"
        bordered
        scroll={{ x: 900 }}
        locale={{ emptyText: 'Không có dữ liệu môn học' }}
      />
    </Card>
  )
}