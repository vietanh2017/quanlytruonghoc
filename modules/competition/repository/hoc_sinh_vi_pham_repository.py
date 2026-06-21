# modules/competition/repository/hoc_sinh_vi_pham_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from modules.competition.models.hoc_sinh_vi_pham import HocSinhViPham


class HocSinhViPhamRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, id: int):
        return self.db.query(HocSinhViPham).filter(HocSinhViPham.id == id).first()

    def get_by_hoc_sinh(self, hoc_sinh_id: int, nam_hoc_id: int = None, tuan: int = None):
        """Lấy tất cả vi phạm của 1 học sinh"""
        query = self.db.query(HocSinhViPham).filter(HocSinhViPham.hoc_sinh_id == hoc_sinh_id)
        if nam_hoc_id:
            query = query.filter(HocSinhViPham.nam_hoc_id == nam_hoc_id)
        if tuan:
            query = query.filter(HocSinhViPham.tuan == tuan)
        return query.order_by(HocSinhViPham.ngay_xay_ra.desc()).all()

    def get_by_lop(self, lop_hoc_id: int, nam_hoc_id: int, tuan: int = None):
        """Lấy tất cả vi phạm của học sinh trong lớp"""
        from core.db.models.hoc_sinh import HocSinh
        
        query = self.db.query(HocSinhViPham).join(
            HocSinh, HocSinhViPham.hoc_sinh_id == HocSinh.id
        ).filter(
            HocSinh.lop_hoc_id == lop_hoc_id,
            HocSinhViPham.nam_hoc_id == nam_hoc_id
        )
        if tuan:
            query = query.filter(HocSinhViPham.tuan == tuan)
        return query.all()

    def get_tong_diem_ca_nhan(self, hoc_sinh_id: int, nam_hoc_id: int, tuan: int = None):
        """Tính tổng điểm thi đua cá nhân (có thể âm)"""
        query = self.db.query(func.sum(HocSinhViPham.so_diem)).filter(
            HocSinhViPham.hoc_sinh_id == hoc_sinh_id,
            HocSinhViPham.nam_hoc_id == nam_hoc_id
        )
        if tuan:
            query = query.filter(HocSinhViPham.tuan == tuan)
        return query.scalar() or 0

    def create(self, **data):
        obj = HocSinhViPham(**data)
        self.db.add(obj)
        return obj

    def delete(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            return True
        return False