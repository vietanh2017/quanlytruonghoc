# modules/competition/service/diem_ca_nhan_service.py

from core.db.session import SessionLocal
from modules.competition.repository.loai_vi_pham_repository import LoaiViPhamRepository
from modules.competition.repository.hoc_sinh_vi_pham_repository import HocSinhViPhamRepository
from modules.competition.repository.diem_doi_ngay_repository import DiemDoiNgayRepository
from modules.lop_hoc.repository import LopHocRepository
from modules.lop_hoc.hoc_sinh_repository import HocSinhRepository
from modules.competition.repository.tap_the_vi_pham_repository import TapTheViPhamRepository
from modules.competition.repository.diem_tap_the_repository import DiemTapTheRepository
from shared.dto.result import ServiceResult
from datetime import datetime


class DiemCaNhanService:
    def __init__(self):
        self.session = SessionLocal()
        self.loai_vp_repo = LoaiViPhamRepository(self.session)
        self.hs_vp_repo = HocSinhViPhamRepository(self.session)
        self.tap_the_vp_repo = TapTheViPhamRepository(self.session)
        self.lop_repo = LopHocRepository(self.session)
        self.hs_repo = HocSinhRepository(self.session)
        self.diem_doi_ngay_repo = DiemDoiNgayRepository(self.session)
        self.diem_tap_the_repo = DiemTapTheRepository(self.session)  # ← THÊM
    
    def close(self):
        self.session.close()
    
    def get_ds_lop_theo_nam_hoc(self, nam_hoc_id: int):
        try:
            ds_lop = self.lop_repo.get_by_nam_hoc(nam_hoc_id)
            return ServiceResult(ok=True, data=ds_lop)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    def get_ds_hoc_sinh_theo_lop(self, lop_id: int):
        try:
            ds_hs = self.hs_repo.get_by_lop(lop_id)
            return ServiceResult(ok=True, data=ds_hs)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    def get_loai_vi_pham(self, loai: str = None):
        try:
            ds = self.loai_vp_repo.get_all(loai=loai)
            return ds
        except Exception as e:
            return []
    
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
            return 8
    
    def get_tong_diem_ca_nhan(self, hoc_sinh_id: int, nam_hoc_id: int, tuan: int = None):
        try:
            tong = self.hs_vp_repo.get_tong_diem_ca_nhan(hoc_sinh_id, nam_hoc_id, tuan)
            return ServiceResult(ok=True, data=tong)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    def get_chi_tiet_vi_pham(self, hoc_sinh_id: int, nam_hoc_id: int, tuan: int = None):
        try:
            ds = self.hs_vp_repo.get_by_hoc_sinh(hoc_sinh_id, nam_hoc_id, tuan)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    def _cap_nhat_diem_doi_ngay(self, nam_hoc_id: int, tuan: int, ngay_xay_ra, 
                                lop_hoc_id: int, so_diem: float):
        """Cập nhật điểm đội ngày và đồng bộ với bảng diem_tap_the_lop"""
        thu = ngay_xay_ra.weekday() + 2
        if thu not in [2, 3, 4, 5, 6]:
            return
        
        so_luong_vp = self.count_active_violations()
        self.diem_doi_ngay_repo.create_or_update(
            nam_hoc_id=nam_hoc_id,
            tuan=tuan,
            thu=thu,
            lop_hoc_id=lop_hoc_id,
            diem_thay_doi=so_diem,
            so_luong_vi_pham=so_luong_vp,
            ngay=ngay_xay_ra
        )
        
        # === CẬP NHẬT LẠI ĐIỂM ĐỘI TUẦN TRONG BẢNG diem_tap_the_lop ===
        self._cap_nhat_diem_doi_tuan(nam_hoc_id, tuan, lop_hoc_id, so_luong_vp)
    
    def _cap_nhat_diem_doi_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int, so_luong_vp: int):
        """Tính lại điểm đội tuần từ bảng diem_doi_ngay và cập nhật vào diem_tap_the_lop"""
        # Tính điểm đội tuần từ bảng diem_doi_ngay
        diem_doi_tuan = self.diem_doi_ngay_repo.get_trung_binh_tuan(nam_hoc_id, tuan, lop_hoc_id, so_luong_vp)
        
        # Cập nhật vào bảng diem_tap_the_lop
        record = self.diem_tap_the_repo.get_by_nam_hoc_tuan_lop(nam_hoc_id, tuan, lop_hoc_id)
        if record:
            record.diem_doi = diem_doi_tuan
        else:
            self.diem_tap_the_repo.create_or_update(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                lop_hoc_id=lop_hoc_id,
                diem_hoc_tap=0,
                diem_doi=diem_doi_tuan,
                ghi_chu="Tự động từ vi phạm",
                nguoi_nhap="Hệ thống"
            )
        self.session.flush()
    
    def _hoan_tac_diem_doi_ngay(self, nam_hoc_id: int, tuan: int, ngay_xay_ra, 
                                lop_hoc_id: int, so_diem: float):
        """Hoàn tác điểm khi xóa vi phạm (âm) hoặc thành tích (dương)"""
        thu = ngay_xay_ra.weekday() + 2
        if thu not in [2, 3, 4, 5, 6]:
            return
        
        so_luong_vp = self.count_active_violations()
        self.diem_doi_ngay_repo.rollback_diem_tru(
            nam_hoc_id=nam_hoc_id,
            tuan=tuan,
            thu=thu,
            lop_hoc_id=lop_hoc_id,
            diem_thay_doi=so_diem,
            so_luong_vi_pham=so_luong_vp
        )
        
        # === CẬP NHẬT LẠI ĐIỂM ĐỘI TUẦN ===
        self._cap_nhat_diem_doi_tuan(nam_hoc_id, tuan, lop_hoc_id, so_luong_vp)
    
    def them_vi_pham(self, hoc_sinh_id: int, loai_vi_pham_id: int, nam_hoc_id: int,
                     tuan: int, so_diem: float, ngay_xay_ra, tiet: int = None,
                     mo_ta: str = "", nguoi_ghi_nhan: str = ""):
        """Thêm vi phạm/thành tích cho học sinh và cập nhật điểm Đội ngày"""
        try:
            # Lấy học sinh để biết lớp
            hoc_sinh = self.hs_repo.get_by_id(hoc_sinh_id)
            if not hoc_sinh:
                return ServiceResult(ok=False, error="Không tìm thấy học sinh!")
            
            lop_hoc_id = hoc_sinh.lop_hoc_id
            
            # Tạo bản ghi vi phạm
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
                da_anh_huong_lop=True
            )
            
            # Cập nhật điểm Đội ngày (sẽ tự động cập nhật diem_tap_the_lop)
            self._cap_nhat_diem_doi_ngay(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                ngay_xay_ra=ngay_xay_ra,
                lop_hoc_id=lop_hoc_id,
                so_diem=so_diem
            )
            
            self.session.commit()
            return ServiceResult(ok=True, data=vp, error="Thành công")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def xoa_vi_pham(self, vp_id: int):
        try:
            vp = self.hs_vp_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy")
         
            hoc_sinh = self.hs_repo.get_by_id(vp.hoc_sinh_id)
            if hoc_sinh:
                self._hoan_tac_diem_doi_ngay(
                    nam_hoc_id=vp.nam_hoc_id,
                    tuan=vp.tuan,
                    ngay_xay_ra=vp.ngay_xay_ra,
                    lop_hoc_id=hoc_sinh.lop_hoc_id,
                    so_diem=vp.so_diem
                )
            
            ok = self.hs_vp_repo.delete(vp_id)
            self.session.commit()
            
            if ok:
                return ServiceResult(ok=True, error="Đã xóa")
            return ServiceResult(ok=False, error="Không tìm thấy")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def them_tap_the_vi_pham(self, lop_hoc_id: int, loai_vi_pham_id: int, nam_hoc_id: int,
                             tuan: int, so_diem: float, ngay_xay_ra, tiet: int = None,
                             mo_ta: str = "", nguoi_ghi_nhan: str = ""):
        """Thêm vi phạm tập thể cho lớp và cập nhật điểm Đội ngày"""
        try:
            # Kiểm tra lớp tồn tại
            lop = self.lop_repo.get_by_id(lop_hoc_id)
            if not lop:
                return ServiceResult(ok=False, error="Không tìm thấy lớp!")
            
            # Tính thứ trong tuần
            thu = ngay_xay_ra.weekday() + 2
            if thu not in [2, 3, 4, 5, 6]:
                return ServiceResult(ok=False, error="Ngày không hợp lệ (chỉ từ Thứ 2 đến Thứ 6)!")
            
            # Tạo bản ghi vi phạm tập thể
            vp = self.tap_the_vp_repo.create(
                lop_hoc_id=lop_hoc_id,
                loai_vi_pham_id=loai_vi_pham_id,
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                thu=thu,
                so_diem=so_diem,
                ngay_xay_ra=ngay_xay_ra,
                tiet=tiet,
                mo_ta=mo_ta,
                nguoi_ghi_nhan=nguoi_ghi_nhan,
                da_xac_nhan=True
            )
            
            # Cập nhật điểm Đội ngày
            self._cap_nhat_diem_doi_ngay(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                ngay_xay_ra=ngay_xay_ra,
                lop_hoc_id=lop_hoc_id,
                so_diem=so_diem
            )
            
            self.session.commit()
            return ServiceResult(ok=True, data=vp, error="Thành công")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def xoa_tap_the_vi_pham(self, vp_id: int):
        """Xóa vi phạm tập thể và hoàn tác điểm Đội"""
        try:
            vp = self.tap_the_vp_repo.get_by_id(vp_id)
            if not vp:
                return ServiceResult(ok=False, error="Không tìm thấy")
            
            # Hoàn tác điểm đội ngày
            self._hoan_tac_diem_doi_ngay(
                nam_hoc_id=vp.nam_hoc_id,
                tuan=vp.tuan,
                ngay_xay_ra=vp.ngay_xay_ra,
                lop_hoc_id=vp.lop_hoc_id,
                so_diem=vp.so_diem
            )
            
            # Xóa bản ghi
            ok = self.tap_the_vp_repo.delete(vp_id)
            self.session.commit()
            
            if ok:
                return ServiceResult(ok=True, error="Đã xóa")
            return ServiceResult(ok=False, error="Không tìm thấy")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def get_tap_the_vi_pham(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int = None):
        """Lấy vi phạm tập thể của lớp"""
        try:
            ds = self.tap_the_vp_repo.get_by_tuan(nam_hoc_id, tuan, lop_hoc_id)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))