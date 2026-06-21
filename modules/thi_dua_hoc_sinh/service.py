# modules/thi_dua_hoc_sinh/service.py
"""
Service thi đua học sinh - phiên bản Web (FastAPI).
Refactor từ DiemCaNhanService + DiemTapTheService (desktop).
Nhận session từ bên ngoài (dependency injection).
"""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from modules.competition.repository.loai_vi_pham_repository import LoaiViPhamRepository
from modules.competition.repository.hoc_sinh_vi_pham_repository import HocSinhViPhamRepository
from modules.competition.repository.tap_the_vi_pham_repository import TapTheViPhamRepository
from modules.competition.repository.diem_doi_ngay_repository import DiemDoiNgayRepository
from modules.competition.repository.diem_tap_the_repository import DiemTapTheRepository
from modules.competition.models.loai_vi_pham import LoaiViPham
from core.db.models.hoc_sinh import HocSinh
from core.db.models.lop_hoc import LopHoc
from core.db.models.nam_hoc import NamHoc
from core.db.models.hoc_ky import HocKy
from shared.dto.result import ServiceResult


class ThiDuaHocSinhService:
    def __init__(self, session: Session):
        self.session        = session
        self.loai_vp_repo   = LoaiViPhamRepository(session)
        self.hs_vp_repo     = HocSinhViPhamRepository(session)
        self.tap_the_repo   = TapTheViPhamRepository(session)
        self.doi_ngay_repo  = DiemDoiNgayRepository(session)
        self.tap_the_diem_repo = DiemTapTheRepository(session)

    def _commit(self):   self.session.commit()
    def _rollback(self): self.session.rollback()

    # ══ METADATA ═════════════════════════════════════════════

    def lay_ds_nam_hoc(self):
        return self.session.query(NamHoc).filter(NamHoc.active == True).all()

    def lay_ds_hoc_ky(self, nam_hoc_id: int):
        return self.session.query(HocKy).filter(
            HocKy.nam_hoc_id == nam_hoc_id, HocKy.active == True
        ).all()

    def lay_ds_lop(self, nam_hoc_id: int = None):
        """Lấy danh sách lớp, nếu có nam_hoc_id thì lọc theo năm học"""
        query = self.session.query(LopHoc).filter(LopHoc.active == True)
        if nam_hoc_id:
            query = query.filter(LopHoc.nam_hoc_id == nam_hoc_id)
        return query.order_by(LopHoc.khoi, LopHoc.ten_lop).all()

    # ⭐ THÊM HÀM NÀY
    def lay_ds_hoc_sinh(self, lop_hoc_id: int):
        """Lấy danh sách học sinh theo lớp"""
        try:
            return self.session.query(HocSinh).filter(
                HocSinh.lop_hoc_id == lop_hoc_id,
                HocSinh.active == True
            ).order_by(HocSinh.ho_ten).all()
        except Exception as e:
            print(f"Lỗi lay_ds_hoc_sinh: {e}")
            return []

    def count_active_violations(self) -> int:
        count = self.session.query(LoaiViPham).filter(
            LoaiViPham.loai == "vi_pham",
            LoaiViPham.is_active == True
        ).count()
        return count if count > 0 else 8

    # ══ DANH MỤC LOẠI VI PHẠM ════════════════════════════════

    def lay_ds_loai_vp(self, loai: str = None) -> ServiceResult:
        try:
            ds = self.loai_vp_repo.get_all(loai=loai)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_loai_vp(self, ma_loi: str, ten_loi: str, loai: str,
                     nhom: str = "", so_diem: float = 0,
                     mo_ta: str = "", thu_tu: int = 0) -> ServiceResult:
        try:
            if self.loai_vp_repo.get_by_ma(ma_loi):
                return ServiceResult(ok=False, error="Mã lỗi đã tồn tại.")
            obj = self.loai_vp_repo.create(
                ma_loi=ma_loi.strip(), ten_loi=ten_loi.strip(),
                loai=loai, nhom=nhom, so_diem=so_diem,
                mo_ta=mo_ta, thu_tu=thu_tu
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_loai_vp(self, id: int, **data) -> ServiceResult:
        try:
            obj = self.loai_vp_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_loai_vp(self, id: int) -> ServiceResult:
        try:
            self.loai_vp_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ VI PHẠM CÁ NHÂN ══════════════════════════════════════

    def lay_vp_ca_nhan(self, lop_hoc_id: int, nam_hoc_id: int,
                       tuan: int = None) -> ServiceResult:
        try:
            ds = self.hs_vp_repo.get_by_lop(lop_hoc_id, nam_hoc_id, tuan)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_vp_ca_nhan(self, hoc_sinh_id: int, loai_vi_pham_id: int,
                        nam_hoc_id: int, tuan: int, ngay_xay_ra: date,
                        tiet: int = None, mo_ta: str = "",
                        nguoi_ghi_nhan: str = "") -> ServiceResult:
        try:
            hs = self.session.get(HocSinh, hoc_sinh_id)
            if not hs:
                return ServiceResult(ok=False, error="Không tìm thấy học sinh.")

            lvp = self.loai_vp_repo.get_by_id(loai_vi_pham_id)
            if not lvp:
                return ServiceResult(ok=False, error="Không tìm thấy loại vi phạm.")

            so_diem = lvp.so_diem

            vp = self.hs_vp_repo.create(
                hoc_sinh_id=hoc_sinh_id,
                loai_vi_pham_id=loai_vi_pham_id,
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                so_diem=so_diem,
                ngay_xay_ra=ngay_xay_ra,
                tiet=tiet,
                mo_ta=mo_ta,
                nguoi_ghi_nhan=nguoi_ghi_nhan,
                da_anh_huong_lop=True,
            )

            thu = ngay_xay_ra.weekday() + 2
            if thu in range(2, 7):
                so_vp = self.count_active_violations()
                self.doi_ngay_repo.create_or_update(
                    nam_hoc_id=nam_hoc_id, tuan=tuan, thu=thu,
                    lop_hoc_id=hs.lop_hoc_id,
                    diem_thay_doi=so_diem,
                    so_luong_vi_pham=so_vp,
                    ngay=ngay_xay_ra,
                )
                self._cap_nhat_diem_doi_tuan(nam_hoc_id, tuan, hs.lop_hoc_id, so_vp)

            self._commit()
            return ServiceResult(ok=True, data=vp, error="Thêm thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_vp_ca_nhan(self, vp_id: int) -> ServiceResult:
        try:
            vp = self.hs_vp_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy.")

            hs = self.session.get(HocSinh, vp.hoc_sinh_id)
            if hs:
                thu = vp.ngay_xay_ra.weekday() + 2
                if thu in range(2, 7):
                    so_vp = self.count_active_violations()
                    self.doi_ngay_repo.rollback_diem_tru(
                        nam_hoc_id=vp.nam_hoc_id, tuan=vp.tuan, thu=thu,
                        lop_hoc_id=hs.lop_hoc_id,
                        diem_thay_doi=vp.so_diem,
                        so_luong_vi_pham=so_vp,
                    )
                    self._cap_nhat_diem_doi_tuan(vp.nam_hoc_id, vp.tuan, hs.lop_hoc_id, so_vp)

            self.hs_vp_repo.delete(vp_id)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ VI PHẠM TẬP THỂ ══════════════════════════════════════

    def lay_vp_tap_the(self, nam_hoc_id: int, tuan: int,
                       lop_hoc_id: int = None) -> ServiceResult:
        try:
            ds = self.tap_the_repo.get_by_tuan(nam_hoc_id, tuan, lop_hoc_id)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_vp_tap_the(self, lop_hoc_id: int, loai_vi_pham_id: int,
                        nam_hoc_id: int, tuan: int, ngay_xay_ra: date,
                        tiet: int = None, mo_ta: str = "",
                        nguoi_ghi_nhan: str = "") -> ServiceResult:
        try:
            thu = ngay_xay_ra.weekday() + 2
            if thu not in range(2, 7):
                return ServiceResult(ok=False, error="Chỉ nhập từ Thứ 2 đến Thứ 6.")

            lvp = self.loai_vp_repo.get_by_id(loai_vi_pham_id)
            if not lvp:
                return ServiceResult(ok=False, error="Không tìm thấy loại vi phạm.")

            so_diem = lvp.so_diem

            vp = self.tap_the_repo.create(
                lop_hoc_id=lop_hoc_id,
                loai_vi_pham_id=loai_vi_pham_id,
                nam_hoc_id=nam_hoc_id,
                tuan=tuan, thu=thu,
                so_diem=so_diem,
                ngay_xay_ra=ngay_xay_ra,
                tiet=tiet,
                mo_ta=mo_ta,
                nguoi_ghi_nhan=nguoi_ghi_nhan,
                da_xac_nhan=True,
            )

            so_vp = self.count_active_violations()
            self.doi_ngay_repo.create_or_update(
                nam_hoc_id=nam_hoc_id, tuan=tuan, thu=thu,
                lop_hoc_id=lop_hoc_id,
                diem_thay_doi=so_diem,
                so_luong_vi_pham=so_vp,
                ngay=ngay_xay_ra,
            )
            self._cap_nhat_diem_doi_tuan(nam_hoc_id, tuan, lop_hoc_id, so_vp)

            self._commit()
            return ServiceResult(ok=True, data=vp, error="Thêm thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_vp_tap_the(self, vp_id: int) -> ServiceResult:
        try:
            vp = self.tap_the_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy.")

            so_vp = self.count_active_violations()
            self.doi_ngay_repo.rollback_diem_tru(
                nam_hoc_id=vp.nam_hoc_id, tuan=vp.tuan, thu=vp.thu,
                lop_hoc_id=vp.lop_hoc_id,
                diem_thay_doi=vp.so_diem,
                so_luong_vi_pham=so_vp,
            )
            self._cap_nhat_diem_doi_tuan(vp.nam_hoc_id, vp.tuan, vp.lop_hoc_id, so_vp)

            self.tap_the_repo.delete(vp_id)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ ĐIỂM TẬP THỂ TUẦN ════════════════════════════════════

    def lay_diem_tuan(self, nam_hoc_id: int, tuan: int) -> ServiceResult:
        try:
            ds_lop = self.lay_ds_lop(nam_hoc_id)
            so_vp  = self.count_active_violations()
            result = []
            for lop in ds_lop:
                diem_doi = self.doi_ngay_repo.get_trung_binh_tuan(
                    nam_hoc_id, tuan, lop.id, so_vp
                )
                record = self.tap_the_diem_repo.get_by_nam_hoc_tuan_lop(
                    nam_hoc_id, tuan, lop.id
                )
                result.append({
                    "lop_hoc_id": lop.id,
                    "ten_lop":    lop.ten_lop,
                    "khoi":       lop.khoi,
                    "diem_doi":   round(diem_doi, 2),
                    "diem_hoc_tap": record.diem_hoc_tap if record else 0,
                    "tong_diem":  round((record.diem_hoc_tap if record else 0) + diem_doi, 2),
                    "da_khoa":    record.da_khoa if record else False,
                    "ghi_chu":    record.ghi_chu if record else "",
                })
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def luu_diem_hoc_tap(self, nam_hoc_id: int, tuan: int,
                         data: list, nguoi_nhap: str = "") -> ServiceResult:
        try:
            so_vp = self.count_active_violations()
            for item in data:
                diem_doi = self.doi_ngay_repo.get_trung_binh_tuan(
                    nam_hoc_id, tuan, item["lop_hoc_id"], so_vp
                )
                self.tap_the_diem_repo.create_or_update(
                    nam_hoc_id=nam_hoc_id,
                    tuan=tuan,
                    lop_hoc_id=item["lop_hoc_id"],
                    diem_hoc_tap=item["diem_hoc_tap"],
                    diem_doi=diem_doi,
                    ghi_chu=item.get("ghi_chu", ""),
                    nguoi_nhap=nguoi_nhap,
                )
            self._commit()
            return ServiceResult(ok=True, error="Lưu thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ BÁO CÁO ══════════════════════════════════════════════

    def bao_cao_xep_hang_tuan(self, nam_hoc_id: int, tuan: int) -> ServiceResult:
        try:
            r = self.lay_diem_tuan(nam_hoc_id, tuan)
            if not r.ok:
                return r
            data = sorted(r.data, key=lambda x: x["tong_diem"], reverse=True)
            for i, item in enumerate(data):
                item["hang"] = i + 1
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def bao_cao_ca_nhan_theo_lop(self, lop_hoc_id: int,
                                  nam_hoc_id: int, tuan: int = None) -> ServiceResult:
        try:
            ds_hs = self.lay_ds_hoc_sinh(lop_hoc_id)
            result = []
            for hs in ds_hs:
                tong = self.hs_vp_repo.get_tong_diem_ca_nhan(hs.id, nam_hoc_id, tuan)
                ds_vp = self.hs_vp_repo.get_by_hoc_sinh(hs.id, nam_hoc_id, tuan)
                result.append({
                    "hoc_sinh_id": hs.id,
                    "ma_hoc_sinh": hs.ma_hoc_sinh,
                    "ho_ten":      hs.ho_ten,
                    "tong_diem":   tong,
                    "so_vi_pham":  len([v for v in ds_vp if v.so_diem < 0]),
                    "so_thanh_tich": len([v for v in ds_vp if v.so_diem > 0]),
                })
            result.sort(key=lambda x: x["tong_diem"])
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    # ══ HELPER ════════════════════════════════════════════════

    def _cap_nhat_diem_doi_tuan(self, nam_hoc_id: int, tuan: int,
                                 lop_hoc_id: int, so_luong_vp: int):
        diem_doi = self.doi_ngay_repo.get_trung_binh_tuan(
            nam_hoc_id, tuan, lop_hoc_id, so_luong_vp
        )
        record = self.tap_the_diem_repo.get_by_nam_hoc_tuan_lop(nam_hoc_id, tuan, lop_hoc_id)
        if record:
            record.diem_doi = diem_doi
        else:
            self.tap_the_diem_repo.create_or_update(
                nam_hoc_id=nam_hoc_id, tuan=tuan,
                lop_hoc_id=lop_hoc_id,
                diem_hoc_tap=0, diem_doi=diem_doi,
                ghi_chu="Tự động", nguoi_nhap="Hệ thống",
            )
        self.session.flush()