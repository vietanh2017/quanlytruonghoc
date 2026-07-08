# modules/thi_dua_hoc_sinh/repository/hoc_ky_repository.py
import json
from sqlalchemy.orm import Session
from typing import Optional
from modules.thi_dua_hoc_sinh.models.hoc_ky import ThiDuaHocKy
from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class HocKyRepository(BaseRepository[ThiDuaHocKy]):  # ⭐ Dùng ThiDuaHocKy
    def __init__(self, session: Session):
        super().__init__(session, ThiDuaHocKy)

    def get_all(self, nam_hoc_id: Optional[int] = None):
        query = self.session.query(ThiDuaHocKy)
        if nam_hoc_id:
            query = query.filter(ThiDuaHocKy.nam_hoc_id == nam_hoc_id)
        return query.order_by(ThiDuaHocKy.created_at.desc()).all()

    def create(self, ten_hoc_ky: str, nam_hoc_id: int, thang_list: list, is_active: bool = True):
        return super().create(
            ten_hoc_ky=ten_hoc_ky,
            nam_hoc_id=nam_hoc_id,
            thang_list=json.dumps(thang_list),
            so_thang=len(thang_list),
            is_active=is_active
        )

    def update(self, id: int, **data):
        if 'thang_list' in data and isinstance(data['thang_list'], list):
            data['thang_list'] = json.dumps(data['thang_list'])
            data['so_thang'] = len(data['thang_list'])
        return super().update(id, **data)

    def save_diem_chi_tiet(self, hoc_ky_id: int, thang_id: int, lop_hoc_id: int, diem_trung_binh_thang: float):
        self.session.query(ThiDuaHocKyDiemChiTiet).filter(
            ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky_id,
            ThiDuaHocKyDiemChiTiet.thang_id == thang_id,
            ThiDuaHocKyDiemChiTiet.lop_hoc_id == lop_hoc_id
        ).delete()
        
        chi_tiet = ThiDuaHocKyDiemChiTiet(
            hoc_ky_id=hoc_ky_id,
            thang_id=thang_id,
            lop_hoc_id=lop_hoc_id,
            diem_trung_binh_thang=diem_trung_binh_thang
        )
        self.session.add(chi_tiet)
        return chi_tiet

    def get_diem_chi_tiet(self, hoc_ky_id: int):
        return self.session.query(ThiDuaHocKyDiemChiTiet).filter(
            ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky_id
        ).all()