// frontend/src/pages/TKB/index.jsx
import React from 'react'
import { Tabs, Typography, Spin, Alert, Button } from 'antd'
import TabCauHinhNgay from './components/TabCauHinhNgay'
import TabCauHinhMon from './components/TabRangBuoc'
import TabCauHinhTiet from './components/TabCauHinhTiet'
import { useTKBMeta } from './hooks/useTKBMeta'
import TabRangBuocGV from './components/TabRangBuocGV'
import TabNhapTKB from './components/TabNhapTKB'

const { Title } = Typography

export default function TKBPage() {
  const meta = useTKBMeta()

  if (meta.loading && !meta.data.cauHinhNgay.length) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" tip="Đang tải dữ liệu..." />
      </div>
    )
  }

  if (meta.error) {
    return (
      <Alert
        message="Lỗi tải dữ liệu"
        description={meta.error}
        type="error"
        showIcon
        action={
          <Button size="small" type="primary" onClick={meta.fetchMeta}>
            Thử lại
          </Button>
        }
      />
    )
  }

  const tabs = [
    {
      key: 'cau-hinh-ngay',
      label: '📅 Cấu hình ngày học',
      children: <TabCauHinhNgay meta={meta} />
    },
    {
      key: 'cau-hinh-tiet',
      label: '⏰ Cấu hình tiết',
      children: <TabCauHinhTiet meta={meta} />
    },
    {
      key: 'cau-hinh-mon',
      label: '📚 Ràng buộc môn học',
      children: <TabCauHinhMon meta={meta} />
    },
    {
      key: 'rang-buoc-gv',
      label: '👨‍🏫 Ràng buộc giáo viên',
      children: <TabRangBuocGV meta={meta} />
    },
    {
      key: 'nhap-tkb',
      label: '📝 Nhập TKB',
      children: <TabNhapTKB meta={meta} />
    },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 12, fontSize: 16 }}>
        📅 Quản lý Thời Khóa Biểu
      </Title>
      <Tabs items={tabs} type="card" />
    </div>
  )
}