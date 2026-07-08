// frontend/src/pages/ThiDuaHS/tables/BangTongHopLop.jsx
import React from 'react'
import { Table, Tag, Typography, Card, Tooltip, Button } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { getMedal, getColorByScore } from '../utils/constants'

const { Text } = Typography

export default function BangTongHopLop({ data, loading, onViewDetail }) {
  const columns = [
    {
      title: 'TT',
      key: 'stt',
      width: 38,
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Lớp',
      dataIndex: 'ten_lop',
      width: 53,
      fixed: 'left',
      align: 'center',
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: 'Vi phạm',
      dataIndex: 'tong_vi_pham',
      width: 60,
      align: 'center',
      render: (v) => v < 0 ? <Tag color="red">{v}</Tag> : <Tag>0</Tag>,
    },
    {
      title: 'Thành tích',
      dataIndex: 'tong_thanh_tich',
      width: 60,
      align: 'center',
      render: (v) => v > 0 ? <Tag color="green">+{v}</Tag> : <Tag>0</Tag>,
    },
    {
      title: 'Tổng điểm đội',
      dataIndex: 'tong_diem_doi',
      width: 90,
      align: 'center',
      render: (v) => <Text strong style={{ fontSize: 12, color: '#1890ff' }}>{v}</Text>,
      sorter: (a, b) => a.tong_diem_doi - b.tong_diem_doi,
      defaultSortOrder: 'descend',
    },
    {
      title: 'Trung bình',
      dataIndex: 'diem_doi_tb',
      width: 80,
      align: 'center',
      render: (v) => {
        const score = v?.toFixed(3) || '0.000'
        return <Tag color={getColorByScore(parseFloat(score))}>{score}</Tag>
      },
      sorter: (a, b) => a.diem_doi_tb - b.diem_doi_tb,
    },
    {
      title: 'Xếp hạng',
      dataIndex: 'xep_hang',
      width: 55,
      align: 'center',
      render: (v) => getMedal(v),
    },
    {
      title: '',
      width: 50,
      align: 'center',
      render: (_, record) => (
        <Tooltip title="Xem chi tiết vi phạm">
          <Button
            size="small"
            type="text"
            icon={<EyeOutlined />}
            onClick={() => onViewDetail?.(record)}
          />
        </Tooltip>
      ),
    },
  ]

  return (
    <Card title="📊 Tổng hợp điểm đội" size="small">
      <Table
        rowKey="lop_hoc_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="small"
        bordered
        pagination={false}
        scroll={{ y: 400 }}
        locale={{ emptyText: 'Chưa có dữ liệu điểm đội' }}
      />
    </Card>
  )
}