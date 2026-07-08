// frontend/src/pages/Reports/components/StatsCards.jsx
import React from 'react'
import { Row, Col, Card, Statistic } from 'antd'
import { BookOutlined, TeamOutlined, TrophyOutlined, WarningOutlined, UserOutlined, StarOutlined } from '@ant-design/icons'

const StatsCards = ({ stats }) => {
  if (!stats) return null

  const items = [
    { title: 'Tổng số lớp', value: stats.tong_lop, icon: <BookOutlined />, color: '#1890ff' },
    { title: 'Tổng học sinh', value: stats.tong_hs, icon: <TeamOutlined />, color: '#52c41a' },
    { title: 'Điểm TB cao nhất', value: stats.diem_cao_nhat, icon: <TrophyOutlined />, color: '#faad14', precision: 2 },
    { title: 'Điểm TB thấp nhất', value: stats.diem_thap_nhat, icon: <StarOutlined />, color: '#ff4d4f', precision: 2 },
    { title: 'Tổng vi phạm', value: stats.tong_vi_pham, icon: <WarningOutlined />, color: '#cf1322' },
    { title: 'Tổng thành tích', value: stats.tong_thanh_tich, icon: <StarOutlined />, color: '#52c41a' },
  ]

  return (
    <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
      {items.map((item, index) => (
        <Col xs={24} sm={12} md={8} lg={4} key={index}>
          <Card size="small">
            <Statistic
              title={item.title}
              value={item.value}
              prefix={item.icon}
              precision={item.precision}
              valueStyle={{ color: item.color, fontSize: 18 }}
            />
          </Card>
        </Col>
      ))}
    </Row>
  )
}

export default StatsCards