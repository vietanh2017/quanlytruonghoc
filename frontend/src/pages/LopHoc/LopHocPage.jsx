// frontend/src/pages/LopHoc/LopHocPage.jsx
import React, { useEffect, useState } from 'react'
import {
  Table, Button, Space, Tag, Modal, Form, Input,
  InputNumber, message, Popconfirm, Tooltip, Switch,
  Typography, Divider, Empty, Select, Card, Row, Col,
  Avatar, Badge, Statistic, DatePicker, Upload, Progress
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  ReloadOutlined, SearchOutlined, TeamOutlined,
  UserOutlined, BookOutlined, CheckCircleOutlined,
  CloseCircleOutlined, UserAddOutlined, ExportOutlined,
  MenuFoldOutlined, MenuUnfoldOutlined, FileExcelOutlined,
  InboxOutlined, DownloadOutlined
} from '@ant-design/icons'
import { lopHocApi } from '../../api/lopHoc'
import axios from 'axios'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const apiGV = axios.create({ baseURL: 'http://localhost:8000/api/v1/giao-vien' })

const { Title, Text } = Typography
const { Dragger } = Upload

export default function LopHocPage() {
  // ── Lớp học state ─────────────────────────────────────────
  const [dsLop, setDsLop] = useState([])
  const [loadingLop, setLoadingLop] = useState(false)
  const [selLop, setSelLop] = useState(null)
  const [searchLop, setSearchLop] = useState('')
  const [modalLop, setModalLop] = useState(false)
  const [editLop, setEditLop] = useState(null)
  const [formLop] = Form.useForm()
  const [isLopCompact, setIsLopCompact] = useState(false)

  // ── Học sinh state ─────────────────────────────────────────
  const [dsHs, setDsHs] = useState([])
  const [loadingHs, setLoadingHs] = useState(false)
  const [modalHs, setModalHs] = useState(false)
  const [editHs, setEditHs] = useState(null)
  const [formHs] = Form.useForm()

  // ── Import Excel state ────────────────────────────────────
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importResult, setImportResult] = useState(null)
  const [fileList, setFileList] = useState([])

  // ── Giáo viên state ───────────────────────────────────────
  const [dsGiaoVien, setDsGiaoVien] = useState([])

  // ── Load lớp học ──────────────────────────────────────────
  const loadLop = async () => {
    setLoadingLop(true)
    try {
      const res = await lopHocApi.getAll()
      setDsLop(res.data.items || [])
    } catch {
      message.error('Không thể tải danh sách lớp')
    } finally {
      setLoadingLop(false)
    }
  }

  // ── Load danh sách giáo viên ──────────────────────────────
  const loadGiaoVien = async () => {
    try {
      const res = await apiGV.get('/')
      setDsGiaoVien(res.data.items || [])
    } catch {
      message.error('Không thể tải danh sách giáo viên')
    }
  }

  useEffect(() => {
    loadLop()
    loadGiaoVien()
  }, [])

  // ── Load học sinh khi chọn lớp ────────────────────────────
  const loadHocSinh = async (lopId) => {
    setLoadingHs(true)
    try {
      const res = await lopHocApi.getHocSinh(lopId)
      setDsHs(res.data || [])
    } catch {
      message.error('Không thể tải danh sách học sinh')
    } finally {
      setLoadingHs(false)
    }
  }

  const onChonLop = (record) => {
    setSelLop(record)
    loadHocSinh(record.id)
    setIsLopCompact(true)
  }

  const onBoChonLop = () => {
    setSelLop(null)
    setDsHs([])
    setIsLopCompact(false)
  }

  // ── Lọc lớp ───────────────────────────────────────────────
  const filteredLop = dsLop.filter(l =>
    l.ma_lop.toLowerCase().includes(searchLop.toLowerCase()) ||
    l.ten_lop.toLowerCase().includes(searchLop.toLowerCase())
  )

  // ── Thống kê ──────────────────────────────────────────────
  const stats = {
    total: dsLop.length,
    active: dsLop.filter(l => l.active).length,
    inactive: dsLop.filter(l => !l.active).length,
    totalStudents: dsLop.reduce((sum, l) => sum + (l.si_so || 0), 0)
  }

  // ── CRUD Lớp ──────────────────────────────────────────────
  const handleThemLop = () => {
    setEditLop(null)
    formLop.resetFields()
    formLop.setFieldsValue({ khoi: 6, si_so: 0 })
    setModalLop(true)
  }

  const handleSuaLop = (record) => {
    setEditLop(record)
    formLop.setFieldsValue({
      ma_lop: record.ma_lop,
      ten_lop: record.ten_lop,
      khoi: record.khoi,
      si_so: record.si_so,
      giao_vien_cn_id: record.giao_vien_cn_id ?? null,
    })
    setModalLop(true)
  }

  const handleLuuLop = async () => {
    try {
      const values = await formLop.validateFields()
      if (editLop) {
        await lopHocApi.update(editLop.id, values)
        message.success('Cập nhật lớp thành công')
      } else {
        await lopHocApi.create(values)
        message.success('Thêm lớp thành công')
      }
      setModalLop(false)
      loadLop()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail) {
        if (Array.isArray(detail)) {
          const errorMsg = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
          message.error(errorMsg)
        } else {
          message.error(detail)
        }
      } else {
        message.error('Thao tác thất bại')
      }
    }
  }

  const handleXoaLop = async (id) => {
    try {
      await lopHocApi.delete(id)
      message.success('Đã xóa lớp')
      if (selLop?.id === id) { onBoChonLop() }
      loadLop()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  const handleToggleLop = async (id) => {
    try {
      await lopHocApi.toggleActive(id)
      loadLop()
    } catch { message.error('Thao tác thất bại') }
  }

  // ── CRUD Học sinh ──────────────────────────────────────────
  const handleThemHs = () => {
    setEditHs(null)
    formHs.resetFields()
    formHs.setFieldsValue({ gioi_tinh: true })
    setModalHs(true)
  }

  const handleSuaHs = (record) => {
    setEditHs(record)
    formHs.setFieldsValue({
      ma_hoc_sinh: record.ma_hoc_sinh,
      ho_ten: record.ho_ten,
      gioi_tinh: record.gioi_tinh ?? true,
      ngay_sinh: record.ngay_sinh ? dayjs(record.ngay_sinh) : null,
      so_dien_thoai: record.so_dien_thoai || '',
    })
    setModalHs(true)
  }

  const handleLuuHs = async () => {
    try {
      const values = await formHs.validateFields()

      const submitData = {
        ma_hoc_sinh: values.ma_hoc_sinh?.trim(),
        ho_ten: values.ho_ten?.trim(),
        gioi_tinh: values.gioi_tinh ?? true,
        so_dien_thoai: values.so_dien_thoai?.trim() || null,
      }

      if (values.ngay_sinh) {
        if (typeof values.ngay_sinh === 'object' && values.ngay_sinh.isValid) {
          submitData.ngay_sinh = values.ngay_sinh.format('YYYY-MM-DD')
        } else if (typeof values.ngay_sinh === 'string') {
          submitData.ngay_sinh = values.ngay_sinh
        }
      } else {
        submitData.ngay_sinh = null
      }

      if (editHs) {
        await lopHocApi.suaHocSinh(editHs.id, submitData)
        message.success('Cập nhật học sinh thành công')
      } else {
        await lopHocApi.themHocSinh(selLop.id, submitData)
        message.success('Thêm học sinh thành công')
      }
      setModalHs(false)
      loadHocSinh(selLop.id)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail) {
        if (Array.isArray(detail)) {
          const errorMsg = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
          message.error(errorMsg)
        } else if (typeof detail === 'string') {
          message.error(detail)
        } else {
          message.error('Có lỗi xảy ra khi cập nhật')
        }
      } else {
        message.error('Thao tác thất bại')
      }
    }
  }

  const handleXoaHs = async (hsId) => {
    try {
      await lopHocApi.xoaHocSinh(hsId)
      message.success('Đã xóa học sinh')
      loadHocSinh(selLop.id)
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ── Import Excel ────────────────────────────────────────────
  const handleImportExcel = async () => {
    if (fileList.length === 0) {
      message.warning('Vui lòng chọn file Excel')
      return
    }

    const file = fileList[0].originFileObj
    if (!file) {
      message.warning('File không hợp lệ')
      return
    }

    setImporting(true)
    setImportProgress(0)
    setImportResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('lop_hoc_id', selLop.id)

      const progressInterval = setInterval(() => {
        setImportProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await axios.post(
        'http://localhost:8000/api/v1/lop-hoc/import-hoc-sinh',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 30000
        }
      )

      clearInterval(progressInterval)
      setImportProgress(100)
      setImportResult(response.data)

      if (response.data.thanh_cong > 0) {
        message.success(`Đã import thành công ${response.data.thanh_cong} học sinh`)
      }
      if (response.data.that_bai > 0) {
        message.warning(`Có ${response.data.that_bai} dòng bị lỗi`)
      }

      setFileList([])
      loadHocSinh(selLop.id)

    } catch (error) {
      console.error('Import error:', error)
      const detail = error.response?.data?.detail
      if (detail) {
        message.error(typeof detail === 'string' ? detail : 'Import thất bại')
      } else {
        message.error('Import thất bại, vui lòng thử lại')
      }
    } finally {
      setImporting(false)
      setImportProgress(0)
    }
  }

  // ── Tải file mẫu ────────────────────────────────────────────
  const downloadSampleFile = () => {
    const sampleData = [
      ['Mã học sinh', 'Họ tên', 'Giới tính', 'Ngày sinh', 'Số điện thoại'],
      ['HS001', 'Nguyễn Văn A', 'Nam', '2000-01-01', '0901234567'],
      ['HS002', 'Trần Thị B', 'Nữ', '2000-02-02', '0909876543'],
      ['HS003', 'Lê Văn C', 'Nam', '2000-03-03', '0912345678'],
      ['HS004', 'Phạm Thị D', 'Nữ', '2000-04-04', '0923456789'],
    ]

    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet(sampleData)

    ws['!cols'] = [
      { wch: 15 },
      { wch: 25 },
      { wch: 15 },
      { wch: 15 },
      { wch: 18 },
    ]

    XLSX.utils.book_append_sheet(wb, ws, 'HocSinh')

    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { type: 'application/octet-stream' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Mau_import_hoc_sinh_${dayjs().format('YYYYMMDD')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)

    message.success('Đã tải file mẫu thành công!')
  }

  const uploadProps = {
    fileList,
    beforeUpload: (file) => {
      const isValidType = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.type === 'application/vnd.ms-excel' ||
        file.name.endsWith('.xlsx') ||
        file.name.endsWith('.xls')
      if (!isValidType) {
        message.error('Chỉ hỗ trợ file Excel (.xlsx, .xls)')
        return false
      }
      const isValidSize = file.size / 1024 / 1024 < 5
      if (!isValidSize) {
        message.error('File quá lớn (tối đa 5MB)')
        return false
      }
      setFileList([{
        uid: file.uid || '-1',
        name: file.name,
        status: 'done',
        originFileObj: file,
      }])
      return false
    },
    onRemove: () => {
      setFileList([])
    },
    maxCount: 1,
    accept: '.xlsx,.xls',
  }

  const renderImportResult = () => {
    if (!importResult) return null

    const { tong_so, thanh_cong, that_bai, chi_tiet, da_them } = importResult

    return (
      <Modal
        title="📊 Kết quả import"
        open={!!importResult}
        onCancel={() => setImportResult(null)}
        footer={[
          <Button key="close" onClick={() => setImportResult(null)}>
            Đóng
          </Button>
        ]}
        width={700}
      >
        <div style={{ marginBottom: 16 }}>
          <Space size="large">
            <div><strong>Tổng số:</strong> {tong_so}</div>
            <div style={{ color: '#52c41a' }}><strong>Thành công:</strong> {thanh_cong}</div>
            <div style={{ color: '#ff4d4f' }}><strong>Thất bại:</strong> {that_bai}</div>
          </Space>
        </div>

        {da_them?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <strong>✅ Đã thêm:</strong>
            <div style={{ maxHeight: 100, overflow: 'auto', background: '#f6ffed', padding: 8, borderRadius: 4 }}>
              {da_them.map((item, idx) => (
                <div key={idx}>
                  {item.ma_hoc_sinh} - {item.ho_ten}
                </div>
              ))}
            </div>
          </div>
        )}

        {chi_tiet?.length > 0 && (
          <div>
            <strong>❌ Lỗi:</strong>
            <div style={{ maxHeight: 200, overflow: 'auto', background: '#fff2f0', padding: 8, borderRadius: 4 }}>
              {chi_tiet.map((item, idx) => (
                <div key={idx} style={{ marginBottom: 4 }}>
                  <strong>Dòng {item.row}:</strong> {item.errors?.join('; ')}
                  <div style={{ fontSize: 12, color: '#999', marginLeft: 20 }}>
                    Dữ liệu: {JSON.stringify(item.data)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>
    )
  }

  // ── Cột bảng lớp (đầy đủ) ─────────────────────────────────
  const colLopFull = [
    {
      title: 'Mã lớp',
      dataIndex: 'ma_lop',
      width: 60,
      align: 'center',
      render: (text) => <Text strong style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Tên lớp',
      dataIndex: 'ten_lop',
      width: 80,
      align: 'center',
      render: (text, record) => (
        <Space size={6}>
          <Avatar size={20} icon={<BookOutlined />} style={{ backgroundColor: '#1890ff', flexShrink: 0 }} />
          <div style={{ minWidth: 0 }}>
            <div><Text strong style={{ fontSize: 13 }}>{text}</Text></div>
            <div><Text type="secondary" style={{ fontSize: 11 }}>Khối {record.khoi}</Text></div>
          </div>
        </Space>
      ),
      ellipsis: true
    },
    {
      title: 'Khối',
      dataIndex: 'khoi',
      width: 55,
      align: 'center',
      render: (text) => <Text style={{ fontSize: 13 }}>{text}</Text>
    },
    {
      title: 'Sĩ số',
      dataIndex: 'si_so',
      width: 40,
      align: 'center',
      render: (text) => <Tag color="blue" style={{ fontSize: 12, margin: 0 }}>{text}</Tag>
    },
    {
      title: 'GVCN',
      dataIndex: 'ten_gvcn',
      width: 150,
      render: (v) => v ? (
        <Space size={4}>
          <Avatar size={18} icon={<UserOutlined />} style={{ flexShrink: 0 }} />
          <span style={{ fontSize: 13, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {v}
          </span>
        </Space>
      ) : <Text type="secondary" style={{ fontSize: 13 }}>—</Text>,
      ellipsis: true
    },
    {
      title: 'Trạng thái',
      width: 80,
      align: 'center',
      render: (_, r) => (
        <Tag color={r.active ? 'success' : 'error'} style={{ fontSize: 12, margin: 0 }}>
          {r.active ? 'Hoạt động' : 'Vô hiệu'}
        </Tag>
      )
    },
    {
      title: 'Thao tác',
      width: 90,
      align: 'center',
      render: (_, r) => (
        <Space size={4} style={{ whiteSpace: 'nowrap' }}>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={e => { e.stopPropagation(); handleSuaLop(r) }} />
          </Tooltip>
          <Tooltip title={r.active ? 'Vô hiệu hóa' : 'Kích hoạt'}>
            <Switch size="small" checked={r.active} onChange={() => handleToggleLop(r.id)} />
          </Tooltip>
          <Tooltip title="Xóa">
            <Popconfirm title="Xác nhận xóa lớp?" onConfirm={() => { handleXoaLop(r.id) }}
              okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
              <Button size="small" danger icon={<DeleteOutlined />} onClick={e => e.stopPropagation()} />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    },
  ]

  // ── Cột bảng lớp (thu gọn) ─────────────────────────────────
  const colLopCompact = [
    {
      title: 'Mã',
      dataIndex: 'ma_lop',
      width: 70,
      render: (text) => <Text strong style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Tên lớp',
      dataIndex: 'ten_lop',
      render: (text, record) => (
        <div style={{ minWidth: 0 }}>
          <div><Text strong style={{ fontSize: 13 }}>{text}</Text></div>
          <div><Text type="secondary" style={{ fontSize: 11 }}>Khối {record.khoi}</Text></div>
        </div>
      ),
      ellipsis: true
    },
  ]

  // ── Cột bảng học sinh (đầy đủ - khi bảng trái thu gọn) ──
  const colHsFull = [
    {
      title: 'Mã HS',
      dataIndex: 'ma_hoc_sinh',
      width: 70,
      align: 'center',
      render: (text) => <Text strong style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Họ tên',
      dataIndex: 'ho_ten',
      width: 160,
      render: (text) => <Text style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Giới tính',
      dataIndex: 'gioi_tinh',
      width: 80,
      align: 'center',
      render: (v) => v ? (
        <Tag color="blue" style={{ fontSize: 12, margin: 0 }}>Nam</Tag>
      ) : (
        <Tag color="pink" style={{ fontSize: 12, margin: 0 }}>Nữ</Tag>
      )
    },
    {
      title: 'Ngày sinh',
      dataIndex: 'ngay_sinh',
      width: 110,
      align: 'center',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : <Text type="secondary">—</Text>
    },
    {
      title: 'SĐT',
      dataIndex: 'so_dien_thoai',
      width: 110,
      align: 'center',
      render: (v) => v || <Text type="secondary">—</Text>
    },
    {
      title: 'Thao tác',
      width: 80,
      align: 'center',
      render: (_, r) => (
        <Space size={4} style={{ whiteSpace: 'nowrap' }}>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => handleSuaHs(r)} />
          </Tooltip>
          <Tooltip title="Xóa">
            <Popconfirm title="Xác nhận xóa học sinh?" onConfirm={() => handleXoaHs(r.id)}
              okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    },
  ]

  // ── Cột bảng học sinh (thu gọn - khi bảng trái mở rộng) ──
  const colHsCompact = [
    {
      title: 'Mã HS',
      dataIndex: 'ma_hoc_sinh',
      width: 55,
      align: 'center',
      render: (text) => <Text strong style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Họ tên',
      dataIndex: 'ho_ten',
      width: 160,
      render: (text) => <Text style={{ fontSize: 13 }}>{text}</Text>,
      ellipsis: true
    },
    {
      title: 'Thao tác',
      width: 55,
      align: 'center',
      render: (_, r) => (
        <Space size={4} style={{ whiteSpace: 'nowrap' }}>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => handleSuaHs(r)} />
          </Tooltip>
          <Tooltip title="Xóa">
            <Popconfirm title="Xác nhận xóa học sinh?" onConfirm={() => handleXoaHs(r.id)}
              okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      )
    },
  ]

  // ── Chọn cột lớp dựa trên trạng thái thu gọn ──────────────
  const getLopColumns = () => {
    return isLopCompact ? colLopCompact : colLopFull
  }

  // ── Chọn cột học sinh dựa trên trạng thái ──────────────────
  const getHsColumns = () => {
    return isLopCompact ? colHsFull : colHsCompact
  }

  // ── Render ────────────────────────────────────────────────
  return (
    <div style={{ padding: 22, background: '#f0f2f5', minHeight: '100vh' }}>

      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', fontSize: 18, gap: 12 }}>
              <BookOutlined style={{ color: '#1890ff' }} />
              Quản lý Học Sinh
              <Badge count={stats.total} style={{ marginLeft: 12 }} />
            </Title>
          </Col>
          <Col>
            <Space size="middle" wrap>
              <Input
                placeholder="Tìm kiếm lớp học..."
                prefix={<SearchOutlined />}
                value={searchLop}
                onChange={e => setSearchLop(e.target.value)}
                style={{ width: 290 }}
                allowClear
                size="small"
              />
              <Button icon={<ReloadOutlined />} onClick={loadLop} size="small">
                Làm mới
              </Button>
              {selLop && (
                <Tooltip title={isLopCompact ? 'Mở rộng bảng lớp' : 'Thu gọn bảng lớp'}>
                  <Button
                    icon={isLopCompact ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                    onClick={() => setIsLopCompact(!isLopCompact)}
                    size="small"
                  >
                    {isLopCompact ? 'Mở rộng' : 'Thu gọn'}
                  </Button>
                </Tooltip>
              )}
              {selLop && (
                <Button onClick={onBoChonLop} size="small">
                  Bỏ chọn
                </Button>
              )}
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleThemLop}
                size="small"
              >
                Thêm lớp
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Thống kê */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Tổng số lớp"
              value={stats.total}
              prefix={<BookOutlined />}
              styles={{ content: { color: '#1890ff', fontSize: 16 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Đang hoạt động"
              value={stats.active}
              prefix={<CheckCircleOutlined />}
              styles={{ content: { color: '#52c41a', fontSize: 16 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Vô hiệu"
              value={stats.inactive}
              prefix={<CloseCircleOutlined />}
              styles={{ content: { color: '#ff4d4f', fontSize: 16 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Tổng học sinh"
              value={stats.totalStudents}
              prefix={<TeamOutlined />}
              styles={{ content: { color: '#faad14', fontSize: 16 } }}
            />
          </Card>
        </Col>
      </Row>

      {/* Main content */}
      <Card>
        <div style={{ display: 'flex', gap: 16, minHeight: 500 }}>

          {/* ── Bảng lớp học (trái) ── */}
          <div style={{
            flex: isLopCompact ? '0 0 200px' : '0 0 65%',
            minWidth: 0,
            transition: 'all 0.3s ease',
            overflow: 'hidden'
          }}>
            {/* ⭐ HEADER BẢNG LỚP - ĐÃ SỬA */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 12,
              padding: '0 4px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  fontWeight: 600,
                  fontSize: isLopCompact ? 15 : 15,
                  color: '#1a1a1a'
                }}>
                  {isLopCompact ? '📋 Lớp' : '🏫 Danh sách lớp học'}
                </span>
                <Badge
                  count={filteredLop.length}
                  style={{
                    backgroundColor: '#1890ff',
                    fontSize: isLopCompact ? 10 : 12
                  }}
                />
              </div>
              {isLopCompact && (
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {selLop?.ten_lop}
                </Text>
              )}
            </div>

            <Table
              rowKey="id"
              columns={getLopColumns()}
              dataSource={filteredLop}
              loading={loadingLop}
              size={isLopCompact ? 'small' : 'middle'}
              bordered
              pagination={isLopCompact ? false : {
                pageSize: 8,
                showTotal: t => `Tổng: ${t} lớp`,
                showSizeChanger: true,
                showQuickJumper: true
              }}
              rowClassName={r => r.id === selLop?.id ? 'ant-table-row-selected' : ''}
              onRow={r => ({
                onClick: () => onChonLop(r),
                style: { cursor: 'pointer' }
              })}
            />
          </div>

          {/* Divider */}
          <Divider orientation="vertical" style={{ height: 'auto', margin: '0 8px' }} />

          {/* ── Bảng học sinh (phải) ── */}
          <div style={{
            flex: isLopCompact ? 1 : '0 0 32%',
            minWidth: 0,
            transition: 'all 0.3s ease',
            overflow: 'hidden'
          }}>
            {/* ⭐ HEADER BẢNG HỌC SINH - ĐÃ SỬA */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',

              marginBottom: 12,
              padding: '0 4px',
              flexWrap: 'nowrap',
              gap: 8
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 1, minWidth: 0 }}>
                <span style={{
                  fontWeight: 600,
                  fontSize: isLopCompact ? 15 : 15, whiteSpace: 'nowrap',
                  color: '#1a1a1a'
                }}>
                  👨‍🎓 {selLop ? `Học sinh lớp ${selLop.ten_lop}` : 'Chọn lớp để xem học sinh'}
                </span>
                {selLop && (
                  <Badge
                    count={dsHs.length}
                    style={{
                      backgroundColor: '#52c41a',
                      fontSize: isLopCompact ? 10 : 12
                    }}
                  />
                )}
              </div>
              {selLop && (
                <Space size={4}>
                  <Tooltip title="Xuất Excel">
                    <Button
                      icon={<ExportOutlined />}
                      size={isLopCompact ? 'small' : 'middle'}
                    />
                  </Tooltip>
                  <Button
                    icon={<FileExcelOutlined />}
                    onClick={() => setImportModalVisible(true)}
                    size={isLopCompact ? 'small' : 'middle'}
                    style={{ color: '#52c41a', borderColor: '#52c41a' }}
                  >
                    {isLopCompact ? 'Import' : 'Import Excel'}
                  </Button>
                  <Button
                    type="primary"
                    icon={<UserAddOutlined />}
                    onClick={handleThemHs}
                    size={isLopCompact ? 'small' : 'middle'}
                  >
                    {isLopCompact ? 'Thêm' : 'Thêm HS'}
                  </Button>
                </Space>
              )}
            </div>

            {selLop ? (
              <Table
                rowKey="id"
                columns={getHsColumns()}
                dataSource={dsHs}
                loading={loadingHs}
                size={isLopCompact ? 'small' : 'middle'}
                bordered
                pagination={{
                  pageSize: isLopCompact ? 15 : 8,
                  showTotal: t => `Tổng: ${t} học sinh`,
                  showSizeChanger: true,
                  showQuickJumper: true
                }}
              />
            ) : (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 300
              }}>
                <Empty
                  description="Chọn một lớp để xem học sinh"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              </div>
            )}
          </div>

        </div>
      </Card>

      {/* ── Modal lớp học ── */}
      <Modal
        title={
          <Space>
            {editLop ? <EditOutlined /> : <PlusOutlined />}
            <span>{editLop ? '✏️ Sửa lớp học' : '➕ Thêm lớp học mới'}</span>
          </Space>
        }
        open={modalLop}
        onOk={handleLuuLop}
        onCancel={() => setModalLop(false)}
        okText={editLop ? 'Cập nhật' : 'Thêm'}
        cancelText="Hủy"
        width={560}
        okButtonProps={{ size: 'large' }}
        cancelButtonProps={{ size: 'large' }}
      >
        <Form form={formLop} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="ma_lop"
                label="Mã lớp"
                rules={[{ required: true, message: 'Nhập mã lớp' }]}
              >
                <Input placeholder="VD: 10A1" size="large" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="ten_lop"
                label="Tên lớp"
                rules={[{ required: true, message: 'Nhập tên lớp' }]}
              >
                <Input placeholder="VD: Lớp 10A1" size="large" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="khoi"
                label="Khối"
                rules={[{ required: true, message: 'Nhập khối' }]}
              >
                <InputNumber min={1} max={12} style={{ width: '100%' }} placeholder="10" size="large" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="si_so" label="Sĩ số">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="0" size="large" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="giao_vien_cn_id" label="Giáo viên chủ nhiệm">
            <Select
              placeholder="-- Chọn giáo viên chủ nhiệm --"
              allowClear
              showSearch
              optionFilterProp="label"
              size="large"
              options={dsGiaoVien
                .filter(gv => gv.active)
                .map(gv => ({
                  value: gv.id,
                  label: `${gv.nguoi_dung?.ho_ten || ''} (${gv.ma_giao_vien})`,
                }))}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* ── Modal học sinh ── */}
      <Modal
        title={
          <Space>
            {editHs ? <EditOutlined /> : <PlusOutlined />}
            <span>{editHs ? '✏️ Sửa học sinh' : '➕ Thêm học sinh mới'}</span>
          </Space>
        }
        open={modalHs}
        onOk={handleLuuHs}
        onCancel={() => setModalHs(false)}
        okText={editHs ? 'Cập nhật' : 'Thêm'}
        cancelText="Hủy"
        width={560}
        okButtonProps={{ size: 'large' }}
        cancelButtonProps={{ size: 'large' }}
      >
        <Form form={formHs} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="ma_hoc_sinh"
            label="Mã học sinh"
            rules={[{ required: true, message: 'Nhập mã học sinh' }]}
          >
            <Input placeholder="VD: HS001" size="large" />
          </Form.Item>

          <Form.Item
            name="ho_ten"
            label="Họ tên"
            rules={[{ required: true, message: 'Nhập họ tên' }]}
          >
            <Input placeholder="Nguyễn Văn A" size="large" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="gioi_tinh" label="Giới tính">
                <Select placeholder="Chọn giới tính" size="large" allowClear>
                  <Select.Option value={true}>Nam</Select.Option>
                  <Select.Option value={false}>Nữ</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="ngay_sinh" label="Ngày sinh">
                <DatePicker
                  style={{ width: '100%' }}
                  size="large"
                  format="DD/MM/YYYY"
                  placeholder="Chọn ngày sinh"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="so_dien_thoai" label="Số điện thoại">
            <Input placeholder="0901234567" size="large" />
          </Form.Item>
        </Form>
      </Modal>

      {/* ── Modal Import Excel ── */}
      <Modal
        title={
          <Space>
            <FileExcelOutlined style={{ color: '#52c41a' }} />
            <span>Import học sinh từ Excel</span>
          </Space>
        }
        open={importModalVisible}
        onCancel={() => {
          setImportModalVisible(false)
          setFileList([])
          setImportResult(null)
          setImportProgress(0)
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setImportModalVisible(false)
            setFileList([])
            setImportResult(null)
            setImportProgress(0)
          }}>
            Hủy
          </Button>,
          <Button
            key="download-sample"
            icon={<DownloadOutlined />}
            onClick={downloadSampleFile}
          >
            Tải file mẫu
          </Button>,
          <Button
            key="import"
            type="primary"
            icon={<FileExcelOutlined />}
            onClick={handleImportExcel}
            loading={importing}
            disabled={fileList.length === 0 || importing}
            style={{ background: '#52c41a' }}
          >
            Import
          </Button>
        ]}
        width={600}
      >
        <div style={{ padding: '16px 0' }}>
          <p style={{ marginBottom: 16 }}>
            <strong>Hướng dẫn:</strong> File Excel cần có các cột sau (hàng đầu là tiêu đề):
          </p>
          <ul style={{ marginBottom: 16 }}>
            <li><strong>Mã học sinh</strong> (bắt buộc) - VD: HS001</li>
            <li><strong>Họ tên</strong> (bắt buộc) - VD: Nguyễn Văn A</li>
            <li><strong>Giới tính</strong> - Nhập "Nam" hoặc "Nữ" (hoặc True/False)</li>
            <li><strong>Ngày sinh</strong> - Định dạng YYYY-MM-DD hoặc DD/MM/YYYY</li>
            <li><strong>Số điện thoại</strong> - 10-11 chữ số</li>
          </ul>

          <div style={{ marginBottom: 16, background: '#f6ffed', padding: 12, borderRadius: 4, border: '1px solid #b7eb8f' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              💡 <strong>Lưu ý:</strong> Click vào nút <strong>"Tải file mẫu"</strong> để tải file Excel mẫu về máy, sau đó điền dữ liệu và upload lên.
            </Text>
          </div>

          {importing && (
            <div style={{ marginBottom: 16 }}>
              <Progress percent={importProgress} status="active" />
              <span style={{ fontSize: 12, color: '#999' }}>Đang xử lý file...</span>
            </div>
          )}

          <Dragger {...uploadProps} disabled={importing}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Kéo thả file Excel vào đây hoặc click để chọn</p>
            <p className="ant-upload-hint">
              Hỗ trợ file .xlsx, .xls (tối đa 5MB)
            </p>
          </Dragger>

          {fileList.length > 0 && (
            <div style={{ marginTop: 12, color: '#52c41a' }}>
              ✅ Đã chọn file: {fileList[0].name}
            </div>
          )}
        </div>
      </Modal>

      {/* ── Modal kết quả import ── */}
      {renderImportResult()}

    </div>
  )
}