# core/db/models/phan_cong.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.base import Base

class PhanCongGiangDay(Base):
    __tablename__ = "phan_cong_giang_day"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=False)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    phan_mon_id = Column(Integer, ForeignKey("phan_mon.id"), nullable=True)  # ✅ Thêm
    
    __table_args__ = (
        UniqueConstraint('nam_hoc_id', 'hoc_ky_id', 'giao_vien_id', 
                        'mon_hoc_id', 'lop_hoc_id', 
                        name='unique_phan_cong'),
    )
    
    nam_hoc = relationship("NamHoc")
    hoc_ky = relationship("HocKy")
    giao_vien = relationship("GiaoVien", back_populates="phan_cong_list")
    mon_hoc = relationship("MonHoc")
    lop_hoc = relationship("LopHoc")
    phan_mon = relationship("PhanMon", foreign_keys=[phan_mon_id])  # ✅ Thêm