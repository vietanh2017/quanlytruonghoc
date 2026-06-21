from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from core.db.base import Base

class HocSinh(Base):
    __tablename__ = "hoc_sinh"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_hoc_sinh = Column(String(20), unique=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date, nullable=True)
    gioi_tinh = Column(Boolean, default=True)  # True = Nam, False = Nữ
    so_dien_thoai = Column(String(20), nullable=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    lop_hoc = relationship("LopHoc", foreign_keys=[lop_hoc_id], backref="hoc_sinhs")