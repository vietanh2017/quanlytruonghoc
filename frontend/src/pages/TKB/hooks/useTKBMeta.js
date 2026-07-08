// frontend/src/pages/TKB/hooks/useTKBMeta.js
import { useState, useEffect } from 'react'
import { tkbAPI } from '../services/api'

export function useTKBMeta() {
  const [dsNamHoc, setDsNamHoc] = useState([])
  const [dsMonHoc, setDsMonHoc] = useState([])
  const [selNamHoc, setSelNamHoc] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load năm học
    tkbAPI.getNamHoc()
      .then(r => {
        const data = r.data || []
        setDsNamHoc(data)
        if (data.length > 0) setSelNamHoc(data[0].id)
      })
      .catch(err => console.error('Lỗi load năm học:', err))

    // Load môn học
    tkbAPI.getMonHoc()
      .then(r => setDsMonHoc(r.data || []))
      .catch(err => console.error('Lỗi load môn học:', err))
  }, [])

  return { dsNamHoc, dsMonHoc, selNamHoc, setSelNamHoc, loading }
}