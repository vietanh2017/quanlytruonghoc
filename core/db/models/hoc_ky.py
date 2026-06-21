from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base

class HocKy(Base):
    __tablename__ = "hoc_ky"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    so_thu_tu = Column(Integer, nullable=False)
    ten_hoc_ky = Column(String(50), nullable=False)
    ngay_bat_dau = Column(Date, nullable=True)
    ngay_ket_thuc = Column(Date, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # Chỉ giữ relationship đơn giản
    nam_hoc = relationship("NamHoc")

    def __repr__(self):
        return f"<HocKy {self.ten_hoc_ky}>"