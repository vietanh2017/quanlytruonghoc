# modules/tkb/auto_schedule.py
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple, Optional
import random
import logging

from modules.tkb.models import ThoiKhoaBieu, TKBCauHinhNgay, TKBCauHinhMon, TKBRangBuocGV
from core.db.models.phan_cong import PhanCongGiangDay
from core.db.models.mon_hoc import MonHocKhoi, MonHoc

logger = logging.getLogger(__name__)


class AutoScheduler:
    def __init__(self, session: Session, nam_hoc_id: int, hoc_ky_id: int):
        self.session = session
        self.nam_hoc_id = nam_hoc_id
        self.hoc_ky_id = hoc_ky_id

        # TKB đã xếp: {(lop_id, thu, buoi, tiet): mon_id}
        self.tkb_lop: Dict[Tuple, int] = {}
        # Lịch GV: {(gv_id, thu, buoi, tiet): True}
        self.tkb_gv: Dict[Tuple, bool] = {}
        # Số tiết đã xếp mỗi ngày: {(lop_id, thu): count}
        self.tiet_ngay: Dict[Tuple, int] = {}
        # Số tiết GV đã xếp mỗi ngày: {(gv_id, thu): count}
        self.tiet_gv_ngay: Dict[Tuple, int] = {}

        # Cache cấu hình
        self.cau_hinh_ngay: Dict[int, dict] = {}
        self.cau_hinh_mon: Dict[int, dict] = {}
        self.rang_buoc_gv: Dict[int, dict] = {}

        self.all_slots: List[Tuple] = []
        self.errors: List[str] = []
        self.success_count = 0
        self.total_jobs = 0

        self.off_slots: set = set()    # ô nghỉ (do người dùng chỉ định)
        self.fixed_slots: set = set()  # ô cố định (không được xếp)

    # ══ LOAD DỮ LIỆU ═══════════════════════════════════════

    def load(self, off_slots: list = None, fixed_slots: list = None):
        """Load tất cả dữ liệu cấu hình"""
        self._load_cau_hinh_ngay()
        self._load_cau_hinh_mon()
        self._load_rang_buoc_gv()
        self._build_slot_list()
        self._load_tkb_hien_tai()
        self._load_off_slots(off_slots or [])
        self._load_fixed_slots(fixed_slots or [])

    def _load_off_slots(self, off_slots: list):
        """Load danh sách tiết nghỉ"""
        self.off_slots = set()
        for slot in off_slots:
            thu = slot.get('thu')
            buoi = slot.get('buoi')
            tiet = slot.get('tiet')
            lop_id = slot.get('lop_id')
            gv_id = slot.get('gv_id')
            if lop_id:
                self.off_slots.add((f'lop_{lop_id}', thu, buoi, tiet))
            if gv_id:
                self.off_slots.add((f'gv_{gv_id}', thu, buoi, tiet))

        if self.off_slots:
            print(f"📋 Đã load {len(self.off_slots)} ô nghỉ")

    def _load_fixed_slots(self, fixed_slots: list):
        """Load danh sách ô cố định (locked)"""
        self.fixed_slots = set()
        for slot in fixed_slots:
            thu = slot.get('thu')
            buoi = slot.get('buoi')
            tiet = slot.get('tiet')
            lop_id = slot.get('lop_id')
            gv_id = slot.get('gv_id')
            if lop_id:
                self.fixed_slots.add((f'lop_{lop_id}', thu, buoi, tiet))
            if gv_id:
                self.fixed_slots.add((f'gv_{gv_id}', thu, buoi, tiet))

        if self.fixed_slots:
            print(f"🔒 Đã load {len(self.fixed_slots)} ô cố định")

    def _load_cau_hinh_ngay(self):
        """Load cấu hình ngày học"""
        rows = self.session.query(TKBCauHinhNgay).filter(
            TKBCauHinhNgay.nam_hoc_id == self.nam_hoc_id
        ).all()
        for r in rows:
            self.cau_hinh_ngay[r.thu] = {
                'co_sang': r.co_buoi_sang,
                'co_chieu': r.co_buoi_chieu,
                'so_tiet_sang': 4 if r.co_buoi_chieu else 5,
                'so_tiet_chieu': 3 if r.co_buoi_chieu else 0,
            }
        # Mặc định nếu chưa cấu hình
        for thu in range(2, 8):
            if thu not in self.cau_hinh_ngay:
                self.cau_hinh_ngay[thu] = {
                    'co_sang': True, 'co_chieu': False,
                    'so_tiet_sang': 5, 'so_tiet_chieu': 0,
                }

    def _load_cau_hinh_mon(self):
        """Load cấu hình ràng buộc môn học"""
        rows = self.session.query(TKBCauHinhMon).filter(
            TKBCauHinhMon.nam_hoc_id == self.nam_hoc_id
        ).all()
        for r in rows:
            self.cau_hinh_mon[r.mon_hoc_id] = {
                'chi_sang': r.chi_buoi_sang,
                'chi_chieu': r.chi_buoi_chieu,
                'khong_lien': r.khong_lien_tiet,
                'max_ngay': r.so_tiet_toi_da_ngay,
                'tiet_doi': r.cho_phep_tiet_doi,
            }

        # ⭐ BỔ SUNG: Đánh dấu môn đặc biệt (lấy từ mã môn)
        mon_list = self.session.query(MonHoc).filter(MonHoc.active == True).all()
        for mon in mon_list:
            if mon.id not in self.cau_hinh_mon:
                self.cau_hinh_mon[mon.id] = {}

            ma_mon = mon.ma_mon.upper() if mon.ma_mon else ''
            ten_mon = mon.ten_mon.lower() if mon.ten_mon else ''

            # ⭐ LOG để kiểm tra
            print(f"📚 Môn: {mon.ten_mon} - mã: '{ma_mon}'")

            # Môn GDTC
            if ma_mon == 'GDTC':
                self.cau_hinh_mon[mon.id]['is_gdtc'] = True
                print(f"   ✅ Đánh dấu GDTC: {mon.ten_mon}")

            # Môn Ngữ Văn - KIỂM TRA MÃ 'VAN' hoặc tên chứa 'ngữ văn'
            if ma_mon in ['VAN', 'NV', 'NGUVAN', 'NGU_VAN'] or 'ngữ văn' in ten_mon:
                self.cau_hinh_mon[mon.id]['is_ngu_van'] = True
                self.cau_hinh_mon[mon.id]['yeu_cau_tiet_doi'] = True
                print(f"   ✅ Đánh dấu Ngữ Văn: {mon.ten_mon} (mã: {ma_mon})")

    def _load_rang_buoc_gv(self):
        """Load ràng buộc giáo viên"""
        rows = self.session.query(TKBRangBuocGV).filter(
            TKBRangBuocGV.nam_hoc_id == self.nam_hoc_id
        ).all()
        for r in rows:
            ngay_nghi = []
            if r.ngay_nghi_list:
                try:
                    ngay_nghi = [int(x) for x in r.ngay_nghi_list.split(',') if x]
                except:
                    pass
            self.rang_buoc_gv[r.giao_vien_id] = {
                'chi_sang': r.chi_buoi_sang,
                'chi_chieu': r.chi_buoi_chieu,
                'max_tiet_ngay': r.so_tiet_toi_da_ngay,
                'min_tiet_ngay': r.so_tiet_toi_thieu_ngay,
                'gom_tiet': r.gom_tiet,
                'ngay_nghi': ngay_nghi,
            }

    def _build_slot_list(self):
        """Tạo danh sách slot T2→T7, Sáng→Chiều, T1→T5"""
        self.all_slots = []
        for thu in range(2, 8):
            cfg = self.cau_hinh_ngay.get(thu, {})
            if cfg.get('co_sang'):
                for tiet in range(1, cfg.get('so_tiet_sang', 5) + 1):
                    self.all_slots.append((thu, 'sang', tiet))
            if cfg.get('co_chieu'):
                for tiet in range(1, cfg.get('so_tiet_chieu', 3) + 1):
                    self.all_slots.append((thu, 'chieu', tiet))

    def _load_tkb_hien_tai(self):
        """Load TKB đã có vào cache"""
        rows = self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nam_hoc_id == self.nam_hoc_id,
            ThoiKhoaBieu.hoc_ky_id == self.hoc_ky_id,
            ThoiKhoaBieu.is_active == True,
        ).all()
        for r in rows:
            self.tkb_lop[(r.lop_hoc_id, r.thu, r.buoi, r.tiet)] = r.mon_hoc_id
            self.tkb_gv[(r.giao_vien_id, r.thu, r.buoi, r.tiet)] = True

            # Cập nhật số tiết/ngày cho lớp
            key_ngay = (r.lop_hoc_id, r.thu)
            self.tiet_ngay[key_ngay] = self.tiet_ngay.get(key_ngay, 0) + 1

            # Cập nhật số tiết/ngày cho GV
            key_gv_ngay = (r.giao_vien_id, r.thu)
            self.tiet_gv_ngay[key_gv_ngay] = self.tiet_gv_ngay.get(key_gv_ngay, 0) + 1

    # ══ THUẬT TOÁN CHÍNH ════════════════════════════════════

    def run(self, clear_old: bool = False) -> dict:
        """Chạy thuật toán xếp TKB"""
        if clear_old:
            self._xoa_tkb_cu()

        jobs = self._build_job_list()
        self.total_jobs = sum(j['so_tiet'] for j in jobs)
        jobs = self._sort_jobs(jobs)

        logger.info(f"Bắt đầu xếp TKB: {len(jobs)} môn, {self.total_jobs} tiết")

        for job in jobs:
            self._xep_mon(job)

        self.session.commit()

        logger.info(f"Xếp TKB hoàn tất: {self.success_count}/{self.total_jobs} tiết")

        return {
            "success": self.success_count,
            "errors": self.errors,
            "total_jobs": self.total_jobs,
        }

    def _xoa_tkb_cu(self):
        """Xóa TKB cũ"""
        self.session.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nam_hoc_id == self.nam_hoc_id,
            ThoiKhoaBieu.hoc_ky_id == self.hoc_ky_id,
        ).delete()
        self.session.flush()
        self.tkb_lop.clear()
        self.tkb_gv.clear()
        self.tiet_ngay.clear()
        self.tiet_gv_ngay.clear()

    def _build_job_list(self) -> List[dict]:
        """Tạo danh sách: mỗi job = 1 môn + 1 lớp + GV + số tiết"""
        pcs = self.session.query(PhanCongGiangDay).filter(
            PhanCongGiangDay.nam_hoc_id == self.nam_hoc_id,
            PhanCongGiangDay.hoc_ky_id == self.hoc_ky_id,
        ).all()

        jobs = []
        for pc in pcs:
            lop = pc.lop_hoc
            mon = pc.mon_hoc
            gv = pc.giao_vien
            if not lop or not mon or not gv:
                continue

            mk = self.session.query(MonHocKhoi).filter(
                MonHocKhoi.mon_hoc_id == mon.id,
                MonHocKhoi.khoi == lop.khoi,
            ).first()
            so_tiet = mk.so_tiet if mk else 1

            jobs.append({
                'lop_id': lop.id,
                'ten_lop': lop.ten_lop,
                'mon_id': mon.id,
                'ten_mon': mon.ten_mon,
                'gv_id': gv.id,
                'ten_gv': gv.nguoi_dung.ho_ten if gv.nguoi_dung else '',
                'so_tiet': so_tiet,
                'khoi': lop.khoi,
                'phan_mon_id': pc.phan_mon_id,
            })
        return jobs

    def _sort_jobs(self, jobs: List[dict]) -> List[dict]:
        """Môn nhiều ràng buộc nhất xếp trước để dễ tìm slot hơn"""
        def score(job):
            s = 0
            cfg_mon = self.cau_hinh_mon.get(job['mon_id'], {})
            if cfg_mon.get('chi_sang') or cfg_mon.get('chi_chieu'):
                s += 3
            if cfg_mon.get('khong_lien'):
                s += 2
            if cfg_mon.get('max_ngay', 0) > 0:
                s += 2
            if cfg_mon.get('yeu_cau_tiet_doi'):
                s += 5  # Ngữ Văn cần ưu tiên xếp trước
            cfg_gv = self.rang_buoc_gv.get(job['gv_id'], {})
            if cfg_gv.get('ngay_nghi'):
                s += len(cfg_gv['ngay_nghi'])
            if cfg_gv.get('chi_sang') or cfg_gv.get('chi_chieu'):
                s += 2
            if cfg_gv.get('max_tiet_ngay', 0) > 0:
                s += 1
            return -s  # Nhiều ràng buộc → xếp trước
        return sorted(jobs, key=score)

    def _xep_mon(self, job: dict):
        """Xếp một môn học"""
        cfg_mon = self.cau_hinh_mon.get(job['mon_id'], {})
        so_tiet = job['so_tiet']
        max_mon_ngay = cfg_mon.get('max_ngay', 0)
        max_mon_ngay = max_mon_ngay if max_mon_ngay > 0 else 1

        # ⭐ LOG để kiểm tra Ngữ Văn
        if cfg_mon.get('is_ngu_van'):
            print(f"📘 XẾP NGỮ VĂN: {job['ten_lop']} - {job['ten_mon']} ({so_tiet} tiết)")

        # ⭐ XỬ LÝ MÔN NGỮ VĂN: bắt buộc có 1 cặp tiết đôi
        if cfg_mon.get('yeu_cau_tiet_doi') and so_tiet >= 2:
            slot_doi = self._find_slot_doi(job)
            if slot_doi:
                self._place(job, slot_doi[0])
                self._place(job, slot_doi[1])
                so_tiet -= 2
                if cfg_mon.get('is_ngu_van'):
                    print(f"   ✅ Xếp tiết đôi Ngữ Văn: {slot_doi}")
            else:
                self.errors.append(
                    f"Không tìm được slot tiết đôi cho Ngữ Văn: {job['ten_lop']} - {job['ten_mon']}"
                )
                if cfg_mon.get('is_ngu_van'):
                    print(f"   ❌ Không tìm được slot tiết đôi!")

        # Cho phép tiết đôi (không bắt buộc) cho các môn khác
        elif cfg_mon.get('tiet_doi') and so_tiet >= 2:
            slot_doi = self._find_slot_doi(job)
            if slot_doi:
                self._place(job, slot_doi[0])
                self._place(job, slot_doi[1])
                so_tiet -= 2

        # Xếp các tiết còn lại
        for i in range(so_tiet):
            slot = self._find_slot(job, max_mon_override=max_mon_ngay)
            if slot:
                self._place(job, slot)
                if cfg_mon.get('is_ngu_van'):
                    print(f"   ✅ Xếp tiết lẻ Ngữ Văn: {slot}")
            else:
                self.errors.append(
                    f"Không tìm được slot: {job['ten_lop']} - "
                    f"{job['ten_mon']} ({job['ten_gv']})"
                )
                logger.warning(f"❌ Không xếp được: {job['ten_lop']} - {job['ten_mon']}")

    # ══ TÌM SLOT ════════════════════════════════════════════

    def _find_slot(self, job: dict, max_mon_override: int = None) -> Optional[Tuple]:
        """Tìm một slot trống cho tiết học"""
        gv_id = job['gv_id']
        lop_id = job['lop_id']
        mon_id = job['mon_id']

        cfg_mon = self.cau_hinh_mon.get(mon_id, {})
        cfg_gv = self.rang_buoc_gv.get(gv_id, {})
        ngay_nghi_gv = cfg_gv.get('ngay_nghi', [])

        max_mon_ngay = max_mon_override if max_mon_override is not None \
                    else (cfg_mon.get('max_ngay', 0) if cfg_mon.get('max_ngay', 0) > 0 else 1)
        max_gv_ngay = cfg_gv.get('max_tiet_ngay', 0)

        slots = self._get_slots_ordered(gv_id, cfg_gv)
        # Lọc ra các slot không bị đánh dấu nghỉ hoặc cố định
        filtered_slots = []
        for (thu, buoi, tiet) in slots:
            # Kiểm tra ô nghỉ của lớp
            if (f'lop_{lop_id}', thu, buoi, tiet) in self.off_slots:
                continue
            # Kiểm tra ô nghỉ của GV
            if (f'gv_{gv_id}', thu, buoi, tiet) in self.off_slots:
                continue
            # Kiểm tra ô cố định của lớp
            if (f'lop_{lop_id}', thu, buoi, tiet) in self.fixed_slots:
                continue
            # Kiểm tra ô cố định của GV
            if (f'gv_{gv_id}', thu, buoi, tiet) in self.fixed_slots:
                continue
            filtered_slots.append((thu, buoi, tiet))

        slots = filtered_slots  # Gán lại danh sách đã lọc
        # Thống kê lý do bị loại để debug
        reject = {
            'ngay_nghi': 0, 'buoi_mon': 0, 'buoi_gv': 0,
            'lop_busy': 0, 'gv_busy': 0, 'max_tiet_ngay': 0,
            'max_mon_ngay': 0, 'max_gv_ngay': 0, 'lien_tiet': 0,
            'gdtc': 0, 'ngu_van': 0
        }

        for (thu, buoi, tiet) in slots:
            # Kiểm tra ngày nghỉ của GV
            if thu in ngay_nghi_gv:
                reject['ngay_nghi'] += 1
                continue

            # ⭐ RÀNG BUỘC MÔN GDTC
            if cfg_mon.get('is_gdtc'):
                if buoi == 'sang' and tiet == 5:
                    reject['gdtc'] += 1
                    continue
                if buoi == 'chieu' and tiet == 1:
                    reject['gdtc'] += 1
                    continue

            # Kiểm tra buổi của môn
            if cfg_mon.get('chi_sang') and buoi != 'sang':
                reject['buoi_mon'] += 1
                continue
            if cfg_mon.get('chi_chieu') and buoi != 'chieu':
                reject['buoi_mon'] += 1
                continue

            # Kiểm tra buổi của GV
            if cfg_gv.get('chi_sang') and buoi != 'sang':
                reject['buoi_gv'] += 1
                continue
            if cfg_gv.get('chi_chieu') and buoi != 'chieu':
                reject['buoi_gv'] += 1
                continue

            # Kiểm tra lớp trống
            if (lop_id, thu, buoi, tiet) in self.tkb_lop:
                reject['lop_busy'] += 1
                continue

            # Kiểm tra GV trống
            if (gv_id, thu, buoi, tiet) in self.tkb_gv:
                reject['gv_busy'] += 1
                continue

            # Kiểm tra số tiết tối đa của lớp trong ngày (7 tiết)
            if self.tiet_ngay.get((lop_id, thu), 0) >= 7:
                reject['max_tiet_ngay'] += 1
                continue

            # Kiểm tra số tiết tối đa của môn trong ngày
            tiet_mon_ngay = sum(
                1 for (l, t, b, tt), mid in self.tkb_lop.items()
                if l == lop_id and t == thu and mid == mon_id
            )
            if tiet_mon_ngay >= max_mon_ngay:
                reject['max_mon_ngay'] += 1
                continue

            # Kiểm tra số tiết tối đa của GV trong ngày
            if max_gv_ngay > 0:
                tiet_gv_ngay = self.tiet_gv_ngay.get((gv_id, thu), 0)
                if tiet_gv_ngay >= max_gv_ngay:
                    reject['max_gv_ngay'] += 1
                    continue

            # Kiểm tra không liên tiết
            if cfg_mon.get('khong_lien'):
                if not self._check_khong_lien_tiet(lop_id, mon_id, thu, buoi, tiet):
                    reject['lien_tiet'] += 1
                    continue

            # ⭐ RÀNG BUỘC MÔN NGỮ VĂN
            if cfg_mon.get('is_ngu_van'):
                if not self._check_ngu_van_vi_tri(lop_id, mon_id, thu, buoi, tiet):
                    reject['ngu_van'] += 1
                    continue

            return (thu, buoi, tiet)

        return None

    def _find_slot_doi(self, job: dict) -> Optional[Tuple[Tuple, Tuple]]:
        """Tìm 2 slot liên tiếp cho tiết đôi"""
        gv_id = job['gv_id']
        lop_id = job['lop_id']
        mon_id = job['mon_id']
        cfg_mon = self.cau_hinh_mon.get(mon_id, {})
        cfg_gv = self.rang_buoc_gv.get(gv_id, {})
        ngay_nghi_gv = cfg_gv.get('ngay_nghi', [])

        # Xây dựng danh sách ngày/buổi có học
        ngay_buoi = []
        for thu in range(2, 8):
            cfg_ngay = self.cau_hinh_ngay.get(thu, {})
            if cfg_ngay.get('co_sang'):
                so_tiet = cfg_ngay.get('so_tiet_sang', 5)
                if cfg_mon.get('is_gdtc'):
                    so_tiet = min(so_tiet, 4)
                ngay_buoi.append((thu, 'sang', so_tiet, 1))
            if cfg_ngay.get('co_chieu'):
                so_tiet = cfg_ngay.get('so_tiet_chieu', 3)
                start_tiet = 2 if cfg_mon.get('is_gdtc') else 1
                ngay_buoi.append((thu, 'chieu', so_tiet, start_tiet))
        random.shuffle(ngay_buoi)

        for thu, buoi, so_tiet_buoi, start_tiet in ngay_buoi:
            # Kiểm tra ràng buộc
            if thu in ngay_nghi_gv:
                continue
            if cfg_mon.get('chi_sang') and buoi != 'sang':
                continue
            if cfg_mon.get('chi_chieu') and buoi != 'chieu':
                continue
            if cfg_gv.get('chi_sang') and buoi != 'sang':
                continue
            if cfg_gv.get('chi_chieu') and buoi != 'chieu':
                continue

            # Tìm 2 tiết liên tiếp trống
            for tiet in range(start_tiet, so_tiet_buoi):
                slot1 = (thu, buoi, tiet)
                slot2 = (thu, buoi, tiet + 1)

                # ⭐ KIỂM TRA Ô NGHỈ (off_slots)
                if (f'lop_{lop_id}', thu, buoi, tiet) in self.off_slots:
                    continue
                if (f'lop_{lop_id}', thu, buoi, tiet + 1) in self.off_slots:
                    continue
                if (f'gv_{gv_id}', thu, buoi, tiet) in self.off_slots:
                    continue
                if (f'gv_{gv_id}', thu, buoi, tiet + 1) in self.off_slots:
                    continue

                # ⭐ KIỂM TRA Ô CỐ ĐỊNH (fixed_slots)
                if (f'lop_{lop_id}', thu, buoi, tiet) in self.fixed_slots:
                    continue
                if (f'lop_{lop_id}', thu, buoi, tiet + 1) in self.fixed_slots:
                    continue
                if (f'gv_{gv_id}', thu, buoi, tiet) in self.fixed_slots:
                    continue
                if (f'gv_{gv_id}', thu, buoi, tiet + 1) in self.fixed_slots:
                    continue

                # Kiểm tra GDTC
                if cfg_mon.get('is_gdtc'):
                    if buoi == 'sang' and (tiet >= 5 or tiet + 1 > 4):
                        continue
                    if buoi == 'chieu' and tiet < 2:
                        continue

                # Kiểm tra Ngữ Văn: không xếp tiết đôi ở ngày đã có tiết đôi
                if cfg_mon.get('is_ngu_van'):
                    if not self._check_ngu_van_vi_tri(lop_id, mon_id, thu, buoi, tiet):
                        continue
                    if not self._check_ngu_van_vi_tri(lop_id, mon_id, thu, buoi, tiet + 1):
                        continue

                # Kiểm tra cả 2 slot đều trống
                if (lop_id, thu, buoi, tiet) in self.tkb_lop:
                    continue
                if (lop_id, thu, buoi, tiet + 1) in self.tkb_lop:
                    continue
                if (gv_id, thu, buoi, tiet) in self.tkb_gv:
                    continue
                if (gv_id, thu, buoi, tiet + 1) in self.tkb_gv:
                    continue

                return (slot1, slot2)

        return None

    def _get_slots_ordered(self, gv_id: int, cfg_gv: dict) -> List[Tuple]:
        """Trả về danh sách slot đã shuffle"""
        if cfg_gv.get('gom_tiet'):
            ngay_co_tiet = set(thu for (g, thu, b, t) in self.tkb_gv if g == gv_id)
            priority = [s for s in self.all_slots if s[0] in ngay_co_tiet]
            rest = [s for s in self.all_slots if s[0] not in ngay_co_tiet]
            random.shuffle(priority)
            random.shuffle(rest)
            return priority + rest

        slots = list(self.all_slots)
        random.shuffle(slots)
        return slots

    def _check_khong_lien_tiet(self, lop_id: int, mon_id: int,
                                thu: int, buoi: str, tiet: int) -> bool:
        """Kiểm tra không xếp 2 tiết liên tiếp cùng môn cùng lớp"""
        if tiet > 1:
            mon_prev = self.tkb_lop.get((lop_id, thu, buoi, tiet - 1))
            if mon_prev == mon_id:
                return False
        mon_next = self.tkb_lop.get((lop_id, thu, buoi, tiet + 1))
        if mon_next == mon_id:
            return False
        return True

    def _check_ngu_van_vi_tri(self, lop_id: int, mon_id: int,
                               thu: int, buoi: str, tiet: int) -> bool:
        """
        Kiểm tra vị trí xếp Ngữ Văn:
        1. Không xếp tiết đôi ở ngày đã có tiết đôi Ngữ Văn
        2. Không xếp quá 2 tiết Ngữ Văn trong 1 ngày
        """
        # Lấy tất cả tiết Ngữ Văn đã xếp trong ngày này
        mon_trong_ngay = []
        for (l, t, b, tt), mid in self.tkb_lop.items():
            if l == lop_id and t == thu and mid == mon_id:
                mon_trong_ngay.append(tt)

        # Nếu đã có 2 tiết trong ngày → không xếp thêm
        if len(mon_trong_ngay) >= 2:
            return False

        # Kiểm tra xem đã có cặp tiết đôi nào trong ngày chưa
        co_cap_tiet_doi = False
        for i in range(1, 6):
            if i in mon_trong_ngay and (i + 1) in mon_trong_ngay:
                co_cap_tiet_doi = True
                break

        # Nếu đã có cặp tiết đôi → không xếp thêm tiết nào
        if co_cap_tiet_doi:
            return False

        # Nếu chưa có cặp tiết đôi:
        # - Chưa có tiết nào trong ngày → cho phép
        if len(mon_trong_ngay) == 0:
            return True

        # - Chỉ cho phép nếu tiết mới tạo thành cặp tiết đôi
        if (tiet - 1) in mon_trong_ngay or (tiet + 1) in mon_trong_ngay:
            return True

        return False

    def _place(self, job: dict, slot: Tuple):
        """Đặt tiết vào slot và cập nhật cache"""
        thu, buoi, tiet = slot
        lop_id = job['lop_id']
        gv_id = job['gv_id']

        o = ThoiKhoaBieu(
            nam_hoc_id=self.nam_hoc_id,
            hoc_ky_id=self.hoc_ky_id,
            lop_hoc_id=lop_id,
            giao_vien_id=gv_id,
            mon_hoc_id=job['mon_id'],
            phan_mon_id=job.get('phan_mon_id'),
            thu=thu, buoi=buoi, tiet=tiet,
            is_active=True,
        )
        self.session.add(o)
        self.session.flush()

        self.tkb_lop[(lop_id, thu, buoi, tiet)] = job['mon_id']
        self.tkb_gv[(gv_id, thu, buoi, tiet)] = True

        key_ngay = (lop_id, thu)
        self.tiet_ngay[key_ngay] = self.tiet_ngay.get(key_ngay, 0) + 1

        key_gv_ngay = (gv_id, thu)
        self.tiet_gv_ngay[key_gv_ngay] = self.tiet_gv_ngay.get(key_gv_ngay, 0) + 1

        self.success_count += 1