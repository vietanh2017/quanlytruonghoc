// frontend/src/pages/GiaoVien/GiaoVienPage.jsx
import React, { useEffect, useState } from 'react'
import {
  Table, Button, Space, Tag, Modal, Form, Input,
  message, Popconfirm, Tooltip, Switch, Typography, Select,
  Upload, Progress, Card, Row, Col, Statistic, Badge
} from 'antd'
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  ReloadOutlined, KeyOutlined, SearchOutlined,
  FileExcelOutlined, InboxOutlined, DownloadOutlined,
  UserOutlined, BookOutlined, CheckCircleOutlined,
  CloseCircleOutlined, TeamOutlined
} from '@ant-design/icons'
import axios from 'axios'
import { giaoVienApi } from '../../api/giaoVien'
import * as XLSX from 'xlsx'
import dayjs from 'dayjs'

const apiCauHinh = axios.create({ baseURL: 'http://localhost:8000/api/v1/cau-hinh' })

const { Title, Text } = Typography
const { Dragger } = Upload

// ⭐ DANH SÁCH KIÊM NHIỆM
const KIEM_NHIEM_LIST = [
  { value: '', label: '-- Không có --' },
  { value: 'Tổ trưởng CM', label: 'Tổ trưởng CM' },
  { value: 'Tổ phó CM', label: 'Tổ phó CM' },
  { value: 'Bí thư Đoàn', label: 'Bí thư Đoàn' },
  { value: 'Phó BT Đoàn', label: 'Phó BT Đoàn' },
  { value: 'TPT Đội', label: 'TPT Đội' },
  { value: 'Nữ công', label: 'Nữ công' },
  { value: 'Phòng bộ môn', label: 'Phòng bộ môn' },
  { value: 'TK hội đồng', label: 'TK hội đồng' },
  { value: 'Thủ quỹ', label: 'Thủ quỹ' },
  { value: 'YT học đường', label: 'YT học đường' },
  { value: 'Khác', label: 'Khác' },
]
// frontend/src/pages/GiaoVien/GiaoVienPage.jsx

// ⭐ THÊM MAP SỐ TIẾT GIẢM
const SO_TIET_GIAM = {
  'Tổ trưởng CM': 2,
  'Tổ phó CM': 1,
  'Bí thư Đoàn': 2,
  'Phó BT Đoàn': 1,
  'TPT Đội': 2,
  'Nữ công': 2,
  'Phòng bộ môn': 3,
  'TK hội đồng': 1,
  'Thủ quỹ': 1,
  'YT đường': 2,
  'Khác': 1,
}

export default function GiaoVienPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editItem, setEditItem] = useState(null)
  const [search, setSearch] = useState('')
  const [danhSachTo, setDanhSachTo] = useState([])
  const [form] = Form.useForm()

  // ── State cho import Excel ──────────────────────────────────
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState(null)
  const [importProgress, setImportProgress] = useState(0)
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [fileList, setFileList] = useState([])

  // ── Tải dữ liệu ────────────────────────────────────────────
  const loadData = async () => {
    setLoading(true)
    try {
      const res = await giaoVienApi.getAll()
      setData(res.data.items || [])
    } catch {
      message.error('Không thể tải danh sách giáo viên')
    } finally {
      setLoading(false)
    }
  }

  // ── Tải danh sách tổ chuyên môn ────────────────────────────
  const loadDanhSachTo = async () => {
    try {
      const res = await apiCauHinh.get('/to-chuyen-mon')
      setDanhSachTo(Array.isArray(res.data) ? res.data : (res.data.items || []))
    } catch {
      message.error('Không thể tải danh sách tổ chuyên môn')
    }
  }

  useEffect(() => {
    loadData()
    loadDanhSachTo()
  }, [])

  // ── Lọc tìm kiếm ───────────────────────────────────────────
  const filtered = data.filter(gv =>
    gv.ma_giao_vien.toLowerCase().includes(search.toLowerCase()) ||
    gv.nguoi_dung?.ho_ten.toLowerCase().includes(search.toLowerCase()) ||
    gv.mon_day?.toLowerCase().includes(search.toLowerCase()) ||
    (gv.kiem_nhiem || '').toLowerCase().includes(search.toLowerCase())  // ⭐ THÊM TÌM THEO KIÊM NHIỆM
  )

  // ── Thống kê ──────────────────────────────────────────────
  const stats = {
    total: data.length,
    active: data.filter(gv => gv.active).length,
    inactive: data.filter(gv => !gv.active).length,
  }

  // ── Mở modal thêm mới ──────────────────────────────────────
  const handleThem = () => {
    setEditItem(null)
    form.resetFields()
    setModalOpen(true)
  }

  // ── Mở modal sửa ───────────────────────────────────────────
  const handleSua = (record) => {
    setEditItem(record)
    form.setFieldsValue({
      ho_ten: record.nguoi_dung?.ho_ten,
      email: record.nguoi_dung?.email,
      ma_giao_vien: record.ma_giao_vien,
      mon_day: record.mon_day,
      so_dien_thoai: record.so_dien_thoai,
      to_id: record.to_chuyen_mon?.id ?? null,
      kiem_nhiem: record.kiem_nhiem || '',  // ⭐ THÊM
    })
    setModalOpen(true)
  }

  // ── Lưu (thêm hoặc sửa) ────────────────────────────────────
  const handleLuu = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ma_giao_vien: values.ma_giao_vien,
        ho_ten: values.ho_ten,
        email: values.email,
        mon_day: values.mon_day || '',
        so_dien_thoai: values.so_dien_thoai || '',
        to_id: values.to_id || null,
        kiem_nhiem: values.kiem_nhiem || '',  // ⭐ THÊM DÒNG NÀY
        active: true,
      }

      if (editItem) {
        await giaoVienApi.update(editItem.id, payload)
        message.success('Cập nhật giáo viên thành công')
      } else {
        await giaoVienApi.create(payload)
        message.success('Thêm giáo viên thành công')
      }
      setModalOpen(false)
      loadData()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail) message.error(detail)
    }
  }
  // ── Xóa ────────────────────────────────────────────────────
  const handleXoa = async (id) => {
    try {
      await giaoVienApi.delete(id)
      message.success('Đã xóa giáo viên')
      loadData()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ── Bật/tắt trạng thái ─────────────────────────────────────
  const handleToggle = async (id) => {
    try {
      await giaoVienApi.toggleActive(id)
      loadData()
    } catch {
      message.error('Thao tác thất bại')
    }
  }

  // ── Đặt lại mật khẩu ───────────────────────────────────────
  const handleResetPwd = async (id) => {
    try {
      await giaoVienApi.resetPassword(id)
      message.success('Đã đặt lại mật khẩu về: eduschool@123')
    } catch {
      message.error('Thao tác thất bại')
    }
  }

  // ── Tải file mẫu ────────────────────────────────────────────
  const downloadSampleFile = () => {
    const toList = danhSachTo.map(to => to.ten_to)
    const defaultTo = toList.length > 0 ? toList[0] : 'Tổ Toán'

    // ⭐ THÊM CỘT KIÊM NHIỆM VÀO FILE MẪU
    const sampleData = [
      ['Mã giáo viên', 'Họ tên', 'Email', 'Mật khẩu', 'Môn dạy', 'Số điện thoại', 'Tổ chuyên môn', 'Kiêm nhiệm', 'Trạng thái'],
      ['GV001', 'Nguyễn Văn A', 'a.nguyen@school.com', 'eduschool@123', 'Toán', '0901234567', defaultTo, 'Tổ trưởng chuyên môn', 'Hoạt động'],
      ['GV002', 'Trần Thị B', 'b.tran@school.com', 'eduschool@123', 'Văn', '0909876543', toList.length > 1 ? toList[1] : defaultTo, 'Bí thư Đoàn', 'Hoạt động'],
      ['GV003', 'Lê Văn C', 'c.le@school.com', 'eduschool@123', 'Anh', '0912345678', toList.length > 2 ? toList[2] : defaultTo, '', 'Hoạt động'],
      ['GV004', 'Phạm Thị D', 'd.pham@school.com', 'eduschool@123', 'Lý', '0923456789', toList.length > 3 ? toList[3] : defaultTo, '', 'Vô hiệu'],
    ]

    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet(sampleData)

    ws['!cols'] = [
      { wch: 15 },
      { wch: 25 },
      { wch: 30 },
      { wch: 20 },
      { wch: 15 },
      { wch: 18 },
      { wch: 20 },
      { wch: 10 },  // ⭐ CỘT KIÊM NHIỆM
      { wch: 15 },
    ]

    XLSX.utils.book_append_sheet(wb, ws, 'GiaoVien')

    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { type: 'application/octet-stream' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Mau_import_giao_vien_${dayjs().format('YYYYMMDD')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)

    message.success('Đã tải file mẫu thành công!')
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
      const progressInterval = setInterval(() => {
        setImportProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const result = await giaoVienApi.importExcel(file)
      clearInterval(progressInterval)
      setImportProgress(100)

      setImportResult(result)

      if (result.thanh_cong > 0) {
        message.success(`Đã import thành công ${result.thanh_cong} giáo viên`)
      }

      if (result.that_bai > 0) {
        message.warning(`Có ${result.that_bai} dòng bị lỗi, vui lòng kiểm tra chi tiết`)
      }

      setFileList([])
      setImportModalVisible(false)
      loadData()

    } catch (error) {
      message.error(error.response?.data?.detail || 'Import thất bại')
    } finally {
      setImporting(false)
      setImportProgress(0)
    }
  }

  // ── Render kết quả import ──────────────────────────────────
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
        <div style={{ marginBottom: 8 }}>
          <Space size="large">
            <div><strong>Tổng số:</strong> {tong_so}</div>
            <div style={{ color: '#52c41a' }}><strong>Thành công:</strong> {thanh_cong}</div>
            <div style={{ color: '#ff4d4f' }}><strong>Thất bại:</strong> {that_bai}</div>
          </Space>
        </div>

        {da_them?.length > 0 && (
          <div style={{ marginBottom: 8 }}>
            <strong>✅ Đã thêm:</strong>
            <div style={{ maxHeight: 100, overflow: 'auto', background: '#f6ffed', padding: 8, borderRadius: 4 }}>
              {da_them.map((item, idx) => (
                <div key={idx}>
                  {item.ma_giao_vien} - {item.ho_ten} ({item.email})
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

  // ⭐ THÊM CỘT KIÊM NHIỆM VÀO BẢNG
  const columns = [
    {
      title: 'Mã GV',
      dataIndex: 'ma_giao_vien',
      width: 80, align: 'center',
      sorter: (a, b) => a.ma_giao_vien.localeCompare(b.ma_giao_vien),
    },
    {
      title: 'Họ tên',
      width: 190,
      render: (_, r) => r.nguoi_dung?.ho_ten || '—',
      sorter: (a, b) =>
        (a.nguoi_dung?.ho_ten || '').localeCompare(b.nguoi_dung?.ho_ten || ''),
    },
    {
      title: 'Email', width: 90,
      render: (_, r) => r.nguoi_dung?.email || '—',
    },
    {
      title: 'Môn dạy', align: 'center', width: 90,
      dataIndex: 'mon_day',
    },
    {
      title: 'Tổ CM',
      width: 90, align: 'center',
      render: (_, r) => r.to_chuyen_mon?.ten_to || '—',
    },
    // ⭐ THÊM CỘT KIÊM NHIỆM
    {
      title: 'Kiêm nhiệm',
      width: 60, align: 'center',
      dataIndex: 'kiem_nhiem',
      render: (v) => v ? <Tag color="purple">{v}</Tag> : <Tag color="default">—</Tag>,
    },
    {
      title: 'Tiết giảm',
      width: 50, align: 'center',
      render: (_, r) => {
        const giam = SO_TIET_GIAM[r.kiem_nhiem] || 0
        return giam > 0 ? <Tag color="orange">{giam}</Tag> : <Tag>0</Tag>
      },
    },
    {
      title: 'Trạng thái',
      align: 'center',
      render: (_, r) => (
        <Tag color={r.active ? 'green' : 'red'}>
          {r.active ? 'Hoạt động' : 'Vô hiệu'}
        </Tag>
      ),
      width: 90,
    },
    {
      title: 'Thao tác', align: 'center',
      width: 140,
      render: (_, r) => (
        <Space size={4}>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />}
              onClick={() => handleSua(r)} />
          </Tooltip>

          <Tooltip title={r.active ? 'Vô hiệu hóa' : 'Kích hoạt'}>
            <Switch size="small" checked={r.active}
              onChange={() => handleToggle(r.id)} />
          </Tooltip>

          <Tooltip title="Đặt lại mật khẩu">
            <Popconfirm title="Đặt lại mật khẩu về mặc định?"
              onConfirm={() => handleResetPwd(r.id)} okText="Đồng ý" cancelText="Hủy">
              <Button size="small" icon={<KeyOutlined />} />
            </Popconfirm>
          </Tooltip>

          <Tooltip title="Xóa">
            <Popconfirm title="Xác nhận xóa giáo viên này?"
              onConfirm={() => handleXoa(r.id)} okText="Xóa" cancelText="Hủy"
              okButtonProps={{ danger: true }}>
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ]

  const uploadProps = {
    fileList,

    beforeUpload: (file) => {
      const isValidType =
        file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.type === 'application/vnd.ms-excel' ||
        file.name.endsWith('.xlsx') ||
        file.name.endsWith('.xls')

      if (!isValidType) {
        message.error('Chỉ hỗ trợ file Excel (.xlsx, .xls)')
        return false
      }
      if (file.size / 1024 / 1024 >= 5) {
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
    disabled: importing,
  }

  // ── Render ──────────────────────────────────────────────────
  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>

      {/* Header */}
      <Card style={{ marginBottom: 8 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', fontSize: 18, gap: 12 }}>
              <BookOutlined style={{ color: '#1890ff' }} />
              Quản lý Giáo Viên
              <Badge count={stats.total} style={{ marginLeft: 10 }} />
            </Title>
          </Col>
          <Col>
            <Space size="middle" wrap>
              <Input
                placeholder="Tìm theo mã, tên, môn, kiêm nhiệm..."
                prefix={<SearchOutlined />}
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ width: 290 }}
                allowClear
                size="small"
              />
              <Button
                icon={<FileExcelOutlined />}
                onClick={() => setImportModalVisible(true)}
                size="small"
                style={{ color: '#52c41a', borderColor: '#52c41a' }}
              >
                Import Excel
              </Button>
              <Button icon={<ReloadOutlined />} onClick={loadData} size="small">
                Làm mới
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleThem} size="small">
                Thêm giáo viên
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Thống kê */}
      <Row gutter={[16, 12]} style={{ marginBottom: 8 }}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Tổng số giáo viên"
              value={stats.total}
              prefix={<UserOutlined />}
              styles={{ content: { color: '#1890ff', fontSize: 16 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Đang hoạt động"
              value={stats.active}
              prefix={<CheckCircleOutlined />}
              styles={{ content: { color: '#52c41a', fontSize: 16 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Vô hiệu"
              value={stats.inactive}
              prefix={<CloseCircleOutlined />}
              styles={{ content: { color: '#ff4d4f', fontSize: 16 } }}
            />
          </Card>
        </Col>
      </Row>

      {/* Progress khi import */}
      {importing && (
        <div style={{ marginBottom: 8 }}>
          <Progress percent={importProgress} status="active" />
          <span style={{ fontSize: 12, color: '#999' }}>
            Đang xử lý file Excel...
          </span>
        </div>
      )}

      {/* Bảng dữ liệu */}
      <Card>
        <Table
          rowKey="id"
          columns={columns}
          dataSource={filtered}
          loading={loading}
          pagination={{ pageSize: 13, showTotal: (t) => `Tổng: ${t} giáo viên` }}
          size="middle"
          bordered
        />
      </Card>

      {/* ── Modal Import Excel ── */}
      <Modal
        title={
          <Space>
            <FileExcelOutlined style={{ color: '#52c41a' }} />
            <span>Import giáo viên từ Excel</span>
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
        centered
      >
        <div style={{ padding: '14px 0' }}>
          <p style={{ marginBottom: 8 }}>
            <strong>Hướng dẫn:</strong> File Excel cần có các cột sau (hàng đầu là tiêu đề):
          </p>
          <ul style={{ marginBottom: 8 }}>
            <li><strong>Mã giáo viên</strong> (bắt buộc) - VD: GV001</li>
            <li><strong>Họ tên</strong> (bắt buộc) - VD: Nguyễn Văn A</li>
            <li><strong>Email</strong> (bắt buộc) - VD: a.nguyen@school.com</li>
            <li><strong>Mật khẩu</strong> - Mặc định: eduschool@123</li>
            <li><strong>Môn dạy</strong> - VD: Toán</li>
            <li><strong>Số điện thoại</strong> - 10-11 chữ số</li>
            <li><strong>Tổ chuyên môn</strong> - Tên tổ đã có trong hệ thống</li>
            <li><strong>Kiêm nhiệm</strong> - VD: Tổ trưởng, Bí thư Đoàn...</li>  {/* ⭐ THÊM */}
            <li><strong>Trạng thái</strong> - "Hoạt động" hoặc "Vô hiệu"</li>
          </ul>

          <div style={{ marginBottom: 8, background: '#f6ffed', padding: 12, borderRadius: 4, border: '1px solid #b7eb8f' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              💡 <strong>Lưu ý:</strong> Click vào nút <strong>"Tải file mẫu"</strong> để tải file Excel mẫu về máy, sau đó điền dữ liệu và upload lên.
            </Text>
          </div>

          {importing && (
            <div style={{ marginBottom: 8 }}>
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
            <div style={{ marginTop: 8, color: '#52c41a' }}>
              ✅ Đã chọn file: {fileList[0].name}
            </div>
          )}
        </div>
      </Modal>

      {/* Modal thêm/sửa - ⭐ THÊM TRƯỜNG KIÊM NHIỆM */}
      <Modal
        title={editItem ? '✏️ Cập nhật giáo viên' : '➕ Thêm giáo viên mới'}
        open={modalOpen}
        onOk={handleLuu}
        onCancel={() => setModalOpen(false)}
        width={500}
        centered
        bodyStyle={{ padding: '12px 16px' }}
      >
        <Form
          form={form}
          layout="horizontal"
          labelCol={{ span: 6 }}
          wrapperCol={{ span: 25 }}
          size="small"
          style={{ marginTop: 16 }}
        >
          <Form.Item name="ho_ten" label="Họ tên"
            rules={[{ required: true, message: 'Nhập họ tên' }]}>
            <Input placeholder="Nguyễn Văn A" size="small" />
          </Form.Item>

          <Form.Item name="email" label="Email"
            rules={[{ required: true, type: 'email', message: 'Email không hợp lệ' }]}>
            <Input placeholder="email@truonghoc.com" size="small" />
          </Form.Item>

          {!editItem && (
            <Form.Item name="mat_khau" label="Mật khẩu">
              <Input.Password placeholder="Mặc định: eduschool@123" size="small" />
            </Form.Item>
          )}

          <Form.Item name="ma_giao_vien" label="Mã giáo viên"
            rules={[{ required: true, message: 'Nhập mã giáo viên' }]}>
            <Input placeholder="GV001" size="small" />
          </Form.Item>

          <Form.Item name="mon_day" label="Môn dạy">
            <Input placeholder="Toán, Văn, Anh..." size="small" />
          </Form.Item>

          <Form.Item name="to_id" label="Tổ chuyên môn">
            <Select
              placeholder="-- Chọn tổ chuyên môn --"
              allowClear
              showSearch
              optionFilterProp="label"
              size="small"
              options={danhSachTo.map(to => ({
                value: to.id,
                label: to.ten_to,
              }))}
            />
          </Form.Item>

          {/* ⭐ THÊM TRƯỜNG KIÊM NHIỆM */}
          <Form.Item name="kiem_nhiem" label="Kiêm nhiệm">
            <Select
              placeholder="-- Chọn kiêm nhiệm --"
              allowClear
              showSearch
              optionFilterProp="label"
              size="small"
              options={KIEM_NHIEM_LIST}
            />
          </Form.Item>

          <Form.Item name="so_dien_thoai" label="Số điện thoại">
            <Input placeholder="0901234567" size="small" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal kết quả import */}
      {renderImportResult()}
    </div>
  )
}