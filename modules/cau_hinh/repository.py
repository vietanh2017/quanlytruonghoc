# modules/cau_hinh/repository.py
from core.db.models.nam_hoc import NamHoc
from core.db.models.to_chuyen_mon import ToChuyenMon
from core.db.models.mon_hoc import MonHoc, PhanMon, MonHocKhoi  # ⭐ Import MonHocKhoi từ mon_hoc
from core.db.models.tiet_hoc import TietHoc
from core.db.models.nguoi_dung import NguoiDung
from core.db.models.hoc_ky import HocKy
from shared.enums import Role
from sqlalchemy.orm import joinedload

class NamHocRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(NamHoc).order_by(NamHoc.id.desc()).all()
    
    def get_by_id(self, id):
        return self.session.query(NamHoc).filter(NamHoc.id == id).first()
    
    def get_by_ten(self, ten_nam_hoc):
        return self.session.query(NamHoc).filter(NamHoc.ten_nam_hoc == ten_nam_hoc).first()
    
    def create(self, **data):
        obj = NamHoc(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class ToChuyenMonRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(ToChuyenMon).order_by(ToChuyenMon.id.desc()).all()
    
    def get_by_id(self, id):
        return self.session.query(ToChuyenMon).filter(ToChuyenMon.id == id).first()
    
    def get_by_ma(self, ma_to):
        return self.session.query(ToChuyenMon).filter(ToChuyenMon.ma_to == ma_to).first()
    
    def create(self, **data):
        obj = ToChuyenMon(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class MonHocRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(MonHoc).options(
            joinedload(MonHoc.phan_mon_list),
            joinedload(MonHoc.khoi_list),
            joinedload(MonHoc.to_chuyen_mon)
        ).order_by(MonHoc.thu_tu).all()
    
    def get_by_id(self, id):
        return self.session.query(MonHoc).options(
            joinedload(MonHoc.phan_mon_list),
            joinedload(MonHoc.khoi_list),
            joinedload(MonHoc.to_chuyen_mon)
        ).filter(MonHoc.id == id).first()
    
    def get_by_ma(self, ma_mon):
        return self.session.query(MonHoc).filter(MonHoc.ma_mon == ma_mon).first()
    
    def create(self, **data):
        obj = MonHoc(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class HocKyRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(HocKy).options(joinedload(HocKy.nam_hoc)).all()
    
    def get_by_id(self, id):
        return self.session.query(HocKy).filter(HocKy.id == id).first()
    
    def create(self, **data):
        obj = HocKy(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class NguoiDungRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(NguoiDung).filter(
            NguoiDung.role != Role.HOC_SINH if hasattr(Role, 'HOC_SINH') else True
        ).order_by(NguoiDung.id.desc()).all()
    
    def get_by_id(self, id):
        return self.session.query(NguoiDung).filter(NguoiDung.id == id).first()
    
    def get_by_email(self, email):
        return self.session.query(NguoiDung).filter(NguoiDung.email == email).first()
    
    def create(self, ho_ten, email, mat_khau_hash, role, active=True):
        nd = NguoiDung(
            ho_ten=ho_ten,
            email=email,
            mat_khau_hash=mat_khau_hash,
            role=role,
            active=active
        )
        self.session.add(nd)
        self.session.flush()
        return nd
    
    def update(self, id, **data):
        nd = self.get_by_id(id)
        if nd:
            for key, value in data.items():
                if hasattr(nd, key):
                    setattr(nd, key, value)
        return nd
    
    def delete(self, id):
        nd = self.get_by_id(id)
        if nd:
            self.session.delete(nd)
            return True
        return False
    
    def update_mat_khau(self, id, mat_khau_hash):
        nd = self.get_by_id(id)
        if nd:
            nd.mat_khau_hash = mat_khau_hash
            return True
        return False


class TietHocRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(TietHoc).filter(TietHoc.active == 1).order_by(TietHoc.so_thu_tu).all()
    
    def get_by_id(self, id):
        return self.session.query(TietHoc).filter(TietHoc.id == id).first()
    
    def create(self, **data):
        obj = TietHoc(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class PhanMonRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(PhanMon).order_by(PhanMon.thu_tu).all()
    
    def get_by_id(self, id):
        return self.session.query(PhanMon).filter(PhanMon.id == id).first()
    
    def get_by_ma(self, ma_phan_mon, mon_hoc_id=None):
        query = self.session.query(PhanMon).filter(PhanMon.ma_phan_mon == ma_phan_mon)
        if mon_hoc_id:
            query = query.filter(PhanMon.mon_hoc_id == mon_hoc_id)
        return query.first()
    
    def get_by_mon_hoc(self, mon_hoc_id):
        return self.session.query(PhanMon).filter(
            PhanMon.mon_hoc_id == mon_hoc_id,
            PhanMon.active == True
        ).order_by(PhanMon.thu_tu).all()
    
    def create(self, **data):
        obj = PhanMon(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False


class MonHocKhoiRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self):
        return self.session.query(MonHocKhoi).all()
    
    def get_by_id(self, id):
        return self.session.query(MonHocKhoi).filter(MonHocKhoi.id == id).first()
    
    def get_by_mon_hoc(self, mon_hoc_id):
        return self.session.query(MonHocKhoi).filter(
            MonHocKhoi.mon_hoc_id == mon_hoc_id
        ).order_by(MonHocKhoi.khoi).all()
    
    def get_by_mon_hoc_khoi(self, mon_hoc_id, khoi):
        return self.session.query(MonHocKhoi).filter(
            MonHocKhoi.mon_hoc_id == mon_hoc_id,
            MonHocKhoi.khoi == khoi
        ).first()
    
    def create(self, **data):
        obj = MonHocKhoi(**data)
        self.session.add(obj)
        return obj
    
    def update(self, id, **data):
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
        return obj
    
    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False
    
    def delete_by_mon_hoc(self, mon_hoc_id):
        self.session.query(MonHocKhoi).filter(
            MonHocKhoi.mon_hoc_id == mon_hoc_id
        ).delete()
        return True