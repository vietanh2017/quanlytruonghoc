# modules/phan_cong/service.py
"""
PhanCongService: logic nghiệp vụ module Phân công giảng dạy.
"""

from collections import defaultdict
from typing import Optional
from sqlalchemy.orm import Session

from modules.phan_cong.repository import PhanCongRepository
from shared.dto.result import ServiceResult
from core.db.models.phan_cong import PhanCongGiangDay
from core.db.models.giao_vien import GiaoVien
from core.db.models.nam_hoc import NamHoc
from core.db.models.hoc_ky import HocKy
from core.db.models.mon_hoc import MonHoc, PhanMon, MonHocKhoi  # ⭐ Đã sửa import
from core.db.models.lop_hoc import LopHoc


# ⭐ Số tiết chủ nhiệm theo quy định (Thông tư 28): 1 lớp chủ nhiệm = 4 tiết/tuần
# (Đồng bộ với TKBExportService.SO_TIET_CN ở modules/tkb/export_service.py)
SO_TIET_CN = 4


class PhanCongService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PhanCongRepository(session)

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()

    # ── Danh sách ─────────────────────────────────────────────

    def lay_ds(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_theo_hoc_ky(self, nam_hoc_id: int, hoc_ky_id: int) -> ServiceResult:
        try:
            data = self.repo.get_by_nam_hoc_hoc_ky(nam_hoc_id, hoc_ky_id)
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_phan_cong_theo_giao_vien(self, giao_vien_id, nam_hoc_id, hoc_ky_id):
        try:
            from sqlalchemy.orm import joinedload
            data = (
                self.session.query(PhanCongGiangDay)
                .options(
                    joinedload(PhanCongGiangDay.mon_hoc),
                    joinedload(PhanCongGiangDay.lop_hoc),
                )
                .filter(
                    PhanCongGiangDay.giao_vien_id == giao_vien_id,
                    PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                    PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
                )
                .all()
            )
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_phan_cong_tong_hop(self) -> ServiceResult:
        try:
            ds = self.repo.get_all()
            gv_dict = defaultdict(lambda: {"phan_cong": [], "tong_tiet": 0})

            for pc in ds:
                try:
                    gv_id = pc.giao_vien_id
                    mon_id = pc.mon_hoc_id
                    lop = pc.lop_hoc
                    
                    if not lop:
                        continue
                    
                    khoi = lop.khoi if lop else 6

                    # Lấy tên môn
                    mon_name = "?"
                    if pc.mon_hoc:
                        mon_name = pc.mon_hoc.ten_mon

                    # Lấy số tiết
                    so_tiet = 1
                    try:
                        so_tiet_mon = self.session.query(MonHocKhoi).filter(
                            MonHocKhoi.mon_hoc_id == mon_id,
                            MonHocKhoi.khoi == khoi,
                        ).first()
                        if so_tiet_mon:
                            so_tiet = so_tiet_mon.so_tiet
                    except:
                        pass

                    lop_name = lop.ten_lop if lop else "?"

                    gv_dict[gv_id]["tong_tiet"] += so_tiet

                    found = False
                    for item in gv_dict[gv_id]["phan_cong"]:
                        if item["mon_hoc"] == mon_name:
                            if lop_name not in item["lops"]:
                                item["lops"].append(lop_name)
                            found = True
                            break
                    if not found:
                        gv_dict[gv_id]["phan_cong"].append({
                            "mon_hoc": mon_name,
                            "lops": [lop_name],
                        })
                except Exception as e:
                    print(f"⚠️ Lỗi xử lý phân công ID={pc.id}: {e}")
                    continue

            # ⭐ Lấy danh sách lớp mà GV làm chủ nhiệm (từ module Giáo viên/Lớp học)
            # để cộng thêm tiết chủ nhiệm vào tổng số tiết.
            gvcn_map = defaultdict(list)  # {gv_id: [ten_lop, ...]}
            try:
                ds_lop = self.session.query(LopHoc).filter(
                    LopHoc.giao_vien_cn_id.isnot(None)
                ).all()
                for lop in ds_lop:
                    gvcn_map[lop.giao_vien_cn_id].append(lop.ten_lop)
            except Exception as e:
                print(f"⚠️ Lỗi lấy danh sách GVCN: {e}")

            result = []
            for gv_id, data in gv_dict.items():
                try:
                    gv = self.session.get(GiaoVien, gv_id)
                    ho_ten = gv.nguoi_dung.ho_ten if gv and gv.nguoi_dung else f"GV_{gv_id}"

                    lop_chu_nhiem = gvcn_map.get(gv_id, [])
                    tiet_day = data["tong_tiet"]
                    tiet_cn = len(lop_chu_nhiem) * SO_TIET_CN

                    result.append({
                        "giao_vien_id": gv_id,
                        "ho_ten": ho_ten,
                        "phan_cong": data["phan_cong"],
                        "tiet_day": tiet_day,
                        "lop_chu_nhiem": lop_chu_nhiem,
                        "tiet_cn": tiet_cn,
                        "tong_tiet": tiet_day + tiet_cn,
                    })
                except Exception as e:
                    print(f"⚠️ Lỗi xử lý giáo viên ID={gv_id}: {e}")
                    continue

            return ServiceResult(ok=True, data=result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ── Thêm ──────────────────────────────────────────────────

    def them(self, giao_vien_id: int, nam_hoc_id: int, hoc_ky_id: int,
            phan_cong_list: list[dict], clear_old: bool = False) -> ServiceResult:
        try:
            if clear_old:
                self.session.query(PhanCongGiangDay).filter(
                    PhanCongGiangDay.giao_vien_id == giao_vien_id,
                    PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                    PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
                ).delete()

            added = 0
            for pc in phan_cong_list:
                mon_hoc_id = pc["mon_hoc_id"]
                phan_mon_id = pc.get("phan_mon_id")  # ✅ Lấy phan_mon_id riêng

                # ✅ Chỉ resolve phan_mon nếu phan_mon_id được truyền vào rõ ràng
                if phan_mon_id:
                    phan_mon = self.session.query(PhanMon).filter(
                        PhanMon.id == phan_mon_id
                    ).first()
                    if phan_mon:
                        mon_hoc_id = phan_mon.mon_hoc_id

                exist = self.session.query(PhanCongGiangDay).filter(
                    PhanCongGiangDay.giao_vien_id == giao_vien_id,
                    PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                    PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
                    PhanCongGiangDay.mon_hoc_id == mon_hoc_id,
                    PhanCongGiangDay.lop_hoc_id == pc["lop_hoc_id"],
                ).first()

                if not exist:
                    self.session.add(PhanCongGiangDay(
                        giao_vien_id=giao_vien_id,
                        nam_hoc_id=nam_hoc_id,
                        hoc_ky_id=hoc_ky_id,
                        mon_hoc_id=mon_hoc_id,
                        lop_hoc_id=pc["lop_hoc_id"],
                    ))
                    added += 1

            self._commit()
            return ServiceResult(ok=True, error=f"Phân công thành công ({added} mục)")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ── Xóa ───────────────────────────────────────────────────

    def xoa(self, pc_id: int) -> ServiceResult:
        try:
            if not self.repo.delete(pc_id):
                return ServiceResult(ok=False, error="Không tìm thấy phân công.")
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa phân công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_phan_cong(self, giao_vien_id: int, nam_hoc_id: int, hoc_ky_id: int,
                      mon_hoc_id: int, lop_hoc_id: int) -> ServiceResult:
        try:
            pc = self.session.query(PhanCongGiangDay).filter(
                PhanCongGiangDay.giao_vien_id == giao_vien_id,
                PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
                PhanCongGiangDay.mon_hoc_id == mon_hoc_id,
                PhanCongGiangDay.lop_hoc_id == lop_hoc_id,
            ).first()

            if not pc:
                return ServiceResult(ok=False, error="Không tìm thấy phân công.")
            self.session.delete(pc)
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa phân công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_tat_ca_phan_cong(self, giao_vien_id: int,
                              nam_hoc_id: int, hoc_ky_id: int) -> ServiceResult:
        try:
            deleted = self.session.query(PhanCongGiangDay).filter(
                PhanCongGiangDay.giao_vien_id == giao_vien_id,
                PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
            ).delete()
            self._commit()
            return ServiceResult(ok=True, error=f"Đã xóa {deleted} phân công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ── Dữ liệu phụ ───────────────────────────────────────────

    def lay_ds_nam_hoc(self) -> list:
        return self.session.query(NamHoc).filter(NamHoc.active == True).all()

    def lay_ds_hoc_ky(self, nam_hoc_id: Optional[int] = None) -> list:
        q = self.session.query(HocKy).filter(HocKy.active == True)
        if nam_hoc_id:
            q = q.filter(HocKy.nam_hoc_id == nam_hoc_id)
        return q.all()

    def lay_ds_giao_vien(self) -> list:
        return self.session.query(GiaoVien).filter(GiaoVien.active == True).all()

    def lay_ds_mon_hoc(self) -> list:
        return self.session.query(MonHoc).filter(MonHoc.active == True).all()

    def lay_ds_lop_hoc(self) -> list:
        return self.session.query(LopHoc).filter(LopHoc.active == True).all()