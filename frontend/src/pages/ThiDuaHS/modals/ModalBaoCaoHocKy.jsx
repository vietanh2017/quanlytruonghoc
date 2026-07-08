// frontend/src/pages/ThiDuaHS/modals/ModalBaoCaoHocKy.jsx
import React from 'react'
import { Modal, Table, Tag, Badge, Space, Button, Tooltip, message } from 'antd'
import { TrophyOutlined, FileExcelOutlined } from '@ant-design/icons'
import { exportBaoCaoHocKy } from '../utils/excelExport'

export default function ModalBaoCaoHocKy({ open, onClose, data }) {
  if (!data) return null

  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      align: 'center',
      render: (_, __, i) => i + 1
    },
    {
      title: 'Lớp',
      dataIndex: 'ten_lop',
      fixed: 'left',
      width: 80,
      align: 'center'
    },
    {
      title: 'Khối',
      dataIndex: 'khoi',
      width: 60,
      align: 'center'
    },
    ...(data.thang_list?.map(t => ({
      title: t,
      dataIndex: ['cac_thang', t],
      width: 100,
      align: 'center',
      render: v => v?.toFixed(3) || '0.000'
    })) || []),
    {
      title: 'Trung bình',
      dataIndex: 'trung_binh',
      width: 100,
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

  // ⭐ Hàm xử lý xuất Excel
  const handleExportExcel = () => {
    if (!data.data || data.data.length === 0) {
      message.warning('Không có dữ liệu để xuất!')
      return
    }
    exportBaoCaoHocKy(data.data, data.hoc_ky, data.thang_list)
  }

  return (
    <Modal
      title={
        <Space>
          <TrophyOutlined style={{ color: '#faad14' }} />
          <span>Báo cáo học kỳ: {data.hoc_ky}</span>
          <Badge count={data.thang_list?.length || 0} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      }
      open={open}
      onCancel={onClose}
      width={950}
      centered  // ⭐ THÊM DÒNG NÀY ĐỂ CANH GIỮA
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