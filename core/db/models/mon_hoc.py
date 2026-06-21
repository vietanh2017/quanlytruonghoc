# core/db/models/mon_hoc.py (thêm class MonHocKhoi vào cuối file)
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.base import Base


class MonHoc(Base):
    __tablename__ = "mon_hoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_mon = Column(String(20), nullable=False, unique=True)
    ten_mon = Column(String(100), nullable=False)
    co_phan_mon = Column(Boolean, default=False, nullable=False)
    to_id = Column(Integer, ForeignKey("to_chuyen_mon.id"), nullable=True)
    thu_tu = Column(Integer, default=0)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    to_chuyen_mon = relationship("ToChuyenMon", foreign_keys=[to_id])
    phan_mon_list = relationship("PhanMon", back_populates="mon_hoc",
                                 cascade="all, delete-orphan",
                                 order_by="PhanMon.thu_tu")
    khoi_list = relationship("MonHocKhoi", back_populates="mon_hoc",
                             cascade="all, delete-orphan",
                             order_by="MonHocKhoi.khoi")

    def __repr__(self):
        return f"<MonHoc {self.ma_mon} - {self.ten_mon}>"


class PhanMon(Base):
    __tablename__ = "phan_mon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    ma_phan_mon = Column(String(20), nullable=False)
    ten_phan_mon = Column(String(100), nullable=False)
    thu_tu = Column(Integer, default=0)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    mon_hoc = relationship("MonHoc", back_populates="phan_mon_list")
    
    __table_args__ = (
        UniqueConstraint('mon_hoc_id', 'ma_phan_mon', name='uq_mon_phan_mon'),
    )

    def __repr__(self):
        return f"<PhanMon {self.ma_phan_mon} - {self.ten_phan_mon}>"


class MonHocKhoi(Base):
    __tablename__ = "mon_hoc_khoi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    khoi = Column(Integer, nullable=False)
    so_tiet = Column(Integer, default=0)

    # Relationships
    mon_hoc = relationship("MonHoc", back_populates="khoi_list")

    __table_args__ = (
        UniqueConstraint('mon_hoc_id', 'khoi', name='unique_mon_khoi'),
    )

    def __repr__(self):
        return f"<MonHocKhoi mon_id={self.mon_hoc_id} khoi={self.khoi} tiet={self.so_tiet}>"