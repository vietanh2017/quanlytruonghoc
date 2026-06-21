# modules/competition/models/diem_tap_the.py

from sqlalchemy import Column, Integer, Float, ForeignKey, Text, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db.base import Base


class DiemTapTheLop(Base):
    """
    Điểm thi đua tập thể lớp theo tuần
    Lưu điểm học tập (từ sổ đầu bài) và điểm Đội cho từng lớp trong từng tuần
    """
    __tablename__ = "diem_tap_the_lop"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)  # Tuần 1-35

    # Hai loại điểm
    diem_hoc_tap = Column(Float, default=0.0)   # Từ sổ đầu bài (0-100)
    diem_doi = Column(Float, default=0.0)       # Từ Đội + điều chỉnh từ cá nhân

    # Trạng thái
    da_khoa = Column(Boolean, default=False)    # Khóa điểm sau khi tổng kết
    ghi_chu = Column(Text, nullable=True)

    # Người nhập & thời gian
    nguoi_nhap = Column(String(200), nullable=True)
    ngay_nhap = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    nam_hoc = relationship("NamHoc", foreign_keys=[nam_hoc_id])
    lop_hoc = relationship("LopHoc", foreign_keys=[lop_hoc_id])

    def __repr__(self):
        return f"<DiemTapTheLop(lop={self.lop_hoc_id}, tuan={self.tuan}, tong={self.tong_diem})>"

    @property
    def tong_diem(self):
        """Tổng điểm tuần = học tập + đội"""
        return (self.diem_hoc_tap or 0) + (self.diem_doi or 0)