// frontend/src/App.jsx
import React, { useState } from 'react'
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  TeamOutlined,
  HomeOutlined,
  BookOutlined,
  CalendarOutlined,
  BarChartOutlined,
  SettingOutlined,
  TrophyOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import LoginPage from './pages/Login/LoginPage'
import GiaoVienPage from './pages/GiaoVien/GiaoVienPage'
import Dashboard from './pages/Dashboard/index'
import LopHocPage from './pages/LopHoc/LopHocPage'
import PhanCongPage from './pages/PhanCong/PhanCongPage'
import TKBPage from './pages/TKB'
import CauHinhPage from './pages/CauHinh/CauHinhPage';
import ThiDuaGVPage from './pages/ThiDuaGV/ThiDuaGVPage'
import ThiDuaHSPage from './pages/ThiDuaHS'
import ReportsPage from './pages/Reports'

const { Sider, Content, Header } = Layout
const marqueeStyle = `
  .marquee-container {
  overflow: hidden;
  white-space: nowrap;
  width: 100%;
  position: relative;
}

.marquee-text {
  display: inline-block;
  padding-left: 100%; /* ⭐ QUAN TRỌNG: để bắt đầu từ bên phải */
  animation: marquee 25s linear infinite;
  font-weight: 600;
  color: #1e293b;
  will-change: transform;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-100%);
  }
}
`;

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: 'TRANG CHỦ' },
  { key: '/giao-vien', icon: <TeamOutlined />, label: 'Giáo Viên' },
  { key: '/lop-hoc', icon: <BookOutlined />, label: 'Học sinh' },
  { key: '/phan-cong', icon: <BookOutlined />, label: 'Phân công giảng dạy' },
  { key: '/timetable', icon: <CalendarOutlined />, label: 'Thời Khóa Biểu' },
  { key: '/thi-dua/giao-vien', icon: <UserOutlined />, label: 'Thi Đua Giáo viên' },
  { key: '/thi-dua/hoc-sinh', icon: <UserOutlined />, label: 'Thi Đua Học Sinh' },
  { key: '/bao-cao', icon: <BarChartOutlined />, label: 'Báo Cáo' },
  { key: '/cau-hinh', icon: <SettingOutlined />, label: 'Cấu Hình' },
]

// ⭐ Lấy thông tin user từ localStorage
const getUserInfo = () => {
  try {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  } catch {
    return null
  }
}

// ⭐ Component bảo vệ route
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const user = getUserInfo()

  // ⭐ Kiểm tra xem có đang ở trang login không
  const isLoginPage = location.pathname === '/login'

  // ⭐ Hàm logout
  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  // ⭐ Nếu đang ở trang login, chỉ hiển thị LoginPage (không có layout)
  if (isLoginPage) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    )
  }

  // ⭐ Kiểm tra token trước khi render layout
  const token = localStorage.getItem('token')
  if (!token) {
    return <Navigate to="/login" replace />
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{ background: '#1e293b' }}
        width={220}
      >
        {/* Logo */}
        <div style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #334155',
          marginBottom: 8,
        }}>
          {!collapsed && (
            <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: 16 }}>
              🏫 EduSchool
            </span>
          )}
          {collapsed && <span style={{ color: '#38bdf8', fontSize: 20 }}>🏫</span>}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ background: '#1e293b', borderRight: 0 }}
        />
      </Sider>

      <Layout>
        {/* Topbar */}
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #10bcf0',
          height: 56,
        }}>
          {/* ⭐ Bọc marquee trong 1 div có flex:1 để chiếm không gian */}
          <div style={{ flex: 1, overflow: 'hidden', marginRight: 16 }}>
            <div className="marquee-container">
              <style>{marqueeStyle}</style>
              <div className="marquee-text">
                Website QUẢN LÍ TRƯỜNG HỌC - Version 1.0 - Design by Le Van Hung - Trường THCS Phong Bắc - Phone: 0985902456 - Email: hailuacx@gmail.com
              </div>
            </div>
          </div>

          {/* Phần bên phải (user info) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
            <span style={{ color: '#3a06f3', fontSize: 13 }}>
              👤 {user?.ho_ten || 'Quản trị viên'}
            </span>
            <span style={{ color: '#ef4444', fontSize: 13, cursor: 'pointer' }} onClick={handleLogout}>
              <LogoutOutlined /> Đăng xuất
            </span>
          </div>
        </Header>

        {/* Content */}
        <Content style={{ background: '#f8fafc', padding: 24, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/giao-vien" element={<GiaoVienPage />} />
            <Route path="/lop-hoc" element={<LopHocPage />} />
            <Route path="/cau-hinh/*" element={<CauHinhPage />} />
            <Route path="/phan-cong" element={<PhanCongPage />} />
            <Route path="/timetable" element={<TKBPage />} />
            <Route path="/thi-dua/giao-vien" element={<ThiDuaGVPage />} />
            <Route path="/thi-dua/hoc-sinh" element={<ThiDuaHSPage />} />
            <Route path="/bao-cao" element={<ReportsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}