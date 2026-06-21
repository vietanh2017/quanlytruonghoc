// frontend/src/App.jsx
import React, { useState } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
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
} from '@ant-design/icons'

import GiaoVienPage from './pages/GiaoVien/GiaoVienPage'
import Dashboard from './pages/Dashboard'
import LopHocPage from './pages/LopHoc/LopHocPage'
import CauHinhPage from './pages/CauHinh/CauHinhPage';
import PhanCongPage from './pages/PhanCong/PhanCongPage'
import ThiDuaHSPage from './pages/ThiDuaHS/ThiDuaHSPage'
import ThiDuaGVPage from './pages/ThiDuaGV/ThiDuaGVPage'

const { Sider, Content, Header } = Layout

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: 'Dashboard' },
  { key: '/giao-vien', icon: <TeamOutlined />, label: 'Giáo Viên' },
  { key: '/lop-hoc', icon: <BookOutlined />, label: 'Lớp Học' },
  { key: '/phan-cong', icon: <BookOutlined />, label: 'Phân công giảng dạy' },
  { key: '/timetable', icon: <CalendarOutlined />, label: 'Thời Khóa Biểu' },
  { key: '/thi-dua/giao-vien', icon: <UserOutlined />, label: 'Thi Đua Giáo viên' },
  { key: '/thi-dua/hoc-sinh', icon: <UserOutlined />, label: 'Thi Đua Học Sinh' },
  { key: '/bao-cao', icon: <BarChartOutlined />, label: 'Báo Cáo' },
  { key: '/cau-hinh', icon: <SettingOutlined />, label: 'Cấu Hình' },
]

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

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
          borderBottom: '1px solid #e2e8f0',
          height: 56,
        }}>
          <span style={{ fontWeight: 600, color: '#1e293b' }}>
            HỆ THỐNG QUẢN LÝ TRƯỜNG HỌC - LƯU HÀNH NỘI BỘ
          </span>
          <span style={{ color: '#64748b', fontSize: 13 }}>
            👤 Quản trị viên
          </span>
        </Header>

        {/* Content */}
        <Content style={{ background: '#f8fafc', padding: 24, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/giao-vien" element={<GiaoVienPage />} />
            <Route path="/lop-hoc" element={<LopHocPage />} />
            <Route path="/cau-hinh" element={<CauHinhPage />} />
            <Route path="/phan-cong" element={<PhanCongPage />} />
            <Route path="/thi-dua/giao-vien" element={<ThiDuaGVPage />} />
            <Route path="/thi-dua/hoc-sinh" element={<ThiDuaHSPage />} />
            {/* Thêm route các module khác ở đây */}
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
