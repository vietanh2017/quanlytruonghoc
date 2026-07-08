// frontend/src/pages/Reports/components/ReportTable.jsx
import React from 'react'
import { Table, Tag, Button, Tooltip, Space } from 'antd'
import { EyeOutlined } from '@ant-design/icons'

const ReportTable = ({ data, loading, onViewDetail }) => {
  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Lớp',
      dataIndex: 'ten_lop',
      fixed: 'left',
      width: 120,
      render: (text) => <span style={{ fontWeight: 500 }}>{text}</span>,
    },
    {
      title: 'Khối',
      dataIndex: 'khoi',
      width: 60,
      align: 'center',
      render: (v) => <Tag color="blue">{v}</Tag>,
    },
    {
      title: 'Sĩ số',
      dataIndex: 'si_so',
      width: 60,
      align: 'center',
    },
    {
      title: 'GVCN',
      dataIndex: 'ten_gvcn',
      width: 150,
      render: (v) => v || <span style={{ color: '#999' }}>—</span>,
    },
    {
      title: 'Điểm đội',
      dataIndex: 'diem_doi',
      width: 80,
      align: 'center',
      render: (v) => v?.toFixed(3) || '0.000',
    },
    {
      title: 'Điểm HT',
      dataIndex: 'diem_hoc_tap',
      width: 80,
      align: 'center',
      render: (v) => v?.toFixed(3) || '0.000',
    },
    {
      title: 'Trung bình',
      dataIndex: 'trung_binh',
      width: 100,
      align: 'center',
      render: (v) => (
        <span style={{ color: '#1890ff', fontWeight: 'bold', fontSize: 15 }}>
          {v?.toFixed(3) || '0.000'}
        </span>
      ),
      sorter: (a, b) => (a.trung_binh || 0) - (b.trung_binh || 0),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Xếp hạng',
      dataIndex: 'xep_hang',
      width: 80,
      align: 'center',
      render: (v) => {
        const medals = ['🥇', '🥈', '🥉']
        if (v <= 3) return <span style={{ fontSize: 20 }}>{medals[v - 1]}</span>
        return <Tag color="default">#{v}</Tag>
      },
    },
    {
      title: 'Thao tác',
      width: 60,
      align: 'center',
      render: (_, record) => (
        <Tooltip title="Xem chi tiết">
          <Button size="small" icon={<EyeOutlined />} onClick={() => onViewDetail?.(record)} />
        </Tooltip>
      ),
    },
  ]

  return (
    <Table
      rowKey="lop_hoc_id"
      columns={columns}
      dataSource={data}
      loading={loading}
      size="small"
      bordered
      pagination={{
        pageSize: 15,
        showTotal: (total) => `Tổng: ${total} lớp`,
        showSizeChanger: true,
        showQuickJumper: true,
      }}
      scroll={{ x: 1000 }}
    />
  )
}

export default ReportTable