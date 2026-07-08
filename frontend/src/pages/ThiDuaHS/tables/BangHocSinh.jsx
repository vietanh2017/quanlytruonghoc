// frontend/src/pages/ThiDuaHS/tables/BangHocSinh.jsx
import React from 'react'
import { Table, Tag, Typography, Button, Space, Tooltip, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'

const { Text } = Typography

export default function BangHocSinh({ data, viPham, loading, onAdd, onDelete }) {
  const getViPhamByHocSinh = (hsId) => {
    return viPham.filter(vp => vp.hoc_sinh_id === hsId)
  }

  const getTongDiem = (hsId) => {
    const viPhams = getViPhamByHocSinh(hsId)
    return viPhams.reduce((sum, vp) => sum + vp.so_diem, 0)
  }

  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Mã HS',
      dataIndex: 'ma_hoc_sinh',
      width: 100,
    },
    {
      title: 'Họ tên',
      dataIndex: 'ho_ten',
      sorter: (a, b) => a.ho_ten.localeCompare(b.ho_ten),
    },
    {
      title: 'Vi phạm / Thành tích',
      key: 'vi_pham',
      render: (_, r) => {
        const viPhams = getViPhamByHocSinh(r.id)
        if (viPhams.length === 0) {
          return <Text type="secondary" style={{ fontSize: 12 }}>—</Text>
        }
        return (
          <Space wrap size={4}>
            {viPhams.map((vp, idx) => (
              <Tag
                key={idx}
                color={vp.so_diem < 0 ? 'red' : 'green'}
                style={{ margin: 2 }}
              >
                {vp.ten_loi} ({vp.so_diem > 0 ? '+' : ''}{vp.so_diem})
              </Tag>
            ))}
          </Space>
        )
      }
    },
    {
      title: 'Tổng điểm',
      key: 'tong_diem',
      width: 100,
      align: 'center',
      render: (_, r) => {
        const tong = getTongDiem(r.id)
        return (
          <Tag color={tong < 0 ? 'red' : tong > 0 ? 'green' : 'default'}>
            {tong > 0 ? '+' : ''}{tong}
          </Tag>
        )
      },
      sorter: (a, b) => getTongDiem(a.id) - getTongDiem(b.id),
    },
    {
      title: 'Thao tác',
      width: 120,
      render: (_, r) => {
        const viPhams = getViPhamByHocSinh(r.id)
        return (
          <Space size={4}>
            <Tooltip title="Thêm vi phạm / thành tích">
              <Button
                size="small"
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => onAdd?.(r.id)}
              />
            </Tooltip>
            {viPhams.length > 0 && (
              <Popconfirm
                title="Xóa tất cả vi phạm của học sinh này?"
                onConfirm={async () => {
                  for (const vp of viPhams) {
                    await onDelete?.(vp.id)
                  }
                }}
                okText="Xóa"
                cancelText="Hủy"
                okButtonProps={{ danger: true }}
              >
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            )}
          </Space>
        )
      }
    }
  ]

  const expandedRowRender = (record) => {
    const viPhams = getViPhamByHocSinh(record.id)
    if (viPhams.length === 0) {
      return <Text type="secondary">Chưa có vi phạm / thành tích</Text>
    }
    return (
      <Table
        rowKey="id"
        dataSource={viPhams}
        columns={[
          { title: 'Loại', dataIndex: 'ten_loi', width: 200 },
          {
            title: 'Điểm',
            dataIndex: 'so_diem',
            width: 80,
            render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text>
          },
          { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 100 },
          { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
          {
            title: 'Xóa',
            width: 60,
            render: (_, vp) => (
              <Popconfirm title="Xóa?" onConfirm={() => onDelete?.(vp.id)}>
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            )
          }
        ]}
        pagination={false}
        size="small"
      />
    )
  }

  return (
    <Table
      rowKey="id"
      columns={columns}
      dataSource={data}
      loading={loading}
      size="small"
      bordered
      pagination={{
        pageSize: 10,
        showTotal: (total) => `Tổng: ${total} học sinh`
      }}
      locale={{
        emptyText: 'Chọn lớp để xem danh sách học sinh'
      }}
      expandable={{
        expandedRowRender,
        expandRowByClick: true,
        expandedRowClassName: () => 'expand-row',
      }}
    />
  )
}