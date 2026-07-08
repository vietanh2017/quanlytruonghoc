# modules/thi_dua_hoc_sinh/models/thi_dua_cau_hinh.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.db.base import Base

class ThiDuaCauHinh(Base):
    __tablename__ = "thi_dua_cau_hinh"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())