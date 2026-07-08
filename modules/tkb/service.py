# modules/tkb/service.py
from sqlalchemy import text, not_
from sqlalchemy.orm import Session
from shared.dto.result import ServiceResult
from .models import TKBCauHinhNgay, TKBCauHinhTiet, TKBCauHinhMon, TKBRangBuocGV, ThoiKhoaBieu
import random
import logging

logger = logging.getLogger(__name__)


class TKBService:
    def __init__(self, session: Session):
        self.session = session

    # ══ CẤU HÌNH NGÀY ══════════════════════════════════════════

    def get_cau_hinh_ngay(self, nam_hoc_id: int) -> ServiceResult:
        try:
            data = self.session.query(TKBCauHinhNgay).filter(
                TKBCauHinhNgay.nam_hoc_id == nam_hoc_id
            ).order_by(TKBCauHinhNgay.thu).all()
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            logger.error(f"get_cau_hinh_ngay error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def save_cau_hinh_ngay(self, nam_hoc_id: int, items: list) -> ServiceResult:
        try:
            for item in items:
                existing = self.session.query(TKBCauHinhNgay).filter(
                    TKBCauHinhNgay.nam_hoc_id == nam_hoc_id,
                    TKBCauHinhNgay.thu == item['thu']
                ).first()
                if existing:
                    existing.co_buoi_sang = item['co_buoi_sang']
                    existing.co_buoi_chieu = item['co_buoi_chieu']
                else:
                    self.session.add(TKBCauHinhNgay(
                        nam_hoc_id=nam_hoc_id,
                        thu=item['thu'],
                        co_buoi_sang=item['co_buoi_sang'],
                        co_buoi_chieu=item['co_buoi_chieu'],
                    ))
            self.session.commit()
            return ServiceResult(ok=True, error="Lưu thành công")
        except Exception as e:
            self.session.rollback()
            logger.error(f"save_cau_hinh_ngay error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ CẤU HÌNH TIẾT ══════════════════════════════════════════

    def get_cau_hinh_tiet(self) -> ServiceResult:
        try:
            data = self.session.query(TKBCauHinhTiet).order_by(
                TKBCauHinhTiet.buoi.desc(), TKBCauHinhTiet.tiet_so
            ).all()
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            logger.error(f"get_cau_hinh_tiet error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def save_cau_hinh_tiet(self, items: list) -> ServiceResult:
        try:
            for item in items:
                existing = self.session.query(TKBCauHinhTiet).filter(
                    TKBCauHinhTiet.buoi == item['buoi'],
                    TKBCauHinhTiet.tiet_so == item['tiet_so']
                ).first()
                if existing:
                    existing.gio_bat_dau = item.get('gio_bat_dau')
                    existing.gio_ket_thuc = item.get('gio_ket_thuc')
                else:
                    self.session.add(TKBCauHinhTiet(
                        buoi=item['buoi'],
                        tiet_so=item['tiet_so'],
                        gio_bat_dau=item.get('gio_bat_dau'),
                        gio_ket_thuc=item.get('gio_ket_thuc'),
                    ))
            self.session.commit()
            return ServiceResult(ok=True, error="Lưu thành công")
        except Exception as e:
            self.session.rollback()
            logger.error(f"save_cau_hinh_tiet error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ CẤU HÌNH MÔN ══════════════════════════════════════════

    def get_cau_hinh_mon(self, nam_hoc_id: int) -> ServiceResult:
        try:
            from core.db.models.mon_hoc import MonHoc, MonHocKhoi

            ds_mon = self.session.query(MonHoc).filter(MonHoc.active == True).all()
            cau_hinh_list = self.session.query(TKBCauHinhMon).filter(
                TKBCauHinhMon.nam_hoc_id == nam_hoc_id
            ).all()
            cau_hinh_map = {c.mon_hoc_id: c for c in cau_hinh_list}

            result = []
            for mon in ds_mon:
                khoi_list = self.session.query(MonHocKhoi).filter(
                    MonHocKhoi.mon_hoc_id == mon.id
                ).order_by(MonHocKhoi.khoi).all()

                so_tiet_theo_khoi = {k.khoi: k.so_tiet for k in khoi_list}
                ch = cau_hinh_map.get(mon.id)

                result.append({
                    "mon_hoc_id": mon.id,
                    "ten_mon": mon.ten_mon,
                    "ma_mon": mon.ma_mon,
                    "so_tiet_theo_khoi": so_tiet_theo_khoi,
                    "chi_buoi_sang": ch.chi_buoi_sang if ch else False,
                    "chi_buoi_chieu": ch.chi_buoi_chieu if ch else False,
                    "khong_lien_tiet": ch.khong_lien_tiet if ch else False,
                    "so_tiet_toi_da_ngay": ch.so_tiet_toi_da_ngay if ch else 0,
                    "cho_phep_tiet_doi": ch.cho_phep_tiet_doi if ch else False,
                })

            return ServiceResult(ok=True, data=result)
        except Exception as e:
            logger.error(f"get_cau_hinh_mon error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def save_cau_hinh_mon(self, nam_hoc_id: int, items: list) -> ServiceResult:
        try:
            for item in items:
                existing = self.session.query(TKBCauHinhMon).filter(
                    TKBCauHinhMon.nam_hoc_id == nam_hoc_id,
                    TKBCauHinhMon.mon_hoc_id == item['mon_hoc_id']
                ).first()
                if existing:
                    existing.chi_buoi_sang = item.get('chi_buoi_sang', False)
                    existing.chi_buoi_chieu = item.get('chi_buoi_chieu', False)
                    existing.khong_lien_tiet = item.get('khong_lien_tiet', False)
                    existing.so_tiet_toi_da_ngay = item.get('so_tiet_toi_da_ngay', 0)
                    existing.cho_phep_tiet_doi = item.get('cho_phep_tiet_doi', False)
                else:
                    self.session.add(TKBCauHinhMon(
                        nam_hoc_id=nam_hoc_id,
                        mon_hoc_id=item['mon_hoc_id'],
                        chi_buoi_sang=item.get('chi_buoi_sang', False),
                        chi_buoi_chieu=item.get('chi_buoi_chieu', False),
                        khong_lien_tiet=item.get('khong_lien_tiet', False),
                        so_tiet_toi_da_ngay=item.get('so_tiet_toi_da_ngay', 0),
                        cho_phep_tiet_doi=item.get('cho_phep_tiet_doi', False),
                    ))
            self.session.commit()
            return ServiceResult(ok=True, error="Lưu thành công")
        except Exception as e:
            self.session.rollback()
            logger.error(f"save_cau_hinh_mon error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ RÀNG BUỘC GIÁO VIÊN ════════════════════════════════════

    def get_rang_buoc_gv(self, nam_hoc_id: int) -> ServiceResult:
        try:
            from core.db.models.giao_vien import GiaoVien

            ds_gv = self.session.query(GiaoVien).filter(
                GiaoVien.active == True
            ).all()

            rb_list = self.session.query(TKBRangBuocGV).filter(
                TKBRangBuocGV.nam_hoc_id == nam_hoc_id
            ).all()
            rb_map = {r.giao_vien_id: r for r in rb_list}

            result = []
            for gv in ds_gv:
                rb = rb_map.get(gv.id)
                ngay_nghi = []
                if rb and rb.ngay_nghi_list:
                    try:
                        ngay_nghi = [int(x) for x in rb.ngay_nghi_list.split(',') if x]
                    except:
                        ngay_nghi = []

                result.append({
                    "giao_vien_id": gv.id,
                    "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
                    "ma_giao_vien": gv.ma_giao_vien,
                    "chi_buoi_sang": rb.chi_buoi_sang if rb else False,
                    "chi_buoi_chieu": rb.chi_buoi_chieu if rb else False,
                    "so_tiet_toi_da_ngay": rb.so_tiet_toi_da_ngay if rb else 0,
                    "so_tiet_toi_thieu_ngay": rb.so_tiet_toi_thieu_ngay if rb else 0,
                    "gom_tiet": rb.gom_tiet if rb else False,
                    "so_ngay_nghi": rb.so_ngay_nghi if rb else 0,
                    "ngay_nghi_list": ngay_nghi,
                })

            return ServiceResult(ok=True, data=result)
        except Exception as e:
            logger.error(f"get_rang_buoc_gv error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def save_rang_buoc_gv(self, nam_hoc_id: int, items: list) -> ServiceResult:
        try:
            for item in items:
                ngay_nghi_str = ','.join(str(x) for x in item.get('ngay_nghi_list', []))

                existing = self.session.query(TKBRangBuocGV).filter(
                    TKBRangBuocGV.nam_hoc_id == nam_hoc_id,
                    TKBRangBuocGV.giao_vien_id == item['giao_vien_id']
                ).first()

                if existing:
                    existing.chi_buoi_sang = item.get('chi_buoi_sang', False)
                    existing.chi_buoi_chieu = item.get('chi_buoi_chieu', False)
                    existing.so_tiet_toi_da_ngay = item.get('so_tiet_toi_da_ngay', 0)
                    existing.so_tiet_toi_thieu_ngay = item.get('so_tiet_toi_thieu_ngay', 0)
                    existing.gom_tiet = item.get('gom_tiet', False)
                    existing.so_ngay_nghi = item.get('so_ngay_nghi', 0)
                    existing.ngay_nghi_list = ngay_nghi_str
                else:
                    self.session.add(TKBRangBuocGV(
                        nam_hoc_id=nam_hoc_id,
                        giao_vien_id=item['giao_vien_id'],
                        chi_buoi_sang=item.get('chi_buoi_sang', False),
                        chi_buoi_chieu=item.get('chi_buoi_chieu', False),
                        so_tiet_toi_da_ngay=item.get('so_tiet_toi_da_ngay', 0),
                        so_tiet_toi_thieu_ngay=item.get('so_tiet_toi_thieu_ngay', 0),
                        gom_tiet=item.get('gom_tiet', False),
                        so_ngay_nghi=item.get('so_ngay_nghi', 0),
                        ngay_nghi_list=ngay_nghi_str,
                    ))

            self.session.commit()
            return ServiceResult(ok=True, error="Lưu thành công")
        except Exception as e:
            self.session.rollback()
            logger.error(f"save_rang_buoc_gv error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ LẤY TKB ════════════════════════════════════════════════

    def lay_tkb_theo_lop(self, nam_hoc_id: int, lop_hoc_id: int,
                         hoc_ky_id: int = None) -> ServiceResult:
        try:
            query = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
                ThoiKhoaBieu.is_active == True
            )
            if hoc_ky_id:
                query = query.filter(ThoiKhoaBieu.hoc_ky_id == hoc_ky_id)
            data = query.all()
            return ServiceResult(ok=True, data=self._format_tkb(data))
        except Exception as e:
            logger.error(f"lay_tkb_theo_lop error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def lay_tkb_theo_gv(self, nam_hoc_id: int, giao_vien_id: int,
                        hoc_ky_id: int = None) -> ServiceResult:
        try:
            query = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.giao_vien_id == giao_vien_id,
                ThoiKhoaBieu.is_active == True
            )
            if hoc_ky_id:
                query = query.filter(ThoiKhoaBieu.hoc_ky_id == hoc_ky_id)
            data = query.all()
            return ServiceResult(ok=True, data=self._format_tkb(data))
        except Exception as e:
            logger.error(f"lay_tkb_theo_gv error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ CRUD Ô TKB ════════════════════════════════════════════

    def luu_o_tkb(self, nam_hoc_id: int, hoc_ky_id: int,
                  lop_hoc_id: int, giao_vien_id: int, mon_hoc_id: int,
                  thu: int, buoi: str, tiet: int,
                  phan_mon_id: int = None) -> ServiceResult:
        try:
            # Kiểm tra GV trùng giờ
            conflict_gv = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                ThoiKhoaBieu.giao_vien_id == giao_vien_id,
                ThoiKhoaBieu.thu == thu,
                ThoiKhoaBieu.buoi == buoi,
                ThoiKhoaBieu.tiet == tiet,
                ThoiKhoaBieu.is_active == True
            ).first()
            if conflict_gv:
                from core.db.models.lop_hoc import LopHoc
                lop = self.session.query(LopHoc).filter(
                    LopHoc.id == conflict_gv.lop_hoc_id
                ).first()
                return ServiceResult(
                    ok=False,
                    error=f"Giáo viên đang dạy lớp {lop.ten_lop if lop else ''} vào thời điểm này"
                )

            # Kiểm tra lớp trùng giờ
            conflict_lop = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
                ThoiKhoaBieu.thu == thu,
                ThoiKhoaBieu.buoi == buoi,
                ThoiKhoaBieu.tiet == tiet,
                ThoiKhoaBieu.is_active == True
            ).first()
            if conflict_lop:
                from core.db.models.mon_hoc import MonHoc
                mon = self.session.query(MonHoc).filter(
                    MonHoc.id == conflict_lop.mon_hoc_id
                ).first()
                return ServiceResult(
                    ok=False,
                    error=f"Lớp đã có môn {mon.ten_mon if mon else ''} vào thời điểm này"
                )

            # Kiểm tra không quá 7 tiết/ngày
            so_tiet_ngay = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
                ThoiKhoaBieu.thu == thu,
                ThoiKhoaBieu.is_active == True
            ).count()
            if so_tiet_ngay >= 7:
                return ServiceResult(ok=False, error="Lớp đã đủ 7 tiết trong ngày này")

            # Xóa ô cũ nếu có (overwrite)
            old = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                ThoiKhoaBieu.lop_hoc_id == lop_hoc_id,
                ThoiKhoaBieu.thu == thu,
                ThoiKhoaBieu.buoi == buoi,
                ThoiKhoaBieu.tiet == tiet,
            ).first()
            if old:
                self.session.delete(old)

            # Lưu ô mới
            o_tkb = ThoiKhoaBieu(
                nam_hoc_id=nam_hoc_id,
                hoc_ky_id=hoc_ky_id,
                lop_hoc_id=lop_hoc_id,
                giao_vien_id=giao_vien_id,
                mon_hoc_id=mon_hoc_id,
                phan_mon_id=phan_mon_id,
                thu=thu, buoi=buoi, tiet=tiet,
                is_active=True,
            )
            self.session.add(o_tkb)
            self.session.commit()
            return ServiceResult(ok=True, data=self._format_tkb([o_tkb])[0])
        except Exception as e:
            self.session.rollback()
            logger.error(f"luu_o_tkb error: {e}")
            return ServiceResult(ok=False, error=str(e))

    def xoa_o_tkb(self, tkb_id: int) -> ServiceResult:
        try:
            o = self.session.get(ThoiKhoaBieu, tkb_id)
            if not o:
                return ServiceResult(ok=False, error="Không tìm thấy")
            self.session.delete(o)
            self.session.commit()
            return ServiceResult(ok=True, error="Đã xóa")
        except Exception as e:
            self.session.rollback()
            logger.error(f"xoa_o_tkb error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ PHÂN CÔNG ══════════════════════════════════════════════

    def lay_phan_cong_theo_lop(self, nam_hoc_id: int, hoc_ky_id: int,
                               lop_hoc_id: int) -> ServiceResult:
        try:
            from core.db.models.phan_cong import PhanCongGiangDay
            from core.db.models.mon_hoc import MonHoc
            from core.db.models.giao_vien import GiaoVien

            ds = self.session.query(PhanCongGiangDay).filter(
                PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
                PhanCongGiangDay.lop_hoc_id == lop_hoc_id,
            ).all()

            result = []
            for pc in ds:
                mon = self.session.query(MonHoc).filter(MonHoc.id == pc.mon_hoc_id).first()
                gv = self.session.query(GiaoVien).filter(GiaoVien.id == pc.giao_vien_id).first()
                result.append({
                    "mon_hoc_id": pc.mon_hoc_id,
                    "ten_mon": mon.ten_mon if mon else "",
                    "ma_mon": mon.ma_mon if mon else "",
                    "giao_vien_id": pc.giao_vien_id,
                    "ten_giao_vien": gv.nguoi_dung.ho_ten if gv and gv.nguoi_dung else "",
                    "phan_mon_id": pc.phan_mon_id,
                    "ten_phan_mon": pc.phan_mon.ten_phan_mon if pc.phan_mon else None,
                })
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            logger.error(f"lay_phan_cong_theo_lop error: {e}")
            return ServiceResult(ok=False, error=str(e))

    # ══ SINH TKB TỰ ĐỘNG ══════════════════════════════════════

    def sinh_tkb_tu_dong(self, nam_hoc_id: int, hoc_ky_id: int,
                        clear_old: bool = False, off_slots: list = None, fixed_slots: list = None) -> ServiceResult:
        try:
            from .auto_schedule import AutoScheduler
            scheduler = AutoScheduler(self.session, nam_hoc_id, hoc_ky_id)
            # ⭐ Truyền cả off_slots và fixed_slots (nếu có)
            scheduler.load(off_slots=off_slots or [], fixed_slots=fixed_slots or [])
            result = scheduler.run(clear_old=clear_old)
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            self.session.rollback()
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ══ SWAP ═══════════════════════════════════════════════════

    def swap_o_tkb(self, id1: int, id2: int) -> ServiceResult:
        try:
            o1 = self.session.get(ThoiKhoaBieu, id1)
            o2 = self.session.get(ThoiKhoaBieu, id2)
            if not o1 or not o2:
                return ServiceResult(ok=False, error="Không tìm thấy tiết")

            # Lưu vị trí của o1
            temp_thu = o1.thu
            temp_buoi = o1.buoi
            temp_tiet = o1.tiet
            temp_lop = o1.lop_hoc_id

            # Cập nhật o1 = vị trí của o2
            o1.thu = o2.thu
            o1.buoi = o2.buoi
            o1.tiet = o2.tiet
            o1.lop_hoc_id = o2.lop_hoc_id

            # Cập nhật o2 = vị trí cũ của o1
            o2.thu = temp_thu
            o2.buoi = temp_buoi
            o2.tiet = temp_tiet
            o2.lop_hoc_id = temp_lop

            self.session.commit()
            return ServiceResult(ok=True, data="Đã đổi chỗ thành công")

        except Exception as e:
            self.session.rollback()
            logger.error(f"swap_o_tkb error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ══ TKB TẠI VỊ TRÍ ════════════════════════════════════════

    def get_tkb_at_position(self, nam_hoc_id: int, hoc_ky_id: int,
                            thu: int, buoi: str, tiet: int) -> ServiceResult:
        try:
            tkb = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                ThoiKhoaBieu.thu == thu,
                ThoiKhoaBieu.buoi == buoi,
                ThoiKhoaBieu.tiet == tiet,
                ThoiKhoaBieu.is_active == True
            ).first()

            if not tkb:
                return ServiceResult(ok=True, data=None)

            result = {
                "id": tkb.id,
                "lop_hoc_id": tkb.lop_hoc_id,
                "ten_lop": tkb.lop_hoc.ten_lop if tkb.lop_hoc else "",
                "giao_vien_id": tkb.giao_vien_id,
                "ten_giao_vien": tkb.giao_vien.nguoi_dung.ho_ten if tkb.giao_vien and tkb.giao_vien.nguoi_dung else "",
                "mon_hoc_id": tkb.mon_hoc_id,
                "ten_mon": tkb.mon_hoc.ten_mon if tkb.mon_hoc else "",
                "thu": tkb.thu,
                "buoi": tkb.buoi,
                "tiet": tkb.tiet,
            }
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            logger.error(f"get_tkb_at_position error: {e}")
            return ServiceResult(ok=False, error=str(e))


    # ══ CASCADE MOVE (đẩy dây chuyền) ═══════════════════════════

    def _load_scheduler_context(self, nam_hoc_id: int, hoc_ky_id: int, off_slots: list = None, fixed_slots: list = None):
        from .auto_schedule import AutoScheduler
        scheduler = AutoScheduler(self.session, nam_hoc_id, hoc_ky_id)
        scheduler.load(off_slots=off_slots or [], fixed_slots=fixed_slots or [])
        return scheduler

    def _la_ngu_van_tiet_doi(self, scheduler, item: ThoiKhoaBieu) -> bool:
        cfg_mon = scheduler.cau_hinh_mon.get(item.mon_hoc_id, {})
        if not cfg_mon.get('is_ngu_van'):
            return False
        prev_mon = scheduler.tkb_lop.get((item.lop_hoc_id, item.thu, item.buoi, item.tiet - 1))
        next_mon = scheduler.tkb_lop.get((item.lop_hoc_id, item.thu, item.buoi, item.tiet + 1))
        return prev_mon == item.mon_hoc_id or next_mon == item.mon_hoc_id

    def _slot_hop_le(self, scheduler, item: ThoiKhoaBieu, thu: int, buoi: str, tiet: int) -> bool:
        cfg_mon = scheduler.cau_hinh_mon.get(item.mon_hoc_id, {})
        cfg_gv = scheduler.rang_buoc_gv.get(item.giao_vien_id, {})

        if thu in cfg_gv.get('ngay_nghi', []):
            return False
        if cfg_mon.get('chi_sang') and buoi != 'sang':
            return False
        if cfg_mon.get('chi_chieu') and buoi != 'chieu':
            return False
        if cfg_gv.get('chi_sang') and buoi != 'sang':
            return False
        if cfg_gv.get('chi_chieu') and buoi != 'chieu':
            return False
        if cfg_mon.get('is_gdtc'):
            if buoi == 'sang' and tiet == 5:
                return False
            if buoi == 'chieu' and tiet == 1:
                return False
        return True

    def _lop_ban_tai_slot(self, nam_hoc_id, hoc_ky_id, lop_hoc_id, thu, buoi, tiet, exclude_ids):
        q = self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nam_hoc_id == nam_hoc_id, ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
            ThoiKhoaBieu.lop_hoc_id == lop_hoc_id, ThoiKhoaBieu.thu == thu,
            ThoiKhoaBieu.buoi == buoi, ThoiKhoaBieu.tiet == tiet, ThoiKhoaBieu.is_active == True,
        )
        if exclude_ids:
            q = q.filter(not_(ThoiKhoaBieu.id.in_(exclude_ids)))
        return q.first()

    def _gv_ban_tai_slot(self, nam_hoc_id, hoc_ky_id, giao_vien_id, thu, buoi, tiet, exclude_ids):
        q = self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nam_hoc_id == nam_hoc_id, ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
            ThoiKhoaBieu.giao_vien_id == giao_vien_id, ThoiKhoaBieu.thu == thu,
            ThoiKhoaBieu.buoi == buoi, ThoiKhoaBieu.tiet == tiet, ThoiKhoaBieu.is_active == True,
        )
        if exclude_ids:
            q = q.filter(not_(ThoiKhoaBieu.id.in_(exclude_ids)))
        return q.first() is not None

    def _tim_slot_trong_hop_le(self, scheduler, item, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots):
        slots = list(scheduler.all_slots)
        random.shuffle(slots)
        for (thu, buoi, tiet) in slots:
            if (thu, buoi, tiet) in visited_slots:
                continue
            if not self._slot_hop_le(scheduler, item, thu, buoi, tiet):
                continue
            if self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, item.lop_hoc_id, thu, buoi, tiet, moved_ids):
                continue
            if self._gv_ban_tai_slot(nam_hoc_id, hoc_ky_id, item.giao_vien_id, thu, buoi, tiet, moved_ids):
                continue
            return (thu, buoi, tiet)
        return None

    def _tim_slot_bi_chiem_hop_le(self, scheduler, item, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots):
        slots = list(scheduler.all_slots)
        random.shuffle(slots)
        for (thu, buoi, tiet) in slots:
            if (thu, buoi, tiet) in visited_slots:
                continue
            if not self._slot_hop_le(scheduler, item, thu, buoi, tiet):
                continue
            if self._gv_ban_tai_slot(nam_hoc_id, hoc_ky_id, item.giao_vien_id, thu, buoi, tiet, moved_ids):
                continue
            occupant = self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, item.lop_hoc_id, thu, buoi, tiet, moved_ids)
            if not occupant:
                continue
            if self._la_ngu_van_tiet_doi(scheduler, occupant):
                continue
            return (thu, buoi, tiet)
        return None

    def _mo_ta_move(self, item: ThoiKhoaBieu, den: tuple) -> dict:
        return {
            "id": item.id,
            "ten_mon": item.mon_hoc.ten_mon if item.mon_hoc else "",
            "ten_gv": item.giao_vien.nguoi_dung.ho_ten if item.giao_vien and item.giao_vien.nguoi_dung else "",
            "ten_lop": item.lop_hoc.ten_lop if item.lop_hoc else "",
            "tu_thu": item.thu, "tu_buoi": item.buoi, "tu_tiet": item.tiet,
            "den_thu": den[0], "den_buoi": den[1], "den_tiet": den[2],
        }

    def _cascade_relocate_occupant(self, scheduler, occupant: ThoiKhoaBieu,
                                    nam_hoc_id: int, hoc_ky_id: int,
                                    moved_ids: set, visited_slots: set,
                                    max_depth: int = 30):
        """
        Đẩy `occupant` (đang chiếm 1 vị trí cần dùng cho việc khác) sang 1 vị trí
        còn trống hợp lệ, hoặc đẩy tiếp dây chuyền nếu vị trí đó cũng bị chiếm.
        CHỈ đổi thu/buổi/tiết — KHÔNG đổi lop_hoc_id của bất kỳ tiết nào trong chuỗi.
        moved_ids/visited_slots được cập nhật trực tiếp (mutate) để lời gọi sau
        (nếu có) biết những gì đã "dùng" trong chuỗi trước.
        Trả về (True, moves) nếu tìm được, (False, error_message) nếu không.
        """
        if self._la_ngu_van_tiet_doi(scheduler, occupant):
            ten = occupant.mon_hoc.ten_mon if occupant.mon_hoc else ""
            return False, f"Không thể đẩy tiếp: {ten} thuộc cặp tiết đôi Ngữ Văn"

        moved_ids.add(occupant.id)
        moves = []
        current_item = occupant

        for _ in range(max_depth):
            empty_slot = self._tim_slot_trong_hop_le(scheduler, current_item, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots)
            if empty_slot:
                moves.append(self._mo_ta_move(current_item, empty_slot))
                visited_slots.add(empty_slot)
                return True, moves

            next_target = self._tim_slot_bi_chiem_hop_le(scheduler, current_item, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots)
            if not next_target:
                ten = current_item.mon_hoc.ten_mon if current_item.mon_hoc else ""
                return False, f"Không tìm được vị trí hợp lệ để đẩy tiết {ten}."

            occupant2 = self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, current_item.lop_hoc_id, *next_target, moved_ids)
            moves.append(self._mo_ta_move(current_item, next_target))
            visited_slots.add(next_target)

            if not occupant2:
                return True, moves

            if self._la_ngu_van_tiet_doi(scheduler, occupant2):
                ten = occupant2.mon_hoc.ten_mon if occupant2.mon_hoc else ""
                return False, f"Không thể đẩy tiếp: {ten} thuộc cặp tiết đôi Ngữ Văn"

            moved_ids.add(occupant2.id)
            current_item = occupant2

        return False, "Chuỗi di chuyển quá dài, không tìm được lời giải."

    def cascade_check_move(self, source_id: int, target_thu: int,
                            target_buoi: str, target_tiet: int,
                            target_lop_hoc_id: int, max_depth: int = 30) -> ServiceResult:
        try:
            item_a = self.session.get(ThoiKhoaBieu, source_id)
            if not item_a:
                return ServiceResult(ok=False, error="Không tìm thấy tiết nguồn")

            nam_hoc_id, hoc_ky_id = item_a.nam_hoc_id, item_a.hoc_ky_id
            scheduler = self._load_scheduler_context(nam_hoc_id, hoc_ky_id)

            if self._la_ngu_van_tiet_doi(scheduler, item_a):
                return ServiceResult(ok=False, error="Tiết này thuộc cặp tiết đôi Ngữ Văn, không thể di chuyển")

            original_slot = (item_a.thu, item_a.buoi, item_a.tiet)
            moves = []
            moved_ids = {item_a.id}
            visited_slots = {original_slot}

            current_item = item_a
            current_target = (target_thu, target_buoi, target_tiet)

            def mo_ta(item, den):
                return {
                    "id": item.id,
                    "ten_mon": item.mon_hoc.ten_mon if item.mon_hoc else "",
                    "ten_gv": item.giao_vien.nguoi_dung.ho_ten if item.giao_vien and item.giao_vien.nguoi_dung else "",
                    "ten_lop": item.lop_hoc.ten_lop if item.lop_hoc else "",
                    "tu_thu": item.thu, "tu_buoi": item.buoi, "tu_tiet": item.tiet,
                    "den_thu": den[0], "den_buoi": den[1], "den_tiet": den[2],
                }

            for _ in range(max_depth):
                if not self._slot_hop_le(scheduler, current_item, *current_target):
                    ten = current_item.mon_hoc.ten_mon if current_item.mon_hoc else ""
                    return ServiceResult(ok=False, error=f"Vị trí không hợp lệ cho môn {ten} (vi phạm ràng buộc)")

                if self._gv_ban_tai_slot(nam_hoc_id, hoc_ky_id, current_item.giao_vien_id, *current_target, moved_ids):
                    ten_gv = current_item.giao_vien.nguoi_dung.ho_ten if current_item.giao_vien and current_item.giao_vien.nguoi_dung else ""
                    return ServiceResult(ok=False, error=f"GV {ten_gv} đã bận ở vị trí này (dạy lớp khác)")

                occupant = self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, current_item.lop_hoc_id, *current_target, moved_ids)

                moves.append(mo_ta(current_item, current_target))
                visited_slots.add(current_target)

                if not occupant:
                    return ServiceResult(ok=True, data={"status": "cascade_ready", "moves": moves})

                if self._la_ngu_van_tiet_doi(scheduler, occupant):
                    ten = occupant.mon_hoc.ten_mon if occupant.mon_hoc else ""
                    return ServiceResult(ok=False, error=f"Không thể đẩy tiếp: {ten} thuộc cặp tiết đôi Ngữ Văn")

                moved_ids.add(occupant.id)

                if (self._slot_hop_le(scheduler, occupant, *original_slot)
                        and not self._gv_ban_tai_slot(nam_hoc_id, hoc_ky_id, occupant.giao_vien_id, *original_slot, moved_ids)
                        and not self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, occupant.lop_hoc_id, *original_slot, moved_ids)):
                    moves.append(mo_ta(occupant, original_slot))
                    return ServiceResult(ok=True, data={"status": "cascade_ready", "moves": moves})

                empty_slot = self._tim_slot_trong_hop_le(scheduler, occupant, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots)
                if empty_slot:
                    moves.append(mo_ta(occupant, empty_slot))
                    return ServiceResult(ok=True, data={"status": "cascade_ready", "moves": moves})

                next_target = self._tim_slot_bi_chiem_hop_le(scheduler, occupant, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots)
                if not next_target:
                    return ServiceResult(ok=False, error="Không tìm được chuỗi vị trí hợp lệ. Hủy thao tác.")

                current_item = occupant
                current_target = next_target

            return ServiceResult(ok=False, error="Chuỗi di chuyển quá dài, không tìm được lời giải. Hủy thao tác.")

        except Exception as e:
            logger.error(f"cascade_check_move error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    def cascade_confirm_move(self, moves: list) -> ServiceResult:
        try:
            # 1) Giai đoạn reserve: đặt tạm mỗi item vào slot tạm riêng (không trùng)
            temps = []
            idx = 1000  # bắt đầu giá trị tạm (đảm bảo vượt ngoài range normale)
            for mv in moves:
                item = self.session.get(ThoiKhoaBieu, mv["id"])
                if not item:
                    self.session.rollback()
                    return ServiceResult(ok=False, error=f"Không tìm thấy tiết ID {mv['id']}")
                # lưu lại vị trí đích để apply sau
                temps.append({"id": mv["id"], "den_thu": mv["den_thu"], "den_buoi": mv["den_buoi"], "den_tiet": mv["den_tiet"]})
                # set to unique temp slot
                item.thu = idx
                item.buoi = f"tmp_{idx}"
                item.tiet = idx
                # optionally change lop_hoc_id to itself (ok) or leave unchanged
                self.session.flush()
                idx += 1

            # 2) Giai đoạn apply: chuyển từ temp -> vị trí đích
            for t in temps:
                item = self.session.get(ThoiKhoaBieu, t["id"])
                item.thu = t["den_thu"]
                item.buoi = t["den_buoi"]
                item.tiet = t["den_tiet"]
                self.session.flush()

            self.session.commit()
            return ServiceResult(ok=True, data={"status": "cascade_applied", "so_tiet_da_doi": len(moves)})
        except Exception as e:
            self.session.rollback()
            logger.error(f"cascade_confirm_move error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ══ MOVE / SWAP ════════════════════════════════════════════

    def check_move_tkb(self, source_id: int, target_thu: int,
                    target_buoi: str, target_tiet: int,
                    target_lop_hoc_id: int = None,
                    off_slots: list = None, fixed_slots: list = None) -> ServiceResult:
        """
        Kiểm tra có thể di chuyển source -> target hay không.
        Nếu target có item_b:
        - nếu same GV + same mon + same khoi => có thể swap (nếu không có bản ghi thứ 3)
        - nếu khác GV => cascade / conflict (như trước)
        """
        try:
            item_a = self.session.get(ThoiKhoaBieu, source_id)
            if not item_a:
                return ServiceResult(ok=False, error="Không tìm thấy tiết nguồn")

            nam_hoc_id = item_a.nam_hoc_id
            hoc_ky_id = item_a.hoc_ky_id
            gv_id = item_a.giao_vien_id
            target_lop = target_lop_hoc_id or item_a.lop_hoc_id

            if (item_a.thu == target_thu and
                item_a.buoi == target_buoi and
                item_a.tiet == target_tiet and
                item_a.lop_hoc_id == target_lop):
                return ServiceResult(ok=False, error="Vị trí không thay đổi")

            # load item_b nếu có
            item_b = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                ThoiKhoaBieu.lop_hoc_id == target_lop,
                ThoiKhoaBieu.thu == target_thu,
                ThoiKhoaBieu.buoi == target_buoi,
                ThoiKhoaBieu.tiet == target_tiet,
                ThoiKhoaBieu.is_active == True,
            ).first()

            # CASE: đích trống
            if not item_b:
                # kiểm tra GV có bận bởi 1 bản ghi khác (ngoài item_a)
                gv_conflict = self.session.query(ThoiKhoaBieu).filter(
                    ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                    ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                    ThoiKhoaBieu.giao_vien_id == gv_id,
                    ThoiKhoaBieu.thu == target_thu,
                    ThoiKhoaBieu.buoi == target_buoi,
                    ThoiKhoaBieu.tiet == target_tiet,
                    ThoiKhoaBieu.is_active == True,
                    ThoiKhoaBieu.id != source_id,
                ).first()

                if gv_conflict:
                    conflict_item = {
                        "id": gv_conflict.id,
                        "lop_hoc_id": gv_conflict.lop_hoc_id,
                        "thu": gv_conflict.thu,
                        "buoi": gv_conflict.buoi,
                        "tiet": gv_conflict.tiet,
                        "ten_lop": gv_conflict.lop_hoc.ten_lop if gv_conflict.lop_hoc else "",
                        "ten_mon": gv_conflict.mon_hoc.ten_mon if gv_conflict.mon_hoc else "",
                        "ten_gv": gv_conflict.giao_vien.nguoi_dung.ho_ten if gv_conflict.giao_vien and gv_conflict.giao_vien.nguoi_dung else ""
                    }
                    return ServiceResult(ok=True, data={
                        "status": "conflict",
                        "ly_do": f"GV {conflict_item['ten_gv']} đã bận ở vị trí này (dạy lớp khác)",
                        "conflict_item": conflict_item,
                        "source_id": item_a.id,
                        "target_thu": target_thu,
                        "target_buoi": target_buoi,
                        "target_tiet": target_tiet,
                        "target_lop_hoc_id": target_lop
                    })

                return ServiceResult(ok=True, data={
                    "status": "empty",
                    "source_id": item_a.id,
                    "ten_mon_a": item_a.mon_hoc.ten_mon if item_a.mon_hoc else "",
                    "ten_gv_a": item_a.giao_vien.nguoi_dung.ho_ten if item_a.giao_vien and item_a.giao_vien.nguoi_dung else "",
                    "target_thu": target_thu,
                    "target_buoi": target_buoi,
                    "target_tiet": target_tiet,
                    "target_lop_hoc_id": target_lop,
                })

            if item_b.id == source_id:
                return ServiceResult(ok=False, error="Vị trí không thay đổi")

            # CASE: cùng giáo viên
            if item_a.giao_vien_id == item_b.giao_vien_id:
                # ⭐ ĐƠN GIẢN HÓA: Cho phép swap mọi trường hợp cùng GV
                # Chỉ cần kiểm tra không có bản ghi thứ 3 chiếm vị trí
                other_at_target = self.session.query(ThoiKhoaBieu).filter(
                    ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                    ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                    ThoiKhoaBieu.giao_vien_id == item_a.giao_vien_id,
                    ThoiKhoaBieu.thu == target_thu,
                    ThoiKhoaBieu.buoi == target_buoi,
                    ThoiKhoaBieu.tiet == target_tiet,
                    ThoiKhoaBieu.is_active == True,
                    not_(ThoiKhoaBieu.id.in_([item_a.id, item_b.id]))
                ).first()
                
                if other_at_target:
                    return ServiceResult(ok=True, data={
                        "status": "conflict",
                        "ly_do": f"GV đã có tiết khác tại vị trí này (ID: {other_at_target.id})",
                        "conflict_item": {
                            "id": other_at_target.id,
                            "ten_lop": other_at_target.lop_hoc.ten_lop if other_at_target.lop_hoc else "",
                            "ten_mon": other_at_target.mon_hoc.ten_mon if other_at_target.mon_hoc else "",
                            "ten_gv": other_at_target.giao_vien.nguoi_dung.ho_ten if other_at_target.giao_vien and other_at_target.giao_vien.nguoi_dung else ""
                        },
                        "source_id": item_a.id,
                        "item_a_id": item_a.id,
                        "item_b_id": item_b.id,
                        "target_thu": target_thu,
                        "target_buoi": target_buoi,
                        "target_tiet": target_tiet,
                        "target_lop_hoc_id": target_lop,
                    })

                other_at_source = self.session.query(ThoiKhoaBieu).filter(
                    ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                    ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                    ThoiKhoaBieu.giao_vien_id == item_a.giao_vien_id,
                    ThoiKhoaBieu.thu == item_a.thu,
                    ThoiKhoaBieu.buoi == item_a.buoi,
                    ThoiKhoaBieu.tiet == item_a.tiet,
                    ThoiKhoaBieu.is_active == True,
                    not_(ThoiKhoaBieu.id.in_([item_a.id, item_b.id]))
                ).first()
                
                if other_at_source:
                    return ServiceResult(ok=True, data={
                        "status": "conflict",
                        "ly_do": f"GV đã có tiết khác tại vị trí nguồn (ID: {other_at_source.id})",
                        "conflict_item": {
                            "id": other_at_source.id,
                            "ten_lop": other_at_source.lop_hoc.ten_lop if other_at_source.lop_hoc else "",
                            "ten_mon": other_at_source.mon_hoc.ten_mon if other_at_source.mon_hoc else "",
                            "ten_gv": other_at_source.giao_vien.nguoi_dung.ho_ten if other_at_source.giao_vien and other_at_source.giao_vien.nguoi_dung else ""
                        },
                        "source_id": item_a.id,
                        "item_a_id": item_a.id,
                        "item_b_id": item_b.id,
                        "target_thu": target_thu,
                        "target_buoi": target_buoi,
                        "target_tiet": target_tiet,
                        "target_lop_hoc_id": target_lop,
                    })

                # ⭐ KIỂM TRA LỚP CÓ BỊ TRÙNG LỊCH KHÔNG (khi khác lớp, lop_hoc_id được GIỮ NGUYÊN,
                # chỉ đổi giờ dạy — nên phải đảm bảo lớp của mỗi tiết còn trống ở giờ mới).
                # Nếu bị chiếm, thử ĐẨY DÂY CHUYỀN (cascade) tiết đang chiếm sang vị trí khác,
                # giống cơ chế đã có cho trường hợp khác GV, thay vì chặn cứng.
                scheduler = self._load_scheduler_context(nam_hoc_id, hoc_ky_id)
                source_pos = (item_a.thu, item_a.buoi, item_a.tiet)
                target_pos = (target_thu, target_buoi, target_tiet)

                moved_ids = {item_a.id, item_b.id}
                visited_slots = {source_pos, target_pos}
                moves = [
                    self._mo_ta_move(item_a, target_pos),
                    self._mo_ta_move(item_b, source_pos),
                ]

                # Lớp của A (item_a.lop_hoc_id) có tiết khác ở giờ của B (vị trí đích) không?
                lop_a_ban = self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, item_a.lop_hoc_id, *target_pos, moved_ids)
                if lop_a_ban:
                    ok, result = self._cascade_relocate_occupant(
                        scheduler, lop_a_ban, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots
                    )
                    if not ok:
                        return ServiceResult(ok=True, data={
                            "status": "conflict",
                            "ly_do": f"Lớp {item_a.lop_hoc.ten_lop if item_a.lop_hoc else ''} đã có tiết khác ({lop_a_ban.mon_hoc.ten_mon if lop_a_ban.mon_hoc else ''}) tại giờ đích và không thể tự sắp xếp lại: {result}",
                        })
                    moves.extend(result)

                # Lớp của B (item_b.lop_hoc_id) có tiết khác ở giờ của A (vị trí nguồn) không?
                lop_b_ban = self._lop_ban_tai_slot(nam_hoc_id, hoc_ky_id, item_b.lop_hoc_id, *source_pos, moved_ids)
                if lop_b_ban:
                    ok, result = self._cascade_relocate_occupant(
                        scheduler, lop_b_ban, nam_hoc_id, hoc_ky_id, moved_ids, visited_slots
                    )
                    if not ok:
                        return ServiceResult(ok=True, data={
                            "status": "conflict",
                            "ly_do": f"Lớp {item_b.lop_hoc.ten_lop if item_b.lop_hoc else ''} đã có tiết khác ({lop_b_ban.mon_hoc.ten_mon if lop_b_ban.mon_hoc else ''}) tại giờ nguồn và không thể tự sắp xếp lại: {result}",
                        })
                    moves.extend(result)

                # Nếu có tiết nào khác ngoài A/B cần đẩy đi -> trả về cascade để FE hiện modal xác nhận
                if len(moves) > 2:
                    return ServiceResult(ok=True, data={
                        "status": "cascade",
                        "moves": moves,
                    })

                # ⭐ CHO PHÉP SWAP (KHÔNG CẦN KIỂM TRA KHỐI/MÔN)
                return ServiceResult(ok=True, data={
                    "status": "can_swap",
                    "item_a_id": item_a.id,
                    "item_b_id": item_b.id,
                    "ten_mon_a": item_a.mon_hoc.ten_mon if item_a.mon_hoc else "",
                    "ten_gv_a": item_a.giao_vien.nguoi_dung.ho_ten if item_a.giao_vien and item_a.giao_vien.nguoi_dung else "",
                    "ten_lop_a": item_a.lop_hoc.ten_lop if item_a.lop_hoc else "",
                    "ten_mon_b": item_b.mon_hoc.ten_mon if item_b.mon_hoc else "",
                    "ten_gv_b": item_b.giao_vien.nguoi_dung.ho_ten if item_b.giao_vien and item_b.giao_vien.nguoi_dung else "",
                    "ten_lop_b": item_b.lop_hoc.ten_lop if item_b.lop_hoc else "",
                    "target_thu": target_thu,
                    "target_buoi": target_buoi,
                    "target_tiet": target_tiet,
                    "target_lop_hoc_id": target_lop,
                })

            # khác GV -> cascade (giữ nguyên)
            cascade_result = self.cascade_check_move(
                source_id=source_id,
                target_thu=target_thu,
                target_buoi=target_buoi,
                target_tiet=target_tiet,
                target_lop_hoc_id=target_lop,
            )
            if not cascade_result.ok:
                return ServiceResult(ok=True, data={
                    "status": "conflict",
                    "ly_do": cascade_result.error,
                })
            return ServiceResult(ok=True, data={
                "status": "cascade",
                "moves": cascade_result.data["moves"],
            })

        except Exception as e:
            logger.error(f"check_move_tkb error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    def confirm_move_tkb(self, source_id: int, target_thu: int,
                         target_buoi: str, target_tiet: int,
                         target_lop_hoc_id: int) -> ServiceResult:
        try:
            item_a = self.session.get(ThoiKhoaBieu, source_id)
            if not item_a:
                return ServiceResult(ok=False, error="Không tìm thấy tiết nguồn")

            item_a.lop_hoc_id = target_lop_hoc_id
            item_a.thu = target_thu
            item_a.buoi = target_buoi
            item_a.tiet = target_tiet
            self.session.commit()

            return ServiceResult(ok=True, data={"status": "moved"})

        except Exception as e:
            self.session.rollback()
            logger.error(f"confirm_move_tkb error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))


    def confirm_swap_tkb(self, item_a_id: int, item_b_id: int) -> ServiceResult:
        try:
            item_a = self.session.get(ThoiKhoaBieu, item_a_id)
            item_b = self.session.get(ThoiKhoaBieu, item_b_id)
            if not item_a or not item_b:
                return ServiceResult(ok=False, error="Không tìm thấy tiết")

            # --- DEBUG LOG: before ---
            logger.info(f"confirm_swap_tkb START: item_a_id={item_a_id}, item_b_id={item_b_id}")
            logger.info(f" BEFORE a: id={item_a.id} lop={item_a.lop_hoc_id} thu={item_a.thu} buoi={item_a.buoi} tiet={item_a.tiet}")
            logger.info(f" BEFORE b: id={item_b.id} lop={item_b.lop_hoc_id} thu={item_b.thu} buoi={item_b.buoi} tiet={item_b.tiet}")

            # lưu vị trí ban đầu
            a_lop, a_thu, a_buoi, a_tiet = item_a.lop_hoc_id, item_a.thu, item_a.buoi, item_a.tiet
            b_lop, b_thu, b_buoi, b_tiet = item_b.lop_hoc_id, item_b.thu, item_b.buoi, item_b.tiet

            # Re-check race: chắc chắn không có bản ghi khác chiếm vị trí ĐÍCH thật sự
            # (item_a giữ nguyên lop=a_lop nhưng chuyển sang giờ của B;
            #  item_b giữ nguyên lop=b_lop nhưng chuyển sang giờ của A)
            other_a = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == item_a.nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == item_a.hoc_ky_id,
                ThoiKhoaBieu.lop_hoc_id == a_lop,
                ThoiKhoaBieu.thu == b_thu,
                ThoiKhoaBieu.buoi == b_buoi,
                ThoiKhoaBieu.tiet == b_tiet,
                ThoiKhoaBieu.is_active == True,
                not_(ThoiKhoaBieu.id.in_([item_a.id, item_b.id]))
            ).first()
            if other_a:
                return ServiceResult(ok=False, error=f"Lớp của tiết A đã bận tại vị trí đích (ID {other_a.id})")

            other_b = self.session.query(ThoiKhoaBieu).filter(
                ThoiKhoaBieu.nam_hoc_id == item_b.nam_hoc_id,
                ThoiKhoaBieu.hoc_ky_id == item_b.hoc_ky_id,
                ThoiKhoaBieu.lop_hoc_id == b_lop,
                ThoiKhoaBieu.thu == a_thu,
                ThoiKhoaBieu.buoi == a_buoi,
                ThoiKhoaBieu.tiet == a_tiet,
                ThoiKhoaBieu.is_active == True,
                not_(ThoiKhoaBieu.id.in_([item_a.id, item_b.id]))
            ).first()
            if other_b:
                return ServiceResult(ok=False, error=f"Lớp của tiết B đã bận tại vị trí đích (ID {other_b.id})")

            # Phase 1: reserve temps (dùng offset lớn để tránh trùng)
            OFFSET = 1000000
            temp_a_thu = OFFSET + item_a.id
            temp_b_thu = OFFSET + item_b.id

            item_a.thu = temp_a_thu
            item_a.tiet = temp_a_thu
            self.session.flush()

            item_b.thu = temp_b_thu
            item_b.tiet = temp_b_thu
            self.session.flush()

            # Phase 2: apply swap (an toàn)
            # ⭐ CHỈ swap vị trí (thu/buổi/tiết), GIỮ NGUYÊN lop_hoc_id của từng item.
            # Lý do: mỗi tiết vẫn thuộc về lớp của nó, chỉ đổi giờ dạy.
            # Nếu swap luôn lop_hoc_id thì với case cùng GV + cùng môn + khác lớp,
            # nội dung hiển thị ở mỗi vị trí sẽ không đổi gì (item_a <-> item_b
            # tráo hết thuộc tính cho nhau => nhìn như không có gì thay đổi).
            item_a.thu = b_thu
            item_a.buoi = b_buoi
            item_a.tiet = b_tiet
            self.session.flush()

            item_b.thu = a_thu
            item_b.buoi = a_buoi
            item_b.tiet = a_tiet
            self.session.flush()

            self.session.commit()

            # --- DEBUG LOG: after commit ---
            logger.info(f"confirm_swap_tkb DONE: a->(id={item_a.id}, lop={item_a.lop_hoc_id}, thu={item_a.thu}, buoi={item_a.buoi}, tiet={item_a.tiet})")
            logger.info(f"confirm_swap_tkb DONE: b->(id={item_b.id}, lop={item_b.lop_hoc_id}, thu={item_b.thu}, buoi={item_b.buoi}, tiet={item_b.tiet})")

            return ServiceResult(ok=True, data={"status": "swapped"})
        except Exception as e:
            self.session.rollback()
            logger.error(f"confirm_swap_tkb error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    def resolve_conflict_auto(self, item_a_id: int, item_b_id: int,
                            target_thu: int, target_buoi: str, target_tiet: int,
                            target_lop_hoc_id: int,
                            off_slots: list = None, fixed_slots: list = None) -> ServiceResult:
        try:
            item_a = self.session.get(ThoiKhoaBieu, item_a_id)
            item_b = self.session.get(ThoiKhoaBieu, item_b_id)
            if not item_a or not item_b:
                return ServiceResult(ok=False, error="Không tìm thấy tiết")

            nam_hoc_id = item_a.nam_hoc_id
            hoc_ky_id = item_a.hoc_ky_id

            # Build scheduler with off/fixed slots so search tôn trọng chúng
            from .auto_schedule import AutoScheduler
            scheduler = AutoScheduler(self.session, nam_hoc_id, hoc_ky_id)
            scheduler.load(off_slots=off_slots or [], fixed_slots=fixed_slots or [])

            # Vị trí cũ của A — nơi item_b CÓ THỂ được đẩy về (ưu tiên)
            old_a_pos = (item_a.thu, item_a.buoi, item_a.tiet, item_a.lop_hoc_id)

            candidate_slots = [old_a_pos[:3]]
            other_slots = [s for s in scheduler.all_slots if s != old_a_pos[:3]]
            random.shuffle(other_slots)
            candidate_slots += other_slots

            found_slot = None
            found_lop = None
            tried = 0

            for (thu, buoi, tiet) in candidate_slots:
                tried += 1
                # Thử 2 khóa lớp ưu tiên: lớp cũ của A rồi lớp gốc của B
                for lop_id in [old_a_pos[3], item_b.lop_hoc_id]:
                    # skip if target equals the spot where A will go (avoid replacing same)
                    if (lop_id == target_lop_hoc_id and thu == target_thu and buoi == target_buoi and tiet == target_tiet):
                        continue

                    # Respect off_slots/fixed_slots: skip if slot is off or fixed for that class or gv
                    if (f'lop_{lop_id}', thu, buoi, tiet) in scheduler.off_slots or (f'gv_{item_b.giao_vien_id}', thu, buoi, tiet) in scheduler.off_slots:
                        continue
                    if (f'lop_{lop_id}', thu, buoi, tiet) in scheduler.fixed_slots or (f'gv_{item_b.giao_vien_id}', thu, buoi, tiet) in scheduler.fixed_slots:
                        continue

                    # Kiểm tra lớp trống
                    conflict_lop = self.session.query(ThoiKhoaBieu).filter(
                        ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                        ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
                        ThoiKhoaBieu.lop_hoc_id == lop_id,
                        ThoiKhoaBieu.thu == thu,
                        ThoiKhoaBieu.buoi == buoi,
                        ThoiKhoaBieu.tiet == tiet,
                        ThoiKhoaBieu.is_active == True,
                        ThoiKhoaBieu.id != item_b.id,
                    ).first()
                    if conflict_lop:
                        continue

                    # Kiểm tra GV trống (tôn trọng exclude item_b)
                    err = self._check_slot_valid_for_gv(item_b.giao_vien_id, nam_hoc_id, hoc_ky_id, thu, buoi, tiet, exclude_id=item_b.id)
                    if err:
                        continue

                    # Kiểm tra giới hạn 7 tiết/ngày cho lớp
                    so_tiet_ngay = self.session.query(ThoiKhoaBieu).filter(
                        ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
                        ThoiKhoaBieu.lop_hoc_id == lop_id,
                        ThoiKhoaBieu.thu == thu,
                        ThoiKhoaBieu.is_active == True,
                        ThoiKhoaBieu.id != item_b.id,
                    ).count()
                    if so_tiet_ngay >= 7:
                        continue

                    found_slot = (thu, buoi, tiet)
                    found_lop = lop_id
                    break

                if found_slot:
                    break

            if not found_slot:
                # Trả lý do chi tiết để frontend hiển thị / debug
                reason = f"Không tìm được vị trí hợp lệ cho tiết {item_b.mon_hoc.ten_mon if item_b.mon_hoc else ''} sau khi thử {tried} slot"
                logger.info("resolve_conflict_auto failed: " + reason)
                return ServiceResult(ok=False, error=reason)

            # Thực hiện: item_a -> vị trí target; item_b -> found_slot (an toàn bằng 2-phase)
            # Phase reserve temps
            temp_thu_a = 2000000 + item_a.id
            temp_thu_b = 2000000 + item_b.id
            item_a.thu = temp_thu_a
            item_a.tiet = temp_thu_a
            item_b.thu = temp_thu_b
            item_b.tiet = temp_thu_b
            self.session.flush()

            # Apply final positions
            item_a.lop_hoc_id = target_lop_hoc_id
            item_a.thu = target_thu
            item_a.buoi = target_buoi
            item_a.tiet = target_tiet

            item_b.lop_hoc_id = found_lop
            item_b.thu = found_slot[0]
            item_b.buoi = found_slot[1]
            item_b.tiet = found_slot[2]

            self.session.commit()
            return ServiceResult(ok=True, data={
                "status": "resolved",
                "new_position_b": {
                    "lop_hoc_id": found_lop,
                    "thu": found_slot[0],
                    "buoi": found_slot[1],
                    "tiet": found_slot[2],
                }
            })
        except Exception as e:
            self.session.rollback()
            logger.error(f"resolve_conflict_auto error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ══ HELPER ════════════════════════════════════════════════

    def _check_slot_valid_for_gv(self, giao_vien_id: int, nam_hoc_id: int,
                                hoc_ky_id: int, thu: int, buoi: str, tiet: int,
                                exclude_id: int = None, exclude_ids: list = None) -> str:
        """Kiểm tra GV có trống tại slot không. Trả về None nếu hợp lệ, trả về lỗi nếu không."""
        query = self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nam_hoc_id == nam_hoc_id,
            ThoiKhoaBieu.hoc_ky_id == hoc_ky_id,
            ThoiKhoaBieu.giao_vien_id == giao_vien_id,
            ThoiKhoaBieu.thu == thu,
            ThoiKhoaBieu.buoi == buoi,
            ThoiKhoaBieu.tiet == tiet,
            ThoiKhoaBieu.is_active == True,
        )

        if exclude_id is not None:
            query = query.filter(ThoiKhoaBieu.id != exclude_id)

        if exclude_ids and len(exclude_ids) > 0:
            # ⭐ QUAN TRỌNG: exclude_ids là list các ID cần bỏ qua
            query = query.filter(not_(ThoiKhoaBieu.id.in_(exclude_ids)))

        conflict = query.first()
        if conflict:
            return f"GV đã có tiết tại vị trí này (ID: {conflict.id})"

        return None  # Hợp lệ

    def _format_tkb(self, data: list) -> list:
        result = []
        for t in data:
            result.append({
                "id": t.id,
                "lop_hoc_id": t.lop_hoc_id,
                "ten_lop": t.lop_hoc.ten_lop if t.lop_hoc else "",
                "giao_vien_id": t.giao_vien_id,
                "ten_giao_vien": (
                    t.giao_vien.nguoi_dung.ho_ten
                    if t.giao_vien and t.giao_vien.nguoi_dung else ""
                ),
                "mon_hoc_id": t.mon_hoc_id,
                "ten_mon": t.mon_hoc.ten_mon if t.mon_hoc else "",
                "ma_mon": t.mon_hoc.ma_mon if t.mon_hoc else "",
                "thu": t.thu,
                "buoi": t.buoi,
                "tiet": t.tiet,
            })
        return result

    def export_tkb(self, nam_hoc_id: int, hoc_ky_id: int) -> ServiceResult:
        """Xuất TKB ra file Excel"""
        try:
            from .export_service import TKBExportService
            export_svc = TKBExportService(self.session)
            excel_data = export_svc.export_tkb(nam_hoc_id, hoc_ky_id)
            return ServiceResult(ok=True, data=excel_data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))