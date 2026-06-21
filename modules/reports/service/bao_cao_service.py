# modules/reports/service/bao_cao_service.py

from core.db.session import SessionLocal
from modules.giao_vien.repository import GiaoVienRepository
from modules.lop_hoc.repository import LopHocRepository
from modules.lop_hoc.hoc_sinh_repository import HocSinhRepository
from modules.competition.service.diem_tap_the_service import DiemTapTheService
from modules.competition.repository.diem_doi_ngay_repository import DiemDoiNgayRepository
from modules.giao_vien_thi_dua.service.thi_dua_gv_service import ThiDuaGVService
from shared.dto.result import ServiceResult


class BaoCaoService:
    def __init__(self):
        self.session = SessionLocal()
        self.gv_repo = GiaoVienRepository(self.session)
        self.lop_repo = LopHocRepository(self.session)
        self.hs_repo = HocSinhRepository(self.session)
        self.tap_the_svc = DiemTapTheService()
        self.gv_thi_dua_svc = ThiDuaGVService()
        self.diem_doi_ngay_repo = DiemDoiNgayRepository(self.session)
    
    def close(self):
        self.session.close()
        self.tap_the_svc.close()
        self.gv_thi_dua_svc.close()
    
    # ==================== THỐNG KÊ TỔNG QUAN ====================
    
    def thong_ke_tong_quan(self, nam_hoc_id: int = None):
        """Lấy số liệu thống kê tổng quan"""
        try:
            from core.db.models.hoc_sinh import HocSinh
            from core.db.models.to_chuyen_mon import ToChuyenMon
            
            ds_gv = self.gv_repo.get_all()
            so_gv = len(ds_gv) if ds_gv else 0
            so_hs = self.session.query(HocSinh).filter(HocSinh.active == True).count()
            
            if nam_hoc_id:
                ds_lop = self.lop_repo.get_by_nam_hoc(nam_hoc_id)
            else:
                ds_lop = self.lop_repo.get_all()
            so_lop = len(ds_lop) if ds_lop else 0
            
            so_to = self.session.query(ToChuyenMon).filter(ToChuyenMon.active == True).count()
            
            return ServiceResult(ok=True, data={
                'so_giao_vien': so_gv,
                'so_hoc_sinh': so_hs,
                'so_lop': so_lop,
                'so_to_chuyen_mon': so_to,
            })
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    # ==================== XẾP HẠNG GIÁO VIÊN ====================
    
    def xep_hang_giao_vien(self, nam_hoc_id: int, hoc_ky_id: int = None, thang: int = None):
        """Lấy xếp hạng giáo viên theo điểm thực tế"""
        print(f"DEBUG xep_hang_lop: hoc_ky_id={hoc_ky_id}, thang={thang}")  # ← THÊM
        try:
            ds_gv = self.gv_repo.get_all()
            ket_qua = []
            
            for gv in ds_gv:
                ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else f"GV{gv.id}"
                
                # Tính điểm theo tháng, học kỳ, hoặc cả năm
                if thang:
                    # Tính điểm tháng
                    r = self.gv_thi_dua_svc.tinh_diem_thang(gv.id, thang, nam_hoc_id)
                    if r.ok:
                        diem = r.data["diem"]
                        xep_loai = self.gv_thi_dua_svc.xep_loai(diem)
                    else:
                        diem = 0
                        xep_loai = "Chưa chấm"
                elif hoc_ky_id is None:
                    # Cả năm: tính TBC của HK1 và HK2
                    r1 = self.gv_thi_dua_svc.tinh_diem_hoc_ky(gv.id, 1, nam_hoc_id)
                    r2 = self.gv_thi_dua_svc.tinh_diem_hoc_ky(gv.id, 2, nam_hoc_id)
                    diem1 = r1.data["diem"] if r1.ok else 0
                    diem2 = r2.data["diem"] if r2.ok else 0
                    diem = (diem1 + diem2) / 2 if (diem1 > 0 or diem2 > 0) else 0
                    xep_loai = self.gv_thi_dua_svc.xep_loai(diem)
                else:
                    # Tính điểm học kỳ
                    r = self.gv_thi_dua_svc.tinh_diem_hoc_ky(gv.id, hoc_ky_id, nam_hoc_id)
                    if r.ok:
                        diem = r.data["diem"]
                        xep_loai = r.data["xep_loai"]
                    else:
                        diem = 0
                        xep_loai = "Chưa có dữ liệu"
                
                ket_qua.append({
                    'id': gv.id,
                    'ma': gv.ma_giao_vien,
                    'ten': ten,
                    'diem': round(diem, 2),
                    'xep_loai': xep_loai
                })
            
            ket_qua.sort(key=lambda x: x['diem'], reverse=True)
            for i, item in enumerate(ket_qua):
                item['thu_hang'] = i + 1
            
            return ServiceResult(ok=True, data=ket_qua)
        except Exception as e:
            print(f"Lỗi xep_hang_giao_vien: {e}")
            return ServiceResult(ok=False, error=str(e))
    
    # ==================== XẾP HẠNG LỚP ====================
    
    def xep_hang_lop(self, nam_hoc_id: int, hoc_ky_id: int = None, thang: int = None):
        """Lấy xếp hạng lớp theo điểm thực tế"""
        try:
            ds_lop = self.lop_repo.get_by_nam_hoc(nam_hoc_id)
            ket_qua = []
            
            for lop in ds_lop:
                if thang:
                    # === TÍNH ĐIỂM THEO THÁNG ===
                    weeks = self._get_weeks_in_month(thang)
                    diem_list = []
                    for tuan in weeks:
                        diem_result = self.tap_the_svc.get_diem_tuan(nam_hoc_id, tuan)
                        diem_hoc = 0
                        diem_doi = 0
                        
                        if diem_result.ok and lop.id in diem_result.data:
                            diem_hoc = diem_result.data[lop.id].get('diem_hoc_tap', 0)
                            diem_doi = diem_result.data[lop.id].get('diem_doi', 0)
                        
                        diem_tb_tuan = (diem_hoc * 2 + diem_doi) / 3
                        diem_list.append(diem_tb_tuan)
                    
                    diem_tb = sum(diem_list) / len(diem_list) if diem_list else 0
                    
                elif hoc_ky_id == 3:
                    # === CẢ NĂM: TBC CỦA HK1 VÀ HK2 ===
                    # HK1 (tuần 1-18)
                    diem_hk1_list = []
                    for tuan in range(1, 19):
                        diem_result = self.tap_the_svc.get_diem_tuan(nam_hoc_id, tuan)
                        diem_hoc = 0
                        diem_doi = 0
                        
                        if diem_result.ok and lop.id in diem_result.data:
                            diem_hoc = diem_result.data[lop.id].get('diem_hoc_tap', 0)
                            diem_doi = diem_result.data[lop.id].get('diem_doi', 0)
                        
                        diem_tb_tuan = (diem_hoc * 2 + diem_doi) / 3
                        diem_hk1_list.append(diem_tb_tuan)
                    
                    tb_hk1 = sum(diem_hk1_list) / len(diem_hk1_list) if diem_hk1_list else 0
                    
                    # HK2 (tuần 19-35)
                    diem_hk2_list = []
                    for tuan in range(19, 36):
                        diem_result = self.tap_the_svc.get_diem_tuan(nam_hoc_id, tuan)
                        diem_hoc = 0
                        diem_doi = 0
                        
                        if diem_result.ok and lop.id in diem_result.data:
                            diem_hoc = diem_result.data[lop.id].get('diem_hoc_tap', 0)
                            diem_doi = diem_result.data[lop.id].get('diem_doi', 0)
                        
                        diem_tb_tuan = (diem_hoc * 2 + diem_doi) / 3
                        diem_hk2_list.append(diem_tb_tuan)
                    
                    tb_hk2 = sum(diem_hk2_list) / len(diem_hk2_list) if diem_hk2_list else 0
                    
                    # Cả năm = (HK1 + HK2) / 2
                    diem_tb = (tb_hk1 + tb_hk2) / 2
                    
                elif hoc_ky_id:
                    # === TÍNH ĐIỂM HỌC KỲ (HK1 hoặc HK2) ===
                    if hoc_ky_id == 1:
                        weeks = list(range(1, 19))
                    else:
                        weeks = list(range(19, 36))
                    
                    diem_list = []
                    for tuan in weeks:
                        diem_result = self.tap_the_svc.get_diem_tuan(nam_hoc_id, tuan)
                        diem_hoc = 0
                        diem_doi = 0
                        
                        if diem_result.ok and lop.id in diem_result.data:
                            diem_hoc = diem_result.data[lop.id].get('diem_hoc_tap', 0)
                            diem_doi = diem_result.data[lop.id].get('diem_doi', 0)
                        
                        diem_tb_tuan = (diem_hoc * 2 + diem_doi) / 3
                        diem_list.append(diem_tb_tuan)
                    
                    diem_tb = sum(diem_list) / len(diem_list) if diem_list else 0
                else:
                    diem_tb = 0
                
                ket_qua.append({
                    'id': lop.id,
                    'ma': lop.ma_lop,
                    'ten': lop.ten_lop,
                    'diem': diem_tb,
                    'si_so': lop.si_so
                })
            
            # Sắp xếp và xếp thứ
            ket_qua.sort(key=lambda x: x['diem'], reverse=True)
            rank = 1
            for i, item in enumerate(ket_qua):
                if i > 0 and item['diem'] < ket_qua[i-1]['diem']:
                    rank = i + 1
                item['thu_hang'] = rank
            
            return ServiceResult(ok=True, data=ket_qua)
        except Exception as e:
            print(f"Lỗi xep_hang_lop: {e}")
            return ServiceResult(ok=False, error=str(e))
        
    def _get_weeks_in_month(self, thang: int, phan: str = None) -> list:
        """
        Lấy danh sách tuần trong tháng
        thang: 9,10,11,12,1,2,3,4,5
        phan: 'a' hoặc 'b' (chỉ áp dụng cho tháng 1)
        """
        weeks_map = {
            9: [1, 2, 3, 4],
            10: [5, 6, 7, 8],
            11: [9, 10, 11, 12],
            12: [13, 14, 15, 16],
            '1a': [17, 18],  # HK1
            '1b': [19, 20],  # HK2
            2: [21, 22, 23, 24],
            3: [25, 26, 27, 28],
            4: [29, 30, 31, 32],
            5: [33, 34, 35],
        }
        
        if thang == 1 and phan:
            key = f"1{phan}"
            return weeks_map.get(key, [])
        
        return weeks_map.get(thang, [])