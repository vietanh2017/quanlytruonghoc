# modules/thi_dua_hoc_sinh/models/diem_doi_ngay.py
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.db.base import Base

class DiemDoiNgay(Base):
    __tablename__ = "diem_doi_ngay"
    
    id = Column(Integer, primary_key=True, index=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)
    thu = Column(Integer, nullable=False)  # 2=Thứ 2, 3=Thứ 3,...
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    diem_thay_doi = Column(Float, default=0)
    so_luong_vi_pham = Column(Integer, default=0)
    ngay = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())