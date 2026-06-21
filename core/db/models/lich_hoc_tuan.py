from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base

class LichHocTuan(Base):
    __tablename__ = "lich_hoc_tuan"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=False)
    thu = Column(Integer, nullable=False)  # 2: Thứ 2, 3: Thứ 3, ..., 8: Chủ nhật
    co_sang = Column(Boolean, default=True)
    co_chieu = Column(Boolean, default=False)
    
    # Relationships
    nam_hoc = relationship("NamHoc")
    hoc_ky = relationship("HocKy")
    
    def __repr__(self):
        return f"<LichHocTuan thu={self.thu} sang={self.co_sang} chieu={self.co_chieu}>"