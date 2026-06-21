# modules/lop_hoc/repository.py
"""
LopHocRepository: truy xuất DB cho module Lớp học.

Thay đổi so với bản desktop:
- Bỏ tự tạo session, nhận session từ bên ngoài
- Bỏ commit/rollback/close — do service quản lý
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload

from core.db.models.lop_hoc import LopHoc
from core.db.models.giao_vien import GiaoVien
from core.db.models.nam_hoc import NamHoc


class LopHocRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_all(self) -> list[LopHoc]:
        return (
            self.db.query(LopHoc)
            .options(
                joinedload(LopHoc.giao_vien_cn).joinedload(GiaoVien.nguoi_dung)
            )
            .order_by(LopHoc.khoi, LopHoc.ten_lop)
            .all()
        )

    def get_by_id(self, lop_id: int) -> Optional[LopHoc]:
        return (
            self.db.query(LopHoc)
            .options(
                joinedload(LopHoc.giao_vien_cn).joinedload(GiaoVien.nguoi_dung)
            )
            .filter(LopHoc.id == lop_id)
            .first()
        )

    def get_by_ma(self, ma_lop: str) -> Optional[LopHoc]:
        return self.db.query(LopHoc).filter(LopHoc.ma_lop == ma_lop).first()

    def get_by_nam_hoc(self, nam_hoc_id: int) -> list[LopHoc]:
        return (
            self.db.query(LopHoc)
            .filter(LopHoc.nam_hoc_id == nam_hoc_id, LopHoc.active == True)
            .order_by(LopHoc.ten_lop)
            .all()
        )

    def create(self, **data) -> LopHoc:
        obj = LopHoc(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, lop_id: int, **data) -> Optional[LopHoc]:
        obj = self.get_by_id(lop_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.flush()
        return obj

    def delete(self, lop_id: int) -> bool:
        obj = self.get_by_id(lop_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.flush()
        return True

    # ── Năm học ───────────────────────────────────────────────

    def get_all_nam_hoc(self) -> list[NamHoc]:
        return (
            self.db.query(NamHoc)
            .filter(NamHoc.active == True)
            .order_by(NamHoc.ten_nam_hoc.desc())
            .all()
        )
