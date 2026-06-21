# modules/competition/repository/loai_vi_pham_repository.py

from sqlalchemy.orm import Session
from modules.competition.models.loai_vi_pham import LoaiViPham


class LoaiViPhamRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_all(self, loai: str = None):
        """Lấy tất cả loại vi phạm, có thể lọc theo loại (vi_pham/thanh_tich)"""
        query = self.db.query(LoaiViPham).filter(LoaiViPham.is_active == True)
        if loai:
            query = query.filter(LoaiViPham.loai == loai)
        return query.order_by(LoaiViPham.thu_tu, LoaiViPham.id).all()

    def get_by_id(self, id: int):
        return self.db.query(LoaiViPham).filter(LoaiViPham.id == id).first()

    def get_by_ma(self, ma_loi: str):
        return self.db.query(LoaiViPham).filter(LoaiViPham.ma_loi == ma_loi).first()

    def get_by_nhom(self, nhom: str, loai: str = None):
        query = self.db.query(LoaiViPham).filter(
            LoaiViPham.nhom == nhom,
            LoaiViPham.is_active == True
        )
        if loai:
            query = query.filter(LoaiViPham.loai == loai)
        return query.all()

    def create(self, **data):
        obj = LoaiViPham(**data)
        self.db.add(obj)
        return obj

    def update(self, id: int, **data):
        obj = self.get_by_id(id)
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        return obj

    def delete(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            obj.is_active = False
            return True
        return False