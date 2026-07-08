// frontend/src/pages/Reports/hooks/useReport.js
import { useState, useCallback, useEffect } from 'react'
import { message } from 'antd'
import { reportsAPI } from '../services/api'
import { metaAPI } from '../../ThiDuaHS/services/api'

export function useReport() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [filters, setFilters] = useState({
    loai: 'tuan',
    nam_hoc_id: null,
    hoc_ky_id: null,
    thang_id: null,
    tuan: null,
    lop_hoc_id: null,
    khoi: null,
  })

  // ⭐ Load danh sách năm học và tự động chọn năm học active
  useEffect(() => {
    const loadNamHoc = async () => {
      try {
        const r = await metaAPI.getNamHoc()
        setDsNamHoc(r.data || [])
        
        // ⭐ Tìm năm học active (mặc định)
        const activeNamHoc = r.data?.find(n => n.active === true)
        if (activeNamHoc) {
          setFilters(prev => ({
            ...prev,
            nam_hoc_id: activeNamHoc.id
          }))
        } else if (r.data && r.data.length > 0) {
          // Nếu không có active, lấy năm học đầu tiên
          setFilters(prev => ({
            ...prev,
            nam_hoc_id: r.data[0].id
          }))
        }
      } catch (error) {
        console.error('❌ Lỗi load năm học:', error)
      }
    }
    loadNamHoc()
  }, [])

  // ⭐ Tự động tạo báo cáo mặc định khi có năm học
  useEffect(() => {
    if (filters.nam_hoc_id) {
      generateReport()
    }
  }, [filters.nam_hoc_id])

  const generateReport = useCallback(async (newFilters) => {
    const finalFilters = { ...filters, ...newFilters }
    setFilters(finalFilters)
    
    // Kiểm tra bộ lọc tối thiểu
    if (!finalFilters.loai) {
      message.warning('Vui lòng chọn loại báo cáo')
      return
    }
    
    if (finalFilters.loai === 'tuan' && !finalFilters.nam_hoc_id) {
      message.warning('Vui lòng chọn năm học')
      return
    }
    
    if (finalFilters.loai === 'thang' && !finalFilters.thang_id) {
      message.warning('Vui lòng chọn tháng')
      return
    }
    
    if (finalFilters.loai === 'hoc_ky' && !finalFilters.hoc_ky_id) {
      message.warning('Vui lòng chọn học kỳ')
      return
    }
    
    if (finalFilters.loai === 'nam_hoc' && !finalFilters.nam_hoc_id) {
      message.warning('Vui lòng chọn năm học')
      return
    }
    
    setLoading(true)
    try {
      console.log('🔍 Gọi API báo cáo với filters:', finalFilters)
      const result = await reportsAPI.getReport(finalFilters)
      console.log('✅ Dữ liệu báo cáo:', result.data)
      setData(result.data)
      return result.data
    } catch (error) {
      console.error('❌ Lỗi tải báo cáo:', error)
      message.error(error.response?.data?.detail || 'Không thể tải báo cáo')
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [filters])

  const updateFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }, [])

  const resetFilters = useCallback(() => {
    setFilters({
      loai: 'tuan',
      nam_hoc_id: dsNamHoc.find(n => n.active === true)?.id || dsNamHoc[0]?.id || null,
      hoc_ky_id: null,
      thang_id: null,
      tuan: null,
      lop_hoc_id: null,
      khoi: null,
    })
    setData(null)
  }, [dsNamHoc])

  return {
    data,
    loading,
    filters,
    dsNamHoc,
    generateReport,
    updateFilter,
    resetFilters,
  }
}