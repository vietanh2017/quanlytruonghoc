// frontend/src/pages/Dashboard/index.jsx
import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Typography, Space, Avatar, Badge, List, Tag } from 'antd'
import {
  UserOutlined, TeamOutlined, CalendarOutlined, TrophyOutlined,
  RiseOutlined, ClockCircleOutlined, BookOutlined, FileTextOutlined
} from '@ant-design/icons'
import axios from 'axios'
import dayjs from 'dayjs'

const { Text } = Typography

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    giaoVien: 0,
    hocSinh: 0,
    lopHoc: 0,
    thiDua: 0,
  })
  const [recentActivities, setRecentActivities] = useState([])

  useEffect(() => {
    loadDashboard()
    loadRecentActivities()  // ⭐ Gọi load hoạt động
  }, [])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      // ⭐ Gọi API lấy danh sách lớp (có sĩ số)
      const [gvRes, lopRes] = await Promise.all([
        axios.get('http://localhost:8000/api/v1/giao-vien/?include_inactive=true'),
        axios.get('http://localhost:8000/api/v1/lop-hoc/?include_inactive=true'),
      ])

      const tongGV = gvRes.data?.total || gvRes.data?.items?.length || 0

      // ⭐ Tính tổng học sinh từ sĩ số các lớp
      const dsLop = lopRes.data?.items || lopRes.data || []
      const tongHS = dsLop.reduce((sum, lop) => sum + (lop.si_so || 0), 0)
      const tongLop = dsLop.length

      setStats({
        giaoVien: tongGV,
        hocSinh: tongHS,
        lopHoc: tongLop,
        thiDua: 12,
        thayDoi: {}
      })
    } catch (error) {
      console.error('Lỗi load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  // ⭐ HÀM LẤY HOẠT ĐỘNG GẦN ĐÂY
  const loadRecentActivities = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/v1/dashboard/recent-activities')
      setRecentActivities(res.data || [])
    } catch (error) {
      console.error('Lỗi load hoạt động:', error)
      // Dữ liệu mẫu nếu lỗi
      setRecentActivities([
        { user: 'Hệ thống', action: 'Đang cập nhật...', time: 'Vừa xong', type: 'default' }
      ])
    }
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'teacher': return <UserOutlined style={{ color: '#1677ff' }} />
      case 'student': return <UserOutlined style={{ color: '#52c41a' }} />
      case 'timetable': return <CalendarOutlined style={{ color: '#fa8c16' }} />
      case 'competition': return <TrophyOutlined style={{ color: '#faad14' }} />
      case 'assignment': return <FileTextOutlined style={{ color: '#722ed1' }} />
      default: return <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
    }
  }

  const getActivityColor = (type) => {
    switch (type) {
      case 'teacher': return '#e6f4ff'
      case 'student': return '#f6ffed'
      case 'timetable': return '#fff7e6'
      case 'competition': return '#fffbe6'
      case 'assignment': return '#f9f0ff'
      default: return '#f5f5f5'
    }
  }

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>

      {/* ─── BANNER ─── */}
      <Card
        style={{
          marginBottom: 24,
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
          borderRadius: 12,
          border: 'none',
        }}
        bodyStyle={{ padding: '32px 40px' }}
      >
        <Row align="middle" gutter={[24, 24]}>
          <Col xs={24} md={16}>
            <Space direction="vertical" size={8}>
              <span style={{ fontSize: 28, fontWeight: 700, color: '#fff' }}>
                🏫 HỆ THỐNG QUẢN LÝ TRƯỜNG HỌC
              </span>
              <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14 }}>
                Quản lý giáo viên, học sinh, thời khóa biểu và thi đua một cách hiệu quả
              </Text>
              <Space size={16} style={{ marginTop: 8 }}>
                <Badge status="success" text={<Text style={{ color: 'rgba(255,255,255,0.8)' }}>Hệ thống hoạt động</Text>} />
                <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>
                  {dayjs().format('DD/MM/YYYY HH:mm')}
                </Text>
              </Space>
            </Space>
          </Col>
          <Col xs={24} md={8} style={{ textAlign: 'right' }}>
            <Avatar.Group size="large">
              <Avatar src="https://images.unsplash.com/photo-1523050854058-8df90110c7f1?w=100" />
              <Avatar src="https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=100" />
              <Avatar style={{ backgroundColor: '#1677ff' }}>
                <UserOutlined />
              </Avatar>
            </Avatar.Group>
            <div style={{ marginTop: 8, color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>
              <Text style={{ color: 'rgba(255,255,255,0.6)' }}>+ {stats.giaoVien} giáo viên đang hoạt động</Text>
            </div>
          </Col>
        </Row>
      </Card>

      {/* ─── THỐNG KÊ ─── */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading} style={{ borderRadius: 12 }}>
            <Statistic
              title={<Space><UserOutlined style={{ color: '#1677ff' }} /> Giáo viên</Space>}
              value={stats.giaoVien}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#1677ff', fontSize: 28 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading} style={{ borderRadius: 12 }}>
            <Statistic
              title={<Space><TeamOutlined style={{ color: '#52c41a' }} /> Học sinh</Space>}
              value={stats.hocSinh}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontSize: 28 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading} style={{ borderRadius: 12 }}>
            <Statistic
              title={<Space><BookOutlined style={{ color: '#fa8c16' }} /> Lớp học</Space>}
              value={stats.lopHoc}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#fa8c16', fontSize: 28 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading} style={{ borderRadius: 12 }}>
            <Statistic
              title={<Space><TrophyOutlined style={{ color: '#faad14' }} /> Thi đua</Space>}
              value={stats.thiDua}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#faad14', fontSize: 28 }}
            />
          </Card>
        </Col>
      </Row>

      {/* ─── HOẠT ĐỘNG GẦN ĐÂY ─── */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="📋 Hoạt động gần đây" style={{ borderRadius: 12 }} loading={loading}>
            <List
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Space>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      background: getActivityColor(item.type),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {getActivityIcon(item.type)}
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 500 }}>
                        <Text strong>{item.user}</Text>
                        <Text style={{ color: '#8c8c8c', marginLeft: 4 }}>{item.action}</Text>
                      </div>
                      <Text type="secondary" style={{ fontSize: 11 }}>{item.time}</Text>
                    </div>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="🎯 Chức năng nhanh" style={{ borderRadius: 12 }}>
            <Row gutter={[12, 12]}>
              <Col span={12}>
                <Card hoverable size="small" style={{ textAlign: 'center' }} onClick={() => window.location.href = '/giao-vien'}>
                  <UserOutlined style={{ fontSize: 24, color: '#1677ff' }} />
                  <div style={{ marginTop: 8, fontSize: 13 }}>Quản lý GV</div>
                </Card>
              </Col>
              <Col span={12}>
                <Card hoverable size="small" style={{ textAlign: 'center' }} onClick={() => window.location.href = '/lop-hoc'}>
                  <TeamOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                  <div style={{ marginTop: 8, fontSize: 13 }}>Quản lý HS</div>
                </Card>
              </Col>
              <Col span={12}>
                <Card hoverable size="small" style={{ textAlign: 'center' }} onClick={() => window.location.href = '/timetable'}>
                  <CalendarOutlined style={{ fontSize: 24, color: '#fa8c16' }} />
                  <div style={{ marginTop: 8, fontSize: 13 }}>Thời khóa biểu</div>
                </Card>
              </Col>
              <Col span={12}>
                <Card hoverable size="small" style={{ textAlign: 'center' }} onClick={() => window.location.href = '/thi-dua/giao-vien'}>
                  <TrophyOutlined style={{ fontSize: 24, color: '#faad14' }} />
                  <div style={{ marginTop: 8, fontSize: 13 }}>Thi đua</div>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}