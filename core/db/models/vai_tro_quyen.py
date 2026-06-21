# core/db/models/vai_tro_quyen.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base
from core.db.models.quyen import QuyenModel
from datetime import datetime

class VaiTroQuyenModel(Base):
    __tablename__ = "vai_tro_quyen"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vai_tro = Column(String(50), nullable=False)  # ← ĐỔI TỪ 'role' THÀNH 'vai_tro'
    quyen_id = Column(Integer, ForeignKey("quyen.id"), nullable=False)
    
#    created_at = Column(DateTime, default=datetime.now)  # Thêm nếu cần
#    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    quyen = relationship("QuyenModel", foreign_keys=[quyen_id], overlaps="quyen")
    
    def __repr__(self):
        return f"<VaiTroQuyenModel vai_tro={self.vai_tro} quyen_id={self.quyen_id}>"