# modules/thi_dua_hoc_sinh/models/thang_thi_dua.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from core.db.base import Base

class ThangThiDua(Base):
    __tablename__ = "thang_thi_dua_modul"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    ten_thang = Column(String(100), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan_list = Column(Text, default="[]")
    so_tuan = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # ❌ KHÔNG có relationship ở đây