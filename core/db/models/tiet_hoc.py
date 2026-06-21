# core/db/models/tiet_hoc.py
from sqlalchemy import Column, Integer, String, Boolean
from core.db.base import Base

class TietHoc(Base):
    __tablename__ = "tiet_hoc"
    __table_args__ = {'extend_existing': True}  # Thêm dòng này
    id = Column(Integer, primary_key=True, autoincrement=True)
    so_thu_tu = Column(Integer, nullable=False)  # Tiết 1, 2, 3,...
    ten_tiet = Column(String(50), nullable=False)
    thoi_gian_bat_dau = Column(String(20), default="")
    thoi_gian_ket_thuc = Column(String(20), default="")
    active = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<TietHoc {self.ten_tiet}>"