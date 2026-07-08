// frontend/src/pages/ThiDuaHS/modals/ModalThemVPTapThe.jsx
import React from 'react'
import { Modal, Form, Select, InputNumber, DatePicker, Input, Row, Col, message } from 'antd'
import dayjs from 'dayjs'
import { tapTheAPI } from '../services/api'

export default function ModalThemVPTapThe({
  open, onClose, onSuccess, dsLop, dsLoaiTapThe, selNamHoc, tuan
}) {
  const [form] = Form.useForm()

  // ⭐ State để lưu điểm tối đa của loại đã chọn
  const [maxScore, setMaxScore] = React.useState(0)

  const handleSubmit = async () => {
    try {
      const v = await form.validateFields()
      const selected = dsLoaiTapThe.find(l => l.id === v.loai_vi_pham_id)
      const finalDiem = selected?.loai === 'vi_pham' ? -v.so_diem : v.so_diem

      await tapTheAPI.create({
        lop_hoc_id: v.lop_hoc_id,
        loai_vi_pham_id: v.loai_vi_pham_id,
        so_diem: finalDiem,
        ngay_xay_ra: v.ngay_xay_ra.format('YYYY-MM-DD'),
        nam_hoc_id: selNamHoc,
        tuan: tuan,
        tiet: v.tiet,
        mo_ta: v.mo_ta || '',
      })

      message.success('Thêm thành công')
      form.resetFields()
      setMaxScore(0)  // Reset state
      onSuccess()
      onClose()
    } catch (err) {
      message.error(err.response?.data?.detail || 'Lỗi')
    }
  }

  return (
    <Modal
      title="Thêm vi phạm / thành tích tập thể"
      open={open}
      onOk={handleSubmit}
      onCancel={() => {
        form.resetFields()
        setMaxScore(0)
        onClose()
      }}
      okText="Lưu"
      cancelText="Hủy"
      centered
    >
      <Form form={form} layout="vertical" style={{ marginTop: 12 }}>
        <Form.Item name="lop_hoc_id" label="Lớp" rules={[{ required: true }]}>
          <Select
            showSearch
            optionFilterProp="label"
            placeholder="Chọn lớp"
            options={dsLop.map(l => ({ value: l.id, label: l.ten_lop }))}
          />
        </Form.Item>

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
                // ⭐ KHÔNG tự động set giá trị, để người dùng nhập
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
          rules={[{ required: true, message: 'Nhập điểm số' }]}
          extra={`Tối đa: ${maxScore} điểm`}  // ⭐ Hiển thị điểm tối đa
        >
          <InputNumber
            min={0}
            max={maxScore || 10}  // ⭐ Giới hạn theo điểm tối đa
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