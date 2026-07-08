// frontend/src/pages/Login/LoginPage.jsx
import React, { useState } from 'react'
import { Form, Input, Button, Card, message, Typography, Row, Col } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const { Title, Text } = Typography
const API_URL = `${import.meta.env.VITE_API_URL}/api/v1`

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email: values.email,
        mat_khau: values.password
      })

      // Lưu token và thông tin user
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify({
        ho_ten: response.data.ho_ten,
        email: response.data.email,
        role: response.data.role
      }))

      message.success(`Chào mừng ${response.data.ho_ten}!`)
      navigate('/')
    } catch (error) {
      message.error(error.response?.data?.detail || 'Đăng nhập thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Row justify="center" align="middle" style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Col xs={22} sm={16} md={10} lg={8}>
        <Card style={{ borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Title level={3}>🏫 Hệ thống quản lý</Title>
            <Text type="secondary">Đăng nhập để tiếp tục</Text>
          </div>

          <Form
            name="login"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Vui lòng nhập email' },
                { type: 'email', message: 'Email không hợp lệ' }
              ]}
            >
              <Input prefix={<UserOutlined />} placeholder="Email" />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Vui lòng nhập mật khẩu' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                Đăng nhập
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Tài khoản mặc định: admin@school.com / eduschool@123
            </Text>
          </div>
        </Card>
      </Col>
    </Row>
  )
}