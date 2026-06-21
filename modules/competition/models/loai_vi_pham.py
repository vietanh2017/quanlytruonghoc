# modules/competition/models/loai_vi_pham.py

from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from core.db.base import Base


class LoaiViPham(Base):
    """
    Danh mục lỗi vi phạm / thành tích cho học sinh
    Dùng cho cả điểm cộng (thành tích) và điểm trừ (vi phạm)
    """
    __tablename__ = "loai_vi_pham"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_loi = Column(String(20), unique=True, nullable=False)  # VP001, TT001
    ten_loi = Column(String(200), nullable=False)  # "Đi học muộn", "Tham gia văn nghệ"
    loai = Column(String(20), nullable=False)  # "vi_pham" hoặc "thanh_tich"
    nhom = Column(String(100))  # "Nề nếp", "ATGT", "Văn nghệ", "Thể thao"
    so_diem = Column(Float, default=0)  # Số âm cho vi phạm, số dương cho thành tích
    mo_ta = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    thu_tu = Column(Integer, default=0)  # Thứ tự hiển thị

    def __repr__(self):
        return f"<LoaiViPham(ma={self.ma_loi}, ten={self.ten_loi}, diem={self.so_diem})>"