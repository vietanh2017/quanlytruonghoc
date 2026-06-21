# modules/cau_hinh/service.py
"""
CauHinhService: logic nghiệp vụ module Cấu hình hệ thống.
"""

from typing import Optional
from sqlalchemy.orm import Session

from modules.cau_hinh.repository import (
    NamHocRepository, ToChuyenMonRepository,
    MonHocRepository, NguoiDungRepository,
    HocKyRepository, TietHocRepository,
)
from modules.cau_hinh.repository import PhanMonRepository, MonHocKhoiRepository
from shared.dto.result import ServiceResult
from shared.enums import Role
from core.auth.password import hash_password
from core.db.models import HocKy
from core.db.models.phan_quyen import Quyen, VaiTroQuyen


class CauHinhService:
    def __init__(self, session: Session):
        self.session            = session
        self.nam_hoc_repo       = NamHocRepository(session)
        self.to_chuyen_mon_repo = ToChuyenMonRepository(session)
        self.mon_hoc_repo       = MonHocRepository(session)
        self.phan_mon_repo = PhanMonRepository(session)
        self.mon_hoc_khoi_repo = MonHocKhoiRepository(session)
        self.nguoi_dung_repo    = NguoiDungRepository(session)
        self.hoc_ky_repo        = HocKyRepository(session)
        self.tiet_hoc_repo      = TietHocRepository(session)

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()

    # ══ NĂM HỌC ══════════════════════════════════════════════

    def lay_ds_nam_hoc(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.nam_hoc_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_nam_hoc(self, ten_nam_hoc: str, active: bool = True) -> ServiceResult:
        try:
            if self.nam_hoc_repo.get_by_ten(ten_nam_hoc):
                return ServiceResult(ok=False, error="Tên năm học đã tồn tại.")
            obj = self.nam_hoc_repo.create(ten_nam_hoc=ten_nam_hoc, active=active)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm năm học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_nam_hoc(self, id: int, ten_nam_hoc: str, active: bool = True) -> ServiceResult:
        try:
            exist = self.nam_hoc_repo.get_by_ten(ten_nam_hoc)
            if exist and exist.id != id:
                return ServiceResult(ok=False, error="Tên năm học đã tồn tại.")
            obj = self.nam_hoc_repo.update(id, ten_nam_hoc=ten_nam_hoc, active=active)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật năm học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_nam_hoc(self, id: int) -> ServiceResult:
        try:
            self.nam_hoc_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa năm học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ HỌC KỲ ═══════════════════════════════════════════════

    def lay_ds_hoc_ky(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.hoc_ky_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_hoc_ky(self, ten_hoc_ky: str, nam_hoc_id: int,
                    so_thu_tu: int, active: bool = True) -> ServiceResult:
        try:
            exist = (self.session.query(HocKy)
                     .filter(HocKy.nam_hoc_id == nam_hoc_id,
                             HocKy.so_thu_tu == so_thu_tu)
                     .first())
            if exist:
                return ServiceResult(ok=False,
                    error=f"Học kỳ {so_thu_tu} của năm học này đã tồn tại.")
            obj = self.hoc_ky_repo.create(
                ten_hoc_ky=ten_hoc_ky, nam_hoc_id=nam_hoc_id,
                so_thu_tu=so_thu_tu, active=active)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm học kỳ thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_hoc_ky(self, id: int, ten_hoc_ky=None, nam_hoc_id=None,
                   so_thu_tu=None, active=None) -> ServiceResult:
        try:
            data = {}
            if ten_hoc_ky is not None: data["ten_hoc_ky"] = ten_hoc_ky.strip()
            if nam_hoc_id is not None: data["nam_hoc_id"] = nam_hoc_id
            if so_thu_tu  is not None: data["so_thu_tu"]  = so_thu_tu
            if active     is not None: data["active"]     = active
            obj = self.hoc_ky_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật học kỳ thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_hoc_ky(self, id: int) -> ServiceResult:
        try:
            self.hoc_ky_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa học kỳ thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ TỔ CHUYÊN MÔN ════════════════════════════════════════

    def lay_ds_to_chuyen_mon(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.to_chuyen_mon_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_to_chuyen_mon(self, ma_to: str, ten_to: str,
                           mo_ta: str = "", active: bool = True) -> ServiceResult:
        try:
            if self.to_chuyen_mon_repo.get_by_ma(ma_to):
                return ServiceResult(ok=False, error="Mã tổ đã tồn tại.")
            obj = self.to_chuyen_mon_repo.create(
                ma_to=ma_to.strip(), ten_to=ten_to.strip(),
                mo_ta=mo_ta, active=active)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm tổ chuyên môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_to_chuyen_mon(self, id: int, ma_to=None, ten_to=None,
                          mo_ta=None, active=None) -> ServiceResult:
        try:
            if ma_to:
                exist = self.to_chuyen_mon_repo.get_by_ma(ma_to)
                if exist and exist.id != id:
                    return ServiceResult(ok=False, error="Mã tổ đã tồn tại.")
            data = {}
            if ma_to  is not None: data["ma_to"]  = ma_to.strip()
            if ten_to is not None: data["ten_to"] = ten_to.strip()
            if mo_ta  is not None: data["mo_ta"]  = mo_ta
            if active is not None: data["active"] = active
            obj = self.to_chuyen_mon_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật tổ chuyên môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_to_chuyen_mon(self, id: int) -> ServiceResult:
        try:
            self.to_chuyen_mon_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa tổ chuyên môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ MÔN HỌC ══════════════════════════════════════════════
    # Model MonHoc thực tế: co_phan_mon, to_id, thu_tu

    def lay_ds_mon_hoc(self) -> ServiceResult:
        try:
            data = self.mon_hoc_repo.get_all()
            # ⭐ Chuyển đổi dữ liệu để bao gồm phân môn và số tiết
            result = []
            for mon in data:
                mon_dict = {
                    'id': mon.id,
                    'ma_mon': mon.ma_mon,
                    'ten_mon': mon.ten_mon,
                    'co_phan_mon': mon.co_phan_mon,
                    'to_id': mon.to_id,
                    'thu_tu': mon.thu_tu,
                    'active': mon.active,
                    'ten_to': mon.to_chuyen_mon.ten_to if mon.to_chuyen_mon else None,
                    'phan_mon_list': [
                        {
                            'id': pm.id,
                            'ma_phan_mon': pm.ma_phan_mon,
                            'ten_phan_mon': pm.ten_phan_mon,
                            'mon_hoc_id': pm.mon_hoc_id,
                            'thu_tu': pm.thu_tu,
                            'active': pm.active
                        }
                        for pm in (mon.phan_mon_list or [])
                    ],
                    'khoi_list': [
                        {
                            'id': k.id,
                            'mon_hoc_id': k.mon_hoc_id,
                            'khoi': k.khoi,
                            'so_tiet': k.so_tiet
                        }
                        for k in (mon.khoi_list or [])
                    ]
                }
                result.append(mon_dict)
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    def them_mon_hoc(self, ma_mon: str, ten_mon: str,
                     co_phan_mon: bool = False,
                     to_id: Optional[int] = None,
                     thu_tu: int = 0,
                     active: bool = True) -> ServiceResult:
        try:
            if self.mon_hoc_repo.get_by_ma(ma_mon):
                return ServiceResult(ok=False, error="Mã môn đã tồn tại.")
            obj = self.mon_hoc_repo.create(
                ma_mon=ma_mon.strip(),
                ten_mon=ten_mon.strip(),
                co_phan_mon=co_phan_mon,
                to_id=to_id,
                thu_tu=thu_tu,
                active=active,
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm môn học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_mon_hoc(self, id: int, **data) -> ServiceResult:
        try:
            if "ma_mon" in data:
                exist = self.mon_hoc_repo.get_by_ma(data["ma_mon"])
                if exist and exist.id != id:
                    return ServiceResult(ok=False, error="Mã môn đã tồn tại.")
            obj = self.mon_hoc_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật môn học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_mon_hoc(self, id: int) -> ServiceResult:
        try:
            self.mon_hoc_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa môn học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
    # ══ PHÂN MÔN ══════════════════════════════════════════════

    def lay_ds_phan_mon(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.phan_mon_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_phan_mon_theo_mon(self, mon_hoc_id: int) -> ServiceResult:
        try:
            data = self.phan_mon_repo.get_by_mon_hoc(mon_hoc_id)
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_phan_mon(self, ma_phan_mon: str, ten_phan_mon: str,
                      mon_hoc_id: int, thu_tu: int = 0,
                      active: bool = True) -> ServiceResult:
        try:
            if self.phan_mon_repo.get_by_ma(ma_phan_mon, mon_hoc_id):
                return ServiceResult(ok=False, error="Mã phân môn đã tồn tại trong môn học này.")
            obj = self.phan_mon_repo.create(
                ma_phan_mon=ma_phan_mon.strip(),
                ten_phan_mon=ten_phan_mon.strip(),
                mon_hoc_id=mon_hoc_id,
                thu_tu=thu_tu,
                active=active
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm phân môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_phan_mon(self, id: int, **data) -> ServiceResult:
        try:
            if "ma_phan_mon" in data:
                obj = self.phan_mon_repo.get_by_id(id)
                exist = self.phan_mon_repo.get_by_ma(data["ma_phan_mon"], obj.mon_hoc_id if obj else None)
                if exist and exist.id != id:
                    return ServiceResult(ok=False, error="Mã phân môn đã tồn tại.")
            obj = self.phan_mon_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật phân môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_phan_mon(self, id: int) -> ServiceResult:
        try:
            self.phan_mon_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa phân môn thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ SỐ TIẾT THEO KHỐI ══════════════════════════════════════

    def lay_ds_so_tiet_theo_khoi(self, mon_hoc_id: int) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.mon_hoc_khoi_repo.get_by_mon_hoc(mon_hoc_id))
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_so_tiet_theo_khoi(self, mon_hoc_id: int, khoi: int, so_tiet: int) -> ServiceResult:
        try:
            exist = self.mon_hoc_khoi_repo.get_by_mon_hoc_khoi(mon_hoc_id, khoi)
            if exist:
                return ServiceResult(ok=False, error=f"Đã có số tiết cho khối {khoi}.")
            obj = self.mon_hoc_khoi_repo.create(
                mon_hoc_id=mon_hoc_id,
                khoi=khoi,
                so_tiet=so_tiet
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm số tiết thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_so_tiet_theo_khoi(self, id: int, so_tiet: int) -> ServiceResult:
        try:
            obj = self.mon_hoc_khoi_repo.update(id, so_tiet=so_tiet)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật số tiết thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_so_tiet_theo_khoi(self, id: int) -> ServiceResult:
        try:
            self.mon_hoc_khoi_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa số tiết thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def xoa_toan_bo_so_tiet_theo_khoi(self, mon_hoc_id: int) -> ServiceResult:
        try:
            self.mon_hoc_khoi_repo.delete_by_mon_hoc(mon_hoc_id)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa toàn bộ số tiết theo khối.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
        
    # ══ TÀI KHOẢN ════════════════════════════════════════════

    def lay_ds_nguoi_dung(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.nguoi_dung_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_nguoi_dung(self, ho_ten: str, email: str, role: str,
                        mat_khau: Optional[str] = None,
                        active: bool = True) -> ServiceResult:
        try:
            if self.nguoi_dung_repo.get_by_email(email.strip().lower()):
                return ServiceResult(ok=False, error="Email đã tồn tại.")
            pw = mat_khau.strip() if mat_khau and mat_khau.strip() else "eduschool@123"
            nd = self.nguoi_dung_repo.create(
                ho_ten=ho_ten.strip(),
                email=email.strip().lower(),
                mat_khau_hash=hash_password(pw),
                role=role, active=active)
            self._commit()
            return ServiceResult(ok=True, data=nd, error="Thêm tài khoản thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_nguoi_dung(self, id: int, ho_ten=None, email=None,
                       role=None, active=None) -> ServiceResult:
        try:
            if email:
                exist = self.nguoi_dung_repo.get_by_email(email.strip().lower())
                if exist and exist.id != id:
                    return ServiceResult(ok=False, error="Email đã tồn tại.")
            data = {}
            if ho_ten is not None: data["ho_ten"] = ho_ten.strip()
            if email  is not None: data["email"]  = email.strip().lower()
            if role   is not None: data["role"]   = role
            if active is not None: data["active"] = active
            obj = self.nguoi_dung_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật tài khoản thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_nguoi_dung(self, id: int) -> ServiceResult:
        try:
            nd = self.nguoi_dung_repo.get_by_id(id)
            if not nd:
                return ServiceResult(ok=False, error="Không tìm thấy tài khoản.")
            if nd.role == Role.ADMIN:
                count = len([u for u in self.nguoi_dung_repo.get_all()
                             if u.role == Role.ADMIN])
                if count <= 1:
                    return ServiceResult(ok=False,
                        error="Không thể xóa tài khoản Admin cuối cùng.")
            self.nguoi_dung_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa tài khoản thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def reset_mat_khau(self, id: int,
                       mat_khau_moi: str = "eduschool@123") -> ServiceResult:
        try:
            self.nguoi_dung_repo.update_mat_khau(id, hash_password(mat_khau_moi))
            self._commit()
            return ServiceResult(ok=True, error=f"Đã đặt lại mật khẩu: {mat_khau_moi}")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ TIẾT HỌC ═════════════════════════════════════════════

    def lay_ds_tiet_hoc(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.tiet_hoc_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_tiet_hoc(self, so_thu_tu: int, ten_tiet: str,
                      thoi_gian_bat_dau: str = "",
                      thoi_gian_ket_thuc: str = "",
                      active: int = 1) -> ServiceResult:
        try:
            obj = self.tiet_hoc_repo.create(
                so_thu_tu=so_thu_tu, ten_tiet=ten_tiet,
                thoi_gian_bat_dau=thoi_gian_bat_dau,
                thoi_gian_ket_thuc=thoi_gian_ket_thuc,
                active=active)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm tiết học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_tiet_hoc(self, id: int, **data) -> ServiceResult:
        try:
            obj = self.tiet_hoc_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật tiết học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_tiet_hoc(self, id: int) -> ServiceResult:
        try:
            self.tiet_hoc_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa tiết học thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
