# core/db/models/diem_tuan.py
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db.base import Base

class DiemTuan(Base):
    __tablename__ = "diem_tuan"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)
    diem_doi = Column(Float, default=0)
    diem_hoc_tap = Column(Float, default=0)
    tong_diem = Column(Float, default=0)
    trung_binh = Column(Float, default=0)
    ghi_chu = Column(Text, default="")
    nguoi_nhap = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())