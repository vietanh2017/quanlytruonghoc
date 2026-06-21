from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base

class LopHoc(Base):
    __tablename__ = "lop_hoc"
    
    id = Column(Integer, primary_key=True)
    ma_lop = Column(String(20), unique=True, nullable=False)
    ten_lop = Column(String(100), nullable=False)
    khoi = Column(Integer)
    si_so = Column(Integer, default=0)
    giao_vien_cn_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=True)
    active = Column(Boolean, default=True)
    
    # Relationships - COMMENT TẠM THỜI
    giao_vien_cn = relationship("GiaoVien", foreign_keys=[giao_vien_cn_id])
    nam_hoc_obj = relationship("NamHoc", foreign_keys=[nam_hoc_id])