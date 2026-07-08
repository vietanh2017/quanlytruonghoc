// frontend/src/pages/ThiDuaHS/modals/ModalBaoCaoNamHoc.jsx
import React from 'react'
import { Modal, Table, Tag, Badge, Space, Button, Tooltip, message } from 'antd'
import { TrophyOutlined, FileExcelOutlined } from '@ant-design/icons'
import { exportBaoCaoNamHoc } from '../utils/excelExport'

export default function ModalBaoCaoNamHoc({ open, onClose, data }) {
  if (!data) return null

  // ⭐ Debug kiểm tra dữ liệu
  console.log('📊 Dữ liệu báo cáo năm học:', data)
  console.log('📋 hoc_ky_list:', data.hoc_ky_list)
  console.log('📊 data.data:', data.data)

  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      render: (_, __, i) => i + 1
    },
    {
      title: 'Lớp',
      dataIndex: 'ten_lop',
      fixed: 'left',
      width: 80
    },
    {
      title: 'Khối',
      dataIndex: 'khoi',
      width: 60,
      align: 'center'
    },
    ...(data.hoc_ky_list?.map((hkName) => ({
      title: hkName,
      dataIndex: ['cac_hoc_ky', hkName],
      width: 100,
      align: 'center',
      render: (v) => v?.toFixed(3) || '0.000'
    })) || []),
    {
      title: 'Trung bình năm',
      dataIndex: 'trung_binh',
      width: 120,
      align: 'center',
      render: v => <span style={{ color: '#1890ff', fontWeight: 'bold' }}>{v?.toFixed(3)}</span>
    },
    {
      title: 'Xếp hạng',
      dataIndex: 'xep_hang',
      width: 80,
      align: 'center',
      render: v => {
        const medals = ['🥇', '🥈', '🥉']
        if (v <= 3) return medals[v - 1]
        return `#${v}`
      }
    }
  ]

  const rowClassName = (record) => {
    if (record.xep_hang === 1) return 'row-top-1'
    if (record.xep_hang === 2) return 'row-top-2'
    if (record.xep_hang === 3) return 'row-top-3'
    return ''
  }

  const handleExportExcel = () => {
    if (!data.data || data.data.length === 0) {
      message.warning('Không có dữ liệu để xuất!')
      return
    }
    exportBaoCaoNamHoc(data.data, data.hoc_ky_list)
  }

  return (
    <Modal
      title={
        <Space>
          <TrophyOutlined style={{ color: '#faad14' }} />
          <span>Báo cáo năm học</span>
          <Badge count={data.hoc_ky_list?.length || 0} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      }
      open={open}
      onCancel={onClose}
      width={1000}
      centered  // ⭐ THÊM DÒNG NÀY ĐỂ CANH GIỮA MODAL
      footer={[
        <Button
          key="export"
          icon={<FileExcelOutlined />}
          onClick={handleExportExcel}
          style={{ marginRight: 8, color: '#52c41a' }}
        >
          Xuất Excel
        </Button>,
        <Button key="close" onClick={onClose}>Đóng</Button>
      ]}
    >
      <Table
        rowKey="lop_hoc_id"
        columns={columns}
        dataSource={data.data || []}
        size="small"
        bordered
        pagination={false}
        scroll={{ x: 800 }}
        rowClassName={rowClassName}
      />
      <style>{`
        .row-top-1 td { background: #FFFDE7 !important; }
        .row-top-2 td { background: #F5F5F5 !important; }
        .row-top-3 td { background: #FFF8F0 !important; }
      `}</style>
    </Modal>
  )
}