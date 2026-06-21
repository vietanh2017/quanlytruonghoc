# modules/competition/models/tap_the_vi_pham.py

from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Text, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db.base import Base


class TapTheViPham(Base):
    """
    Vi phạm tập thể của lớp (ảnh hưởng đến điểm Đội)
    """
    __tablename__ = "tap_the_vi_pham"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    loai_vi_pham_id = Column(Integer, ForeignKey("loai_vi_pham.id"), nullable=False)
    tuan = Column(Integer, nullable=False)  # Tuần 1-35
    thu = Column(Integer, nullable=False)   # 2: Thứ 2, 3: Thứ 3, ..., 6: Thứ 6
    
    so_diem = Column(Float, default=0)      # Số điểm trừ (luôn âm)
    ngay_xay_ra = Column(Date, nullable=False)
    tiet = Column(Integer, nullable=True)   # Tiết nào (1-8)
    
    mo_ta = Column(Text, nullable=True)
    nguoi_ghi_nhan = Column(String(200), nullable=True)
    da_xac_nhan = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    lop_hoc = relationship("LopHoc", foreign_keys=[lop_hoc_id])
    nam_hoc = relationship("NamHoc", foreign_keys=[nam_hoc_id])
    loai_vi_pham = relationship("LoaiViPham", foreign_keys=[loai_vi_pham_id])

    def __repr__(self):
        return f"<TapTheViPham(lop={self.lop_hoc_id}, tuan={self.tuan}, diem={self.so_diem})>"