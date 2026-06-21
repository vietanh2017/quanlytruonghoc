from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.base import Base

class ThoiKhoaBieu(Base):
    __tablename__ = "thoi_khoa_bieu"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=False)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    thu = Column(Integer, nullable=False)  # 2: Thứ 2, 3: Thứ 3, ..., 8: Chủ nhật
    tiet_bat_dau = Column(Integer, nullable=False)  # Tiết bắt đầu (1-5)
    so_tiet = Column(Integer, default=1)  # Số tiết liên tiếp
    phong_hoc = Column(String(50), default="")
    
    __table_args__ = (
        UniqueConstraint('lop_hoc_id', 'thu', 'tiet_bat_dau', 
                        name='unique_tkb_lop_thu_tiet'),
    )
    
    # Relationships
    nam_hoc = relationship("NamHoc")
    hoc_ky = relationship("HocKy")
    lop_hoc = relationship("LopHoc")
    mon_hoc = relationship("MonHoc")
    giao_vien = relationship("GiaoVien")
