# modules/thi_dua_hoc_sinh/models/loai_vi_pham.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from core.db.base import Base

class LoaiViPham(Base):
    __tablename__ = "loai_vi_pham"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_loi = Column(String(20), unique=True, nullable=False, index=True)
    ten_loi = Column(String(100), nullable=False)
    loai = Column(String(20), nullable=False)
    doi_tuong = Column(String(20), default="tap_the")
    loai_diem = Column(String(10), default="tru")
    nhom = Column(String(50), default="")
    so_diem = Column(Float, default=0)
    mo_ta = Column(Text, default="")
    thu_tu = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    # ⭐ Sửa: KHÔNG truyền giá trị khi insert, để database tự động set
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())