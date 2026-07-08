// frontend/src/pages/ThiDuaHS/components/TabNamHoc.jsx
import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Space, message, Tag, Badge, Select, Row, Col, Tooltip } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { hocKyAPI, namHocAPI } from '../services/api'
import ModalBaoCaoNamHoc from '../modals/ModalBaoCaoNamHoc'

export default function TabNamHoc({ meta }) {
  const { dsNamHoc = [] } = meta || {}  // ⭐ Thêm giá trị mặc định
  const [dsHocKy, setDsHocKy] = useState([])
  const [selectedHocKy, setSelectedHocKy] = useState([])
  const [loading, setLoading] = useState(false)
  const [baoCaoData, setBaoCaoData] = useState(null)
  const [openBaoCao, setOpenBaoCao] = useState(false)
  const [filterNamHoc, setFilterNamHoc] = useState(null)

  // Load danh sách học kỳ
  const loadHocKy = async () => {
    setLoading(true)
    try {
      console.log('🔄 Load học kỳ với filter:', filterNamHoc)
      const r = await hocKyAPI.get(filterNamHoc)
      console.log('✅ Dữ liệu học kỳ:', r.data)
      setDsHocKy(r.data || [])
    } catch (err) {
      console.error('❌ Lỗi load học kỳ:', err)
      message.error('Không thể tải danh sách học kỳ')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHocKy()
  }, [filterNamHoc])

  // Xem báo cáo năm học
  const xemBaoCao = async () => {
    if (!selectedHocKy || selectedHocKy.length === 0) {
      message.warning('Vui lòng chọn ít nhất một học kỳ!')
      return
    }

    try {
      setLoading(true)
      console.log('🔍 Gọi API báo cáo năm học với học kỳ:', selectedHocKy)
      const r = await namHocAPI.baoCao({ hoc_ky_list: selectedHocKy })
      console.log('✅ Dữ liệu báo cáo:', r.data)
      setBaoCaoData(r.data)
      setOpenBaoCao(true)
    } catch (err) {
      console.error('❌ Lỗi báo cáo năm học:', err)
      message.error(err.response?.data?.detail || 'Không thể tải báo cáo')
    } finally {
      setLoading(false)
    }
  }

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
          <Col span={8}>
            <Select
              mode="multiple"
              placeholder="Chọn học kỳ để tổng hợp"
              style={{ width: '100%' }}
              value={selectedHocKy}
              onChange={setSelectedHocKy}
              options={dsHocKy.map(h => ({ value: h.id, label: h.ten_hoc_ky }))}
              loading={loading}
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={xemBaoCao}
              loading={loading}
              disabled={selectedHocKy.length === 0}
            >
              Xem báo cáo năm học
            </Button>
          </Col>
          <Col>
            <Badge count={dsHocKy.length} showZero>
              <span style={{ marginLeft: 8 }}>Học kỳ</span>
            </Badge>
          </Col>
        </Row>
      </Card>

      <Card title="📚 Hướng dẫn" size="small">
        <p>
          Chọn các học kỳ từ danh sách bên trên, sau đó nhấn
          <Tag color="blue">Xem báo cáo năm học</Tag>
          để xem tổng hợp điểm trung bình năm.
        </p>
        <p>
          <Tag color="green">💡 Lưu ý:</Tag>
          Điểm trung bình năm = trung bình cộng của các học kỳ đã chọn.
        </p>
      </Card>

      <ModalBaoCaoNamHoc
        open={openBaoCao}
        onClose={() => {
          setOpenBaoCao(false)
          setBaoCaoData(null)
        }}
        data={baoCaoData}
      />
    </div>
  )
}