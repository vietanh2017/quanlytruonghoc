# modules/giao_vien/repository.py
"""
GiaoVienRepository: truy xuất DB cho module Giáo viên.
Không có business logic — chỉ query/insert/update/delete.

Thay đổi so với bản desktop:
- Bỏ hàm create() và get_by_to() trùng lặp
- Thống nhất dùng self.s cho tất cả query
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from core.db.models import NguoiDung, GiaoVien, ToChuyenMon
from shared.enums import Role


class GiaoVienRepository:
    def __init__(self, session: Session):
        self.s = session

    # ── Giáo viên ─────────────────────────────────────────────

    def get_all(self, include_inactive: bool = False) -> list[GiaoVien]:
        q = (
            self.s.query(GiaoVien)
            .options(
                joinedload(GiaoVien.nguoi_dung),
                joinedload(GiaoVien.to_chuyen_mon),
            )
            .join(GiaoVien.nguoi_dung)
        )
        if not include_inactive:
            q = q.filter(GiaoVien.active == True)
        return q.order_by(
            func.length(GiaoVien.ma_giao_vien), GiaoVien.ma_giao_vien
        ).all()

    def get_by_id(self, gv_id: int) -> Optional[GiaoVien]:
        return (
            self.s.query(GiaoVien)
            .options(
                joinedload(GiaoVien.nguoi_dung),
                joinedload(GiaoVien.to_chuyen_mon),
            )
            .filter_by(id=gv_id)
            .first()
        )

    def get_by_ma(self, ma_gv: str) -> Optional[GiaoVien]:
        return (
            self.s.query(GiaoVien)
            .filter(GiaoVien.ma_giao_vien == ma_gv)
            .first()
        )

    def get_by_to(self, to_id: int) -> list[GiaoVien]:
        return (
            self.s.query(GiaoVien)
            .options(joinedload(GiaoVien.nguoi_dung))
            .filter(GiaoVien.to_id == to_id, GiaoVien.active == True)
            .join(GiaoVien.nguoi_dung)
            .order_by(NguoiDung.ho_ten)
            .all()
        )

    def create(
        self,
        nguoi_dung_id: int,
        ma_gv: str,
        mon_day: str = "",
        to_id: Optional[int] = None,
        so_dien_thoai: str = "",
        kiem_nhiem: str = "",  # ⭐ THÊM
        active: bool = True,
    ) -> GiaoVien:
        gv = GiaoVien(
            nguoi_dung_id=nguoi_dung_id,
            ma_giao_vien=ma_gv,
            mon_day=mon_day,
            to_id=to_id,
            so_dien_thoai=so_dien_thoai,
            
            active=active,
        )
        self.s.add(gv)
        self.s.flush()
        return gv

    def update(self, gv_id: int, **data) -> Optional[GiaoVien]:
        gv = self.get_by_id(gv_id)
        if not gv:
            return None

        # ⭐ THÊM 'kiem_nhiem' VÀO DANH SÁCH
        gv_fields = {"ma_giao_vien", "mon_day", "to_id", "so_dien_thoai", "active", "kiem_nhiem"}
        for key, value in data.items():
            if key in gv_fields and hasattr(gv, key):
                setattr(gv, key, value)

        if gv.nguoi_dung:
            nd_fields = {"ho_ten", "email", "mat_khau_hash", "active", "role"}
            for key, value in data.items():
                if key in nd_fields and hasattr(gv.nguoi_dung, key):
                    setattr(gv.nguoi_dung, key, value)

        self.s.flush()
        return gv

    def toggle_active(self, gv_id: int) -> Optional[GiaoVien]:
        gv = self.s.get(GiaoVien, gv_id)
        if gv:
            gv.active = not gv.active
            self.s.flush()
        return gv

    def delete(self, gv_id: int) -> bool:
        """Xóa cứng GiaoVien và NguoiDung liên kết."""
        gv = self.s.get(GiaoVien, gv_id)
        if not gv:
            return False
        nd_id = gv.nguoi_dung_id
        self.s.delete(gv)
        self.s.flush()
        nd = self.s.get(NguoiDung, nd_id)
        if nd:
            self.s.delete(nd)
            self.s.flush()
        return True

    # ── Người dùng ────────────────────────────────────────────

    def get_nguoi_dung_by_email(self, email: str) -> Optional[NguoiDung]:
        return self.s.query(NguoiDung).filter_by(email=email).first()

    def create_nguoi_dung(
        self,
        ho_ten: str,
        email: str,
        mat_khau_hash: str,
        role: Role,
        active: bool = True,
    ) -> NguoiDung:
        nd = NguoiDung(
            ho_ten=ho_ten,
            email=email,
            mat_khau_hash=mat_khau_hash,
            role=role,
            active=active,
        )
        self.s.add(nd)
        self.s.flush()
        return nd

    def update_nguoi_dung(self, uid: int, **kwargs) -> Optional[NguoiDung]:
        nd = self.s.get(NguoiDung, uid)
        if nd:
            for k, v in kwargs.items():
                setattr(nd, k, v)
            self.s.flush()
        return nd

    def toggle_active_nguoi_dung(self, uid: int) -> Optional[NguoiDung]:
        nd = self.s.get(NguoiDung, uid)
        if nd:
            nd.active = not nd.active
            self.s.flush()
        return nd

    # ── Tổ chuyên môn (chỉ đọc) ───────────────────────────────

    def get_all_to(self) -> list[ToChuyenMon]:
        return (
            self.s.query(ToChuyenMon)
            .filter_by(active=True)
            .order_by(ToChuyenMon.ten_to)
            .all()
        )
    def get_to_by_ten(self, ten_to: str):
        from core.db.models.to_chuyen_mon import ToChuyenMon
        return self.s.query(ToChuyenMon).filter(
            ToChuyenMon.ten_to == ten_to
        ).first()

    def get_to_by_id(self, to_id: int):
        from core.db.models.to_chuyen_mon import ToChuyenMon
        return self.s.get(ToChuyenMon, to_id)