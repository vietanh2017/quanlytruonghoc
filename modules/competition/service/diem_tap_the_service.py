# modules/competition/service/diem_tap_the_service.py

from core.db.session import SessionLocal
from modules.competition.repository.diem_tap_the_repository import DiemTapTheRepository
from modules.competition.repository.diem_doi_ngay_repository import DiemDoiNgayRepository
from modules.lop_hoc.repository import LopHocRepository
from shared.dto.result import ServiceResult


class DiemTapTheService:
    def __init__(self):
        self.session = SessionLocal()
        self.repo = DiemTapTheRepository(self.session)
        self.lop_repo = LopHocRepository(self.session)
        self.diem_doi_ngay_repo = DiemDoiNgayRepository(self.session)  # ← THÊM

    def close(self):
        self.session.close()

    def get_ds_lop_theo_nam_hoc(self, nam_hoc_id: int):
        try:
            ds_lop = self.lop_repo.get_by_nam_hoc(nam_hoc_id)
            return ServiceResult(ok=True, data=ds_lop)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def get_diem_tuan(self, nam_hoc_id: int, tuan: int):
        """Lấy tất cả điểm của 1 tuần (từ bảng diem_tap_the_lop)"""
        try:
            data = self.repo.get_all_by_nam_hoc_tuan(nam_hoc_id, tuan)
            result = {}
            for item in data:
                result[item.lop_hoc_id] = {
                    'diem_hoc_tap': item.diem_hoc_tap,
                    'diem_doi': item.diem_doi,
                    'ghi_chu': item.ghi_chu,
                    'da_khoa': item.da_khoa
                }
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def get_diem_doi_tuan_tu_ngay(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int):
        """Lấy điểm Đội trung bình tuần từ bảng diem_doi_ngay"""
        try:
            diem_tb = self.diem_doi_ngay_repo.get_trung_binh_tuan(nam_hoc_id, tuan, lop_hoc_id)
            return diem_tb
        except Exception as e:
            return 0
    # modules/competition/service/diem_tap_the_service.py

    def count_active_violations(self):
        """Đếm số lượng vi phạm đang active"""
        try:
            from modules.competition.models.loai_vi_pham import LoaiViPham
            count = self.session.query(LoaiViPham).filter(
                LoaiViPham.loai == "vi_pham",
                LoaiViPham.is_active == True
            ).count()
            return count if count > 0 else 8
        except:
            return 8  # Mặc định 8 nếu chưa có dữ liệu
        
    def get_diem_doi_tuan_all_lop(self, nam_hoc_id: int, tuan: int):
        ds_lop = self.lop_repo.get_by_nam_hoc(nam_hoc_id)
        so_luong_vp = self.count_active_violations()  # Lấy số lượng VP active
        
        result = {}
        for lop in ds_lop:
            diem = self.diem_doi_ngay_repo.get_trung_binh_tuan(
                nam_hoc_id, tuan, lop.id, so_luong_vp
            )
            result[lop.id] = diem
        return result
    
    def save_diem_tuan(self, nam_hoc_id: int, tuan: int, data: list, nguoi_nhap: str = ""):
        """Lưu điểm cho 1 tuần (chỉ lưu điểm học tập, điểm Đội đã tự động)"""
        try:
            # Chỉ cập nhật điểm học tập, giữ nguyên điểm Đội
            for item in data:
                record = self.repo.get_by_nam_hoc_tuan_lop(nam_hoc_id, tuan, item['lop_hoc_id'])
                if record:
                    record.diem_hoc_tap = item['diem_hoc_tap']
                    record.ghi_chu = item.get('ghi_chu', '')
                    record.updated_at = None
                else:
                    self.repo.create_or_update(
                        nam_hoc_id=nam_hoc_id,
                        tuan=tuan,
                        lop_hoc_id=item['lop_hoc_id'],
                        diem_hoc_tap=item['diem_hoc_tap'],
                        diem_doi=0,  # Điểm Đội sẽ được tính từ bảng diem_doi_ngay
                        ghi_chu=item.get('ghi_chu', ''),
                        nguoi_nhap=nguoi_nhap
                    )
            self.session.commit()
            return ServiceResult(ok=True, error="Đã lưu thành công")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))

    def tinh_tb_thang(self, nam_hoc_id: int, lop_hoc_id: int, weeks: list):
        try:
            tb = self.repo.get_tb_thang(nam_hoc_id, lop_hoc_id, weeks)
            return ServiceResult(ok=True, data=tb)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def get_weeks_have_data(self, nam_hoc_id: int, lop_hoc_id: int, weeks: list):
        try:
            weeks_data = self.repo.get_weeks_have_data_in_month(nam_hoc_id, lop_hoc_id, weeks)
            return ServiceResult(ok=True, data=weeks_data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def kiem_tra_da_khoa(self, nam_hoc_id: int, tuan: int):
        try:
            data = self.repo.get_all_by_nam_hoc_tuan(nam_hoc_id, tuan)
            for item in data:
                if item.da_khoa:
                    return ServiceResult(ok=True, data=True)
            return ServiceResult(ok=True, data=False)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))