// frontend/src/pages/ThiDuaHS/utils/excelExport.js
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

/**
 * Xuất dữ liệu ra file Excel
 */
export const exportToExcel = (data, fileName = 'export', headers = null) => {
  if (!data || data.length === 0) {
    alert('Không có dữ liệu để xuất!')
    return
  }

  let exportData = data
  if (headers) {
    exportData = data.map(row => {
      const newRow = {}
      headers.forEach(h => {
        newRow[h.label] = row[h.key] !== undefined ? row[h.key] : ''
      })
      return newRow
    })
  }

  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')

  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })
  saveAs(blob, `${fileName}.xlsx`)
}

/**
 * Xuất dữ liệu bảng điểm tuần
 */
export const exportDiemTuan = (data, tuan, namHoc) => {
  const namHocText = namHoc || '2024-2025'

  console.log('📊 Dữ liệu xuất Excel:', data) // Debug kiểm tra dữ liệu

  const headers = [
    { key: 'ten_lop', label: 'Lớp' },
    { key: 'khoi', label: 'Khối' },
    { key: 'diem_doi', label: 'TB điểm đội' },
    { key: 'diem_hoc_tap', label: 'Điểm HT (SĐB)' },
    { key: 'trung_binh', label: 'Trung bình' },
    { key: 'xep_hang', label: 'Xếp hạng' },
    { key: 'ghi_chu', label: 'Ghi chú' },
  ]

  const exportData = data.map(row => ({
    ten_lop: row.ten_lop || '',
    khoi: row.khoi || '',
    diem_doi: row.diem_doi?.toFixed(3) || '0.000',
    diem_hoc_tap: row.diem_hoc_tap?.toFixed(3) || '0.000',
    trung_binh: row.trung_binh?.toFixed(3) || '0.000',
    xep_hang: row.xep_hang || '',  // ⭐ Lấy từ dữ liệu đã tính
    ghi_chu: row.ghi_chu || '',
  }))

  const fileName = `Diem_thi_dua_tuan_${tuan}_${namHocText}`
  exportToExcel(exportData, fileName, headers)
}

/**
 * Xuất dữ liệu báo cáo tháng
 */
export const exportBaoCaoThang = (data, thang, tuanList) => {
  if (!data || data.length === 0) {
    alert('Không có dữ liệu để xuất!')
    return
  }

  console.log('📊 Xuất báo cáo tháng:', { thang, tuanList, data }) // Debug

  // Tạo headers động từ danh sách tuần
  const headers = [
    { key: 'ten_lop', label: 'Lớp' },
    { key: 'khoi', label: 'Khối' },
  ]

  // Thêm các cột tuần
  tuanList.forEach(t => {
    headers.push({ key: `tuan_${t}`, label: `Tuần ${t}` })
  })

  headers.push(
    { key: 'trung_binh', label: 'Trung bình' },
    { key: 'xep_hang', label: 'Xếp hạng' }
  )

  // Chuyển đổi dữ liệu
  const exportData = data.map(row => {
    const newRow = {
      ten_lop: row.ten_lop || '',
      khoi: row.khoi || '',
    }
    // Thêm điểm từng tuần
    tuanList.forEach(t => {
      newRow[`tuan_${t}`] = row.cac_tuan?.[t]?.toFixed(3) || '0.000'
    })
    newRow.trung_binh = row.trung_binh?.toFixed(3) || '0.000'
    newRow.xep_hang = row.xep_hang || ''
    return newRow
  })

  const fileName = `Bao_cao_thang_${thang}`
  exportToExcel(exportData, fileName, headers)
}

// frontend/src/pages/ThiDuaHS/utils/excelExport.js

/**
 * Xuất dữ liệu báo cáo học kỳ
 */
export const exportBaoCaoHocKy = (data, hocKy, thangList) => {
  if (!data || data.length === 0) {
    alert('Không có dữ liệu để xuất!')
    return
  }

  console.log('📊 Xuất báo cáo học kỳ:', { hocKy, thangList, data }) // Debug

  // Tạo headers động từ danh sách tháng
  const headers = [
    { key: 'ten_lop', label: 'Lớp' },
    { key: 'khoi', label: 'Khối' },
  ]

  // Thêm các cột tháng
  thangList.forEach(t => {
    headers.push({ key: `thang_${t}`, label: t })
  })

  headers.push(
    { key: 'trung_binh', label: 'Trung bình' },
    { key: 'xep_hang', label: 'Xếp hạng' }
  )

  // Chuyển đổi dữ liệu
  const exportData = data.map(row => {
    const newRow = {
      ten_lop: row.ten_lop || '',
      khoi: row.khoi || '',
    }
    // Thêm điểm từng tháng
    thangList.forEach(t => {
      newRow[`thang_${t}`] = row.cac_thang?.[t]?.toFixed(3) || '0.000'
    })
    newRow.trung_binh = row.trung_binh?.toFixed(3) || '0.000'
    newRow.xep_hang = row.xep_hang || ''
    return newRow
  })

  const fileName = `Bao_cao_hoc_ky_${hocKy}`
  exportToExcel(exportData, fileName, headers)
}
/**
 * Xuất dữ liệu báo cáo năm học
 */
export const exportBaoCaoNamHoc = (data, hocKyList) => {
  if (!data || data.length === 0) {
    alert('Không có dữ liệu để xuất!')
    return
  }

  console.log('📊 Xuất Excel báo cáo năm học:', { hocKyList, data })

  const headers = [
    { key: 'ten_lop', label: 'Lớp' },
    { key: 'khoi', label: 'Khối' },
  ]

  hocKyList.forEach(hk => {
    headers.push({ key: `hoc_ky_${hk}`, label: hk })
  })

  headers.push(
    { key: 'trung_binh', label: 'Trung bình năm' },
    { key: 'xep_hang', label: 'Xếp hạng' }
  )

  const exportData = data.map(row => {
    const newRow = {
      ten_lop: row.ten_lop || '',
      khoi: row.khoi || '',
    }
    hocKyList.forEach(hk => {
      newRow[`hoc_ky_${hk}`] = row.cac_hoc_ky?.[hk]?.toFixed(3) || '0.000'
    })
    newRow.trung_binh = row.trung_binh?.toFixed(3) || '0.000'
    newRow.xep_hang = row.xep_hang || ''
    return newRow
  })

  const fileName = `Bao_cao_nam_hoc`
  exportToExcel(exportData, fileName, headers)
}