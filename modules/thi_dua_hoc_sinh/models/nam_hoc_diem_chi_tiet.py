# modules/thi_dua_hoc_sinh/models/nam_hoc_diem_chi_tiet.py
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db.base import Base

class NamHocDiemChiTiet(Base):
    __tablename__ = "nam_hoc_diem_chi_tiet"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    hoc_ky_list = Column(Text, default="[]")  # JSON: [1, 2, 3, 4]
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    diem_trung_binh_hoc_ky = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())