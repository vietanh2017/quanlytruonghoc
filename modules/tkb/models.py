# modules/tkb/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.base import Base


class TKBCauHinhNgay(Base):
    __tablename__ = "tkb_cau_hinh_ngay"
    __table_args__ = (
        UniqueConstraint('nam_hoc_id', 'thu', name='uq_tkb_ngay'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    thu = Column(Integer, nullable=False)
    co_buoi_sang = Column(Boolean, default=True)
    co_buoi_chieu = Column(Boolean, default=False)


class TKBCauHinhTiet(Base):
    __tablename__ = "tkb_cau_hinh_tiet"
    __table_args__ = (
        UniqueConstraint('buoi', 'tiet_so', name='uq_tkb_tiet'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    buoi = Column(String(10), nullable=False)
    tiet_so = Column(Integer, nullable=False)
    gio_bat_dau = Column(String(5))
    gio_ket_thuc = Column(String(5))
    is_active = Column(Boolean, default=True)


class TKBCauHinhMon(Base):
    __tablename__ = "tkb_cau_hinh_mon"
    __table_args__ = (
        UniqueConstraint('mon_hoc_id', 'nam_hoc_id', name='uq_tkb_cauhinh_mon'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    chi_buoi_sang = Column(Boolean, default=False)
    chi_buoi_chieu = Column(Boolean, default=False)
    khong_lien_tiet = Column(Boolean, default=False)
    so_tiet_toi_da_ngay = Column(Integer, default=0)
    cho_phep_tiet_doi = Column(Boolean, default=False)  # ✅ thêm dòng này

    mon_hoc = relationship("MonHoc", foreign_keys=[mon_hoc_id])


class ThoiKhoaBieu(Base):
    __tablename__ = "thoi_khoa_bieu"
    __table_args__ = (
        UniqueConstraint('nam_hoc_id', 'hoc_ky_id', 'lop_hoc_id',
                         'thu', 'buoi', 'tiet', name='uq_tkb_lop'),
        UniqueConstraint('nam_hoc_id', 'hoc_ky_id', 'giao_vien_id',
                         'thu', 'buoi', 'tiet', name='uq_tkb_gv'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    hoc_ky_id = Column(Integer, ForeignKey("hoc_ky.id"), nullable=True)
    lop_hoc_id = Column(Integer, ForeignKey("lop_hoc.id"), nullable=False)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("mon_hoc.id"), nullable=False)
    phan_mon_id = Column(Integer, ForeignKey("phan_mon.id"), nullable=True)
    thu = Column(Integer, nullable=False)
    buoi = Column(String(10), nullable=False)
    tiet = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    lop_hoc = relationship("LopHoc", foreign_keys=[lop_hoc_id])
    giao_vien = relationship("GiaoVien", foreign_keys=[giao_vien_id])
    mon_hoc = relationship("MonHoc", foreign_keys=[mon_hoc_id])
    phan_mon = relationship("PhanMon", foreign_keys=[phan_mon_id])
    
class TKBRangBuocGV(Base):
    __tablename__ = "tkb_rang_buoc_gv"
    __table_args__ = (
        UniqueConstraint('giao_vien_id', 'nam_hoc_id', name='uq_tkb_rb_gv'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    giao_vien_id = Column(Integer, ForeignKey("giao_vien.id"), nullable=False)
    nam_hoc_id = Column(Integer, ForeignKey("nam_hoc.id"), nullable=False)
    chi_buoi_sang = Column(Boolean, default=False)
    chi_buoi_chieu = Column(Boolean, default=False)
    so_tiet_toi_da_ngay = Column(Integer, default=0)
    so_tiet_toi_thieu_ngay = Column(Integer, default=0)
    gom_tiet = Column(Boolean, default=False)
    so_ngay_nghi = Column(Integer, default=0)
    ngay_nghi_list = Column(String(50), default="")  # "2,4" = nghỉ thứ 2, thứ 4

    giao_vien = relationship("GiaoVien", foreign_keys=[giao_vien_id])