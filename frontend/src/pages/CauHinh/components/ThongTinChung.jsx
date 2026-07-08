// frontend/src/pages/CauHinh/components/ThongTinChung.jsx
import React, { useState, useEffect } from 'react'
import {
  Card, Form, Input, Select, DatePicker, Button, message,
  Row, Col, Space, Divider, Spin, Upload
} from 'antd'
import { SaveOutlined, ReloadOutlined, UploadOutlined } from '@ant-design/icons'
// ⭐ Import API từ file cauHinh.js
import { thongTinTruongAPI, namHocAPI, hocKyAPI } from '../../../api/cauHinh'
import dayjs from 'dayjs'

export default function ThongTinChung() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsHocKy, setDsHocKy] = useState([])

  useEffect(() => {
    loadData()
    loadNamHoc()
    loadHocKy()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const r = await thongTinTruongAPI.get()
      if (r.data) {
        const data = { ...r.data }
        if (data.ngay_bat_dau) {
          data.ngay_bat_dau = dayjs(data.ngay_bat_dau)
        }
        if (data.ngay_ket_thuc) {
          data.ngay_ket_thuc = dayjs(data.ngay_ket_thuc)
        }
        form.setFieldsValue(data)
      }
    } catch (error) {
      message.error('Không tải được thông tin: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadNamHoc = async () => {
    try {
      const r = await namHocAPI.getAll()
      setDsNamHoc(r.data || [])
    } catch (error) {
      console.error('Load năm học lỗi:', error)
    }
  }

  const loadHocKy = async () => {
    try {
      const r = await hocKyAPI.getAll()
      setDsHocKy(r.data || [])
    } catch (error) {
      console.error('Load học kỳ lỗi:', error)
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      
      const data = { ...values }
      if (data.ngay_bat_dau) {
        data.ngay_bat_dau = data.ngay_bat_dau.format('YYYY-MM-DD')
      }
      if (data.ngay_ket_thuc) {
        data.ngay_ket_thuc = data.ngay_ket_thuc.format('YYYY-MM-DD')
      }
      
      await thongTinTruongAPI.create(data)
      message.success('Lưu thông tin thành công!')
      await loadData()
    } catch (error) {
      if (error.errorFields) return
      message.error('Lưu thất bại: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Spin spinning={loading}>
      <Card
        title={
          <Space>
            <span>🏫 Thông tin chung</span>
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={loadData}
              loading={loading}
            />
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
            style={{ background: '#1D9E75', borderColor: '#1D9E75' }}
          >
            Lưu thông tin
          </Button>
        }
      >
        <Form form={form} layout="vertical" disabled={loading}>
          <Divider orientation="left">🏛️ Thông tin trường</Divider>

          <Row gutter={24}>
            <Col span={24}>
              <Form.Item
                label="Tên trường"
                name="ten_truong"
                rules={[{ required: true, message: 'Vui lòng nhập tên trường' }]}
              >
                <Input placeholder="Nhập tên trường" size="large" />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item label="Tên trường (Tiếng Anh)" name="ten_truong_tieng_anh">
                <Input placeholder="Nhập tên trường tiếng Anh" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Mã số trường" name="ma_so_truong">
                <Input placeholder="Nhập mã số trường" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Website" name="website">
                <Input placeholder="https://truong.edu.vn" />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item label="Địa chỉ" name="dia_chi">
                <Input placeholder="Nhập địa chỉ trường" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Điện thoại" name="dien_thoai">
                <Input placeholder="(0234) 3xxx.xxx" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Email" name="email">
                <Input placeholder="truong@tinh.edu.vn" />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item label="Logo" name="logo">
                <Upload maxCount={1} listType="picture-card" beforeUpload={() => false}>
                  <div>
                    <UploadOutlined />
                    <div style={{ marginTop: 8 }}>Upload Logo</div>
                  </div>
                </Upload>
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">📅 Năm học - Học kỳ</Divider>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item label="Năm học" name="nam_hoc_id">
                <Select placeholder="Chọn năm học" allowClear showSearch optionFilterProp="label">
                  {dsNamHoc.map(item => (
                    <Select.Option key={item.id} value={item.id} label={item.ten_nam_hoc}>
                      {item.ten_nam_hoc}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Học kỳ" name="hoc_ky_id">
                <Select placeholder="Chọn học kỳ" allowClear showSearch optionFilterProp="label">
                  {dsHocKy.map(item => (
                    <Select.Option key={item.id} value={item.id} label={item.ten_hoc_ky}>
                      {item.ten_hoc_ky}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Ngày bắt đầu" name="ngay_bat_dau">
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Ngày kết thúc" name="ngay_ket_thuc">
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">👨‍🏫 Lãnh đạo</Divider>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item label="Hiệu trưởng" name="hieu_truong">
                <Input placeholder="Tên hiệu trưởng" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Hiệu phó" name="hieu_pho">
                <Input placeholder="Tên hiệu phó" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Tổ trưởng chuyên môn" name="to_truong_cm">
                <Input placeholder="Tên tổ trưởng chuyên môn" />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item label="Người lập" name="nguoi_lap">
                <Input placeholder="Tên người lập" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
    </Spin>
  )
}