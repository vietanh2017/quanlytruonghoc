// frontend/src/pages/ThiDuaHS/ThiDuaHSPage.jsx
import React, { useEffect, useState, useCallback, useRef } from 'react'
import {
  Tabs, Table, Button, Space, Select, Modal, Form, Input,
  InputNumber, DatePicker, message, Popconfirm, Tooltip,
  Typography, Tag, Card, Row, Col, Badge, Switch,
} from 'antd'
import {
  PlusOutlined, DeleteOutlined, SaveOutlined,
  MinusCircleOutlined, PlusCircleOutlined, EyeOutlined,
} from '@ant-design/icons'
import axios from 'axios'
import dayjs from 'dayjs'

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1/thi-dua-hs' })
const { Title, Text } = Typography
const THU_LABELS = { 2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5', 6: 'Thứ 6' }

// ── Hook load metadata 1 lần ──────────────────────────────────
function useMeta() {
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsLoaiVP, setDsLoaiVP] = useState([])
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [dsLop, setDsLop] = useState([])
  const [loading, setLoading] = useState(false)

  const loadLop = async () => {
    setLoading(true)
    try {
      const r = await api.get('/meta/lop')
      console.log('🏫 Danh sách lớp:', r.data)
      setDsLop(r.data)
    } catch (err) {
      console.error('Lỗi load lớp:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    api.get('/meta/nam-hoc')
      .then(r => {
        console.log('📚 Năm học từ API:', r.data)
        setDsNamHoc(r.data)
        if (r.data && r.data.length > 0) {
          const namHoc2026 = r.data.find(n => n.ten_nam_hoc.includes('2026-2027'))
          const selectedId = namHoc2026 ? namHoc2026.id : r.data[0].id
          console.log('✅ Chọn năm học ID:', selectedId)
          setSelNamHoc(selectedId)
        }
      })
      .catch(err => console.error('Lỗi load năm học:', err))

    api.get('/loai-vi-pham')
      .then(r => {
        console.log('📋 Loại vi phạm:', r.data)
        setDsLoaiVP(r.data)
      })
      .catch(err => console.error('Lỗi load loại vi phạm:', err))

    loadLop()
  }, [])

  const onSelectNamHoc = async (id) => {
    console.log('🔄 Chọn năm học ID:', id)
    setSelNamHoc(id)
  }

  return {
    dsNamHoc,
    dsLoaiVP,
    selNamHoc,
    dsLop,
    loading,
    onSelectNamHoc,
    setDsLoaiVP
  }
}
// ════════════════════════════════════════════════════
//  TAB TẬP THỂ
// ════════════════════════════════════════════════════
function TabTapThe({ meta }) {
  const { dsNamHoc, dsLoaiVP, selNamHoc, dsLop, onSelectNamHoc } = meta
  const [tuan, setTuan] = useState(1)
  const [dsVPTapThe, setDsVPTapThe] = useState([])
  const [dsVPCaNhan, setDsVPCaNhan] = useState([])
  const [diemTuan, setDiemTuan] = useState([])
  const [tongHopLop, setTongHopLop] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingCaNhan, setLoadingCaNhan] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [saved, setSaved] = useState(true)
  const [form] = Form.useForm()

  const dsVPTapTheList = dsLoaiVP.filter(l => l.loai === 'vi_pham')
  const dsTTTapTheList = dsLoaiVP.filter(l => l.loai === 'thanh_tich')
  const dsLoaiTapThe = [...dsVPTapTheList, ...dsTTTapTheList]

  const soTieuChi = dsLoaiVP.filter(l => l.is_active !== false).length || 8
  const soNgayTrongTuan = parseInt(localStorage.getItem('soNgayTrongTuan')) || 5

  // ⭐ Load vi phạm tập thể
  const loadVPTapThe = useCallback(async () => {
    if (!selNamHoc || !tuan) return
    setLoading(true)
    try {
      const params = `nam_hoc_id=${selNamHoc}&tuan=${tuan}`
      const r = await api.get(`/tap-the?${params}`)
      setDsVPTapThe(r.data)
    } catch (err) {
      console.error('Lỗi load vi phạm tập thể:', err)
    } finally {
      setLoading(false)
    }
  }, [selNamHoc, tuan])

  // ⭐ Load vi phạm cá nhân
  const loadVPCaNhan = useCallback(async () => {
    if (!selNamHoc || !tuan) return
    setLoadingCaNhan(true)
    try {
      let allViPham = []
      for (const lop of dsLop) {
        try {
          const r = await api.get(`/ca-nhan?lop_hoc_id=${lop.id}&nam_hoc_id=${selNamHoc}&tuan=${tuan}`)
          const viPhamWithLop = (r.data || []).map(vp => ({
            ...vp,
            lop_hoc_id: lop.id,
            ten_lop: lop.ten_lop,
          }))
          allViPham = [...allViPham, ...viPhamWithLop]
        } catch (err) {
          console.error(`Lỗi load vi phạm lớp ${lop.ten_lop}:`, err)
        }
      }
      setDsVPCaNhan(allViPham)
    } catch (err) {
      console.error('Lỗi load vi phạm cá nhân:', err)
    } finally {
      setLoadingCaNhan(false)
    }
  }, [selNamHoc, tuan, dsLop])

  // ⭐ Load điểm tuần từ database
  const loadDiemTuan = useCallback(async () => {
    if (!selNamHoc || !tuan) return
    try {
      const r = await api.get(`/diem-tuan?nam_hoc_id=${selNamHoc}&tuan=${tuan}`)
      const data = r.data || []

      const fullData = dsLop.map(lop => {
        const existing = data.find(d => d.lop_hoc_id === lop.id)
        return {
          lop_hoc_id: lop.id,
          ten_lop: lop.ten_lop,
          khoi: lop.khoi,
          diem_doi: 0,
          diem_doi_tb: 0,
          diem_hoc_tap: existing?.diem_hoc_tap || 0,
          tong_diem: existing?.tong_diem || 0,
          trung_binh: existing?.trung_binh || 0,
          ghi_chu: existing?.ghi_chu || '',
        }
      })

      setDiemTuan(fullData)
      setSaved(true)
    } catch (err) {
      console.error('Lỗi load điểm tuần:', err)
    }
  }, [selNamHoc, tuan, dsLop])

  // ⭐ Hàm tính tổng hợp điểm đội
  const tinhTongHopLop = useCallback(() => {
    if (!dsLop.length) return

    const soNgayTrongTuan = parseInt(localStorage.getItem('soNgayTrongTuan')) || 5
    const soTieuChi = dsLoaiVP.filter(l => l.is_active !== false).length || 8

    const lopMap = {}
    dsLop.forEach(lop => {
      lopMap[lop.id] = {
        lop_hoc_id: lop.id,
        ten_lop: lop.ten_lop,
        khoi: lop.khoi,
        tong_vi_pham: 0,
        tong_thanh_tich: 0,
        tong_diem_doi: 0,
        diem_doi_tb: 0,
      }
    })

    dsVPTapThe.forEach(vp => {
      const lopId = vp.lop_hoc_id
      if (lopMap[lopId]) {
        if (vp.so_diem < 0) {
          lopMap[lopId].tong_vi_pham += vp.so_diem
        } else {
          lopMap[lopId].tong_thanh_tich += vp.so_diem
        }
      }
    })

    dsVPCaNhan.forEach(vp => {
      const lopId = vp.lop_hoc_id
      if (lopId && lopMap[lopId]) {
        if (vp.so_diem < 0) {
          lopMap[lopId].tong_vi_pham += vp.so_diem
        } else {
          lopMap[lopId].tong_thanh_tich += vp.so_diem
        }
      }
    })

    const diemMacDinhMoiNgay = 10 * soTieuChi
    const diemMacDinhTuan = diemMacDinhMoiNgay * soNgayTrongTuan

    const result = Object.values(lopMap).map((item) => {
      const tongDiemDoi = diemMacDinhTuan + item.tong_thanh_tich + item.tong_vi_pham
      const diemDoiTB = parseFloat(((tongDiemDoi / soNgayTrongTuan) / soTieuChi).toFixed(3))

      return {
        ...item,
        tong_diem_doi: tongDiemDoi,
        diem_doi_tb: diemDoiTB,
      }
    })

    result.sort((a, b) => b.tong_diem_doi - a.tong_diem_doi)
    result.forEach((item, index) => {
      item.xep_hang = index + 1
    })

    setTongHopLop(result)
  }, [dsLop, dsVPTapThe, dsVPCaNhan, dsLoaiVP])

  // ⭐ Lưu điểm học tập
  const onLuuDiemHocTap = async () => {
    try {
      const dataToSave = diemTuan.map(d => ({
        lop_hoc_id: d.lop_hoc_id,
        diem_hoc_tap: parseFloat(d.diem_hoc_tap) || 0,
        ghi_chu: d.ghi_chu || '',
      }))

      await api.post('/diem-tuan/luu', {
        nam_hoc_id: selNamHoc,
        tuan: tuan,
        nguoi_nhap: 'Admin',
        data: dataToSave
      })
      setSaved(true)
    } catch (err) {
      console.error('Lỗi lưu điểm HT:', err)
      message.error('Lỗi khi lưu điểm học tập')
    }
  }

  // ⭐ Load dữ liệu ban đầu
  useEffect(() => {
    if (selNamHoc && tuan) {
      loadVPTapThe()
      loadVPCaNhan()
      loadDiemTuan()
    }
  }, [selNamHoc, tuan])

  // ⭐ Khi có dữ liệu vi phạm, tính tổng hợp
  useEffect(() => {
    if (dsLop.length > 0) {
      tinhTongHopLop()
    }
  }, [dsVPTapThe, dsVPCaNhan, dsLop])

  // ⭐ Khi tongHopLop thay đổi, cập nhật điểm đội vào diemTuan
  useEffect(() => {
    if (tongHopLop.length > 0 && diemTuan.length > 0) {
      setDiemTuan(prev => prev.map(item => {
        const lopTongHop = tongHopLop.find(t => t.lop_hoc_id === item.lop_hoc_id)
        return {
          ...item,
          diem_doi: lopTongHop?.diem_doi_tb || 0,
          diem_doi_tb: lopTongHop?.diem_doi_tb || 0,
        }
      }))
    }
  }, [tongHopLop])

  // ⭐ Debounce: tự động lưu sau 1.5 giây không nhập
  useEffect(() => {
    if (selNamHoc && tuan && diemTuan.length > 0 && !saved) {
      const timer = setTimeout(() => {
        onLuuDiemHocTap()
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [diemTuan, saved])

  const onThemVP = async () => {
    try {
      const v = await form.validateFields()
      await api.post('/tap-the', {
        ...v,
        ngay_xay_ra: v.ngay_xay_ra.format('YYYY-MM-DD'),
        nam_hoc_id: selNamHoc,
        tuan,
      })
      message.success('Thêm thành công')
      setModalOpen(false)
      form.resetFields()
      loadVPTapThe()
      loadDiemTuan()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  const onXoa = async (id) => {
    await api.delete(`/tap-the/${id}`)
    message.success('Đã xóa')
    loadVPTapThe()
    loadDiemTuan()
  }

  const colTongHop = [
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
      title: 'TB điểm đội',
      dataIndex: 'diem_doi_tb',
      width: 80,
      align: 'center',
      render: (v) => {
        const displayValue = v !== undefined && v !== null ? v.toFixed(3) : '0.000'
        let color = 'green'
        if (parseFloat(displayValue) < 8) color = 'red'
        else if (parseFloat(displayValue) < 9.5) color = 'orange'
        return <Tag color={color}>{displayValue}</Tag>
      },
      sorter: (a, b) => a.diem_doi_tb - b.diem_doi_tb,
    },
    {
      title: 'Xếp hạng',
      dataIndex: 'xep_hang',
      width: 55,
      align: 'center',
      render: (v) => {
        const medals = ['🥇', '🥈', '🥉']
        if (v <= 3) return medals[v - 1]
        return `#${v}`
      },
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
            onClick={() => {
              const tapThe = dsVPTapThe.filter(vp => vp.lop_hoc_id === record.lop_hoc_id)
              const caNhan = dsVPCaNhan.filter(vp => vp.lop_hoc_id === record.lop_hoc_id)

              // ⭐ Hàm xóa vi phạm tập thể
              const handleXoaTapThe = async (id) => {
                try {
                  await api.delete(`/tap-the/${id}`)
                  message.success('Đã xóa vi phạm tập thể')
                  // Reload lại dữ liệu
                  loadVPTapThe()
                  loadDiemTuan()
                  // Đóng modal hiện tại
                  Modal.destroyAll()
                } catch (err) {
                  message.error(err.response?.data?.detail || 'Xóa thất bại')
                }
              }

              // ⭐ Hàm xóa vi phạm cá nhân
              const handleXoaCaNhan = async (id) => {
                try {
                  await api.delete(`/ca-nhan/${id}`)
                  message.success('Đã xóa vi phạm cá nhân')
                  // Reload lại dữ liệu
                  loadVPCaNhan()
                  loadDiemTuan()
                  // Đóng modal hiện tại
                  Modal.destroyAll()
                } catch (err) {
                  message.error(err.response?.data?.detail || 'Xóa thất bại')
                }
              }

              Modal.info({
                title: `Chi tiết vi phạm - ${record.ten_lop}`,
                width: 750,
                okText: 'Đóng',
                content: (
                  <div>
                    <Tabs
                      items={[
                        {
                          key: 'tap-the',
                          label: `Tập thể (${tapThe.length})`,
                          children: tapThe.length > 0 ? (
                            <Table
                              dataSource={tapThe}
                              columns={[
                                { title: 'Vi phạm', dataIndex: 'ten_loi', width: 150 },
                                {
                                  title: 'Điểm',
                                  dataIndex: 'so_diem',
                                  width: 80,
                                  render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text>
                                },
                                { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 120 },
                                { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
                                {
                                  title: 'Xóa',
                                  width: 60,
                                  align: 'center',
                                  render: (_, vp) => (
                                    <Popconfirm
                                      title="Xóa vi phạm này?"
                                      onConfirm={() => handleXoaTapThe(vp.id)}
                                      okText="Xóa"
                                      cancelText="Hủy"
                                      okButtonProps={{ danger: true }}
                                    >
                                      <Button size="small" danger icon={<DeleteOutlined />} />
                                    </Popconfirm>
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
                              columns={[
                                { title: 'Học sinh', dataIndex: 'ho_ten', width: 120 },
                                { title: 'Vi phạm', dataIndex: 'ten_loi', width: 150 },
                                {
                                  title: 'Điểm',
                                  dataIndex: 'so_diem',
                                  width: 80,
                                  render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text>
                                },
                                { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 120 },
                                { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
                                {
                                  title: 'Xóa',
                                  width: 60,
                                  align: 'center',
                                  render: (_, vp) => (
                                    <Popconfirm
                                      title="Xóa vi phạm này?"
                                      onConfirm={() => handleXoaCaNhan(vp.id)}
                                      okText="Xóa"
                                      cancelText="Hủy"
                                      okButtonProps={{ danger: true }}
                                    >
                                      <Button size="small" danger icon={<DeleteOutlined />} />
                                    </Popconfirm>
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
                  </div>
                )
              })
            }}
          />
        </Tooltip>
      )
    },
  ]

  const colDiem = [
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
      title: 'Điểm Đội',
      dataIndex: 'diem_doi',
      width: 90,
      align: 'center',
      render: (v, record) => {
        const value = record.diem_doi_tb !== undefined ? record.diem_doi_tb : v
        const displayValue = value !== undefined && value !== null ? value.toFixed(3) : '0.000'
        let color = 'green'
        if (parseFloat(displayValue) < 8) color = 'red'
        else if (parseFloat(displayValue) < 9.5) color = 'orange'
        return <Tag color={color}>{displayValue}</Tag>
      },
    },
    {
      title: 'Điểm HT',
      dataIndex: 'diem_hoc_tap',
      width: 90,
      align: 'center',
      render: (v, r) => (
        <InputNumber
          size="small"
          min={0}
          max={10}
          step={0.5}
          value={v || 0}
          style={{ width: 80 }}
          formatter={value => {
            if (value === undefined || value === null || value === '') return '0.000'
            return parseFloat(value).toFixed(3)
          }}
          parser={value => {
            if (!value) return 0
            return parseFloat(value.replace(/,/g, ''))
          }}
          onChange={val => {
            setDiemTuan(prev => prev.map(d =>
              d.lop_hoc_id === r.lop_hoc_id ? { ...d, diem_hoc_tap: val || 0 } : d
            ))
            setSaved(false)
          }}
          onFocus={(e) => {
            e.target.select()
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === 'Tab') {
              e.preventDefault()
              e.target.select()
              const inputs = document.querySelectorAll('.ant-input-number-input')
              const currentIndex = Array.from(inputs).indexOf(e.target)
              const nextIndex = currentIndex + 1
              if (nextIndex < inputs.length) {
                setTimeout(() => {
                  inputs[nextIndex].focus()
                }, 10)
              }
            }
          }}
        />
      )
    },
    {
      title: 'Trung bình',
      dataIndex: 'trung_binh',
      width: 95,
      align: 'center',
      render: (v, record) => {
        const diemHT = record.diem_hoc_tap || 0
        const diemDoi = record.diem_doi || 0
        const trungBinh = ((diemHT * 2) + diemDoi) / 3
        const displayValue = trungBinh !== undefined && trungBinh !== null ? trungBinh.toFixed(3) : '0.000'
        let color = 'green'
        if (parseFloat(displayValue) < 8) color = 'red'
        else if (parseFloat(displayValue) < 9.5) color = 'orange'
        return <Tag color={color}>{displayValue}</Tag>
      },
    },
    {
      title: 'Xếp hạng',
      key: 'xep_hang',
      width: 65,
      align: 'center',
      render: (_, record) => {
        const sorted = [...diemTuan].sort((a, b) => {
          const aTB = ((a.diem_hoc_tap || 0) * 2 + (a.diem_doi || 0)) / 3
          const bTB = ((b.diem_hoc_tap || 0) * 2 + (b.diem_doi || 0)) / 3
          return bTB - aTB
        })

        let rank = 1
        let prevTB = null
        let sameRankCount = 0

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

          if (item.lop_hoc_id === record.lop_hoc_id) {
            return <Text strong style={{ fontStyle: 'italic', fontSize: 15 }}>{rank}</Text>
          }
        }

        return <Text strong style={{ fontStyle: 'italic', fontSize: 15 }}>—</Text>
      },
    },
    {
      title: 'Ghi chú',
      dataIndex: 'ghi_chu',
      width: 100,
      render: (v, r) => (
        <Input
          size="small"
          value={v || ''}
          placeholder="..."
          onChange={e => {
            setDiemTuan(prev => prev.map(d =>
              d.lop_hoc_id === r.lop_hoc_id ? { ...d, ghi_chu: e.target.value } : d
            ))
            setSaved(false)
          }}
        />
      )
    },
  ]

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}
              onChange={onSelectNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={4}>
            <InputNumber
              placeholder="Tuần"
              min={1}
              max={52}
              style={{ width: '100%' }}
              value={tuan}
              onChange={setTuan}
              addonBefore="Tuần"
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              disabled={!selNamHoc}
              onClick={() => { form.resetFields(); setModalOpen(true) }}
            >
              Thêm vi phạm
            </Button>
          </Col>
          <Col>
            <span>
              <Text type="secondary" style={{ marginRight: 4 }}>
                Tổng VP/TT
              </Text>
              <Badge
                count={dsVPTapThe.length + dsVPCaNhan.length}
                showZero
                style={{ backgroundColor: '#ff4d4f' }}
              />
            </span>
          </Col>
        </Row>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <Card
            title="📊 Tổng hợp điểm đội"
            size="small"
            extra={
              <Badge count={tongHopLop.length} style={{ backgroundColor: '#1890ff' }} />
            }
          >
            <Table
              rowKey="lop_hoc_id"
              columns={colTongHop}
              dataSource={tongHopLop}
              loading={loading || loadingCaNhan}
              size="small"
              bordered
              pagination={false}
              scroll={{ y: 400 }}
              locale={{ emptyText: 'Chưa có dữ liệu điểm đội' }}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card
            title={`📋 Điểm thi đua tuần ${tuan}`}
            size="small"
            extra={
              <Button
                size="small"
                icon={<SaveOutlined />}
                type="primary"
                onClick={async () => {
                  await onLuuDiemHocTap()
                  message.success('Đã lưu điểm học tập!')
                }}
                disabled={!selNamHoc}
              >
                Lưu điểm HT
              </Button>
            }
          >
            <Table
              rowKey="lop_hoc_id"
              columns={colDiem}
              dataSource={diemTuan}
              size="small"
              bordered
              pagination={false}
              scroll={{ y: 400 }}
              locale={{ emptyText: 'Không có lớp nào trong năm học này' }}
            />
          </Card>
        </Col>
      </Row>

      <Modal
        title="Thêm vi phạm / thành tích tập thể"
        open={modalOpen}
        onOk={onThemVP}
        onCancel={() => setModalOpen(false)}
        okText="Lưu"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="lop_hoc_id" label="Lớp" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="Chọn lớp"
              options={dsLop.map(l => ({
                value: l.id,
                label: l.ten_lop,
              }))}
            />
          </Form.Item>
          <Form.Item name="loai_vi_pham_id" label="Loại vi phạm / thành tích" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="Chọn loại"
              options={dsLoaiTapThe.map(l => ({
                value: l.id,
                label: `${l.ten_loi} (${l.so_diem > 0 ? '+' : ''}${l.so_diem})`,
              }))}
            />
          </Form.Item>
          <Row gutter={8}>
            <Col span={14}>
              <Form.Item name="ngay_xay_ra" label="Ngày" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={10}>
              <Form.Item name="tiet" label="Tiết">
                <InputNumber min={1} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
// ════════════════════════════════════════════════════
//  TAB CÁ NHÂN
// ════════════════════════════════════════════════════
function TabCaNhan({ meta }) {
  const { dsNamHoc, dsLoaiVP, selNamHoc, dsLop, onSelectNamHoc } = meta
  const [tuan, setTuan] = useState(1)
  const [selLop, setSelLop] = useState(null)
  const [dsHS, setDsHS] = useState([])
  const [dsVP, setDsVP] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingHS, setLoadingHS] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const loadHS = async (lopId) => {
    if (!lopId) {
      setDsHS([])
      setDsVP([])
      setSelLop(null)
      return
    }

    setSelLop(lopId)
    setLoadingHS(true)
    try {
      const r = await api.get(`/meta/hoc-sinh?lop_hoc_id=${lopId}`)
      setDsHS(r.data)
      if (selNamHoc && tuan) {
        await loadVP(lopId)
      }
    } catch (err) {
      console.error('Lỗi load học sinh:', err)
      message.error('Không thể tải danh sách học sinh')
    } finally {
      setLoadingHS(false)
    }
  }

  const loadVP = useCallback(async (lopId) => {
    if (!selNamHoc || !lopId) return
    setLoading(true)
    try {
      const params = `lop_hoc_id=${lopId}&nam_hoc_id=${selNamHoc}&tuan=${tuan}`
      const r = await api.get(`/ca-nhan?${params}`)
      setDsVP(r.data)
    } catch (err) {
      console.error('Lỗi load vi phạm:', err)
    } finally {
      setLoading(false)
    }
  }, [selNamHoc, tuan])

  useEffect(() => {
    if (selLop) {
      loadVP(selLop)
    }
  }, [selLop, tuan, selNamHoc])

  useEffect(() => {
    if (selLop && selNamHoc) {
      loadVP(selLop)
    }
  }, [tuan, selNamHoc])

  const onThem = async () => {
    try {
      const v = await form.validateFields()
      await api.post('/ca-nhan', {
        ...v,
        ngay_xay_ra: v.ngay_xay_ra.format('YYYY-MM-DD'),
        nam_hoc_id: selNamHoc,
        tuan,
      })
      message.success('Thêm thành công')
      setModalOpen(false)
      form.resetFields()
      if (selLop) {
        await loadVP(selLop)
      }
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  const onXoa = async (id) => {
    try {
      await api.delete(`/ca-nhan/${id}`)
      message.success('Đã xóa')
      if (selLop) {
        await loadVP(selLop)
      }
    } catch (err) {
      message.error(err.response?.data?.detail || 'Xóa thất bại')
    }
  }

  const getViPhamByHocSinh = (hsId) => {
    return dsVP.filter(vp => vp.hoc_sinh_id === hsId)
  }

  const getTongDiem = (hsId) => {
    const viPhams = getViPhamByHocSinh(hsId)
    return viPhams.reduce((sum, vp) => sum + vp.so_diem, 0)
  }

  const cols = [
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
                onClick={() => {
                  form.setFieldsValue({ hoc_sinh_id: r.id })
                  setModalOpen(true)
                }}
              />
            </Tooltip>
            {viPhams.length > 0 && (
              <Popconfirm
                title="Xóa tất cả vi phạm của học sinh này?"
                onConfirm={async () => {
                  for (const vp of viPhams) {
                    await api.delete(`/ca-nhan/${vp.id}`)
                  }
                  message.success('Đã xóa tất cả')
                  if (selLop) await loadVP(selLop)
                }}
                okText="Xóa" cancelText="Hủy"
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

  return (
    <div>
      <Card size="small" style={{ marginBottom: 12 }}>
        <Row gutter={12} align="middle">
          <Col span={5}>
            <Select
              placeholder="Năm học"
              style={{ width: '100%' }}
              value={selNamHoc}
              onChange={onSelectNamHoc}
              options={dsNamHoc.map(n => ({ value: n.id, label: n.ten_nam_hoc }))}
            />
          </Col>
          <Col span={4}>
            <InputNumber
              placeholder="Tuần"
              min={1}
              max={52}
              style={{ width: '100%' }}
              value={tuan}
              onChange={setTuan}
              addonBefore="Tuần"
            />
          </Col>
          <Col span={5}>
            <Select
              placeholder="Chọn lớp"
              style={{ width: '100%' }}
              disabled={!selNamHoc}
              value={selLop}
              onChange={loadHS}
              options={dsLop.map(l => ({ value: l.id, label: l.ten_lop }))}
            />
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              disabled={!selLop || !selNamHoc}
              onClick={() => {
                form.resetFields()
                setModalOpen(true)
              }}
            >
              Thêm
            </Button>
          </Col>
          <Col>
            <Badge count={dsHS.length} showZero>
              <Text type="secondary" style={{ marginLeft: 8 }}>
                Học sinh: {dsHS.length}
              </Text>
            </Badge>
          </Col>
        </Row>
      </Card>

      <Table
        rowKey="id"
        columns={cols}
        dataSource={dsHS}
        loading={loadingHS || loading}
        size="small"
        bordered
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Tổng: ${total} học sinh`
        }}
        locale={{
          emptyText: selLop ? 'Không có học sinh trong lớp này' : 'Chọn lớp để xem danh sách'
        }}
        expandable={{
          expandedRowRender: (record) => {
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
                    title: 'Điểm', dataIndex: 'so_diem', width: 80,
                    render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text>
                  },
                  { title: 'Ngày', dataIndex: 'ngay_xay_ra', width: 100 },
                  { title: 'Mô tả', dataIndex: 'mo_ta', render: v => v || '—' },
                  {
                    title: 'Xóa',
                    width: 60,
                    render: (_, vp) => (
                      <Popconfirm title="Xóa?" onConfirm={() => onXoa(vp.id)}>
                        <Button size="small" danger icon={<DeleteOutlined />} />
                      </Popconfirm>
                    )
                  }
                ]}
                pagination={false}
                size="small"
              />
            )
          },
          expandRowByClick: true,
          expandedRowClassName: () => 'expand-row',
        }}
      />

      <Modal
        title="Thêm vi phạm / thành tích cá nhân"
        open={modalOpen}
        onOk={onThem}
        onCancel={() => setModalOpen(false)}
        okText="Lưu"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Form.Item name="hoc_sinh_id" label="Học sinh" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="Chọn học sinh"
              options={dsHS.map(h => ({
                value: h.id,
                label: `${h.ma_hoc_sinh} - ${h.ho_ten}`
              }))}
            />
          </Form.Item>
          <Form.Item name="loai_vi_pham_id" label="Loại vi phạm / thành tích" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="Chọn loại"
              options={dsLoaiVP.map(l => ({
                value: l.id,
                label: `${l.ten_loi} (${l.so_diem > 0 ? '+' : ''}${l.so_diem})`,
              }))}
            />
          </Form.Item>
          <Row gutter={8}>
            <Col span={14}>
              <Form.Item name="ngay_xay_ra" label="Ngày" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={10}>
              <Form.Item name="tiet" label="Tiết">
                <InputNumber min={1} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

// ════════════════════════════════════════════════════
//  TAB DANH MỤC
// ════════════════════════════════════════════════════
function TabDanhMuc({ meta }) {
  const { setDsLoaiVP } = meta
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState(null)
  const [form] = Form.useForm()

  // ⭐ State lưu số ngày trong tuần (lấy từ localStorage)
  const [soNgayTrongTuan, setSoNgayTrongTuan] = useState(() => {
    return parseInt(localStorage.getItem('soNgayTrongTuan')) || 5
  })

  const load = async () => {
    setLoading(true)
    try {
      const r = await api.get('/loai-vi-pham')
      setData(r.data)
      setDsLoaiVP(r.data)
    } catch { } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  // ⭐ Cập nhật số ngày trong tuần
  const handleChangeSoNgay = (value) => {
    setSoNgayTrongTuan(value)
    localStorage.setItem('soNgayTrongTuan', value)
    message.success(`Đã cập nhật số ngày trong tuần: ${value} ngày`)
    // ⭐ Reload lại trang để áp dụng
    setTimeout(() => {
      window.location.reload()
    }, 500)
  }

  const onSave = async () => {
    try {
      const v = await form.validateFields()
      if (edit) await api.put(`/loai-vi-pham/${edit.id}`, v)
      else await api.post('/loai-vi-pham', v)
      message.success('Lưu thành công')
      setOpen(false)
      load()
    } catch (err) { message.error(err.response?.data?.detail || 'Lỗi') }
  }

  const onXoa = async (id) => {
    await api.delete(`/loai-vi-pham/${id}`)
    message.success('Đã xóa')
    load()
  }

  const cols = [
    { title: 'Mã', dataIndex: 'ma_loi', width: 90 },
    { title: 'Tên', dataIndex: 'ten_loi' },
    {
      title: 'Loại', dataIndex: 'loai', width: 110,
      render: v => <Tag color={v === 'vi_pham' ? 'red' : 'green'}>
        {v === 'vi_pham' ? '⚠ Vi phạm' : '⭐ Thành tích'}
      </Tag>
    },
    { title: 'Nhóm', dataIndex: 'nhom', width: 120, render: v => v || '—' },
    {
      title: 'Điểm', dataIndex: 'so_diem', width: 80,
      render: v => <Text type={v < 0 ? 'danger' : 'success'}>{v > 0 ? `+${v}` : v}</Text>
    },
    { title: 'Thứ tự', dataIndex: 'thu_tu', width: 80 },
    {
      title: 'Thao tác', width: 100,
      render: (_, r) => (
        <Space size={4}>
          <Button size="small" onClick={() => { setEdit(r); form.setFieldsValue(r); setOpen(true) }}>Sửa</Button>
          <Popconfirm title="Xóa?" onConfirm={() => onXoa(r.id)}
            okText="Xóa" cancelText="Hủy" okButtonProps={{ danger: true }}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <>
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Text strong style={{ marginRight: 8 }}>📅 Số ngày trong tuần:</Text>
          <Select
            value={soNgayTrongTuan}
            onChange={handleChangeSoNgay}
            style={{ width: 120 }}
            options={[
              { value: 5, label: '5 ngày' },
              { value: 6, label: '6 ngày' },
            ]}
          />
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
            (Áp dụng cho tất cả lớp trong tuần)
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { setEdit(null); form.resetFields(); setOpen(true) }}>
          Thêm danh mục
        </Button>
      </div>

      <Table rowKey="id" columns={cols} dataSource={data}
        loading={loading} size="small" bordered
        pagination={{ pageSize: 15 }} />

      <Modal title={edit ? 'Sửa danh mục' : 'Thêm danh mục'} open={open}
        onOk={onSave} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
        <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
          <Row gutter={8}>
            <Col span={10}>
              <Form.Item name="ma_loi" label="Mã" rules={[{ required: true }]}>
                <Input placeholder="VP001" />
              </Form.Item>
            </Col>
            <Col span={14}>
              <Form.Item name="loai" label="Loại" rules={[{ required: true }]}>
                <Select options={[
                  { value: 'vi_pham', label: '⚠ Vi phạm' },
                  { value: 'thanh_tich', label: '⭐ Thành tích' },
                ]} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="ten_loi" label="Tên" rules={[{ required: true }]}>
            <Input placeholder="VD: Đi học muộn" />
          </Form.Item>
          <Row gutter={8}>
            <Col span={12}>
              <Form.Item name="nhom" label="Nhóm">
                <Input placeholder="VD: Nề nếp" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="so_diem" label="Điểm" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} step={0.5} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="thu_tu" label="Thứ tự" initialValue={0}>
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
// ════════════════════════════════════════════════════
//  TRANG CHÍNH
// ════════════════════════════════════════════════════
export default function ThiDuaHSPage() {
  const meta = useMeta()

  const tabs = [
    { key: 'tap-the', label: '🏫 Tập thể', children: <TabTapThe meta={meta} /> },
    { key: 'ca-nhan', label: '👤 Cá nhân', children: <TabCaNhan meta={meta} /> },
    { key: 'danh-muc', label: '📋 Danh mục', children: <TabDanhMuc meta={meta} /> },
  ]

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>🎓 Thi Đua Học Sinh</Title>
      <Tabs items={tabs} type="card" />
    </div>
  )
}