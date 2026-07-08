// frontend/src/pages/Reports/index.jsx
import React, { useEffect } from 'react'
import { Typography, Card, Spin, Empty, Button } from 'antd'
import { useReport } from './hooks/useReport'
import FilterBar from './components/FilterBar'
import StatsCards from './components/StatsCards'
import ChartSection from './components/ChartSection'
import ReportTable from './components/ReportTable'

const { Title } = Typography

export default function ReportsPage() {
  const { 
    data, 
    loading, 
    filters, 
    dsNamHoc,  // ⭐ Lấy dsNamHoc từ hook
    generateReport, 
    updateFilter, 
    resetFilters 
  } = useReport()

  const handleViewDetail = (record) => {
    console.log('Xem chi tiết:', record)
  }

  return (
    <div style={{ padding: 22, background: '#f0f2f5', minHeight: '100vh' }}>
      
      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0, fontSize: 18, display: 'flex', alignItems: 'center', gap: 12 }}>
          📊 Báo cáo thống kê
        </Title>
      </Card>

      {/* Filter */}
      <FilterBar
        filters={filters}
        onFilterChange={updateFilter}
        onGenerate={() => generateReport()}
        onReset={resetFilters}
        loading={loading}
        dsNamHoc={dsNamHoc}  // ⭐ Truyền dsNamHoc vào FilterBar
      />

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" tip="Đang tải báo cáo..." />
        </div>
      )}

      {/* Content */}
      {!loading && data && (
        <>
          <StatsCards stats={data.stats} />
          <ChartSection data={data.data} loading={loading} />
          <ReportTable
            data={data.data}
            loading={loading}
            onViewDetail={handleViewDetail}
          />
        </>
      )}

      {/* Empty state */}
      {!loading && !data && (
        <Card>
          <Empty
            description="Chưa có dữ liệu báo cáo"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => generateReport()}>
              Tạo báo cáo
            </Button>
          </Empty>
        </Card>
      )}

    </div>
  )
}