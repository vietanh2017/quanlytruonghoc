# modules\timetable\repository.py
# TODO: implement
from sqlalchemy.orm import joinedload
from core.db.models.thoi_khoa_bieu import ThoiKhoaBieu
from core.db.models.tiet_hoc import TietHoc

class TimetableRepository:
    def __init__(self, session):
        self.session = session
    
    def get_by_lop(self, lop_hoc_id, nam_hoc_id, hoc_ky_id):
        return self.session.query(ThoiKhoaBieu).options(
            joinedload(ThoiKhoaBieu.mon_hoc),
            joinedload(ThoiKhoaBieu.giao_vien)
        ).filter(
            ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
            ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
            ThoiKhoaBieu.hoc_ky_id == hoc_ky_id
        ).all()
    
    def create(self, **data):
        obj = ThoiKhoaBieu(**data)
        self.session.add(obj)
        return obj
    
    def delete_by_lop(self, lop_hoc_id, nam_hoc_id, hoc_ky_id):
        self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
            ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
            ThoiKhoaBieu.hoc_ky_id == hoc_ky_id
        ).delete()
    
    def get_tiet_hoc_list(self):
        return self.session.query(TietHoc).filter(TietHoc.active == 1).order_by(TietHoc.so_thu_tu).all()