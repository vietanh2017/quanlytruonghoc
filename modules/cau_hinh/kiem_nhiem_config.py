# modules/cau_hinh/kiem_nhiem_config.py
"""
Cấu hình số tiết giảm theo kiêm nhiệm (Thông tư 28)
"""

SO_TIET_GIAM_THEO_KIEM_NHIEM = {
    "Tổ trưởng CM": 2,
    "Tổ phó CM": 1,
    "Bí thư Đoàn": 2,
    "Phó Bí thư Đoàn": 1,
    "Tổng phụ trách Đội": 2,
    "Nữ công": 1,
    "Phụ trách phòng bộ môn": 3,
    "Thư ký hội đồng": 2,
    "Thủ quỹ": 1,
    "Y tế học đường": 2,
    "Khác": 1,
}

# Danh sách kiêm nhiệm để hiển thị dropdown
DANH_SACH_KIEM_NHIEM = list(SO_TIET_GIAM_THEO_KIEM_NHIEM.keys())


def get_so_tiet_giam(kiem_nhiem: str) -> int:
    """Lấy số tiết được giảm theo kiêm nhiệm"""
    return SO_TIET_GIAM_THEO_KIEM_NHIEM.get(kiem_nhiem, 0)


def get_ten_kiem_nhiem(giam_tiet: int) -> list:
    """Lấy danh sách kiêm nhiệm có số tiết giảm tương ứng"""
    result = []
    for ten, so_tiet in SO_TIET_GIAM_THEO_KIEM_NHIEM.items():
        if so_tiet == giam_tiet:
            result.append(ten)
    return result