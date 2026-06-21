from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.db.base import Base


class TieuChi(Base):
    __tablename__ = "tieu_chi"

    id = Column(Integer, primary_key=True)
    ma_tieu_chi = Column(String(20), unique=True, nullable=False)
    ten_tieu_chi = Column(String(200), nullable=False)
    diem_toi_da = Column(Float, default=0)  # Điểm cộng/trừ
    mo_ta = Column(Text, nullable=True)
    loai = Column(String(10), default="cong")  # "cong" hoặc "tru"
    to_chuyen_mon_id = Column(Integer, ForeignKey("to_chuyen_mon.id"), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(String(20), default="2024-01-01")

    to_chuyen_mon = relationship("ToChuyenMon", foreign_keys=[to_chuyen_mon_id])
    diem_gv_list = relationship("DiemGiaoVien", back_populates="tieu_chi")