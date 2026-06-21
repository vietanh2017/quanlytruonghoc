# core/db/models/quyen.py

from sqlalchemy import Column, Integer, String, Text
from core.db.base import Base


class QuyenModel(Base):
    __tablename__ = "quyen"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_quyen = Column(String(50), nullable=False, unique=True)  # ← THÊM DÒNG NÀY
    module = Column(String(100), nullable=False)
    ten_quyen = Column(String(200), nullable=False)
    mo_ta = Column(Text, nullable=True)
    active = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<QuyenModel {self.module}.{self.ten_quyen}>"