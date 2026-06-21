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
    gv.mon_day?.toLowerCase().includes(search.toLowerCase())
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
    })
    setModalOpen(true)
  }

  // ── Lưu (thêm hoặc sửa) ────────────────────────────────────
  const handleLuu = async () => {
    try {
      const values = await form.validateFields()
      if (editItem) {
        await giaoVienApi.update(editItem.id, values)
        message.success('Cập nhật giáo viên thành công')
      } else {
        await giaoVienApi.create(values)
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
    // Lấy danh sách tổ từ state
    const toList = danhSachTo.map(to => to.ten_to)
    const defaultTo = toList.length > 0 ? toList[0] : 'Tổ Toán'

    const sampleData = [
      ['Mã giáo viên', 'Họ tên', 'Email', 'Mật khẩu', 'Môn dạy', 'Số điện thoại', 'Tổ chuyên môn', 'Trạng thái'],
      ['GV001', 'Nguyễn Văn A', 'a.nguyen@school.com', 'eduschool@123', 'Toán', '0901234567', defaultTo, 'Hoạt động'],
      ['GV002', 'Trần Thị B', 'b.tran@school.com', 'eduschool@123', 'Văn', '0909876543', toList.length > 1 ? toList[1] : defaultTo, 'Hoạt động'],
      ['GV003', 'Lê Văn C', 'c.le@school.com', 'eduschool@123', 'Anh', '0912345678', toList.length > 2 ? toList[2] : defaultTo, 'Hoạt động'],
      ['GV004', 'Phạm Thị D', 'd.pham@school.com', 'eduschool@123', 'Lý', '0923456789', toList.length > 3 ? toList[3] : defaultTo, 'Vô hiệu'],
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
    // ⭐ Lấy file từ fileList thay vì nhận tham số
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

  // ── Cột bảng ───────────────────────────────────────────────
  const columns = [
    {
      title: 'Mã GV',
      dataIndex: 'ma_giao_vien',
      width: 100, align: 'center',
      sorter: (a, b) => a.ma_giao_vien.localeCompare(b.ma_giao_vien),
    },
    {
      title: 'Họ tên',
      render: (_, r) => r.nguoi_dung?.ho_ten || '—',
      sorter: (a, b) =>
        (a.nguoi_dung?.ho_ten || '').localeCompare(b.nguoi_dung?.ho_ten || ''),
    },
    {
      title: 'Email',
      render: (_, r) => r.nguoi_dung?.email || '—',
    },
    {
      title: 'Môn dạy', align: 'center',
      dataIndex: 'mon_day',
    },
    {
      title: 'Tổ CM',
      render: (_, r) => r.to_chuyen_mon?.ten_to || '—',
    },
    {
      title: 'SĐT', align: 'center',
      dataIndex: 'so_dien_thoai',
    },
    {
      title: 'Trạng thái', align: 'center',
      render: (_, r) => (
        <Tag color={r.active ? 'green' : 'red'}>
          {r.active ? 'Hoạt động' : 'Vô hiệu'}
        </Tag>
      ),
      width: 110,
    },
    {
      title: 'Thao tác', align: 'center',
      width: 160,
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
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
              <BookOutlined style={{ color: '#1890ff' }} />
              Quản lý Giáo Viên
              <Badge count={stats.total} style={{ marginLeft: 12 }} />
            </Title>
          </Col>
          <Col>
            <Space size="middle" wrap>
              <Input
                placeholder="Tìm theo mã, tên, môn..."
                prefix={<SearchOutlined />}
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ width: 240 }}
                allowClear
                size="large"
              />
              <Button
                icon={<FileExcelOutlined />}
                onClick={() => setImportModalVisible(true)}
                size="large"
                style={{ color: '#52c41a', borderColor: '#52c41a' }}
              >
                Import Excel
              </Button>
              <Button icon={<ReloadOutlined />} onClick={loadData} size="large">
                Làm mới
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleThem} size="large">
                Thêm giáo viên
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Thống kê */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Tổng số giáo viên"
              value={stats.total}
              prefix={<UserOutlined />}
              styles={{ content: { color: '#1890ff', fontSize: 24 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Đang hoạt động"
              value={stats.active}
              prefix={<CheckCircleOutlined />}
              styles={{ content: { color: '#52c41a', fontSize: 24 } }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="Vô hiệu"
              value={stats.inactive}
              prefix={<CloseCircleOutlined />}
              styles={{ content: { color: '#ff4d4f', fontSize: 24 } }}
            />
          </Card>
        </Col>
      </Row>

      {/* Progress khi import */}
      {importing && (
        <div style={{ marginBottom: 16 }}>
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
          pagination={{ pageSize: 15, showTotal: (t) => `Tổng: ${t} giáo viên` }}
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
        <div style={{ padding: '16px 0' }}>
          <p style={{ marginBottom: 16 }}>
            <strong>Hướng dẫn:</strong> File Excel cần có các cột sau (hàng đầu là tiêu đề):
          </p>
          <ul style={{ marginBottom: 16 }}>
            <li><strong>Mã giáo viên</strong> (bắt buộc) - VD: GV001</li>
            <li><strong>Họ tên</strong> (bắt buộc) - VD: Nguyễn Văn A</li>
            <li><strong>Email</strong> (bắt buộc) - VD: a.nguyen@school.com</li>
            <li><strong>Mật khẩu</strong> - Mặc định: eduschool@123</li>
            <li><strong>Môn dạy</strong> - VD: Toán</li>
            <li><strong>Số điện thoại</strong> - 10-11 chữ số</li>
            <li><strong>Tổ chuyên môn</strong> - Tên tổ đã có trong hệ thống</li>
            <li><strong>Trạng thái</strong> - "Hoạt động" hoặc "Vô hiệu"</li>
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

      {/* Modal thêm/sửa */}
      <Modal
        title={editItem ? '✏️ Cập nhật giáo viên' : '➕ Thêm giáo viên mới'}
        open={modalOpen}
        onOk={handleLuu}
        onCancel={() => setModalOpen(false)}
        okText={editItem ? 'Cập nhật' : 'Thêm mới'}
        cancelText="Hủy"
        width={520}
        centered
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="ho_ten" label="Họ tên"
            rules={[{ required: true, message: 'Nhập họ tên' }]}>
            <Input placeholder="Nguyễn Văn A" size="large" />
          </Form.Item>

          <Form.Item name="email" label="Email"
            rules={[{ required: true, type: 'email', message: 'Email không hợp lệ' }]}>
            <Input placeholder="email@truonghoc.com" size="large" />
          </Form.Item>

          {!editItem && (
            <Form.Item name="mat_khau" label="Mật khẩu">
              <Input.Password placeholder="Mặc định: eduschool@123" size="large" />
            </Form.Item>
          )}

          <Form.Item name="ma_giao_vien" label="Mã giáo viên"
            rules={[{ required: true, message: 'Nhập mã giáo viên' }]}>
            <Input placeholder="GV001" size="large" />
          </Form.Item>

          <Form.Item name="mon_day" label="Môn dạy">
            <Input placeholder="Toán, Văn, Anh..." size="large" />
          </Form.Item>

          <Form.Item name="to_id" label="Tổ chuyên môn">
            <Select
              placeholder="-- Chọn tổ chuyên môn --"
              allowClear
              showSearch
              optionFilterProp="label"
              size="large"
              options={danhSachTo.map(to => ({
                value: to.id,
                label: to.ten_to,
              }))}
            />
          </Form.Item>

          <Form.Item name="so_dien_thoai" label="Số điện thoại">
            <Input placeholder="0901234567" size="large" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal kết quả import */}
      {renderImportResult()}
    </div>
  )
}