from sqlalchemy.orm import joinedload
from core.db.models.phan_cong import PhanCongGiangDay
from core.db.models.nam_hoc import NamHoc
from core.db.models.hoc_ky import HocKy
from core.db.models.giao_vien import GiaoVien
from core.db.models.mon_hoc import MonHoc
from core.db.models.lop_hoc import LopHoc

class PhanCongRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(PhanCongGiangDay).options(
            joinedload(PhanCongGiangDay.nam_hoc),
            joinedload(PhanCongGiangDay.hoc_ky),
            joinedload(PhanCongGiangDay.giao_vien),
            joinedload(PhanCongGiangDay.mon_hoc),
            joinedload(PhanCongGiangDay.lop_hoc)
        ).all()
    
    def get_by_id(self, id):
        return self.session.query(PhanCongGiangDay).filter(PhanCongGiangDay.id == id).first()
    
    def create(self, **data):
        obj = PhanCongGiangDay(**data)
        self.session.add(obj)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False
    
    def get_by_nam_hoc_hoc_ky(self, nam_hoc_id, hoc_ky_id):
        return self.session.query(PhanCongGiangDay).options(
            joinedload(PhanCongGiangDay.giao_vien),
            joinedload(PhanCongGiangDay.mon_hoc),
            joinedload(PhanCongGiangDay.lop_hoc)
        ).filter(
            PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
            PhanCongGiangDay.hoc_ky_id == hoc_ky_id
        ).all()