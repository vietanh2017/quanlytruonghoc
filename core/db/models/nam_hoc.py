from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from core.db.base import Base

class NamHoc(Base):
    __tablename__ = "nam_hoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_nam_hoc = Column(String(20), nullable=False, unique=True)
    active = Column(Boolean, default=False, nullable=False)

    # Comment hoặc xóa dòng này
    # hoc_ky_list = relationship("HocKy", back_populates="nam_hoc")

    def __repr__(self):
        return f"<NamHoc {self.ten_nam_hoc}>"