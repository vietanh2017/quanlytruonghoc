// frontend/src/pages/CauHinh/components/TabPhanQuyen.jsx
// Dùng độc lập hoặc nhúng vào CauHinhPage.jsx

import React, { useEffect, useState, useCallback } from 'react'
import {
  Select, Checkbox, Button, Spin, Tag, Space,
  Typography, Divider, message, Card, Row, Col, Badge,
} from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import axios from 'axios'

const { Title, Text } = Typography
const api = axios.create({ baseURL: 'http://localhost:8000/api/v1/cau-hinh' })

// ── Cấu hình vai trò ─────────────────────────────────────────
const ROLES = [
  { value: 'ADMIN',          label: 'Admin',          color: 'red'    },
  { value: 'TO_TRUONG',      label: 'Tổ trưởng',      color: 'orange' },
  { value: 'PHO_TO_TRUONG',  label: 'Phó tổ trưởng',  color: 'gold'   },
  { value: 'TONG_PHU_TRACH', label: 'Tổng phụ trách', color: 'purple' },
  { value: 'GIAO_VIEN',      label: 'Giáo viên',      color: 'blue'   },
  { value: 'NHAN_VIEN',      label: 'Nhân viên',      color: 'cyan'   },
]

// Tên hiển thị đẹp hơn cho từng module
const MODULE_LABELS = {
  thi_dua_giao_vien: '🏆 Thi đua giáo viên',
  thi_dua_hoc_sinh:  '🎓 Thi đua học sinh',
  thoi_khoa_bieu:    '📅 Thời khóa biểu',
  phan_cong:         '📋 Phân công',
  bao_cao:           '📊 Báo cáo',
}

export default function TabPhanQuyen() {
  const [selectedRole, setSelectedRole]   = useState(null)
  const [allQuyen, setAllQuyen]           = useState([])   // toàn bộ quyền
  const [checkedIds, setCheckedIds]       = useState([])   // quyền đang tick
  const [originalIds, setOriginalIds]     = useState([])   // để detect thay đổi
  const [loadingQuyen, setLoadingQuyen]   = useState(false)
  const [saving, setSaving]               = useState(false)

  // Load toàn bộ danh sách quyền 1 lần
  useEffect(() => {
    api.get('/phan-quyen/tat-ca-quyen')
      .then(res => setAllQuyen(res.data))
      .catch(() => message.error('Không tải được danh sách quyền'))
  }, [])

  // Load quyền của vai trò được chọn
  const loadQuyenCuaVaiTro = useCallback(async (vaiTro) => {
    setLoadingQuyen(true)
    try {
      const res = await api.get(`/phan-quyen/${vaiTro}`)
      setCheckedIds(res.data)
      setOriginalIds(res.data)
    } catch {
      message.error('Không tải được quyền của vai trò')
    } finally {
      setLoadingQuyen(false)
    }
  }, [])

  const onSelectRole = (val) => {
    setSelectedRole(val)
    setCheckedIds([])
    loadQuyenCuaVaiTro(val)
  }

  // Tick / untick một quyền
  const onToggle = (quyenId, checked) => {
    setCheckedIds(prev =>
      checked ? [...prev, quyenId] : prev.filter(id => id !== quyenId)
    )
  }

  // Chọn / bỏ chọn cả module
  const onToggleModule = (moduleIds, checked) => {
    setCheckedIds(prev => {
      const set = new Set(prev)
      moduleIds.forEach(id => checked ? set.add(id) : set.delete(id))
      return Array.from(set)
    })
  }

  // Lưu
  const onSave = async () => {
    if (!selectedRole) return
    setSaving(true)
    try {
      await api.post(`/phan-quyen/${selectedRole}`, { quyen_ids: checkedIds })
      setOriginalIds(checkedIds)
      message.success('Đã lưu phân quyền thành công!')
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi khi lưu')
    } finally {
      setSaving(false)
    }
  }

  const onReset = () => {
    setCheckedIds(originalIds)
    message.info('Đã hoàn tác thay đổi')
  }

  // Nhóm quyền theo module
  const grouped = allQuyen.reduce((acc, q) => {
    const mod = q.module || 'khac'
    if (!acc[mod]) acc[mod] = []
    acc[mod].push(q)
    return acc
  }, {})

  const hasChanged = JSON.stringify([...checkedIds].sort()) !==
                     JSON.stringify([...originalIds].sort())

  const roleCfg = ROLES.find(r => r.value === selectedRole)

  return (
    <div>
      {/* Chọn vai trò */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={16}>
          <Col>
            <Text strong>Chọn vai trò:</Text>
          </Col>
          <Col flex="300px">
            <Select
              style={{ width: '100%' }}
              placeholder="-- Chọn vai trò để phân quyền --"
              onChange={onSelectRole}
              value={selectedRole}
              options={ROLES.map(r => ({
                value: r.value,
                label: <Tag color={r.color}>{r.label}</Tag>,
              }))}
            />
          </Col>
          {selectedRole && (
            <Col>
              <Space>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={onReset}
                  disabled={!hasChanged}
                >
                  Hoàn tác
                </Button>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  loading={saving}
                  onClick={onSave}
                  disabled={!hasChanged}
                >
                  Lưu thay đổi
                </Button>
              </Space>
            </Col>
          )}
        </Row>
      </Card>

      {/* Danh sách quyền */}
      {!selectedRole && (
        <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
          <Text type="secondary">👆 Chọn một vai trò để xem và chỉnh sửa quyền</Text>
        </div>
      )}

      {selectedRole && loadingQuyen && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin tip="Đang tải quyền..." />
        </div>
      )}

      {selectedRole && !loadingQuyen && (
        <>
          {/* Header tóm tắt */}
          <div style={{ marginBottom: 16 }}>
            <Tag color={roleCfg?.color} style={{ fontSize: 14, padding: '4px 12px' }}>
              {roleCfg?.label}
            </Tag>
            <Text type="secondary">
              — đang có <Text strong>{checkedIds.length}</Text> / {allQuyen.length} quyền
              {hasChanged && <Text type="warning"> (chưa lưu)</Text>}
            </Text>
          </div>

          {/* Từng module */}
          <Row gutter={[16, 16]}>
            {Object.entries(grouped).map(([mod, quyens]) => {
              const moduleIds  = quyens.map(q => q.id)
              const checkedCnt = moduleIds.filter(id => checkedIds.includes(id)).length
              const allChecked = checkedCnt === moduleIds.length
              const partChecked = checkedCnt > 0 && !allChecked

              return (
                <Col key={mod} xs={24} sm={12} lg={8}>
                  <Card
                    size="small"
                    title={
                      <Checkbox
                        checked={allChecked}
                        indeterminate={partChecked}
                        onChange={e => onToggleModule(moduleIds, e.target.checked)}
                      >
                        <Text strong>{MODULE_LABELS[mod] || mod}</Text>
                        <Badge
                          count={checkedCnt}
                          showZero
                          style={{
                            marginLeft: 8,
                            backgroundColor: checkedCnt > 0 ? '#52c41a' : '#d9d9d9',
                          }}
                        />
                      </Checkbox>
                    }
                    style={{
                      borderColor: checkedCnt > 0 ? '#b7eb8f' : '#d9d9d9',
                      background: checkedCnt === moduleIds.length ? '#f6ffed' : '#fff',
                    }}
                  >
                    <Space direction="vertical" style={{ width: '100%' }} size={4}>
                      {quyens.map(q => (
                        <Checkbox
                          key={q.id}
                          checked={checkedIds.includes(q.id)}
                          onChange={e => onToggle(q.id, e.target.checked)}
                        >
                          <span>{q.ten_quyen}</span>
                          {q.mo_ta && (
                            <Text type="secondary" style={{ fontSize: 11, display: 'block', marginLeft: 0 }}>
                              {q.mo_ta}
                            </Text>
                          )}
                        </Checkbox>
                      ))}
                    </Space>
                  </Card>
                </Col>
              )
            })}
          </Row>

          {/* Nút lưu ở dưới cùng nếu nhiều module */}
          {Object.keys(grouped).length > 3 && (
            <div style={{ marginTop: 24, textAlign: 'right' }}>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={onReset} disabled={!hasChanged}>
                  Hoàn tác
                </Button>
                <Button type="primary" icon={<SaveOutlined />}
                  loading={saving} onClick={onSave} disabled={!hasChanged}>
                  Lưu thay đổi
                </Button>
              </Space>
            </div>
          )}
        </>
      )}
    </div>
  )
}
