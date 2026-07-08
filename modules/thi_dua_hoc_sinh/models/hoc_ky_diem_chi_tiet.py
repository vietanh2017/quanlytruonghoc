# modules/thi_dua_hoc_sinh/models/hoc_ky_diem_chi_tiet.py
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.db.base import Base

class ThiDuaHocKyDiemChiTiet(Base):
    __tablename__ = "hoc_ky_diem_chi_tiet"  # Giữ nguyên tên bảng
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky_thi_dua.id", ondelete="CASCADE"), nullable=False)  # ⭐ Đổi tên tham chiếu
    thang_id = Column(Integer, ForeignKey("thang_thi_dua.id"), nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    diem_trung_binh_thang = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())