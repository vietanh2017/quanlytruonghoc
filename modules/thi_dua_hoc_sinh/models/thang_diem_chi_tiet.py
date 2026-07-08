# modules/thi_dua_hoc_sinh/models/thang_diem_chi_tiet.py
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.db.base import Base

class ThangDiemChiTiet(Base):
    __tablename__ = "thang_diem_chi_tiet"

    id = Column(Integer, primary_key=True, index=True)
    thang_id = Column(Integer, ForeignKey("thang_thi_dua.id", ondelete="CASCADE"), nullable=False)
    tuan = Column(Integer, nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    diem_trung_binh_tuan = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())