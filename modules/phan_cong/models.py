# modules/phan_cong/models.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base

class PhanCong(Base):  # ✅ Tên model là PhanCong
    __tablename__ = "phan_cong"
    
    id = Column(Integer, primary_key=True, index=True)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=False)
    
    # Relationships
    giao_vien = relationship("GiaoVien")
    mon_hoc = relationship("MonHoc")
    lop_hoc = relationship("LopHoc")
    nam_hoc = relationship("NamHoc")
    hoc_ky = relationship("HocKy")