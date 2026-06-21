# core\db\models\to_chuyen_mon.py
# TODO: implement
# D:\QUANLYTRUONGHOC\core\db\models\to_chuyen_mon.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from core.db.base import Base

class ToChuyenMon(Base):
    __tablename__ = "to_chuyen_mon"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_to = Column(String(20), nullable=False, unique=True)
    ten_to = Column(String(100), nullable=False)
    mo_ta = Column(String(255), default="")
    active = Column(Boolean, default=True)
    
    giao_vien_list = relationship("GiaoVien", back_populates="to_chuyen_mon")
    
    def __repr__(self):
        return f"<ToChuyenMon {self.ten_to}>"