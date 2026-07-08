// frontend/src/pages/Reports/components/FilterBar.jsx
import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Select, Button, Space } from 'antd'
import { SearchOutlined, FileExcelOutlined, PrinterOutlined, ReloadOutlined } from '@ant-design/icons'
import { thangAPI, hocKyAPI } from '../../ThiDuaHS/services/api'

const FilterBar = ({ 
  filters, 
  onFilterChange, 
  onGenerate, 
  onReset, 
  loading,
  dsNamHoc  // ⭐ Nhận dsNamHoc từ props
}) => {
  const [dsThang, setDsThang] = useState([])
  const [dsHocKy, setDsHocKy] = useState([])

  // Load tháng và học kỳ khi chọn năm học
  useEffect(() => {
    if (filters.nam_hoc_id) {
      thangAPI.get(filters.nam_hoc_id).then(r => setDsThang(r.data || [])).catch(() => {})
      hocKyAPI.get(filters.nam_hoc_id).then(r => setDsHocKy(r.data || [])).catch(() => {})
    }
  }, [filters.nam_hoc_id])

  const loaiOptions = [
    { value: 'tuan', label: '📅 Báo cáo tuần' },
    { value: 'thang', label: '📅 Báo cáo tháng' },
    { value: 'hoc_ky', label: '📚 Báo cáo học kỳ' },
    { value: 'nam_hoc', label: '📊 Báo cáo năm học' },
    { value: 'ca_nhan', label: '👤 Vi phạm cá nhân' },
    { value: 'giao_vien', label: '👨‍🏫 Báo cáo GVCN' },
  ]

  const khoiOptions = [
    { value: 6, label: 'Khối 6' },
    { value: 7, label: 'Khối 7' },
    { value: 8, label: 'Khối 8' },
    { value: 9, label: 'Khối 9' },
    { value: 10, label: 'Khối 10' },
    { value: 11, label: 'Khối 11' },
    { value: 12, label: 'Khối 12' },
  ]

  return (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Row gutter={12} align="middle" wrap>
        <Col xs={24} sm={12} md={4}>
          <Select
            placeholder="Loại báo cáo"
            style={{ width: '100%' }}
            value={filters.loai}
            onChange={(v) => onFilterChange('loai', v)}
            options={loaiOptions}
          />
        </Col>
        
        <Col xs={24} sm={12} md={3}>
          <Select
            placeholder="Năm học"
            style={{ width: '100%' }}
            value={filters.nam_hoc_id}
            onChange={(v) => onFilterChange('nam_hoc_id', v)}
            options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            allowClear
          />
        </Col>
        
        {filters.loai === 'tuan' && (
          <Col xs={24} sm={12} md={3}>
            <Select
              placeholder="Tuần"
              style={{ width: '100%' }}
              value={filters.tuan}
              onChange={(v) => onFilterChange('tuan', v)}
              options={Array.from({ length: 35 }, (_, i) => ({ value: i + 1, label: `Tuần ${i + 1}` }))}
              allowClear
            />
          </Col>
        )}
        
        {filters.loai === 'thang' && (
          <Col xs={24} sm={12} md={3}>
            <Select
              placeholder="Tháng"
              style={{ width: '100%' }}
              value={filters.thang_id}
              onChange={(v) => onFilterChange('thang_id', v)}
              options={dsThang.map(t => ({ value: t.id, label: t.ten_thang }))}
              allowClear
            />
          </Col>
        )}
        
        {filters.loai === 'hoc_ky' && (
          <Col xs={24} sm={12} md={3}>
            <Select
              placeholder="Học kỳ"
              style={{ width: '100%' }}
              value={filters.hoc_ky_id}
              onChange={(v) => onFilterChange('hoc_ky_id', v)}
              options={dsHocKy.map(h => ({ value: h.id, label: h.ten_hoc_ky }))}
              allowClear
            />
          </Col>
        )}
        
        {(filters.loai === 'ca_nhan' || filters.loai === 'giao_vien') && (
          <Col xs={24} sm={12} md={3}>
            <Select
              placeholder="Khối"
              style={{ width: '100%' }}
              value={filters.khoi}
              onChange={(v) => onFilterChange('khoi', v)}
              options={khoiOptions}
              allowClear
            />
          </Col>
        )}
        
        <Col>
          <Space size={4}>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={() => onGenerate()}
              loading={loading}
            >
              Xem báo cáo
            </Button>
            <Button
              icon={<FileExcelOutlined />}
              style={{ color: '#52c41a', borderColor: '#52c41a' }}
              disabled={!filters}
            >
              Excel
            </Button>
            <Button icon={<PrinterOutlined />}>
              In
            </Button>
            <Button icon={<ReloadOutlined />} onClick={onReset}>
              Làm mới
            </Button>
          </Space>
        </Col>
      </Row>
    </Card>
  )
}

export default FilterBar