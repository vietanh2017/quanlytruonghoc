# modules/thi_dua_giao_vien/service.py
"""
ThiDuaGVService - phiên bản Web (FastAPI).
Refactor từ ThiDuaGVService desktop, nhận session từ bên ngoài.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from modules.thi_dua_giao_vien.repository.tieu_chi_repository import TieuChiRepository
from modules.thi_dua_giao_vien.repository.diem_gv_repository import DiemGiaoVienRepository
from core.db.models.giao_vien import GiaoVien
from core.db.models.nam_hoc import NamHoc
from core.db.models.hoc_ky import HocKy
from core.db.models.to_chuyen_mon import ToChuyenMon
from shared.dto.result import ServiceResult


class ThiDuaGVServiceWeb:
    def __init__(self, session: Session):
        self.session       = session
        self.tieu_chi_repo = TieuChiRepository(session)
        self.diem_repo     = DiemGiaoVienRepository(session)

    def _commit(self):   self.session.commit()
    def _rollback(self): self.session.rollback()

    # ══ METADATA ═════════════════════════════════════════════

    def lay_ds_nam_hoc(self):
        return self.session.query(NamHoc).filter(NamHoc.active == True)\
            .order_by(NamHoc.ten_nam_hoc.desc()).all()

    def lay_ds_hoc_ky(self, nam_hoc_id: int):
        return self.session.query(HocKy)\
            .filter(HocKy.nam_hoc_id == nam_hoc_id)\
            .order_by(HocKy.so_thu_tu).all()

    def lay_ds_to(self):
        return self.session.query(ToChuyenMon)\
            .filter(ToChuyenMon.active == True).all()

    def lay_ds_giao_vien(self, to_id: int = None):
        q = self.session.query(GiaoVien)\
            .options(joinedload(GiaoVien.nguoi_dung))\
            .filter(GiaoVien.active == True)
        if to_id:
            q = q.filter(GiaoVien.to_id == to_id)
        return q.all()

    # ══ TIÊU CHÍ ═════════════════════════════════════════════

    def lay_ds_tieu_chi(self, to_id=None) -> ServiceResult:
        try:
            data = self.tieu_chi_repo.get_all(to_id=to_id)
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_tieu_chi(self, ten_tieu_chi: str, diem_toi_da: float,
                      loai: str, mo_ta: str = "",
                      to_chuyen_mon_id: int = None) -> ServiceResult:
        try:
            # Sinh mã tự động
            ds = self.tieu_chi_repo.get_all(active_only=False)
            numbers = []
            for tc in ds:
                if tc.ma_tieu_chi and tc.ma_tieu_chi.startswith("TC"):
                    try: numbers.append(int(tc.ma_tieu_chi[2:]))
                    except: pass
            num = 1
            while num in numbers: num += 1
            ma = f"TC{num:02d}"

            obj = self.tieu_chi_repo.create(
                ma_tieu_chi=ma,
                ten_tieu_chi=ten_tieu_chi.strip(),
                diem_toi_da=float(diem_toi_da),
                loai=loai,
                mo_ta=mo_ta,
                to_chuyen_mon_id=to_chuyen_mon_id,
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_tieu_chi(self, tc_id: int, **data) -> ServiceResult:
        try:
            obj = self.tieu_chi_repo.update(tc_id, **data)
            if not obj:
                return ServiceResult(ok=False, error="Không tìm thấy tiêu chí.")
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_tieu_chi(self, tc_id: int) -> ServiceResult:
        try:
            ok = self.tieu_chi_repo.delete(tc_id)
            if not ok:
                return ServiceResult(ok=False, error="Không tìm thấy tiêu chí.")
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ CHẤM ĐIỂM ════════════════════════════════════════════

    def nhap_diem_hang_loat(self, giao_vien_id: int, thang: int,
                            nam_hoc_id: int, diem_list: list,
                            nguoi_cham_id: int = 1) -> ServiceResult:
        """Lưu điểm cho nhiều tiêu chí cùng lúc."""
        try:
            saved = 0
            for item in diem_list:
                tc_id = item["tieu_chi_id"]
                diem  = item["diem"]
                ghi_chu = item.get("ghi_chu", "")

                exist = self.diem_repo.get_by_tieu_chi_gv_thang(
                    giao_vien_id, tc_id, thang, nam_hoc_id
                )
                if exist:
                    self.diem_repo.update(exist.id,
                        diem=diem, ghi_chu=ghi_chu,
                        nguoi_cham_id=nguoi_cham_id)
                else:
                    self.diem_repo.create(
                        giao_vien_id=giao_vien_id,
                        tieu_chi_id=tc_id,
                        thang=thang,
                        nam_hoc_id=nam_hoc_id,
                        diem=float(diem),
                        ghi_chu=ghi_chu,
                        nguoi_cham_id=nguoi_cham_id,
                        ngay_cham=datetime.now(),
                    )
                saved += 1
            self._commit()
            return ServiceResult(ok=True, error=f"Đã lưu {saved} tiêu chí.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def lay_diem_thang(self, gv_id: int, thang: int,
                       nam_hoc_id: int) -> ServiceResult:
        try:
            data = self.diem_repo.get_by_gv_thang(gv_id, thang, nam_hoc_id)
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    # ══ TÍNH ĐIỂM ════════════════════════════════════════════

    def xep_loai(self, diem: float) -> str:
        if diem >= 90: return "Hoàn thành xuất sắc nhiệm vụ"
        if diem >= 80: return "Hoàn thành tốt nhiệm vụ"
        if diem >= 70: return "Hoàn thành nhiệm vụ"
        return "Không hoàn thành nhiệm vụ"

    def tinh_diem_thang(self, gv_id: int, thang: int,
                        nam_hoc_id: int) -> dict:
        """Trả về dict {diem, xep_loai}"""
        diem_list = self.diem_repo.get_by_gv_thang(gv_id, thang, nam_hoc_id)
        diem_tong = 100.0
        for d in diem_list:
            if d.tieu_chi.loai == "cong":
                diem_tong += d.diem
            else:
                diem_tong -= d.diem
        diem_tong = max(0, diem_tong)
        return {"diem": round(diem_tong, 2), "xep_loai": self.xep_loai(diem_tong)}

    def tinh_diem_hoc_ky(self, gv_id: int, hoc_ky_so_thu_tu: int,
                          nam_hoc_id: int) -> dict:
        """HK1: tháng 8-12, HK2: tháng 1-5"""
        thangs = [8, 9, 10, 11, 12] if hoc_ky_so_thu_tu == 1 else [1, 2, 3, 4, 5]
        diem_list = [self.tinh_diem_thang(gv_id, t, nam_hoc_id)["diem"] for t in thangs]
        diem_tb = sum(diem_list) / len(diem_list) if diem_list else 0
        return {"diem": round(diem_tb, 2), "xep_loai": self.xep_loai(diem_tb)}

    def xep_hang_theo_thang(self, thang: int, nam_hoc_id: int,
                             to_id: int = None) -> list:
        ds_gv = self.lay_ds_giao_vien(to_id)
        result = []
        for gv in ds_gv:
            d = self.tinh_diem_thang(gv.id, thang, nam_hoc_id)
            result.append({
                "giao_vien_id": gv.id,
                "ma_giao_vien": gv.ma_giao_vien or "",
                "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
                "diem":     d["diem"],
                "xep_loai": d["xep_loai"],
            })
        result.sort(key=lambda x: x["diem"], reverse=True)
        for i, item in enumerate(result):
            item["hang"] = i + 1
        return result

    def xep_hang_theo_hoc_ky(self, hoc_ky_so_thu_tu: int,
                              nam_hoc_id: int, to_id: int = None) -> list:
        ds_gv = self.lay_ds_giao_vien(to_id)
        result = []
        for gv in ds_gv:
            d = self.tinh_diem_hoc_ky(gv.id, hoc_ky_so_thu_tu, nam_hoc_id)
            result.append({
                "giao_vien_id": gv.id,
                "ma_giao_vien": gv.ma_giao_vien or "",
                "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
                "diem":     d["diem"],
                "xep_loai": d["xep_loai"],
            })
        result.sort(key=lambda x: x["diem"], reverse=True)
        for i, item in enumerate(result):
            item["hang"] = i + 1
        return result

    def xep_hang_ca_nam(self, nam_hoc_id: int, to_id: int = None) -> list:
        ds_gv = self.lay_ds_giao_vien(to_id)
        result = []
        for gv in ds_gv:
            d_hk1 = self.tinh_diem_hoc_ky(gv.id, 1, nam_hoc_id)["diem"]
            d_hk2 = self.tinh_diem_hoc_ky(gv.id, 2, nam_hoc_id)["diem"]
            diem_tb = round((d_hk1 + d_hk2) / 2, 2)
            result.append({
                "giao_vien_id": gv.id,
                "ma_giao_vien": gv.ma_giao_vien or "",
                "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
                "diem":     diem_tb,
                "diem_hk1": d_hk1,
                "diem_hk2": d_hk2,
                "xep_loai": self.xep_loai(diem_tb),
            })
        result.sort(key=lambda x: x["diem"], reverse=True)
        for i, item in enumerate(result):
            item["hang"] = i + 1
        return result