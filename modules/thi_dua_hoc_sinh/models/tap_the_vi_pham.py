# modules/thi_dua_hoc_sinh/models/tap_the_vi_pham.py
from sqlalchemy import Column, Integer, Float, Date, Boolean, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.base import Base

class TapTheViPham(Base):
    __tablename__ = "tap_the_vi_pham"
    
    id = Column(Integer, primary_key=True, index=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    # ⭐ Thêm ondelete="CASCADE" vào dòng dưới
    loai_vi_pham_id = Column(Integer, ForeignKey("loai_vi_pham.id", ondelete="CASCADE"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)
    thu = Column(Integer, nullable=False)
    so_diem = Column(Float, default=0)
    ngay_xay_ra = Column(Date, nullable=False)
    tiet = Column(Integer, nullable=True)
    mo_ta = Column(Text, default="")
    nguoi_ghi_nhan = Column(String(100), default="")
    da_xac_nhan = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    lop_hoc = relationship("LopHoc", backref="tap_the_vi_phams")
    loai_vi_pham = relationship("LoaiViPham", backref="tap_the_vi_phams")