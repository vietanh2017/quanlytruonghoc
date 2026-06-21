# core\db\models\nguoi_dung.py
# TODO: implement
# D:\QUANLYTRUONGHOC\core\db\models\nguoi_dung.py
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from core.db.base import Base
from shared.enums import Role


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten        = Column(String(100), nullable=False)
    email         = Column(String(100), nullable=False, unique=True)
    mat_khau_hash = Column(String(255), nullable=False)
    role          = Column(SAEnum(Role), nullable=False, default=Role.GIAO_VIEN)
    active        = Column(Boolean, default=True, nullable=False)

    giao_vien = relationship("GiaoVien", back_populates="nguoi_dung",
                             uselist=False)

    def __repr__(self):
        return f"<NguoiDung {self.email} ({self.role})>"