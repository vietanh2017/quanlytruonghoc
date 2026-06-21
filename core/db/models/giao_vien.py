# core\db\models\giao_vien.py
# TODO: implement
# D:\QUANLYTRUONGHOC\core\db\models\giao_vien.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base


class GiaoVien(Base):
    __tablename__ = "giao_vien"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    nguoi_dung_id = Column(Integer, ForeignKey("nguoi_dung.id"),
                           nullable=False, unique=True)
    ma_giao_vien  = Column(String(20), nullable=False, unique=True)
    mon_day       = Column(String(100), default="")
    to_id         = Column(Integer, ForeignKey("to_chuyen_mon.id"), nullable=True)
    so_dien_thoai = Column(String(15), default="")
    active        = Column(Boolean, default=True, nullable=False)

    nguoi_dung    = relationship("NguoiDung", back_populates="giao_vien")
    to_chuyen_mon = relationship("ToChuyenMon", back_populates="giao_vien_list",foreign_keys=[to_id])
  
    phan_cong_list = relationship("PhanCongGiangDay", back_populates="giao_vien")
   # lop_chu_nhiem = relationship("LopHoc", back_populates="giao_vien_cn")
    def __repr__(self):
        return f"<GiaoVien {self.ma_giao_vien}>"