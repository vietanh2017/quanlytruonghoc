# modules/thi_dua_giao_vien/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from core.db.base import Base

class TieuChi(Base):
    __tablename__ = "tieu_chi_thi_dua_gv"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_tieu_chi = Column(String(20), unique=True, nullable=False)
    ten_tieu_chi = Column(String(200), nullable=False)
    diem_toi_da = Column(Float, default=0)
    loai = Column(String(20), default="cong")  # "cong" hoặc "tru"
    mo_ta = Column(Text, default="")
    to_chuyen_mon_id = Column(Integer, ForeignKey("to_chuyen_mon.id"), nullable=True)
    thu_tu = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Relationships
    to_chuyen_mon = relationship("ToChuyenMon", foreign_keys=[to_chuyen_mon_id])

class DiemGiaoVien(Base):
    __tablename__ = "diem_thi_dua_gv"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    tieu_chi_id = Column(Integer, ForeignKey("tieu_chi_thi_dua_gv.id"), nullable=False)
    thang = Column(Integer, nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    diem = Column(Float, default=0)
    ghi_chu = Column(Text, default="")
    nguoi_cham_id = Column(Integer, nullable=True)
    ngay_cham = Column(DateTime, nullable=True)
    
    # Relationships
    giao_vien = relationship("GiaoVien", foreign_keys=[giao_vien_id])
    tieu_chi = relationship("TieuChi", foreign_keys=[tieu_chi_id])