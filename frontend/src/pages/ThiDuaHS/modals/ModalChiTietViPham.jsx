// frontend/src/pages/ThiDuaHS/modals/ModalChiTietViPham.jsx
import React, { useState, useEffect } from 'react'
import { Modal, Table, Tabs, Space, Button, Tooltip, Popconfirm, message, Typography } from 'antd'
import { EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { tapTheAPI, caNhanAPI } from '../services/api'

const { Text } = Typography

export default function ModalChiTietViPham({
  open,
  onClose,
  record,
  dsVPTapThe,
  dsVPCaNhan,
  onRefresh
}) {
  const [loading, setLoading] = useState(false)
  const [tapTheData, setTapTheData] = useState([])
  const [caNhanData, setCaNhanData] = useState([])

  // ⭐ Cập nhật dữ liệu khi props thay đổi
  useEffect(() => {
    if (record) {
      setTapTheData(dsVPTapThe.filter(vp => vp.lop_hoc_id === record.lop_hoc_id))
      setCaNhanData(dsVPCaNhan.filter(vp => vp.lop_hoc_id === record.lop_hoc_id))
    }
  }, [record, dsVPTapThe, dsVPCaNhan])

  // ⭐ Hàm xóa vi phạm tập thể
  const handleXoaTapThe = async (id) => {
    try {
      await tapTheAPI.delete(id)
      message.success('Đã xóa vi phạm tập thể')
      // ⭐ Gọi refresh từ parent
      await onRefresh()
      // ⭐ Cập nhật lại data local
      setTapTheData(prev => prev.filter(vp => vp.id !== id))
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ⭐ Hàm xóa vi phạm cá nhân
  const handleXoaCaNhan = async (id) => {
    try {
      await caNhanAPI.delete(id)
      message.success('Đã xóa vi phạm cá nhân')
      // ⭐ Gọi refresh từ parent
      await onRefresh()
      // ⭐ Cập nhật lại data local
      setCaNhanData(prev => prev.filter(vp => vp.id !== id))
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  if (!record) return null

  const tapThe = tapTheData
  const caNhan = caNhanData

  return (
    <Modal
      title={`Chi tiết vi phạm - ${record.ten_lop}`}
      open={open}
      onCancel={onClose}
      width={750}
      centered  // ⭐ THÊM DÒNG NÀY ĐỂ CANH GIỮA
      footer={[
        <Button key="close" onClick={onClose}>Đóng</Button>
      ]}
    >
      <Tabs
        items={[
          {
            key: 'tap-the',
            label: `Tập thể (${tapThe.length})`,
            children: tapThe.length > 0 ? (
              <Table
                dataSource={tapThe}
                rowKey="id"
                columns={[
                  { title: 'Vi phạm', dataIndex: 'ten_loi', width: 150 },
                  { title: 'Điểm', dataIndex: 'so_diem', width: 80, render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text> },
                  { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 120 },
                  { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
                  {
                    title: 'Thao tác',
                    width: 110,
                    align: 'center',
                    render: (_, vp) => (
                      <Space size={4}>
                        <Tooltip title="Sửa">
                          <Button size="small" icon={<EditOutlined />} />
                        </Tooltip>
                        <Popconfirm
                          title="Xóa vi phạm này?"
                          onConfirm={() => handleXoaTapThe(vp.id)}
                          okText="Xóa"
                          cancelText="Hủy"
                          okButtonProps={{ danger: true }}
                        >
                          <Button size="small" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      </Space>
                    )
                  }
                ]}
                pagination={false}
                size="small"
              />
            ) : <Text type="secondary">Chưa có vi phạm tập thể</Text>
          },
          {
            key: 'ca-nhan',
            label: `Cá nhân (${caNhan.length})`,
            children: caNhan.length > 0 ? (
              <Table
                dataSource={caNhan}
                rowKey="id"
                columns={[
                  { title: 'Học sinh', dataIndex: 'ho_ten', width: 120 },
                  { title: 'Vi phạm', dataIndex: 'ten_loi', width: 150 },
                  { title: 'Điểm', dataIndex: 'so_diem', width: 80, render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text> },
                  { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 120 },
                  { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
                  {
                    title: 'Thao tác',
                    width: 110,
                    align: 'center',
                    render: (_, vp) => (
                      <Space size={4}>
                        <Tooltip title="Sửa">
                          <Button size="small" icon={<EditOutlined />} />
                        </Tooltip>
                        <Popconfirm
                          title="Xóa vi phạm này?"
                          onConfirm={() => handleXoaCaNhan(vp.id)}
                          okText="Xóa"
                          cancelText="Hủy"
                          okButtonProps={{ danger: true }}
                        >
                          <Button size="small" danger icon={<DeleteOutlined />} />
                        </Popconfirm>
                      </Space>
                    )
                  }
                ]}
                pagination={false}
                size="small"
              />
            ) : <Text type="secondary">Chưa có vi phạm cá nhân</Text>
          }
        ]}
        size="small"
      />
    </Modal>
  )
}