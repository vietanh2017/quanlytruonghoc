# core/db/models/thang_thi_dua.py
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # ⭐ Thêm import relationship
from core.db.base import Base

class ThangThiDua(Base):
    __tablename__ = "thang_thi_dua"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_thang = Column(String(100), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan_list = Column(Text, nullable=False)  # JSON: [1,2,3,4]
    so_tuan = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ⭐ Thêm relationship
    nam_hoc = relationship("NamHoc", foreign_keys=[nam_hoc_id])