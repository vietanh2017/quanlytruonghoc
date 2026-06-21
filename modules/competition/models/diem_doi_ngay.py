# modules/competition/models/diem_doi_ngay.py

from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db.base import Base


class DiemDoiNgay(Base):
    """
    Điểm đội theo ngày của từng lớp
    Mỗi ngày có điểm tối đa = số lượng vi phạm × 10
    Vi phạm (điểm âm) làm giảm điểm, thành tích (điểm dương) làm tăng điểm
    """
    __tablename__ = "diem_doi_ngay"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)      # Tuần 1-35
    thu = Column(Integer, nullable=False)       # 2: Thứ 2, 3: Thứ 3, ..., 6: Thứ 6
    
    # Cấu hình
    so_luong_vi_pham = Column(Integer, default=8)  # Số lượng vi phạm đang active
    diem_toi_da = Column(Integer, default=80)      # = so_luong_vi_pham × 10
    
    # Điểm thực tế
    tong_diem_tru = Column(Float, default=0)       # Tổng điểm đã trừ (từ vi phạm)
    tong_diem_cong = Column(Float, default=0)      # Tổng điểm đã cộng (từ thành tích)
    diem_con_lai = Column(Float, default=80)       # Điểm còn lại
    
    ngay = Column(Date, nullable=True)
    ghi_chu = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    lop_hoc = relationship("LopHoc", foreign_keys=[lop_hoc_id])
    nam_hoc = relationship("NamHoc", foreign_keys=[nam_hoc_id])
    
    def __repr__(self):
        return f"<DiemDoiNgay(lop={self.lop_hoc_id}, tuan={self.tuan}, thu={self.thu}, diem={self.diem_con_lai})>"
    
    def cap_nhat_diem_toi_da(self, so_luong_vi_pham: int):
        """Cập nhật điểm tối đa khi số lượng vi phạm thay đổi"""
        self.so_luong_vi_pham = so_luong_vi_pham
        self.diem_toi_da = so_luong_vi_pham * 10
        self.diem_con_lai = max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)
    
    def cong_diem_tru(self, diem_tru: float):
        """Cộng thêm điểm trừ (vi phạm)"""
        self.tong_diem_tru += abs(diem_tru)
        self.diem_con_lai = max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)
    
    def cong_diem_cong(self, diem_cong: float):
        """Cộng thêm điểm cộng (thành tích)"""
        self.tong_diem_cong += diem_cong
        self.diem_con_lai = max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)
    
    def tru_diem_tru(self, diem_tru: float):
        """Trừ bớt điểm trừ (khi xóa vi phạm)"""
        self.tong_diem_tru -= abs(diem_tru)
        if self.tong_diem_tru < 0:
            self.tong_diem_tru = 0
        self.diem_con_lai = max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)
    
    def tru_diem_cong(self, diem_cong: float):
        """Trừ bớt điểm cộng (khi xóa thành tích)"""
        self.tong_diem_cong -= diem_cong
        if self.tong_diem_cong < 0:
            self.tong_diem_cong = 0
        self.diem_con_lai = max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)
    
    @property
    def diem_ngay(self):
        """Điểm ngày hiện tại (đã bao gồm cả trừ và cộng)"""
        return max(0, self.diem_toi_da + self.tong_diem_cong - self.tong_diem_tru)