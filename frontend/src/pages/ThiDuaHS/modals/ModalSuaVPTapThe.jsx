// frontend/src/pages/ThiDuaHS/modals/ModalSuaVPTapThe.jsx
import React from 'react'
import { Modal, Form, Select, InputNumber, DatePicker, Input, Row, Col, message } from 'antd'
import dayjs from 'dayjs'
import { tapTheAPI } from '../services/api'

export default function ModalSuaVPTapThe({ open, onClose, onSuccess, editing, dsLoaiTapThe, form }) {
  const [maxScore, setMaxScore] = React.useState(0)

  // ⭐ Khi editing thay đổi, cập nhật maxScore
  React.useEffect(() => {
    if (editing) {
      const selected = dsLoaiTapThe.find(l => l.id === editing.loai_vi_pham_id)
      setMaxScore(selected ? Math.abs(selected.so_diem) : 0)
    }
  }, [editing, dsLoaiTapThe])

  const handleSubmit = async () => {
    try {
      const v = await form.validateFields()
      const selected = dsLoaiTapThe.find(l => l.id === v.loai_vi_pham_id)
      const finalDiem = selected?.loai === 'vi_pham' ? -v.so_diem : v.so_diem

      await tapTheAPI.update(editing.id, {
        loai_vi_pham_id: v.loai_vi_pham_id,
        so_diem: finalDiem,
        ngay_xay_ra: v.ngay_xay_ra.format('YYYY-MM-DD'),
        tiet: v.tiet,
        mo_ta: v.mo_ta || '',
      })

      message.success('Cập nhật thành công')
      onSuccess()
      onClose()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  return (
    <Modal
      title="Sửa vi phạm / thành tích tập thể"
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      okText="Cập nhật"
      cancelText="Hủy"
    >
      <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
        <Form.Item name="loai_vi_pham_id" label="Loại vi phạm / thành tích" rules={[{ required: true }]}>
          <Select
            showSearch
            optionFilterProp="label"
            placeholder="Chọn loại"
            onChange={(value) => {
              const selected = dsLoaiTapThe.find(l => l.id === value)
              if (selected) {
                const max = Math.abs(selected.so_diem)
                setMaxScore(max)
                form.setFieldsValue({ so_diem: undefined })
              }
            }}
            options={dsLoaiTapThe.map(l => ({
              value: l.id,
              label: `${l.ten_loi} (tối đa ${Math.abs(l.so_diem)} điểm)`,
            }))}
          />
        </Form.Item>

        <Form.Item
          name="so_diem"
          label="Điểm số"
          rules={[{ required: true }]}
          extra={`Tối đa: ${maxScore} điểm`}
        >
          <InputNumber
            min={0}
            max={maxScore || 10}
            step={0.5}
            style={{ width: '100%' }}
            placeholder={`Nhập điểm (0 - ${maxScore})`}
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
  )
}