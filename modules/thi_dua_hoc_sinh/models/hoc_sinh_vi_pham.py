# modules/thi_dua_hoc_sinh/models/hoc_sinh_vi_pham.py
from sqlalchemy import Column, Integer, Float, Date, Boolean, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.base import Base

class HocSinhViPham(Base):
    __tablename__ = "hoc_sinh_vi_pham"
    
    id = Column(Integer, primary_key=True, index=True)
    hoc_sinh_id = Column(Integer, ForeignKey("hoc_sinh.id"), nullable=False)
    # ⭐ Thêm ondelete="CASCADE" vào dòng dưới
    loai_vi_pham_id = Column(Integer, ForeignKey("loai_vi_pham.id", ondelete="CASCADE"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)
    so_diem = Column(Float, default=0)
    ngay_xay_ra = Column(Date, nullable=False)
    tiet = Column(Integer, nullable=True)
    mo_ta = Column(Text, default="")
    nguoi_ghi_nhan = Column(String(100), default="")
    da_anh_huong_lop = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    hoc_sinh = relationship("HocSinh", backref="vi_phams")
    loai_vi_pham = relationship("LoaiViPham", backref="hoc_sinh_vi_phams")