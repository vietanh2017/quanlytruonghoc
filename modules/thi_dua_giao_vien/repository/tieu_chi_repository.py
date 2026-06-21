from core.db.models.tieu_chi import TieuChi
from sqlalchemy.orm import joinedload


class TieuChiRepository:
    def __init__(self, session):
        self.db = session

    def get_all(self, to_id=None, active_only=True):
        q = self.db.query(TieuChi)
        if to_id:
            q = q.filter(TieuChi.to_chuyen_mon_id == to_id)
        if active_only:
            q = q.filter(TieuChi.active == True)
        return q.order_by(TieuChi.loai, TieuChi.ma_tieu_chi).all()

    def get_by_id(self, tc_id: int):
        return self.db.query(TieuChi).filter(TieuChi.id == tc_id).first()

    def get_by_ma(self, ma: str):
        return self.db.query(TieuChi).filter(TieuChi.ma_tieu_chi == ma).first()

    def create(self, **data):
        obj = TieuChi(**data)
        self.db.add(obj)
        return obj

    def update(self, tc_id: int, **data):
        obj = self.get_by_id(tc_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        return obj

    def delete(self, tc_id: int):
        obj = self.get_by_id(tc_id)
        if not obj:
            return False
        self.db.delete(obj)
        return True

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()