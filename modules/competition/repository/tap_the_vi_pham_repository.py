# modules/competition/repository/tap_the_vi_pham_repository.py

from sqlalchemy.orm import Session
from modules.competition.models.tap_the_vi_pham import TapTheViPham


class TapTheViPhamRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, id: int):
        return self.db.query(TapTheViPham).filter(TapTheViPham.id == id).first()

    def get_by_lop(self, lop_hoc_id: int, nam_hoc_id: int, tuan: int = None):
        """Lấy tất cả vi phạm tập thể của 1 lớp"""
        query = self.db.query(TapTheViPham).filter(
            TapTheViPham.lop_hoc_id == lop_hoc_id,
            TapTheViPham.nam_hoc_id == nam_hoc_id
        )
        if tuan:
            query = query.filter(TapTheViPham.tuan == tuan)
        return query.order_by(TapTheViPham.ngay_xay_ra.desc()).all()

    def get_by_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int = None):
        """Lấy tất cả vi phạm tập thể trong tuần"""
        query = self.db.query(TapTheViPham).filter(
            TapTheViPham.nam_hoc_id == nam_hoc_id,
            TapTheViPham.tuan == tuan
        )
        if lop_hoc_id:
            query = query.filter(TapTheViPham.lop_hoc_id == lop_hoc_id)
        return query.all()

    def create(self, **data):
        obj = TapTheViPham(**data)
        self.db.add(obj)
        return obj

    def delete(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            return True
        return False