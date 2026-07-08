// frontend/src/pages/ThiDuaHS/utils/constants.js
export const THU_LABELS = {
  2: 'Thứ 2',
  3: 'Thứ 3',
  4: 'Thứ 4',
  5: 'Thứ 5',
  6: 'Thứ 6',
}

export const TUAN_OPTIONS = Array.from({ length: 35 }, (_, i) => ({
  value: i + 1,
  label: `Tuần ${i + 1}`
}))

export const getMedal = (rank) => {
  const medals = ['🥇', '🥈', '🥉']
  return rank <= 3 ? medals[rank - 1] : `#${rank}`
}

export const getColorByScore = (score) => {
  if (score < 8) return 'red'
  if (score < 9.5) return 'orange'
  return 'green'
}

export const getSoNgayTrongTuan = () => {
  return parseInt(localStorage.getItem('soNgayTrongTuan')) || 5
}