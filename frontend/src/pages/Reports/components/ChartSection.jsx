// frontend/src/pages/Reports/components/ChartSection.jsx
import React from 'react'
import { Card, Empty, Progress, Row, Col, Tag, Spin } from 'antd'

const ChartSection = ({ data, loading }) => {
  if (loading) {
    return (
      <Card size="small" style={{ marginBottom: 16 }}>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin tip="Đang tải biểu đồ..." />
        </div>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card size="small" style={{ marginBottom: 16 }}>
        <Empty description="Chưa có dữ liệu để hiển thị biểu đồ" />
      </Card>
    )
  }

  // Lấy top 15 lớp
  const topData = data.slice(0, 15)

  return (
    <Card size="small" style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 12, fontWeight: 600, fontSize: 14 }}>
        📊 Top {topData.length} lớp có điểm TB cao nhất
      </div>
      <Row gutter={[8, 6]}>
        {topData.map((item, index) => {
          const percent = Math.min((item.trung_binh || 0) * 10, 100)
          const medals = ['🥇', '🥈', '🥉']
          const prefix = index < 3 ? medals[index] : `#${index + 1}`

          return (
            <Col span={24} key={item.lop_hoc_id}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ width: 36, fontSize: 13, textAlign: 'center' }}>{prefix}</span>
                <span style={{ width: 80, fontSize: 13, fontWeight: 500 }}>{item.ten_lop}</span>
                <Progress
                  percent={percent}
                  status={percent >= 80 ? 'success' : percent >= 50 ? 'active' : 'exception'}
                  size="small"
                  style={{ flex: 1, minWidth: 0 }}
                  format={() => item.trung_binh?.toFixed(3) || '0.000'}
                />
                <Tag color={percent >= 80 ? 'green' : percent >= 50 ? 'orange' : 'red'} style={{ minWidth: 60, textAlign: 'center' }}>
                  {item.trung_binh?.toFixed(3) || '0.000'}
                </Tag>
              </div>
            </Col>
          )
        })}
      </Row>
    </Card>
  )
}

export default ChartSection