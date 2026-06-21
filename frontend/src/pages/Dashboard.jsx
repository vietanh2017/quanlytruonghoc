// frontend/src/pages/Dashboard.jsx
import React from 'react'
import { Card, Col, Row, Typography } from 'antd'
import { TeamOutlined, BookOutlined, TrophyOutlined, CalendarOutlined } from '@ant-design/icons'

const { Title, Text } = Typography

const stats = [
  { title: 'Giáo Viên',       icon: <TeamOutlined />,     color: '#3b82f6', value: '—' },
  { title: 'Lớp Học',         icon: <BookOutlined />,     color: '#10b981', value: '—' },
  { title: 'Thi Đua',         icon: <TrophyOutlined />,   color: '#f59e0b', value: '—' },
  { title: 'Thời Khóa Biểu',  icon: <CalendarOutlined />, color: '#8b5cf6', value: '—' },
]

export default function Dashboard() {
  return (
    <div>
      <Title level={4}>🏠 Tổng quan</Title>
      <Row gutter={[16, 16]}>
        {stats.map((s) => (
          <Col xs={24} sm={12} lg={6} key={s.title}>
            <Card bordered={false} style={{ borderRadius: 12,
              boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 12,
                  background: s.color + '20',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 22, color: s.color,
                }}>
                  {s.icon}
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 13 }}>{s.title}</Text>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#1e293b' }}>
                    {s.value}
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  )
}
