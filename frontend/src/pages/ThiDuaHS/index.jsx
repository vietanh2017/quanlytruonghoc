// frontend/src/pages/ThiDuaHS/index.jsx
import React, { useState } from 'react'
import { Tabs, Typography } from 'antd'
import { useMeta } from './hooks/useMeta'
import TabTapThe from './components/TabTapThe'
import TabCaNhan from './components/TabCaNhan'
import TabDanhMuc from './components/TabDanhMuc'
import TabThang from './components/TabThang'
import TabHocKy from './components/TabHocKy'  // ⭐ Thêm import
import TabNamHoc from './components/TabNamHoc'
const { Title } = Typography

export default function ThiDuaHSPage() {
  const meta = useMeta()

  // ⭐ State để trigger refresh
  const [refreshKey, setRefreshKey] = useState(0)

  // ⭐ Hàm refresh toàn bộ dữ liệu
  const refreshData = () => {
    console.log('🔄 Refresh all tabs:', refreshKey + 1)
    setRefreshKey(prev => prev + 1)
  }

  const tabs = [
    {
      key: 'tap-the',
      label: '🏫 Tập thể',
      children: <TabTapThe meta={meta} refreshKey={refreshKey} onDataChange={refreshData} />
    },
    {
      key: 'ca-nhan',
      label: '👤 Cá nhân',
      children: <TabCaNhan meta={meta} onDataChange={refreshData} />
    },
    {
      key: 'danh-muc',
      label: '📋 Danh mục',
      children: <TabDanhMuc meta={meta} />
    },
    {
      key: 'thang',
      label: '📅 Quản lý tháng',
      children: <TabThang meta={meta} refreshKey={refreshKey} />
    },
    {
      key: 'hoc-ky',
      label: '📚 Học kỳ',
      children: <TabHocKy meta={meta} refreshKey={refreshKey} />
    },
    {
      key: 'nam-hoc', label: '📊 Năm học',
      children: <TabNamHoc meta={meta} />
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 12, fontSize: 16 }}>
        🎓 Thi Đua Học Sinh
      </Title>
      <Tabs items={tabs} type="card" />
    </div>
  )
}