# modules/competition/models/hoc_sinh_vi_pham.py

from sqlalchemy import Column, Integer, Float, ForeignKey, Date, Text, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db.base import Base


class HocSinhViPham(Base):
    """
    Chi tiết vi phạm / thành tích của từng học sinh
    """
    __tablename__ = "hoc_sinh_vi_pham"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hoc_sinh_id = Column(Integer, ForeignKey("hoc_sinh.id"), nullable=False)
    loai_vi_pham_id = Column(Integer, ForeignKey("loai_vi_pham.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    tuan = Column(Integer, nullable=False)  # Tuần xảy ra (1-35)
    
    so_diem = Column(Float, default=0)  # Số điểm cộng/trừ (copy từ LoaiViPham để lưu lịch sử)
    ngay_xay_ra = Column(Date, nullable=False)
    tiet = Column(Integer, nullable=True)  # Tiết nào (1-8)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=True)  # Môn học liên quan
    
    mo_ta = Column(Text, nullable=True)  # Mô tả chi tiết sự việc
    nguoi_ghi_nhan = Column(String(200), nullable=True)  # GVCN, Sao đỏ, Tổng phụ trách
    da_xac_nhan = Column(Boolean, default=False)  # Cần xác nhận?
    da_anh_huong_lop = Column(Boolean, default=True)  # Đã trừ vào điểm Đội của lớp chưa?
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    hoc_sinh = relationship("HocSinh", foreign_keys=[hoc_sinh_id])
    loai_vi_pham = relationship("LoaiViPham", foreign_keys=[loai_vi_pham_id])
    nam_hoc = relationship("NamHoc", foreign_keys=[nam_hoc_id])
    mon_hoc = relationship("MonHoc", foreign_keys=[mon_hoc_id])

    def __repr__(self):
        return f"<HocSinhViPham(hs={self.hoc_sinh_id}, diem={self.so_diem})>"