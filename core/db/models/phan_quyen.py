from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base

class Quyen(Base):
    __tablename__ = "quyen"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_quyen = Column(String(50), nullable=False, unique=True)
    ten_quyen = Column(String(100), nullable=False)
    mo_ta = Column(String(255), default="")
    module = Column(String(50))  # module nào: giao_vien, lop_hoc, cau_hinh...
    active = Column(Boolean, default=True)

class VaiTroQuyen(Base):
    __tablename__ = "vai_tro_quyen"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vai_tro = Column(String(50), nullable=False)  # admin, giao_vien, to_truong...
    quyen_id = Column(Integer, ForeignKey("quyen.id"), nullable=False)
    
    quyen = relationship("Quyen")

class NguoiDungQuyen(Base):
    __tablename__ = "nguoi_dung_quyen"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nguoi_dung_id = Column(Integer, ForeignKey("nguoi_dung.id"), nullable=False)
    quyen_id = Column(Integer, ForeignKey("quyen.id"), nullable=False)
    
    nguoi_dung = relationship("NguoiDung")
    quyen = relationship("Quyen")