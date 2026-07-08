// frontend/src/pages/ThiDuaHS/tables/BangDiemTuan.jsx
import React from 'react'
import { Table, Tag, Typography, Card, Button, Input, InputNumber, Tooltip, message } from 'antd'
import { SaveOutlined, FileExcelOutlined } from '@ant-design/icons'
import { getColorByScore } from '../utils/constants'
import { exportDiemTuan } from '../utils/excelExport'

const { Text } = Typography

export default function BangDiemTuan({
  data,
  loading,
  onSave,
  setData,
  setSaved,
  tuan,
  namHoc,
  saving
}) {
  // ⭐ Hàm tính xếp hạng
  const getRanking = (data) => {
    if (!data || data.length === 0) return data

    const sorted = [...data].sort((a, b) => {
      const aTB = ((a.diem_hoc_tap || 0) * 2 + (a.diem_doi || 0)) / 3
      const bTB = ((b.diem_hoc_tap || 0) * 2 + (b.diem_doi || 0)) / 3
      return bTB - aTB
    })

    let rank = 1
    let prevTB = null
    let sameRankCount = 0
    const result = data.map(item => ({ ...item }))

    for (let i = 0; i < sorted.length; i++) {
      const item = sorted[i]
      const currentTB = ((item.diem_hoc_tap || 0) * 2 + (item.diem_doi || 0)) / 3

      if (i === 0) {
        prevTB = currentTB
        rank = 1
        sameRankCount = 1
      } else if (currentTB === prevTB) {
        sameRankCount++
      } else {
        rank += sameRankCount
        sameRankCount = 1
        prevTB = currentTB
      }

      const target = result.find(r => r.lop_hoc_id === item.lop_hoc_id)
      if (target) {
        target.xep_hang = rank
      }
    }

    return result
  }

  // ⭐ Hàm xử lý thay đổi điểm
  const handleDiemChange = (value, record) => {
    const newVal = value !== null && value !== undefined ? parseFloat(value) || 0 : 0

    // ⭐ LOG để debug
    console.log(`📝 Lớp ${record.ten_lop} (ID: ${record.lop_hoc_id}): nhập điểm = ${newVal}`)

    setData(prev => prev.map(d =>
      d.lop_hoc_id === record.lop_hoc_id
        ? { ...d, diem_hoc_tap: newVal }
        : d
    ))
    setSaved(false)
  }

  const columns = [
    {
      title: 'Lớp',
      dataIndex: 'ten_lop',
      width: 60,
      fixed: 'left',
      align: 'center',
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: 'Khối',
      dataIndex: 'khoi',
      width: 50,
      align: 'center',
    },
    {
      title: 'TB điểm đội',
      dataIndex: 'diem_doi',
      width: 70,
      align: 'center',
      render: (v, record) => {
        const value = record.diem_doi_tb !== undefined ? record.diem_doi_tb : v
        const displayValue = value !== undefined && value !== null ? value.toFixed(3) : '0.000'
        return <Tag color={getColorByScore(parseFloat(displayValue))}>{displayValue}</Tag>
      },
    },
    {
      title: 'Điểm HT (SĐB)',
      dataIndex: 'diem_hoc_tap',
      width: 80,
      align: 'center',
      render: (v, r) => (
        <InputNumber
          size="small"
          min={0}
          max={10}
          step={0.5}
          value={v ?? 0}
          style={{ width: 65, fontSize: 11.5 }}
          formatter={value => {
            if (value === undefined || value === null || value === '') return '0.000'
            return parseFloat(value).toFixed(3)
          }}
          parser={value => {
            if (!value) return 0
            return parseFloat(value.replace(/,/g, ''))
          }}
          onChange={(val) => handleDiemChange(val, r)}
          onBlur={(e) => {
            // ⭐ Đảm bảo lưu khi rời khỏi ô
            const val = parseFloat(e.target.value)
            if (!isNaN(val) && val !== r.diem_hoc_tap) {
              console.log(`📝 Lớp ${r.ten_lop}: onBlur lưu = ${val}`)
              handleDiemChange(val, r)
            }
          }}
          onFocus={(e) => e.target.select()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === 'Tab') {
              e.preventDefault()
              // ⭐ Lưu giá trị hiện tại trước khi chuyển ô
              const val = parseFloat(e.target.value)
              if (!isNaN(val) && val !== r.diem_hoc_tap) {
                console.log(`📝 Lớp ${r.ten_lop}: Enter/Tab lưu = ${val}`)
                handleDiemChange(val, r)
              }
              e.target.select()
              const inputs = document.querySelectorAll('.ant-input-number-input')
              const currentIndex = Array.from(inputs).indexOf(e.target)
              const nextIndex = currentIndex + 1
              if (nextIndex < inputs.length) {
                setTimeout(() => inputs[nextIndex].focus(), 10)
              }
            }
          }}
        />
      )
    },
    {
      title: 'Trung bình',
      dataIndex: 'trung_binh',
      width: 80,
      align: 'center',
      render: (v, record) => {
        const diemHT = record.diem_hoc_tap || 0
        const diemDoi = record.diem_doi || 0
        const trungBinh = ((diemHT * 2) + diemDoi) / 3
        const displayValue = trungBinh !== undefined && trungBinh !== null ? trungBinh.toFixed(3) : '0.000'
        return <Tag color={getColorByScore(parseFloat(displayValue))}>{displayValue}</Tag>
      },
    },
    {
      title: 'Xếp hạng',
      key: 'xep_hang',
      width: 65,
      align: 'center',
      render: (_, record) => {
        const dataWithRank = getRanking(data)
        const item = dataWithRank.find(d => d.lop_hoc_id === record.lop_hoc_id)
        return <Text strong style={{ fontStyle: 'italic', fontSize: 12 }}>{item?.xep_hang || '—'}</Text>
      },
    },
    {
      title: 'Ghi chú',
      dataIndex: 'ghi_chu',
      width: 80,
      render: (v, r) => (
        <Input
          size="small"
          value={v || ''}
          placeholder="..."
          onChange={e => {
            setData(prev => prev.map(d =>
              d.lop_hoc_id === r.lop_hoc_id ? { ...d, ghi_chu: e.target.value } : d
            ))
            setSaved(false)
          }}
        />
      )
    },
  ]

  // ⭐ Xuất Excel
  const handleExportExcel = () => {
    if (!data || data.length === 0) {
      message.warning('Không có dữ liệu để xuất!')
      return
    }
    const dataWithRank = getRanking(data)
    exportDiemTuan(dataWithRank, tuan, namHoc)
  }

  return (
    <Card
      title={`📋 Điểm thi đua tuần`}
      size="small"
      extra={
        <div style={{ display: 'flex', gap: 8 }}>
          <Tooltip title="Xuất Excel">
            <Button
              size="small"
              icon={<FileExcelOutlined />}
              onClick={handleExportExcel}
              style={{ color: '#52c41a' }}
            />
          </Tooltip>
          <Button
            size="small"
            icon={<SaveOutlined />}
            type="primary"
            loading={saving}
            disabled={saving}
            onClick={onSave}
          >
            Lưu điểm HT
          </Button>
        </div>
      }
    >
      <Table
        rowKey="lop_hoc_id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="small"
        bordered
        pagination={false}
        scroll={{ y: 400 }}
        locale={{ emptyText: 'Không có dữ liệu' }}
      />
    </Card>
  )
}