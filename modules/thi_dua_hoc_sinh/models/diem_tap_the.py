# modules/thi_dua_hoc_sinh/models/diem_tap_the.py
from sqlalchemy import Column, Integer, Float, Boolean, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db.base import Base

class DiemTapThe(Base):
    __tablename__ = "diem_tap_the"
    
    id = Column(Integer, primary_key=True, index=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    diem_hoc_tap = Column(Float, default=0)
    diem_doi = Column(Float, default=0)
    ghi_chu = Column(String(255), default="")
    nguoi_nhap = Column(String(100), default="")
    da_khoa = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    lop_hoc = relationship("LopHoc", backref="diem_tap_the")
    __table_args__ = (
        UniqueConstraint('nam_hoc_id', 'tuan', 'lop_hoc_id', name='uq_diem_tap_the_nam_tuan_lop'),
    )