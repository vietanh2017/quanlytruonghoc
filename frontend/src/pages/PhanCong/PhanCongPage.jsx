// frontend/src/pages/PhanCong/PhanCongPage.jsx
import React, { useEffect, useState } from 'react'
import {
  Table, Button, Space, Select, message, Popconfirm,
  Typography, Card, Row, Col, Tag, Modal,
  Checkbox, Badge
} from 'antd'
import {
  PlusOutlined, DeleteOutlined, ReloadOutlined,
  SaveOutlined, ClearOutlined,
} from '@ant-design/icons'
import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1/phan-cong' })
const apiCH = axios.create({ baseURL: 'http://localhost:8000/api/v1/cau-hinh' })
const { Title, Text } = Typography

export default function PhanCongPage() {
  // ── Metadata ───────────────────────────────────────────────
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsHocKy, setDsHocKy] = useState([])
  const [dsGiaoVien, setDsGiaoVien] = useState([])
  const [dsMonHoc, setDsMonHoc] = useState([])
  const [dsLopHoc, setDsLopHoc] = useState([])
  const [dsPhanMon, setDsPhanMon] = useState([])

  // ── Filter ────────────────────────────────────────────────
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [selHocKy, setSelHocKy] = useState(null)
  const [selGiaoVien, setSelGiaoVien] = useState(null)

  // ── Dữ liệu ───────────────────────────────────────────────
  const [dsPhanCong, setDsPhanCong] = useState([])
  const [tongHop, setTongHop] = useState([])
  const [loading, setLoading] = useState(false)

  // ── Modal ─────────────────────────────────────────────────
  const [modalOpen, setModalOpen] = useState(false)
  const [selMon, setSelMon] = useState(null)
  const [selPhanMon, setSelPhanMon] = useState(null)
  const [selLop, setSelLop] = useState(null)
  const [clearOld, setClearOld] = useState(false)
  const [pendingList, setPendingList] = useState([])

  // ── Load metadata ──────────────────────────────────────────
  const loadMeta = async () => {
    try {
      const [nh, gv, lop] = await Promise.all([
        api.get('/meta/nam-hoc'),
        api.get('/meta/giao-vien'),
        api.get('/meta/lop-hoc'),
      ])
      setDsNamHoc(nh.data)
      setDsGiaoVien(gv.data)
      setDsLopHoc(lop.data)

      const monRes = await apiCH.get('/mon-hoc')
      setDsMonHoc(monRes.data)
    } catch {
      message.error('Không thể tải dữ liệu')
    }
  }

  const loadHocKy = async (namHocId) => {
    if (!namHocId) return
    try {
      const res = await api.get(`/meta/hoc-ky?nam_hoc_id=${namHocId}`)
      setDsHocKy(res.data)
    } catch { }
  }

  const onSelectMon = async (monId) => {
    setSelMon(monId)
    setSelPhanMon(null)
    setDsPhanMon([])

    const mon = dsMonHoc.find(m => m.id === monId)
    if (mon?.co_phan_mon) {
      try {
        const res = await apiCH.get(`/phan-mon/mon-hoc/${monId}`)
        setDsPhanMon(res.data)
      } catch {
        message.warning('Không tải được danh sách phân môn')
      }
    }
  }

  useEffect(() => {
    loadMeta()
    loadTongHop()
  }, [])

  // ── Load tổng hợp ─────────────────────────────────────────
  const loadTongHop = async () => {
    try {
      const res = await api.get('/tong-hop')
      setTongHop(res.data)
    } catch { }
  }

  // ── Load phân công theo GV + học kỳ ──────────────────────
  const loadPhanCong = async () => {
    if (!selGiaoVien || !selNamHoc || !selHocKy) return
    setLoading(true)
    try {
      const res = await api.get(
        `/giao-vien/${selGiaoVien}?nam_hoc_id=${selNamHoc}&hoc_ky_id=${selHocKy}`
      )
      setDsPhanCong(res.data)
    } catch {
      message.error('Không thể tải phân công')
    }
    finally { setLoading(false) }
  }

  useEffect(() => {
    loadPhanCong()
  }, [selGiaoVien, selNamHoc, selHocKy])

  // ── Mở modal ──────────────────────────────────────────────
  const handleOpenModal = () => {
    setPendingList([])
    setSelMon(null)
    setSelPhanMon(null)
    setSelLop(null)
    setClearOld(false)
    setModalOpen(true)
  }

  // ── Thêm vào danh sách chờ ────────────────────────────────
  const handleThemVaoPending = () => {
    console.log('🔄 Bắt đầu thêm vào danh sách chờ')
    console.log('  - selMon:', selMon)
    console.log('  - selPhanMon:', selPhanMon)
    console.log('  - selLop:', selLop)
    console.log('  - pendingList hiện tại:', pendingList)

    if (!selMon) {
      message.warning('Vui lòng chọn môn học')
      return
    }
    if (!selLop) {
      message.warning('Vui lòng chọn lớp')
      return
    }

    const mon = dsMonHoc.find(m => m.id === selMon)
    if (mon?.co_phan_mon && !selPhanMon) {
      message.warning('Môn này có phân môn, vui lòng chọn phân môn')
      return
    }

    const monIdThucTe = selMon
    const tenMonHienThi = mon?.co_phan_mon
      ? dsPhanMon.find(pm => pm.id === selPhanMon)?.ten_phan_mon || mon.ten_mon
      : mon?.ten_mon

    // Kiểm tra trùng lặp
    const dup = pendingList.find(
      p => p.mon_hoc_id === monIdThucTe && p.lop_hoc_id === selLop
    )
    if (dup) {
      message.warning('Đã có trong danh sách')
      return
    }

    const lop = dsLopHoc.find(l => l.id === selLop)
    const newItem = {
      mon_hoc_id: monIdThucTe,
      lop_hoc_id: selLop,
      ten_mon: tenMonHienThi,
      ten_lop: lop?.ten_lop || '',
      phan_mon_id: selPhanMon,
      co_phan_mon: mon?.co_phan_mon || false,
    }

    console.log('📝 Thêm item mới:', newItem)
    setPendingList(prev => [...prev, newItem])

    // Reset selection
    setSelMon(null)
    setSelPhanMon(null)
    setSelLop(null)
    setDsPhanMon([])

    message.success(`Đã thêm "${tenMonHienThi} - ${lop?.ten_lop}" vào danh sách`)
  }

  const handleXoaPending = (idx) => {
    setPendingList(prev => prev.filter((_, i) => i !== idx))
  }

  // ── Lưu phân công ─────────────────────────────────────────
  const handleLuu = async () => {
    console.log('🔄 Bắt đầu lưu phân công')
    console.log('  - selGiaoVien:', selGiaoVien)
    console.log('  - selNamHoc:', selNamHoc)
    console.log('  - selHocKy:', selHocKy)
    console.log('  - pendingList:', pendingList)
    console.log('  - pendingList.length:', pendingList.length)

    if (!selGiaoVien) {
      message.warning('Vui lòng chọn giáo viên')
      return
    }
    if (!selNamHoc) {
      message.warning('Vui lòng chọn năm học')
      return
    }
    if (!selHocKy) {
      message.warning('Vui lòng chọn học kỳ')
      return
    }

    if (pendingList.length === 0) {
      message.warning('Chưa có phân công nào để lưu. Vui lòng thêm môn và lớp vào danh sách.')
      return
    }

    try {
      const data = {
        giao_vien_id: selGiaoVien,
        nam_hoc_id: selNamHoc,
        hoc_ky_id: selHocKy,
        phan_cong_list: pendingList.map(p => ({
          mon_hoc_id: p.mon_hoc_id,
          lop_hoc_id: p.lop_hoc_id,
        })),
        clear_old: clearOld,
      }

      console.log('📤 Dữ liệu gửi lên:', JSON.stringify(data, null, 2))

      const response = await api.post('/', data)
      console.log('✅ Response:', response.data)

      message.success('Lưu phân công thành công!')
      setPendingList([])
      setModalOpen(false)
      loadPhanCong()
      loadTongHop()
    } catch (err) {
      console.error('❌ Lỗi lưu:', err)
      console.error('❌ Response:', err.response?.data)
      message.error(err.response?.data?.detail || 'Lỗi khi lưu phân công')
    }
  }

  // ── Xóa 1 phân công ───────────────────────────────────────
  const handleXoa = async (pc) => {
    try {
      await api.delete(`/${pc.id}`)
      message.success('Đã xóa phân công')
      loadPhanCong()
      loadTongHop()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ── Xóa tất cả ────────────────────────────────────────────
  const handleXoaTatCa = async () => {
    try {
      await api.delete('/tat-ca/xoa', {
        data: {
          giao_vien_id: selGiaoVien,
          nam_hoc_id: selNamHoc,
          hoc_ky_id: selHocKy,
        }
      })
      message.success('Đã xóa tất cả phân công')
      loadPhanCong()
      loadTongHop()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  // ── Cột bảng ──────────────────────────────────────────────
  const colPhanCong = [
    { title: 'Môn học', render: (_, r) => r.mon_hoc?.ten_mon || '—' },
    { title: 'Lớp', render: (_, r) => r.lop_hoc?.ten_lop || '—' },
    { title: 'Khối', render: (_, r) => r.lop_hoc?.khoi || '—', width: 70 },
    {
      title: '', width: 60,
      render: (_, r) => (
        <Popconfirm title="Xóa phân công này?" onConfirm={() => handleXoa(r)}
          okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    }
  ]

  const colTongHop = [
    {
      title: 'Giáo viên', dataIndex: 'ho_ten',
      sorter: (a, b) => a.ho_ten.localeCompare(b.ho_ten),
    },
    {
      title: 'Phân công',
      render: (_, r) => (
        <Space wrap size={4}>
          {r.phan_cong.map((pc, i) => (
            <Tag key={i} color="blue">{pc.mon_hoc}: {pc.lops.join(', ')}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: 'Tổng tiết', dataIndex: 'tong_tiet', width: 100, align: 'center',
      render: v => (
        <Tag color={v > 18 ? 'red' : v > 12 ? 'orange' : 'green'}>{v} tiết</Tag>
      ),
      sorter: (a, b) => a.tong_tiet - b.tong_tiet,
    },
  ]

  const monDangChon = dsMonHoc.find(m => m.id === selMon)
  const cooPhanMon = !!monDangChon?.co_phan_mon

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>📋 Phân Công Giảng Dạy</Title>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Phân công theo giáo viên" size="small"
            extra={
              <Button type="primary" icon={<PlusOutlined />}
                onClick={handleOpenModal}
                disabled={!selGiaoVien || !selNamHoc || !selHocKy}>
                Thêm phân công
              </Button>
            }>

            <Space direction="vertical" style={{ width: '100%', marginBottom: 12 }}>
              <Select placeholder="Chọn năm học" style={{ width: '100%' }}
                onChange={v => { setSelNamHoc(v); setSelHocKy(null); loadHocKy(v) }}
                options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))} />
              <Select placeholder="Chọn học kỳ" style={{ width: '100%' }}
                value={selHocKy} onChange={setSelHocKy} disabled={!selNamHoc}
                options={dsHocKy.map(h => ({ value: h.id, label: h.ten_hoc_ky }))} />
              <Select placeholder="Chọn giáo viên" style={{ width: '100%' }}
                showSearch optionFilterProp="label" value={selGiaoVien}
                onChange={setSelGiaoVien}
                options={dsGiaoVien.map(gv => ({
                  value: gv.id,
                  label: `${gv.ho_ten} (${gv.ma_giao_vien})`,
                }))} />
            </Space>

            {dsPhanCong.length > 0 && (
              <div style={{ marginBottom: 8, textAlign: 'right' }}>
                <Popconfirm title="Xóa tất cả phân công của GV này trong học kỳ?"
                  onConfirm={handleXoaTatCa} okText="Xóa tất cả" cancelText="Hủy"
                  okButtonProps={{ danger: true }}>
                  <Button danger icon={<ClearOutlined />} size="small">Xóa tất cả</Button>
                </Popconfirm>
              </div>
            )}

            <Table rowKey="id" columns={colPhanCong} dataSource={dsPhanCong}
              loading={loading} size="small" bordered
              pagination={{ pageSize: 8, size: 'small' }}
              locale={{ emptyText: selGiaoVien ? 'Chưa có phân công' : 'Chọn giáo viên để xem' }} />
          </Card>
        </Col>

        <Col span={12}>
          <Card
            title={<span>Tổng hợp phân công <Badge count={tongHop.length} /></span>}
            size="small"
            extra={<Button icon={<ReloadOutlined />} size="small" onClick={loadTongHop} />}>
            <Table rowKey="giao_vien_id" columns={colTongHop} dataSource={tongHop}
              size="small" bordered pagination={{ pageSize: 8, size: 'small' }} />
          </Card>
        </Col>
      </Row>

      {/* ── Modal thêm phân công ── */}
      <Modal
        title="➕ Thêm phân công"
        open={modalOpen}
        centered
        width={580}
        onCancel={() => {
          setModalOpen(false)
          setPendingList([])
        }}
        footer={[
          <Button key="cancel" onClick={() => {
            setModalOpen(false)
            setPendingList([])
          }}>Hủy</Button>,
          <Button
            key="save"
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleLuu}
            disabled={pendingList.length === 0}
          >
            Lưu phân công ({pendingList.length})
          </Button>
        ]}>

        <Space direction="vertical" style={{ width: '100%', marginTop: 12 }} size={10}>

          <Row gutter={8} align="bottom">
            <Col span={9}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: 12 }}>Môn học</Text>
              </div>
              <Select
                placeholder="Chọn môn"
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="label"
                value={selMon}
                onChange={onSelectMon}
                options={dsMonHoc.map(m => ({
                  value: m.id,
                  label: m.co_phan_mon ? `${m.ten_mon} ★` : m.ten_mon,
                }))}
              />
            </Col>

            {cooPhanMon && (
              <Col span={8}>
                <div style={{ marginBottom: 4 }}>
                  <Text style={{ fontSize: 12, color: '#1677ff' }}>Phân môn</Text>
                </div>
                <Select
                  placeholder="Chọn phân môn"
                  style={{ width: '100%' }}
                  value={selPhanMon}
                  onChange={setSelPhanMon}
                  options={dsPhanMon.map(pm => ({
                    value: pm.id,
                    label: pm.ten_phan_mon,
                  }))}
                />
              </Col>
            )}

            <Col span={cooPhanMon ? 5 : 11}>
              <div style={{ marginBottom: 4 }}>
                <Text style={{ fontSize: 12 }}>Lớp</Text>
              </div>
              <Select
                placeholder="Chọn lớp"
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="label"
                value={selLop}
                onChange={setSelLop}
                options={dsLopHoc.map(l => ({ value: l.id, label: l.ten_lop }))}
              />
            </Col>

            <Col span={2}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleThemVaoPending}
                style={{ width: '100%', marginTop: 22 }}
              />
            </Col>
          </Row>

          {cooPhanMon && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              ★ Môn này có phân môn — vui lòng chọn phân môn cụ thể
            </Text>
          )}

          {/* ⭐ Hiển thị danh sách chờ */}
          <div style={{
            background: pendingList.length > 0 ? '#f6ffed' : '#f5f5f5',
            border: `1px solid ${pendingList.length > 0 ? '#b7eb8f' : '#d9d9d9'}`,
            borderRadius: 6,
            padding: 10,
            minHeight: 60
          }}>
            <Text strong style={{ fontSize: 12 }}>
              Danh sách sẽ thêm ({pendingList.length} mục):
            </Text>
            {pendingList.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '10px 0' }}>
                <Text type="secondary">Chưa có mục nào. Hãy chọn môn và lớp để thêm.</Text>
              </div>
            ) : (
              <div style={{ marginTop: 8 }}>
                {pendingList.map((p, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between',
                    alignItems: 'center', padding: '4px 0',
                    borderBottom: i < pendingList.length - 1 ? '1px solid #e8e8e8' : 'none'
                  }}>
                    <Text style={{ fontSize: 13 }}>
                      <Tag color="blue">{p.ten_mon}</Tag> → <Tag>{p.ten_lop}</Tag>
                    </Text>
                    <Button
                      size="small"
                      danger
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={() => handleXoaPending(i)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          <Checkbox checked={clearOld} onChange={e => setClearOld(e.target.checked)}>
            <Text type="warning">Xóa phân công cũ trước khi thêm mới</Text>
          </Checkbox>
        </Space>
      </Modal>
    </div>
  )
}