# modules/thi_dua_hoc_sinh/service.py
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload
import json

# Repository imports
from modules.thi_dua_hoc_sinh.repository.loai_vi_pham_repository import LoaiViPhamRepository
from modules.thi_dua_hoc_sinh.repository.hoc_sinh_vi_pham_repository import HocSinhViPhamRepository
from modules.thi_dua_hoc_sinh.repository.tap_the_vi_pham_repository import TapTheViPhamRepository
from modules.thi_dua_hoc_sinh.repository.diem_tap_the_repository import DiemTapTheRepository
from modules.thi_dua_hoc_sinh.repository.diem_doi_ngay_repository import DiemDoiNgayRepository
from modules.thi_dua_hoc_sinh.repository.thang_thi_dua_repository import ThangThiDuaRepository  # ⭐ THÊM

# Core models
from core.db.models.hoc_sinh import HocSinh
from core.db.models.lop_hoc import LopHoc
from core.db.models.nam_hoc import NamHoc
from modules.thi_dua_hoc_sinh.models.loai_vi_pham import LoaiViPham
from modules.thi_dua_hoc_sinh.models.tap_the_vi_pham import TapTheViPham
from modules.thi_dua_hoc_sinh.models.hoc_sinh_vi_pham import HocSinhViPham
from modules.thi_dua_hoc_sinh.models.diem_doi_ngay import DiemDoiNgay
from modules.thi_dua_hoc_sinh.models.thang_thi_dua import ThangThiDua  # ⭐ THÊM
from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet  # ⭐ THÊM
from modules.thi_dua_hoc_sinh.models.hoc_ky import ThiDuaHocKy
from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet

# Shared
from shared.dto.result import ServiceResult

class ThiDuaHocSinhService:
    def __init__(self, session: Session):
        self.session = session
        self.loai_vp_repo = LoaiViPhamRepository(session)
        self.hs_vp_repo = HocSinhViPhamRepository(session)
        self.tap_the_repo = TapTheViPhamRepository(session)
        self.doi_ngay_repo = DiemDoiNgayRepository(session)
        self.tap_the_diem_repo = DiemTapTheRepository(session)
        self.thang_repo = None
        self.hoc_ky_repo = None  # ⭐ THÊM DÒNG NÀY
        self._init_thang_repo()
        self._init_hoc_ky_repo()  # ⭐ THÊM DÒNG NÀY

    def _commit(self):
        self.session.commit()
    
    def _rollback(self):
        self.session.rollback()

    # ══ METADATA ═════════════════════════════════════════════

    def lay_ds_nam_hoc(self):
        return self.session.query(NamHoc).filter(NamHoc.active == True).all()

    def lay_ds_lop(self, nam_hoc_id: int = None):
        query = self.session.query(LopHoc).filter(LopHoc.active == True)
        if nam_hoc_id:
            query = query.filter(LopHoc.nam_hoc_id == nam_hoc_id)
        return query.order_by(LopHoc.khoi, LopHoc.ten_lop).all()

    def lay_ds_hoc_sinh(self, lop_hoc_id: int):
        try:
            return self.session.query(HocSinh).filter(
                HocSinh.lop_hoc_id == lop_hoc_id,
                HocSinh.active == True
            ).order_by(HocSinh.ho_ten).all()
        except Exception as e:
            print(f"Lỗi lay_ds_hoc_sinh: {e}")
            return []

    def count_active_violations(self) -> int:
        # ✅ Đếm TẤT CẢ tiêu chí (cả vi_pham lẫn thanh_tich) giống frontend
        count = self.session.query(LoaiViPham).filter(
            LoaiViPham.is_active == True  # ❌ Bỏ filter loai == "vi_pham"
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
                     doi_tuong: str = "tap_the", loai_diem: str = "tru",
                     nhom: str = "", so_diem: float = 0,
                     mo_ta: str = "", thu_tu: int = 0) -> ServiceResult:
        try:
            if self.loai_vp_repo.get_by_ma(ma_loi):
                return ServiceResult(ok=False, error="Mã lỗi đã tồn tại.")
            final_diem = -abs(so_diem) if loai == "vi_pham" else abs(so_diem)
            obj = self.loai_vp_repo.create(
                ma_loi=ma_loi.strip(), ten_loi=ten_loi.strip(),
                loai=loai, doi_tuong=doi_tuong, loai_diem=loai_diem,
                nhom=nhom, so_diem=final_diem, mo_ta=mo_ta, thu_tu=thu_tu
            )
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Thêm thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

# modules/thi_dua_hoc_sinh/service.py

    def sua_loai_vp(self, id: int, **data) -> ServiceResult:
        try:
            # ⭐ Kiểm tra nếu có cập nhật ma_loi
            if "ma_loi" in data and data["ma_loi"]:
                # Kiểm tra mã mới đã tồn tại chưa (trừ chính nó)
                existing = self.loai_vp_repo.get_by_ma(data["ma_loi"])
                if existing and existing.id != id:
                    return ServiceResult(ok=False, error=f"Mã '{data['ma_loi']}' đã tồn tại.")
            
            # Xử lý so_diem nếu có
            if "so_diem" in data and "loai" in data:
                so_diem = data["so_diem"]
                loai = data["loai"]
                data["so_diem"] = -abs(so_diem) if loai == "vi_pham" else abs(so_diem)
            
            obj = self.loai_vp_repo.update(id, **data)
            self._commit()
            return ServiceResult(ok=True, data=obj, error="Cập nhật thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_loai_vp(self, id: int) -> ServiceResult:
        try:
            # ⭐ Xóa tất cả vi phạm tham chiếu đến loại này
            self.session.query(TapTheViPham).filter(TapTheViPham.loai_vi_pham_id == id).delete()
            self.session.query(HocSinhViPham).filter(HocSinhViPham.loai_vi_pham_id == id).delete()
            
            # Sau đó xóa loại vi phạm
            self.loai_vp_repo.delete(id)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa loại vi phạm và các vi phạm liên quan.")
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
                        so_diem: float = 0, tiet: int = None,
                        mo_ta: str = "", nguoi_ghi_nhan: str = "") -> ServiceResult:
        try:
            hs = self.session.get(HocSinh, hoc_sinh_id)
            if not hs:
                return ServiceResult(ok=False, error="Không tìm thấy học sinh.")
            lvp = self.loai_vp_repo.get_by_id(loai_vi_pham_id)
            if not lvp:
                return ServiceResult(ok=False, error="Không tìm thấy loại vi phạm.")

            vp = self.hs_vp_repo.create(
                hoc_sinh_id=hoc_sinh_id,
                loai_vi_pham_id=loai_vi_pham_id,
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                so_diem=so_diem,
                ngay_xay_ra=ngay_xay_ra,
                tiet=tiet, mo_ta=mo_ta,
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

    def sua_vp_ca_nhan(self, vp_id: int, loai_vi_pham_id: int = None,
                       so_diem: float = None, ngay_xay_ra=None,
                       tiet: int = None, mo_ta: str = None) -> ServiceResult:
        try:
            vp = self.hs_vp_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy vi phạm.")
            if loai_vi_pham_id is not None: vp.loai_vi_pham_id = loai_vi_pham_id
            if so_diem is not None:         vp.so_diem = so_diem
            if tiet is not None:            vp.tiet = tiet
            if mo_ta is not None:           vp.mo_ta = mo_ta
            if ngay_xay_ra is not None:
                if isinstance(ngay_xay_ra, str):
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                        try:
                            vp.ngay_xay_ra = datetime.strptime(ngay_xay_ra, fmt).date()
                            break
                        except ValueError:
                            continue
                else:
                    vp.ngay_xay_ra = ngay_xay_ra
            self._commit()
            return ServiceResult(ok=True, error="Cập nhật thành công.")
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
                        so_diem: float = 0, tiet: int = None,
                        mo_ta: str = "", nguoi_ghi_nhan: str = "") -> ServiceResult:
        try:
            thu = ngay_xay_ra.weekday() + 2
            if thu not in range(2, 7):
                return ServiceResult(ok=False, error="Chỉ nhập từ Thứ 2 đến Thứ 6.")
            lvp = self.loai_vp_repo.get_by_id(loai_vi_pham_id)
            if not lvp:
                return ServiceResult(ok=False, error="Không tìm thấy loại vi phạm.")

            vp = self.tap_the_repo.create(
                lop_hoc_id=lop_hoc_id,
                loai_vi_pham_id=loai_vi_pham_id,
                nam_hoc_id=nam_hoc_id,
                tuan=tuan, thu=thu,
                so_diem=so_diem,
                ngay_xay_ra=ngay_xay_ra,
                tiet=tiet, mo_ta=mo_ta,
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

    def sua_vp_tap_the(self, vp_id: int, loai_vi_pham_id: int = None,
                       so_diem: float = None, ngay_xay_ra=None,
                       tiet: int = None, mo_ta: str = None) -> ServiceResult:
        try:
            vp = self.tap_the_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy vi phạm.")
            if loai_vi_pham_id is not None: vp.loai_vi_pham_id = loai_vi_pham_id
            if so_diem is not None:         vp.so_diem = so_diem
            if tiet is not None:            vp.tiet = tiet
            if mo_ta is not None:           vp.mo_ta = mo_ta
            if ngay_xay_ra is not None:
                if isinstance(ngay_xay_ra, str):
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                        try:
                            vp.ngay_xay_ra = datetime.strptime(ngay_xay_ra, fmt).date()
                            break
                        except ValueError:
                            continue
                else:
                    vp.ngay_xay_ra = ngay_xay_ra
            self._commit()
            return ServiceResult(ok=True, error="Cập nhật thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ ĐIỂM TẬP THỂ TUẦN ════════════════════════════════════

    def lay_diem_tuan(self, nam_hoc_id: int, tuan: int) -> ServiceResult:
        try:
            from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe
            
            ds_lop = self.lay_ds_lop(nam_hoc_id)
            so_vp = self.count_active_violations()
            so_ngay = self._get_so_ngay_trong_tuan()
            result = []
            
            print(f"🔍 lay_diem_tuan: nam_hoc={nam_hoc_id}, tuan={tuan}, so_lop={len(ds_lop)}")
            
            for lop in ds_lop:
                # Tính điểm đội
                diem_doi = self.doi_ngay_repo.get_trung_binh_tuan(
                    nam_hoc_id, tuan, lop.id, so_vp, so_ngay
                )
                
                # ⭐ Tìm bản ghi trong diem_tap_the
                record = self.session.query(DiemTapThe).filter(
                    DiemTapThe.nam_hoc_id == nam_hoc_id,
                    DiemTapThe.tuan == tuan,
                    DiemTapThe.lop_hoc_id == lop.id
                ).first()
                
                # ⭐ LOG để debug
                if record:
                    print(f"   Lớp {lop.id}: tìm thấy record ID={record.id}, diem_hoc_tap={record.diem_hoc_tap}")
                else:
                    print(f"   Lớp {lop.id}: KHÔNG TÌM THẤY record -> tạo mới")
                    # ⭐ Tạo mới nếu chưa có
                    record = DiemTapThe(
                        nam_hoc_id=nam_hoc_id,
                        tuan=tuan,
                        lop_hoc_id=lop.id,
                        diem_hoc_tap=0,
                        diem_doi=diem_doi,
                        ghi_chu="",
                        nguoi_nhap="Hệ thống",
                        da_khoa=False
                    )
                    self.session.add(record)
                    self.session.flush()
                
                diem_ht = record.diem_hoc_tap if record else 0
                ghi_chu = record.ghi_chu if record else ""
                tb = round(((diem_ht * 2) + diem_doi) / 3, 3)
                
                result.append({
                    "lop_hoc_id": lop.id,
                    "ten_lop": lop.ten_lop,
                    "khoi": lop.khoi,
                    "diem_doi": round(diem_doi, 3),
                    "diem_hoc_tap": diem_ht,
                    "tong_diem": round(diem_doi + diem_ht, 3),
                    "trung_binh": tb,
                    "da_khoa": record.da_khoa if record else False,
                    "ghi_chu": ghi_chu,
                })
            
            # ⭐ COMMIT để lưu các bản ghi mới tạo
            self._commit()
            
            print(f"✅ lay_diem_tuan: trả về {len(result)} lớp")
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi lay_diem_tuan: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    def luu_diem_hoc_tap(self, nam_hoc_id: int, tuan: int,
                            data: list, nguoi_nhap: str = "") -> ServiceResult:
        try:
            from datetime import datetime, date as date_type
            from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe

            print(f"📥 ===== LUU DIEM HOC TAP =====")
            print(f"   nam_hoc_id: {nam_hoc_id}, tuan: {tuan}, so_lop: {len(data)}")

            for item in data:
                lop_hoc_id   = item.get("lop_hoc_id")
                diem_hoc_tap = item.get("diem_hoc_tap", 0)
                diem_doi     = item.get("diem_doi", 0)
                ghi_chu      = item.get("ghi_chu", "")

                print(f"   📌 Lớp {lop_hoc_id}: diem_hoc_tap={diem_hoc_tap}")

                # ⭐ Tìm bản ghi trong bảng diem_tap_the
                record = self.session.query(DiemTapThe).filter(
                    DiemTapThe.nam_hoc_id == nam_hoc_id,
                    DiemTapThe.tuan == tuan,
                    DiemTapThe.lop_hoc_id == lop_hoc_id
                ).first()

                if record:
                    record.diem_hoc_tap = float(diem_hoc_tap)
                    record.diem_doi = float(diem_doi)
                    record.ghi_chu = ghi_chu
                    record.nguoi_nhap = nguoi_nhap
                    print(f"      ✅ Cập nhật diem_tap_the ID={record.id}: diem_hoc_tap={record.diem_hoc_tap}")
                else:
                    # ⭐ Nếu chưa có, tạo mới
                    new_record = DiemTapThe(
                        nam_hoc_id=nam_hoc_id,
                        tuan=tuan,
                        lop_hoc_id=lop_hoc_id,
                        diem_hoc_tap=float(diem_hoc_tap),
                        diem_doi=float(diem_doi),
                        ghi_chu=ghi_chu,
                        nguoi_nhap=nguoi_nhap,
                    )
                    self.session.add(new_record)
                    self.session.flush()
                    print(f"      ✅ Tạo mới diem_tap_the ID={new_record.id}: diem_hoc_tap={new_record.diem_hoc_tap}")

                # ⭐ Cập nhật vào diem_doi_ngay (để tính điểm đội)
                existing = self.session.query(DiemDoiNgay).filter(
                    DiemDoiNgay.nam_hoc_id == nam_hoc_id,
                    DiemDoiNgay.lop_hoc_id == lop_hoc_id,
                    DiemDoiNgay.tuan == tuan,
                    DiemDoiNgay.thu == 1
                ).first()

                if existing:
                    existing.diem_thay_doi = float(diem_hoc_tap)
                    print(f"      ✅ Cập nhật diem_doi_ngay: diem_thay_doi={existing.diem_thay_doi}")
                else:
                    new_record = DiemDoiNgay(
                        nam_hoc_id=nam_hoc_id,
                        lop_hoc_id=lop_hoc_id,
                        tuan=tuan,
                        thu=1,
                        diem_thay_doi=float(diem_hoc_tap),
                        so_luong_vi_pham=0,
                        ngay=datetime.now().date()
                    )
                    self.session.add(new_record)
                    print(f"      ✅ Tạo mới diem_doi_ngay: diem_thay_doi={diem_hoc_tap}")

            self._commit()
            print(f"✅ Lưu thành công {len(data)} lớp!")
            return ServiceResult(ok=True, data=data, error="Lưu thành công.")

        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi luu_diem_hoc_tap: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ══ BÁO CÁO ══════════════════════════════════════════════

    def bao_cao_xep_hang_tuan(self, nam_hoc_id: int, tuan: int) -> ServiceResult:
        try:
            r = self.lay_diem_tuan(nam_hoc_id, tuan)
            if not r.ok: return r
            data = sorted(r.data, key=lambda x: x["trung_binh"], reverse=True)
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
                    "ho_ten": hs.ho_ten,
                    "tong_diem": tong,
                    "so_vi_pham": len([v for v in ds_vp if v.so_diem < 0]),
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

    def _get_diem_tuan_lop(self, lop_hoc_id: int, nam_hoc_id: int,
                            tuan: int, so_tieu_chi: int) -> float:
        try:
            record = self.tap_the_diem_repo.get_by_nam_hoc_tuan_lop(
                nam_hoc_id, tuan, lop_hoc_id
            )
            if record:
                diem_ht = record.diem_hoc_tap or 0
                diem_doi = record.diem_doi or 0
                return round(((diem_ht * 2) + diem_doi) / 3, 3)
            return 0.0
        except Exception:
            return 0.0
    
    def _get_so_ngay_trong_tuan(self) -> int:
        """Lấy số ngày trong tuần từ cấu hình DB"""
        try:
            from modules.thi_dua_hoc_sinh.models.thi_dua_cau_hinh import ThiDuaCauHinh
            record = self.session.query(ThiDuaCauHinh).filter(
                ThiDuaCauHinh.key == 'so_ngay_trong_tuan'
            ).first()
            return int(record.value) if record else 5
        except:
            return 5  # fallback mặc định

    # ════════════════════════════════════════════════════════════
    # ══ QUẢN LÝ THÁNG ══════════════════════════════════════════
    # ════════════════════════════════════════════════════════════

    def _init_thang_repo(self):
        """Khởi tạo repository cho tháng"""
        try:
            from modules.thi_dua_hoc_sinh.repository.thang_thi_dua_repository import ThangThiDuaRepository
            self.thang_repo = ThangThiDuaRepository(self.session)
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo thang_repo: {e}")
            self.thang_repo = None

    def lay_ds_thang(self, nam_hoc_id: int = None) -> ServiceResult:
        """Lấy danh sách tháng"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            data = self.thang_repo.get_all(nam_hoc_id)
            result = []
            for item in data:
                try:
                    tuan_list = json.loads(item.tuan_list) if item.tuan_list else []
                except:
                    tuan_list = []
                ten_nam_hoc = None
                if item.nam_hoc_id:
                    nh = self.session.query(NamHoc).filter(NamHoc.id == item.nam_hoc_id).first()
                    if nh:
                        ten_nam_hoc = nh.ten_nam_hoc
                result.append({
                    "id": item.id,
                    "ten_thang": item.ten_thang,
                    "nam_hoc_id": item.nam_hoc_id,
                    "tuan_list": tuan_list,
                    "so_tuan": item.so_tuan or len(tuan_list),
                    "is_active": item.is_active if item.is_active is not None else True,
                    "ten_nam_hoc": ten_nam_hoc,
                    "created_at": item.created_at.strftime("%d/%m/%Y %H:%M") if item.created_at else "",
                })
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def tinh_diem_trung_binh_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int) -> float:
        """Tính điểm trung bình của một lớp trong một tuần"""
        so_tieu_chi = self.count_active_violations()
        diem_doi = self.doi_ngay_repo.get_trung_binh_tuan(
            nam_hoc_id, tuan, lop_hoc_id, so_tieu_chi
        )
        record = self.tap_the_diem_repo.get_by_nam_hoc_tuan_lop(
            nam_hoc_id, tuan, lop_hoc_id
        )
        diem_ht = record.diem_hoc_tap if record else 0
        return round(((diem_ht * 2) + diem_doi) / 3, 3)

    def tao_thang_va_luu_diem(self, ten_thang: str, nam_hoc_id: int, 
                               tuan_list: list, is_active: bool = True) -> ServiceResult:
        """Tạo tháng mới và lưu điểm chi tiết"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            # Tạo tháng
            thang = self.thang_repo.create(ten_thang, nam_hoc_id, tuan_list, is_active)
            self._commit()

            # Lấy danh sách lớp
            ds_lop = self.lay_ds_lop(nam_hoc_id)

            # Tính và lưu điểm cho từng lớp, từng tuần
            for lop in ds_lop:
                for tuan in tuan_list:
                    diem_tb_tuan = self.tinh_diem_trung_binh_tuan(nam_hoc_id, tuan, lop.id)
                    self.thang_repo.save_diem_chi_tiet(
                        thang_id=thang.id,
                        tuan=tuan,
                        lop_hoc_id=lop.id,
                        diem_trung_binh_tuan=diem_tb_tuan
                    )
            self._commit()
            return ServiceResult(ok=True, data=thang, error="Tạo tháng thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_thang_va_cap_nhat_diem(self, thang_id: int, ten_thang: str = None, 
                                    tuan_list: list = None, is_active: bool = None) -> ServiceResult:
        """Sửa tháng và cập nhật lại điểm"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            thang = self.thang_repo.get_by_id(thang_id)
            if not thang:
                return ServiceResult(ok=False, error="Không tìm thấy tháng.")

            update_data = {}
            if ten_thang is not None:
                update_data["ten_thang"] = ten_thang
            if is_active is not None:
                update_data["is_active"] = is_active

            # Nếu thay đổi danh sách tuần, tính lại điểm
            if tuan_list is not None:
                update_data["tuan_list"] = tuan_list
                # Xóa điểm cũ
                from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
                self.session.query(ThangDiemChiTiet).filter(
                    ThangDiemChiTiet.thang_id == thang_id
                ).delete()
                self._commit()

                # Tính lại điểm mới
                ds_lop = self.lay_ds_lop(thang.nam_hoc_id)
                for lop in ds_lop:
                    for tuan in tuan_list:
                        diem_tb_tuan = self.tinh_diem_trung_binh_tuan(
                            thang.nam_hoc_id, tuan, lop.id
                        )
                        self.thang_repo.save_diem_chi_tiet(
                            thang_id=thang_id,
                            tuan=tuan,
                            lop_hoc_id=lop.id,
                            diem_trung_binh_tuan=diem_tb_tuan
                        )

            if update_data:
                self.thang_repo.update(thang_id, **update_data)
            self._commit()
            return ServiceResult(ok=True, data=thang, error="Cập nhật tháng thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_thang(self, thang_id: int) -> ServiceResult:
        """Xóa tháng và điểm chi tiết"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
            self.session.query(ThangDiemChiTiet).filter(
                ThangDiemChiTiet.thang_id == thang_id
            ).delete()
            self.thang_repo.delete(thang_id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa tháng thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # modules/thi_dua_hoc_sinh/service.py

    def get_bao_cao_thang(self, thang_id: int) -> ServiceResult:
        """Lấy báo cáo tháng - Xếp hạng kiểu cạnh tranh"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            thang = self.thang_repo.get_by_id(thang_id)
            if not thang:
                return ServiceResult(ok=False, error="Không tìm thấy tháng.")

            tuan_list = json.loads(thang.tuan_list) if thang.tuan_list else []
            if not tuan_list:
                return ServiceResult(ok=False, error="Chưa có tuần nào được chọn.")

            chi_tiet_list = self.thang_repo.get_diem_chi_tiet(thang_id)

            # Gom dữ liệu theo lớp
            result = {}
            for item in chi_tiet_list:
                lop_id = item.lop_hoc_id
                if lop_id not in result:
                    lop = self.session.query(LopHoc).filter(LopHoc.id == lop_id).first()
                    result[lop_id] = {
                        "lop_hoc_id": lop_id,
                        "ten_lop": lop.ten_lop if lop else "",
                        "khoi": lop.khoi if lop else 0,
                        "cac_tuan": {},
                        "tong_diem": 0,
                    }
                result[lop_id]["cac_tuan"][item.tuan] = item.diem_trung_binh_tuan

            # Tính trung bình tháng cho từng lớp
            final_result = []
            for lop_id, data in result.items():
                cac_tuan = data["cac_tuan"]
                tong_diem = sum(cac_tuan.values())
                tb_thang = round(tong_diem / len(tuan_list), 3) if tuan_list else 0
                final_result.append({
                    "lop_hoc_id": lop_id,
                    "ten_lop": data["ten_lop"],
                    "khoi": data["khoi"],
                    "cac_tuan": cac_tuan,
                    "tong_diem": tong_diem,
                    "trung_binh": tb_thang,
                })

            # ⭐ Sắp xếp theo điểm trung bình giảm dần
            final_result.sort(key=lambda x: x["trung_binh"], reverse=True)

            # ⭐ Xếp hạng kiểu cạnh tranh (1, 1, 3, 4, 4, 6...)
            rank = 1
            for i, item in enumerate(final_result):
                if i == 0:
                    item["xep_hang"] = rank
                else:
                    # Nếu điểm bằng với lớp trước, giữ nguyên hạng
                    if item["trung_binh"] == final_result[i-1]["trung_binh"]:
                        item["xep_hang"] = rank
                    else:
                        # Nếu khác điểm, hạng = vị trí + 1
                        rank = i + 1
                        item["xep_hang"] = rank

            return ServiceResult(ok=True, data={
                "thang": thang.ten_thang,
                "tuan_list": tuan_list,
                "data": final_result,
            })
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    # modules/thi_dua_hoc_sinh/service.py

    def cap_nhat_diem_cho_thang(self, thang_id: int) -> ServiceResult:
        """Cập nhật lại điểm cho một tháng cụ thể"""
        if not self.thang_repo:
            self._init_thang_repo()
            if not self.thang_repo:
                return ServiceResult(ok=False, error="Chưa có repository tháng.")
        try:
            thang = self.thang_repo.get_by_id(thang_id)
            if not thang:
                return ServiceResult(ok=False, error="Không tìm thấy tháng.")

            tuan_list = json.loads(thang.tuan_list) if thang.tuan_list else []
            if not tuan_list:
                return ServiceResult(ok=False, error="Tháng chưa có tuần nào.")

            # Xóa điểm cũ
            from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
            self.session.query(ThangDiemChiTiet).filter(
                ThangDiemChiTiet.thang_id == thang_id
            ).delete()
            self._commit()

            # Tính lại điểm mới
            ds_lop = self.lay_ds_lop(thang.nam_hoc_id)
            for lop in ds_lop:
                for tuan in tuan_list:
                    diem_tb_tuan = self.tinh_diem_trung_binh_tuan(
                        thang.nam_hoc_id, tuan, lop.id
                    )
                    self.thang_repo.save_diem_chi_tiet(
                        thang_id=thang_id,
                        tuan=tuan,
                        lop_hoc_id=lop.id,
                        diem_trung_binh_tuan=diem_tb_tuan
                    )
            self._commit()
            return ServiceResult(ok=True, error="Cập nhật điểm tháng thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ══ QUẢN LÝ HỌC KỲ ══════════════════════════════════════════

    # modules/thi_dua_hoc_sinh/service.py

    # ══ QUẢN LÝ HỌC KỲ ══════════════════════════════════════════

    def _init_hoc_ky_repo(self):
        """Khởi tạo repository cho học kỳ"""
        try:
            from modules.thi_dua_hoc_sinh.repository.hoc_ky_repository import HocKyRepository
            self.hoc_ky_repo = HocKyRepository(self.session)
            print("✅ Đã khởi tạo hoc_ky_repo")
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo hoc_ky_repo: {e}")
            self.hoc_ky_repo = None

    def lay_ds_hoc_ky(self, nam_hoc_id: int = None) -> ServiceResult:
        """Lấy danh sách học kỳ"""
        print(f"🔍 lay_ds_hoc_ky: nam_hoc_id={nam_hoc_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            print("⚠️ hoc_ky_repo chưa được khởi tạo, đang init...")
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                print("❌ Không thể khởi tạo hoc_ky_repo")
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            data = self.hoc_ky_repo.get_all(nam_hoc_id)
            print(f"✅ Lấy được {len(data)} học kỳ")
            
            result = []
            for item in data:
                try:
                    thang_list = json.loads(item.thang_list) if item.thang_list else []
                except:
                    thang_list = []
                ten_nam_hoc = None
                if item.nam_hoc_id:
                    nh = self.session.query(NamHoc).filter(NamHoc.id == item.nam_hoc_id).first()
                    if nh:
                        ten_nam_hoc = nh.ten_nam_hoc
                result.append({
                    "id": item.id,
                    "ten_hoc_ky": item.ten_hoc_ky,
                    "nam_hoc_id": item.nam_hoc_id,
                    "thang_list": thang_list,
                    "so_thang": item.so_thang or len(thang_list),
                    "is_active": item.is_active if item.is_active is not None else True,
                    "ten_nam_hoc": ten_nam_hoc,
                    "created_at": item.created_at.strftime("%d/%m/%Y %H:%M") if item.created_at else "",
                })
            print(f"✅ Trả về {len(result)} học kỳ")
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            print(f"❌ Lỗi lay_ds_hoc_ky: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    def tao_hoc_ky_va_luu_diem(self, ten_hoc_ky: str, nam_hoc_id: int, 
                            thang_list: list, is_active: bool = True) -> ServiceResult:
        """Tạo học kỳ mới và lưu điểm chi tiết từ các tháng"""
        print(f"🔍 tao_hoc_ky_va_luu_diem: {ten_hoc_ky}, nam_hoc_id={nam_hoc_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            # 1. Tạo học kỳ
            hoc_ky = self.hoc_ky_repo.create(ten_hoc_ky, nam_hoc_id, thang_list, is_active)
            self._commit()
            print(f"✅ Đã tạo học kỳ ID: {hoc_ky.id}")

            # 2. Lấy danh sách lớp
            ds_lop = self.lay_ds_lop(nam_hoc_id)
            print(f"📊 Có {len(ds_lop)} lớp")

            # 3. Lấy điểm trung bình tháng của từng tháng
            count = 0
            for lop in ds_lop:
                for thang_id in thang_list:
                    diem_tb_thang = self._get_diem_trung_binh_thang(thang_id, lop.id)
                    self.hoc_ky_repo.save_diem_chi_tiet(
                        hoc_ky_id=hoc_ky.id,
                        thang_id=thang_id,
                        lop_hoc_id=lop.id,
                        diem_trung_binh_thang=diem_tb_thang
                    )
                    count += 1
            self._commit()
            print(f"✅ Đã lưu {count} bản ghi điểm chi tiết")
            
            return ServiceResult(ok=True, data=hoc_ky, error="Tạo học kỳ thành công.")
        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi tao_hoc_ky_va_luu_diem: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    def _get_diem_trung_binh_thang(self, thang_id: int, lop_hoc_id: int) -> float:
        """Lấy điểm trung bình của một tháng cho một lớp"""
        from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
        try:
            result = self.session.query(ThangDiemChiTiet).filter(
                ThangDiemChiTiet.thang_id == thang_id,
                ThangDiemChiTiet.lop_hoc_id == lop_hoc_id
            ).first()
            return result.diem_trung_binh_tuan if result else 0
        except Exception as e:
            print(f"⚠️ Lỗi lấy điểm tháng {thang_id} cho lớp {lop_hoc_id}: {e}")
            return 0

    def sua_hoc_ky(self, hoc_ky_id: int, ten_hoc_ky: str = None, 
                thang_list: list = None, is_active: bool = None) -> ServiceResult:
        """Sửa học kỳ"""
        print(f"🔍 sua_hoc_ky: hoc_ky_id={hoc_ky_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            hoc_ky = self.hoc_ky_repo.get_by_id(hoc_ky_id)
            if not hoc_ky:
                return ServiceResult(ok=False, error="Không tìm thấy học kỳ.")

            update_data = {}
            if ten_hoc_ky is not None:
                update_data["ten_hoc_ky"] = ten_hoc_ky
            if is_active is not None:
                update_data["is_active"] = is_active

            # Nếu thay đổi danh sách tháng, tính lại điểm
            if thang_list is not None:
                update_data["thang_list"] = thang_list
                # Xóa điểm cũ
                from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
                self.session.query(ThiDuaHocKyDiemChiTiet).filter(
                    ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky_id
                ).delete()
                self._commit()

                # Tính lại điểm mới
                ds_lop = self.lay_ds_lop(hoc_ky.nam_hoc_id)
                for lop in ds_lop:
                    for thang_id in thang_list:
                        diem_tb_thang = self._get_diem_trung_binh_thang(thang_id, lop.id)
                        self.hoc_ky_repo.save_diem_chi_tiet(
                            hoc_ky_id=hoc_ky_id,
                            thang_id=thang_id,
                            lop_hoc_id=lop.id,
                            diem_trung_binh_thang=diem_tb_thang
                        )

            if update_data:
                self.hoc_ky_repo.update(hoc_ky_id, **update_data)
            self._commit()
            return ServiceResult(ok=True, data=hoc_ky, error="Cập nhật học kỳ thành công.")
        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi sua_hoc_ky: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    def xoa_hoc_ky(self, hoc_ky_id: int) -> ServiceResult:
        """Xóa học kỳ và điểm chi tiết"""
        print(f"🔍 xoa_hoc_ky: hoc_ky_id={hoc_ky_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
            self.session.query(ThiDuaHocKyDiemChiTiet).filter(
                ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky_id
            ).delete()
            self.hoc_ky_repo.delete(hoc_ky_id)
            self._commit()
            return ServiceResult(ok=True, error="Xóa học kỳ thành công.")
        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi xoa_hoc_ky: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    # modules/thi_dua_hoc_sinh/service.py

    def cap_nhat_diem_cho_hoc_ky(self, hoc_ky_id: int) -> ServiceResult:
        """Cập nhật lại điểm cho một học kỳ cụ thể"""
        print(f"🔄 cap_nhat_diem_cho_hoc_ky: hoc_ky_id={hoc_ky_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            # 1. Lấy thông tin học kỳ
            hoc_ky = self.hoc_ky_repo.get_by_id(hoc_ky_id)
            if not hoc_ky:
                return ServiceResult(ok=False, error="Không tìm thấy học kỳ.")
            
            # 2. Lấy danh sách tháng từ học kỳ
            thang_list = json.loads(hoc_ky.thang_list) if hoc_ky.thang_list else []
            if not thang_list:
                return ServiceResult(ok=False, error="Học kỳ chưa có tháng nào.")
            
            # 3. Xóa điểm cũ
            from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
            deleted = self.session.query(ThiDuaHocKyDiemChiTiet).filter(
                ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky_id
            ).delete()
            print(f"🗑️ Đã xóa {deleted} bản ghi cũ của học kỳ {hoc_ky_id}")
            self._commit()
            
            # 4. Lấy danh sách lớp
            ds_lop = self.lay_ds_lop(hoc_ky.nam_hoc_id)
            print(f"📊 Có {len(ds_lop)} lớp cần cập nhật điểm")
            
            # 5. Tính và lưu lại điểm mới
            count = 0
            for lop in ds_lop:
                for thang_id in thang_list:
                    diem_tb_thang = self._get_diem_trung_binh_thang(thang_id, lop.id)
                    self.hoc_ky_repo.save_diem_chi_tiet(
                        hoc_ky_id=hoc_ky_id,
                        thang_id=thang_id,
                        lop_hoc_id=lop.id,
                        diem_trung_binh_thang=diem_tb_thang
                    )
                    count += 1
            
            self._commit()
            print(f"✅ Đã cập nhật {count} bản ghi điểm cho học kỳ {hoc_ky_id}")
            
            return ServiceResult(ok=True, error=f"Cập nhật điểm học kỳ thành công ({count} bản ghi).")
        except Exception as e:
            self._rollback()
            print(f"❌ Lỗi cap_nhat_diem_cho_hoc_ky: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    def get_bao_cao_hoc_ky(self, hoc_ky_id: int) -> ServiceResult:
        """Lấy báo cáo học kỳ"""
        print(f"🔍 get_bao_cao_hoc_ky: hoc_ky_id={hoc_ky_id}")
        
        if not hasattr(self, 'hoc_ky_repo') or not self.hoc_ky_repo:
            self._init_hoc_ky_repo()
            if not self.hoc_ky_repo:
                return ServiceResult(ok=False, error="Chưa có repository học kỳ.")
        
        try:
            hoc_ky = self.hoc_ky_repo.get_by_id(hoc_ky_id)
            if not hoc_ky:
                return ServiceResult(ok=False, error="Không tìm thấy học kỳ.")

            thang_list = json.loads(hoc_ky.thang_list) if hoc_ky.thang_list else []
            if not thang_list:
                return ServiceResult(ok=False, error="Chưa có tháng nào được chọn.")

            chi_tiet_list = self.hoc_ky_repo.get_diem_chi_tiet(hoc_ky_id)
            print(f"✅ Lấy được {len(chi_tiet_list)} bản ghi điểm chi tiết")
            
            # Gom dữ liệu theo lớp
            result = {}
            for item in chi_tiet_list:
                lop_id = item.lop_hoc_id
                if lop_id not in result:
                    lop = self.session.query(LopHoc).filter(LopHoc.id == lop_id).first()
                    result[lop_id] = {
                        "lop_hoc_id": lop_id,
                        "ten_lop": lop.ten_lop if lop else "",
                        "khoi": lop.khoi if lop else 0,
                        "cac_thang": {},
                        "tong_diem": 0,
                    }
                # Lấy tên tháng từ bảng thang_thi_dua
                from modules.thi_dua_hoc_sinh.models.thang_thi_dua import ThangThiDua
                thang = self.session.query(ThangThiDua).filter(ThangThiDua.id == item.thang_id).first()
                ten_thang = thang.ten_thang if thang else f"Tháng {item.thang_id}"
                result[lop_id]["cac_thang"][ten_thang] = item.diem_trung_binh_thang

            # Tính trung bình học kỳ
            final_result = []
            for lop_id, data in result.items():
                cac_thang = data["cac_thang"]
                tong_diem = sum(cac_thang.values())
                tb_hoc_ky = round(tong_diem / len(thang_list), 3) if thang_list else 0
                final_result.append({
                    "lop_hoc_id": lop_id,
                    "ten_lop": data["ten_lop"],
                    "khoi": data["khoi"],
                    "cac_thang": cac_thang,
                    "tong_diem": tong_diem,
                    "trung_binh": tb_hoc_ky,
                })

            # Sắp xếp và xếp hạng
            final_result.sort(key=lambda x: x["trung_binh"], reverse=True)
            rank = 1
            for i, item in enumerate(final_result):
                if i == 0:
                    item["xep_hang"] = rank
                else:
                    if item["trung_binh"] == final_result[i-1]["trung_binh"]:
                        item["xep_hang"] = rank
                    else:
                        rank = i + 1
                        item["xep_hang"] = rank

            # Lấy danh sách tên tháng
            from modules.thi_dua_hoc_sinh.models.thang_thi_dua import ThangThiDua
            thang_ten_list = []
            for t in thang_list:
                thang = self.session.query(ThangThiDua).filter(ThangThiDua.id == t).first()
                thang_ten_list.append(thang.ten_thang if thang else f"Tháng {t}")

            return ServiceResult(ok=True, data={
                "hoc_ky": hoc_ky.ten_hoc_ky,
                "thang_list": thang_ten_list,
                "data": final_result,
            })
        except Exception as e:
            print(f"❌ Lỗi get_bao_cao_hoc_ky: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
        finally:
            self.session.close()

    # ══ QUẢN LÝ NĂM HỌC ══════════════════════════════════════════

    def get_bao_cao_nam_hoc(self, hoc_ky_list: list) -> ServiceResult:
        """Lấy báo cáo năm học từ danh sách các học kỳ"""
        try:
            if not hoc_ky_list or len(hoc_ky_list) == 0:
                return ServiceResult(ok=False, error="Chưa chọn học kỳ nào.")
            
            # ⭐ Lấy thông tin các học kỳ
            hoc_ky_info = []
            for hk_id in hoc_ky_list:
                hk = self.hoc_ky_repo.get_by_id(hk_id) if self.hoc_ky_repo else None
                if hk:
                    hoc_ky_info.append({
                        "id": hk_id,
                        "ten": hk.ten_hoc_ky
                    })
                else:
                    hoc_ky_info.append({
                        "id": hk_id,
                        "ten": f"Học kỳ {hk_id}"
                    })
            
            # Lấy danh sách lớp
            ds_lop = self.lay_ds_lop()
            if not ds_lop:
                return ServiceResult(ok=False, error="Không có lớp học.")
            
            # ⭐ GOM dữ liệu theo lớp
            result = {}
            for lop in ds_lop:
                result[lop.id] = {
                    "lop_hoc_id": lop.id,
                    "ten_lop": lop.ten_lop,
                    "khoi": lop.khoi,
                    "cac_hoc_ky": {},
                    "tong_diem_hoc_ky": 0,  # ⭐ Đổi tên cho rõ
                    "so_hoc_ky": 0,
                }
            
            # ⭐ Lấy điểm TRUNG BÌNH HỌC KỲ cho từng lớp
            from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
            
            for hk_id in hoc_ky_list:
                # ⭐ Lấy tất cả điểm chi tiết của học kỳ này
                chi_tiet_list = self.session.query(ThiDuaHocKyDiemChiTiet).filter(
                    ThiDuaHocKyDiemChiTiet.hoc_ky_id == hk_id
                ).all()
                
                # ⭐ Gom điểm theo lớp
                diem_theo_lop = {}
                for item in chi_tiet_list:
                    lop_id = item.lop_hoc_id
                    if lop_id not in diem_theo_lop:
                        diem_theo_lop[lop_id] = []
                    diem_theo_lop[lop_id].append(item.diem_trung_binh_thang)
                
                # ⭐ Tính điểm trung bình học kỳ cho từng lớp
                for lop_id, diem_list in diem_theo_lop.items():
                    if lop_id in result:
                        # ⭐ Tính trung bình cộng của các tháng
                        tb_hoc_ky = round(sum(diem_list) / len(diem_list), 3) if diem_list else 0
                        result[lop_id]["cac_hoc_ky"][hk_id] = tb_hoc_ky
                        result[lop_id]["tong_diem_hoc_ky"] += tb_hoc_ky
                        result[lop_id]["so_hoc_ky"] += 1
            
            # ⭐ Tạo dữ liệu hiển thị
            final_result = []
            for lop_id, data in result.items():
                # Tạo dict với key là TÊN học kỳ
                cac_hoc_ky_display = {}
                for hk in hoc_ky_info:
                    diem = data["cac_hoc_ky"].get(hk["id"], 0)
                    cac_hoc_ky_display[hk["ten"]] = diem
                
                tong_diem = data["tong_diem_hoc_ky"]
                so_hoc_ky = data["so_hoc_ky"]
                
                # ⭐ Trung bình năm = Tổng điểm các học kỳ / Số học kỳ
                if so_hoc_ky == 0:
                    tb_nam = 0
                else:
                    tb_nam = round(tong_diem / so_hoc_ky, 3)
                
                final_result.append({
                    "lop_hoc_id": lop_id,
                    "ten_lop": data["ten_lop"],
                    "khoi": data["khoi"],
                    "cac_hoc_ky": cac_hoc_ky_display,
                    "tong_diem": tong_diem,
                    "trung_binh": tb_nam,
                })
            
            # Sắp xếp và xếp hạng
            final_result.sort(key=lambda x: x["trung_binh"], reverse=True)
            rank = 1
            for i, item in enumerate(final_result):
                if i == 0:
                    item["xep_hang"] = rank
                else:
                    if item["trung_binh"] == final_result[i-1]["trung_binh"]:
                        item["xep_hang"] = rank
                    else:
                        rank = i + 1
                        item["xep_hang"] = rank
            
            hoc_ky_names = [hk["ten"] for hk in hoc_ky_info]
            
            return ServiceResult(ok=True, data={
                "hoc_ky_list": hoc_ky_names,
                "data": final_result,
            })
        except Exception as e:
            print(f"❌ Lỗi get_bao_cao_nam_hoc: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))