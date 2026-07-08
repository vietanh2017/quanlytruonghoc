# modules/thi_dua_hoc_sinh/models/hoc_ky.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from core.db.base import Base

# ⭐ Đổi tên class để phân biệt với HocKy của hệ thống
class ThiDuaHocKy(Base):
    __tablename__ = "hoc_ky_thi_dua"  # ⭐ Đổi tên bảng để không xung đột
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    ten_hoc_ky = Column(String(100), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    thang_list = Column(Text, default="[]")
    so_thang = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())