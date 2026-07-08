# modules/reports/service.py
from typing import Optional, List
from sqlalchemy.orm import Session
import json

from modules.thi_dua_hoc_sinh.service import ThiDuaHocSinhService
from modules.thi_dua_hoc_sinh.models.thang_thi_dua import ThangThiDua
from modules.thi_dua_hoc_sinh.models.thang_diem_chi_tiet import ThangDiemChiTiet
from modules.thi_dua_hoc_sinh.models.hoc_ky import ThiDuaHocKy
from modules.thi_dua_hoc_sinh.models.hoc_ky_diem_chi_tiet import ThiDuaHocKyDiemChiTiet
from modules.thi_dua_hoc_sinh.models.tap_the_vi_pham import TapTheViPham
from modules.thi_dua_hoc_sinh.models.hoc_sinh_vi_pham import HocSinhViPham
from core.db.models.lop_hoc import LopHoc
from core.db.models.nam_hoc import NamHoc
from core.db.models.giao_vien import GiaoVien
from shared.dto.result import ServiceResult
from .schemas import ReportResponse, ReportItem, ReportStats, ReportFilter


class ReportService:
    def __init__(self, session: Session):
        self.session = session
        self.thi_dua_service = ThiDuaHocSinhService(session)

    # ════════════════════════════════════════════════════════════
    # ══ MAIN ════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════

    def get_report(self, filter_data: ReportFilter) -> ServiceResult:
        try:
            loai = filter_data.loai

            if not filter_data.nam_hoc_id:
                nam_hoc = self.session.query(NamHoc).filter(NamHoc.active == True).first()
                if nam_hoc:
                    filter_data.nam_hoc_id = nam_hoc.id
                else:
                    return ServiceResult(ok=False, error="Không có năm học nào đang active")

            if loai == 'tuan' and not filter_data.tuan:
                from datetime import datetime
                today = datetime.now()
                start_date = datetime(today.year, 9, 1)
                delta = today - start_date
                tuan = max(1, min(52, (delta.days // 7) + 1))
                filter_data.tuan = tuan

            dispatch = {
                'tuan':     self._report_tuan,
                'thang':    self._report_thang,
                'hoc_ky':   self._report_hoc_ky,
                'nam_hoc':  self._report_nam_hoc,
                'ca_nhan':  self._report_ca_nhan,
                'giao_vien':self._report_giao_vien,
            }
            handler = dispatch.get(loai)
            if not handler:
                return ServiceResult(ok=False, error=f"Loại báo cáo '{loai}' không hỗ trợ")
            return handler(filter_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))

    # ════════════════════════════════════════════════════════════
    # ══ BÁO CÁO TUẦN — real-time từ lay_diem_tuan() ════════════
    # ════════════════════════════════════════════════════════════

    def _report_tuan(self, filter_data: ReportFilter) -> ServiceResult:
        if not filter_data.nam_hoc_id or not filter_data.tuan:
            return ServiceResult(ok=False, error="Thiếu năm học hoặc tuần")

        result = self.thi_dua_service.lay_diem_tuan(
            filter_data.nam_hoc_id, filter_data.tuan
        )
        if not result.ok:
            return result

        data = result.data

        # Đếm vi phạm / thành tích
        for item in data:
            lop_id = item.get('lop_hoc_id')
            if lop_id:
                counts = self._count_vi_pham_tuan(
                    lop_id, filter_data.nam_hoc_id, filter_data.tuan
                )
                item.update(counts)

        data = self._enrich_data(data, filter_data.nam_hoc_id)

        if filter_data.khoi:
            data = [i for i in data if i.get('khoi') == filter_data.khoi]

        data.sort(key=lambda x: x.get('trung_binh', 0), reverse=True)
        for idx, item in enumerate(data):
            item['xep_hang'] = idx + 1

        nam_hoc = self.session.query(NamHoc).filter(
            NamHoc.id == filter_data.nam_hoc_id
        ).first()

        return ServiceResult(ok=True, data=ReportResponse(
            loai='tuan',
            ten_bao_cao=f"Báo cáo thi đua tuần {filter_data.tuan}",
            nam_hoc=nam_hoc.ten_nam_hoc if nam_hoc else None,
            tuan=filter_data.tuan,
            stats=self._calculate_stats(data),
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    # ════════════════════════════════════════════════════════════
    # ══ BÁO CÁO THÁNG — đọc ThangDiemChiTiet ══════════════════
    # ════════════════════════════════════════════════════════════

    def _report_thang(self, filter_data: ReportFilter) -> ServiceResult:
        if not filter_data.thang_id:
            return ServiceResult(ok=False, error="Thiếu ID tháng")

        thang = self.session.query(ThangThiDua).filter(
            ThangThiDua.id == filter_data.thang_id
        ).first()
        if not thang:
            return ServiceResult(ok=False, error="Không tìm thấy tháng")

        tuan_list = json.loads(thang.tuan_list) if thang.tuan_list else []
        if not tuan_list:
            return ServiceResult(ok=False, error="Tháng chưa có tuần nào")

        # ✅ Đọc thẳng từ ThangDiemChiTiet — cùng nguồn với get_bao_cao_thang()
        chi_tiet_list = self.session.query(ThangDiemChiTiet).filter(
            ThangDiemChiTiet.thang_id == filter_data.thang_id
        ).all()

        if not chi_tiet_list:
            return ServiceResult(
                ok=False,
                error="Chưa có dữ liệu điểm tháng. Vui lòng cập nhật điểm tháng trước."
            )

        # Gom theo lớp — tính trung bình các tuần
        data_map: dict = {}
        for row in chi_tiet_list:
            lop_id = row.lop_hoc_id
            if lop_id not in data_map:
                data_map[lop_id] = {
                    'lop_hoc_id': lop_id,
                    'tong_tb_tuan': 0.0,
                    'count': 0,
                }
            data_map[lop_id]['tong_tb_tuan'] += row.diem_trung_binh_tuan
            data_map[lop_id]['count'] += 1

        # ✅ trung_binh tháng = TB của các TB tuần
        #    (đúng vì ThangDiemChiTiet.diem_trung_binh_tuan đã dùng công thức ((ht*2)+doi)/3 )
        data = []
        for lop_id, acc in data_map.items():
            count = acc['count']
            tb = round(acc['tong_tb_tuan'] / count, 3) if count else 0.0
            data.append({
                'lop_hoc_id': lop_id,
                'trung_binh': tb,
            })

        # Đếm vi phạm cộng dồn từng tuần
        for item in data:
            lop_id = item['lop_hoc_id']
            tong_vp = tong_tt = 0
            for tuan in tuan_list:
                counts = self._count_vi_pham_tuan(lop_id, thang.nam_hoc_id, tuan)
                tong_vp += counts['so_vi_pham']
                tong_tt += counts['so_thanh_tich']
            item['so_vi_pham'] = tong_vp
            item['so_thanh_tich'] = tong_tt

        data = self._enrich_data(data, thang.nam_hoc_id)

        if filter_data.khoi:
            data = [i for i in data if i.get('khoi') == filter_data.khoi]

        data.sort(key=lambda x: x.get('trung_binh', 0), reverse=True)
        for idx, item in enumerate(data):
            item['xep_hang'] = idx + 1

        return ServiceResult(ok=True, data=ReportResponse(
            loai='thang',
            ten_bao_cao=f"Báo cáo thi đua tháng: {thang.ten_thang}",
            thang=thang.ten_thang,
            stats=self._calculate_stats(data),
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    # ════════════════════════════════════════════════════════════
    # ══ BÁO CÁO HỌC KỲ — đọc ThiDuaHocKyDiemChiTiet ══════════
    # ════════════════════════════════════════════════════════════

    def _report_hoc_ky(self, filter_data: ReportFilter) -> ServiceResult:
        if not filter_data.hoc_ky_id:
            return ServiceResult(ok=False, error="Thiếu ID học kỳ")

        hoc_ky = self.session.query(ThiDuaHocKy).filter(
            ThiDuaHocKy.id == filter_data.hoc_ky_id
        ).first()
        if not hoc_ky:
            return ServiceResult(ok=False, error="Không tìm thấy học kỳ")

        thang_list = json.loads(hoc_ky.thang_list) if hoc_ky.thang_list else []
        if not thang_list:
            return ServiceResult(ok=False, error="Học kỳ chưa có tháng nào")

        # ✅ Đọc thẳng từ ThiDuaHocKyDiemChiTiet
        chi_tiet_list = self.session.query(ThiDuaHocKyDiemChiTiet).filter(
            ThiDuaHocKyDiemChiTiet.hoc_ky_id == filter_data.hoc_ky_id
        ).all()

        if not chi_tiet_list:
            return ServiceResult(
                ok=False,
                error="Chưa có dữ liệu điểm học kỳ. Vui lòng cập nhật điểm học kỳ trước."
            )

        # Gom theo lớp — mỗi row là điểm TB một tháng
        data_map: dict = {}
        for row in chi_tiet_list:
            lop_id = row.lop_hoc_id
            if lop_id not in data_map:
                data_map[lop_id] = {
                    'lop_hoc_id': lop_id,
                    'tong_tb_thang': 0.0,
                    'so_vi_pham': 0,
                    'so_thanh_tich': 0,
                    'count': 0,
                }
            data_map[lop_id]['tong_tb_thang'] += row.diem_trung_binh_thang
            data_map[lop_id]['count'] += 1

        # Vi phạm: cộng dồn qua các tháng → tuần
        thang_tuan_map = self._build_thang_tuan_map(thang_list)
        for lop_id, acc in data_map.items():
            tong_vp = tong_tt = 0
            for thang_id, tuan_list in thang_tuan_map.items():
                for tuan in tuan_list:
                    counts = self._count_vi_pham_tuan(lop_id, hoc_ky.nam_hoc_id, tuan)
                    tong_vp += counts['so_vi_pham']
                    tong_tt += counts['so_thanh_tich']
            acc['so_vi_pham'] = tong_vp
            acc['so_thanh_tich'] = tong_tt

        data = []
        for lop_id, acc in data_map.items():
            count = acc['count']
            data.append({
                'lop_hoc_id': lop_id,
                'trung_binh': round(acc['tong_tb_thang'] / count, 3) if count else 0.0,
                'so_vi_pham': acc['so_vi_pham'],
                'so_thanh_tich': acc['so_thanh_tich'],
            })

        data = self._enrich_data(data, hoc_ky.nam_hoc_id)

        if filter_data.khoi:
            data = [i for i in data if i.get('khoi') == filter_data.khoi]

        data.sort(key=lambda x: x.get('trung_binh', 0), reverse=True)
        for idx, item in enumerate(data):
            item['xep_hang'] = idx + 1

        return ServiceResult(ok=True, data=ReportResponse(
            loai='hoc_ky',
            ten_bao_cao=f"Báo cáo thi đua học kỳ: {hoc_ky.ten_hoc_ky}",
            hoc_ky=hoc_ky.ten_hoc_ky,
            stats=self._calculate_stats(data),
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    # ════════════════════════════════════════════════════════════
    # ══ BÁO CÁO NĂM HỌC ════════════════════════════════════════
    # ════════════════════════════════════════════════════════════

    def _report_nam_hoc(self, filter_data: ReportFilter) -> ServiceResult:
        if not filter_data.nam_hoc_id:
            return ServiceResult(ok=False, error="Thiếu năm học")

        hoc_ky_list = self.session.query(ThiDuaHocKy).filter(
            ThiDuaHocKy.nam_hoc_id == filter_data.nam_hoc_id,
            ThiDuaHocKy.is_active == True
        ).all()

        if not hoc_ky_list:
            return ServiceResult(ok=False, error="Chưa có học kỳ nào trong năm học này")

        # ✅ Gom điểm TB học kỳ cho từng lớp
        data_map: dict = {}
        for hoc_ky in hoc_ky_list:
            thang_list = json.loads(hoc_ky.thang_list) if hoc_ky.thang_list else []

            chi_tiet_list = self.session.query(ThiDuaHocKyDiemChiTiet).filter(
                ThiDuaHocKyDiemChiTiet.hoc_ky_id == hoc_ky.id
            ).all()

            # TB học kỳ của từng lớp = TB các diem_trung_binh_thang
            tb_hoc_ky_map: dict = {}
            count_map: dict = {}
            for row in chi_tiet_list:
                lop_id = row.lop_hoc_id
                tb_hoc_ky_map.setdefault(lop_id, 0.0)
                count_map.setdefault(lop_id, 0)
                tb_hoc_ky_map[lop_id] += row.diem_trung_binh_thang
                count_map[lop_id] += 1

            for lop_id, tong in tb_hoc_ky_map.items():
                tb = round(tong / count_map[lop_id], 3) if count_map[lop_id] else 0.0
                if lop_id not in data_map:
                    data_map[lop_id] = {
                        'lop_hoc_id': lop_id,
                        'tong_tb_hoc_ky': 0.0,
                        'so_vi_pham': 0,
                        'so_thanh_tich': 0,
                        'count': 0,
                    }
                data_map[lop_id]['tong_tb_hoc_ky'] += tb
                data_map[lop_id]['count'] += 1

            # Vi phạm cộng dồn
            thang_tuan_map = self._build_thang_tuan_map(
                [t for t in json.loads(hoc_ky.thang_list)] if hoc_ky.thang_list else []
            )
            for lop_id in data_map:
                for tuan_list in thang_tuan_map.values():
                    for tuan in tuan_list:
                        counts = self._count_vi_pham_tuan(
                            lop_id, filter_data.nam_hoc_id, tuan
                        )
                        data_map[lop_id]['so_vi_pham'] += counts['so_vi_pham']
                        data_map[lop_id]['so_thanh_tich'] += counts['so_thanh_tich']

        data = []
        for lop_id, acc in data_map.items():
            count = acc['count']
            data.append({
                'lop_hoc_id': lop_id,
                'trung_binh': round(acc['tong_tb_hoc_ky'] / count, 3) if count else 0.0,
                'so_vi_pham': acc['so_vi_pham'],
                'so_thanh_tich': acc['so_thanh_tich'],
            })

        data = self._enrich_data(data, filter_data.nam_hoc_id)

        if filter_data.khoi:
            data = [i for i in data if i.get('khoi') == filter_data.khoi]

        data.sort(key=lambda x: x.get('trung_binh', 0), reverse=True)
        for idx, item in enumerate(data):
            item['xep_hang'] = idx + 1

        nam_hoc = self.session.query(NamHoc).filter(
            NamHoc.id == filter_data.nam_hoc_id
        ).first()

        return ServiceResult(ok=True, data=ReportResponse(
            loai='nam_hoc',
            ten_bao_cao=f"Báo cáo thi đua năm học {nam_hoc.ten_nam_hoc if nam_hoc else ''}",
            nam_hoc=nam_hoc.ten_nam_hoc if nam_hoc else None,
            stats=self._calculate_stats(data),
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    # ════════════════════════════════════════════════════════════
    # ══ BÁO CÁO CÁ NHÂN & GIÁO VIÊN (giữ nguyên) ═════════════
    # ════════════════════════════════════════════════════════════

    def _report_ca_nhan(self, filter_data: ReportFilter) -> ServiceResult:
        if not filter_data.lop_hoc_id:
            return ServiceResult(ok=False, error="Thiếu lớp học")

        result = self.thi_dua_service.bao_cao_ca_nhan_theo_lop(
            filter_data.lop_hoc_id,
            filter_data.nam_hoc_id or 0,
            filter_data.tuan
        )
        if not result.ok:
            return result

        data = result.data
        stats = ReportStats(
            tong_hs=len(data),
            tong_vi_pham=sum(item.get('so_vi_pham', 0) for item in data),
            tong_thanh_tich=sum(item.get('so_thanh_tich', 0) for item in data),
        )
        return ServiceResult(ok=True, data=ReportResponse(
            loai='ca_nhan',
            ten_bao_cao="Báo cáo vi phạm cá nhân",
            stats=stats,
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    def _report_giao_vien(self, filter_data: ReportFilter) -> ServiceResult:
        query = self.session.query(GiaoVien).filter(GiaoVien.active == True)
        if filter_data.khoi:
            query = query.filter(GiaoVien.khoi == filter_data.khoi)

        data = []
        for gv in query.all():
            so_lop = self.session.query(LopHoc).filter(
                LopHoc.giao_vien_cn_id == gv.id
            ).count()
            data.append({
                'giao_vien_id': gv.id,
                'ten_giao_vien': gv.nguoi_dung.ho_ten if gv.nguoi_dung else '',
                'ma_giao_vien': gv.ma_giao_vien,
                'so_lop_chu_nhiem': so_lop,
                'mon_day': gv.mon_day,
                'to_chuyen_mon': gv.to_chuyen_mon.ten_to if gv.to_chuyen_mon else '',
            })

        return ServiceResult(ok=True, data=ReportResponse(
            loai='giao_vien',
            ten_bao_cao="Báo cáo giáo viên chủ nhiệm",
            stats=ReportStats(tong_gv=len(data)),
            data=[ReportItem(**item) for item in data]
        ).model_dump())

    # ════════════════════════════════════════════════════════════
    # ══ HELPER ══════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════

    def _count_vi_pham_tuan(self, lop_id: int, nam_hoc_id: int, tuan: int) -> dict:
        """Đếm vi phạm / thành tích của một lớp trong một tuần"""
        tap_the = self.session.query(TapTheViPham).filter(
            TapTheViPham.lop_hoc_id == lop_id,
            TapTheViPham.nam_hoc_id == nam_hoc_id,
            TapTheViPham.tuan == tuan
        ).all()

        hs_vp = self.session.query(HocSinhViPham).join(
            HocSinhViPham.hoc_sinh
        ).filter(
            HocSinhViPham.nam_hoc_id == nam_hoc_id,
            HocSinhViPham.tuan == tuan,
            HocSinhViPham.hoc_sinh.has(lop_hoc_id=lop_id)
        ).all()

        all_vp = tap_the + hs_vp
        return {
            'so_vi_pham':   sum(1 for v in all_vp if v.so_diem < 0),
            'so_thanh_tich': sum(1 for v in all_vp if v.so_diem > 0),
        }

    def _build_thang_tuan_map(self, thang_id_list: list) -> dict:
        """Trả về {thang_id: [tuan1, tuan2, ...]} để duyệt vi phạm"""
        result = {}
        for thang_id in thang_id_list:
            thang = self.session.query(ThangThiDua).filter(
                ThangThiDua.id == thang_id
            ).first()
            if thang:
                tuan_list = json.loads(thang.tuan_list) if thang.tuan_list else []
                result[thang_id] = tuan_list
        return result

    def _enrich_data(self, data: list, nam_hoc_id: int) -> list:
        """Thêm ten_lop, khoi, si_so, ten_gvcn vào từng item"""
        result = []
        for item in data:
            lop_id = item.get('lop_hoc_id')
            if lop_id:
                lop = self.session.query(LopHoc).filter(LopHoc.id == lop_id).first()
                if lop:
                    item.setdefault('ten_lop', lop.ten_lop)
                    item.setdefault('khoi', lop.khoi)
                    item['si_so'] = lop.si_so or 0
                    gv = self.session.query(GiaoVien).filter(
                        GiaoVien.id == lop.giao_vien_cn_id
                    ).first() if lop.giao_vien_cn_id else None
                    item['ten_gvcn'] = (
                        gv.nguoi_dung.ho_ten if gv and gv.nguoi_dung else None
                    )
                else:
                    item.setdefault('ten_lop', '')
                    item.setdefault('khoi', 0)
                    item['si_so'] = 0
                    item['ten_gvcn'] = None
            result.append(item)
        return result

    def _calculate_stats(self, data: list) -> ReportStats:
        if not data:
            return ReportStats()
        diem_list = [i.get('trung_binh', 0) for i in data if i.get('trung_binh') is not None]
        return ReportStats(
            tong_lop=len(data),
            tong_hs=sum(i.get('si_so', 0) for i in data),
            tong_vi_pham=sum(i.get('so_vi_pham', 0) for i in data),
            tong_thanh_tich=sum(i.get('so_thanh_tich', 0) for i in data),
            diem_cao_nhat=max(diem_list) if diem_list else 0,
            diem_thap_nhat=min(diem_list) if diem_list else 0,
            diem_trung_binh=round(sum(diem_list) / len(diem_list), 3) if diem_list else 0,
        )