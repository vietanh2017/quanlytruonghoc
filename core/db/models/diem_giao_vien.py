from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from core.db.base import Base
from datetime import datetime


class DiemGiaoVien(Base):
    __tablename__ = "diem_giao_vien"

    id = Column(Integer, primary_key=True)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    tieu_chi_id = Column(Integer, ForeignKey("tieu_chi.id"), nullable=False)
    thang = Column(Integer, nullable=False)  # 1-12
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=True)
    
    diem = Column(Float, default=0)
    ghi_chu = Column(Text, nullable=True)
    
    nguoi_cham_id = Column(Integer, ForeignKey("nguoi_dung.id"), nullable=True)  # ← nullable=True
    ngay_cham = Column(DateTime, default=datetime.now)

    # Relationships
    giao_vien = relationship("GiaoVien", foreign_keys=[giao_vien_id])
    tieu_chi = relationship("TieuChi", back_populates="diem_gv_list")
    nguoi_cham = relationship("NguoiDung", foreign_keys=[nguoi_cham_id])  # ← Sửa lại
    nam_hoc = relationship("NamHoc")
    hoc_ky = relationship("HocKy")