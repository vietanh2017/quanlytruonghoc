// frontend/src/pages/ThiDuaHS/hooks/useMeta.js
import { useState, useEffect } from 'react'
import { metaAPI, loaiVpAPI } from '../services/api'

export function useMeta() {
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsLoaiVP, setDsLoaiVP] = useState([])
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [dsLop, setDsLop] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load năm học
    metaAPI.getNamHoc()
      .then(r => {
        setDsNamHoc(r.data)
        if (r.data?.length > 0) {
          const namHoc2026 = r.data.find(n => n.ten_nam_hoc.includes('2026-2027'))
          setSelNamHoc(namHoc2026 ? namHoc2026.id : r.data[0].id)
        }
      })
      .catch(err => console.error('Lỗi load năm học:', err))

    // Load loại vi phạm
    loaiVpAPI.getAll()
      .then(r => setDsLoaiVP(r.data))
      .catch(err => console.error('Lỗi load loại vi phạm:', err))

    // Load lớp
    metaAPI.getLop()
      .then(r => setDsLop(r.data))
      .catch(err => console.error('Lỗi load lớp:', err))
  }, [])

  return {
    dsNamHoc,
    dsLoaiVP,
    selNamHoc,
    dsLop,
    loading,
    setDsLoaiVP,
    setSelNamHoc,
  }
}