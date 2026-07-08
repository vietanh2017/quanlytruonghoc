# modules/thi_dua_hoc_sinh/repository/thang_thi_dua_repository.py
import json
from sqlalchemy.orm import Session
from typing import Optional, List
from modules.thi_dua_hoc_sinh.models.thang_thi_dua import ThangThiDua
from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class ThangThiDuaRepository(BaseRepository[ThangThiDua]):
    def __init__(self, session: Session):
        super().__init__(session, ThangThiDua)

    def get_all(self, nam_hoc_id: Optional[int] = None):
        query = self.session.query(ThangThiDua)
        if nam_hoc_id:
            query = query.filter(ThangThiDua.nam_hoc_id == nam_hoc_id)
        return query.order_by(ThangThiDua.created_at.desc()).all()

    def create(self, ten_thang: str, nam_hoc_id: int, tuan_list: list, is_active: bool = True):
        # ⭐ Lọc các tuần hợp lệ (1-52) và loại bỏ trùng lặp
        tuan_list_valid = sorted(set([t for t in tuan_list if isinstance(t, int) and 1 <= t <= 52]))
        return super().create(
            ten_thang=ten_thang,
            nam_hoc_id=nam_hoc_id,
            tuan_list=json.dumps(tuan_list_valid),
            so_tuan=len(tuan_list_valid),  # ⭐ Đếm số tuần thực tế
            is_active=is_active
        )

    def update(self, id: int, **data):
        if 'tuan_list' in data and isinstance(data['tuan_list'], list):
            # ⭐ Lọc các tuần hợp lệ và loại bỏ trùng lặp
            tuan_list_valid = sorted(set([t for t in data['tuan_list'] if isinstance(t, int) and 1 <= t <= 52]))
            data['tuan_list'] = json.dumps(tuan_list_valid)
            data['so_tuan'] = len(tuan_list_valid)  # ⭐ Đếm số tuần thực tế
        return super().update(id, **data)

    # ⭐ Lưu điểm chi tiết của từng tuần
    def save_diem_chi_tiet(self, thang_id: int, tuan: int, lop_hoc_id: int, diem_trung_binh_tuan: float):
        # Xóa cũ nếu có
        self.session.query(ThangDiemChiTiet).filter(
            ThangDiemChiTiet.thang_id == thang_id,
            ThangDiemChiTiet.tuan == tuan,
            ThangDiemChiTiet.lop_hoc_id == lop_hoc_id
        ).delete()

        # Tạo mới
        chi_tiet = ThangDiemChiTiet(
            thang_id=thang_id,
            tuan=tuan,
            lop_hoc_id=lop_hoc_id,
            diem_trung_binh_tuan=diem_trung_binh_tuan
        )
        self.session.add(chi_tiet)
        return chi_tiet

    # ⭐ Lấy tất cả điểm chi tiết của một tháng
    def get_diem_chi_tiet(self, thang_id: int):
        return self.session.query(ThangDiemChiTiet).filter(
            ThangDiemChiTiet.thang_id == thang_id
        ).all()