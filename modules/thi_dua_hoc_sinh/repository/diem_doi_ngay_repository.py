# modules/thi_dua_hoc_sinh/repository/diem_doi_ngay_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from modules.thi_dua_hoc_sinh.models.diem_doi_ngay import DiemDoiNgay
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class DiemDoiNgayRepository(BaseRepository[DiemDoiNgay]):
    def __init__(self, session: Session):
        super().__init__(session, DiemDoiNgay)
    
    def get_by_nam_hoc_tuan_thu_lop(self, nam_hoc_id: int, tuan: int, thu: int, lop_hoc_id: int):
        """Lấy điểm theo năm học, tuần, thứ, lớp"""
        return self.session.query(DiemDoiNgay).filter(
            DiemDoiNgay.nam_hoc_id == nam_hoc_id,
            DiemDoiNgay.tuan == tuan,
            DiemDoiNgay.thu == thu,
            DiemDoiNgay.lop_hoc_id == lop_hoc_id
        ).first()
    
    def create_or_update(self, nam_hoc_id: int, tuan: int, thu: int,
                        lop_hoc_id: int, diem_thay_doi: float,
                        so_luong_vi_pham: int, ngay):
        record = self.get_by_nam_hoc_tuan_thu_lop(nam_hoc_id, tuan, thu, lop_hoc_id)

        if record:
            record.diem_thay_doi += diem_thay_doi
            # ✅ Luôn cập nhật so_luong_vi_pham theo thời điểm hiện tại
            record.so_luong_vi_pham = so_luong_vi_pham
            record.ngay = ngay
        else:
            record = self.create(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                thu=thu,
                lop_hoc_id=lop_hoc_id,
                diem_thay_doi=diem_thay_doi,
                so_luong_vi_pham=so_luong_vi_pham,  # ✅ lưu tại thời điểm nhập
                ngay=ngay
            )
        return record
    
    def rollback_diem_tru(self, nam_hoc_id: int, tuan: int, thu: int, 
                          lop_hoc_id: int, diem_thay_doi: float, 
                          so_luong_vi_pham: int):
        """Rollback điểm trừ khi xóa vi phạm"""
        record = self.get_by_nam_hoc_tuan_thu_lop(nam_hoc_id, tuan, thu, lop_hoc_id)
        if record:
            record.diem_thay_doi -= diem_thay_doi
            record.so_luong_vi_pham = so_luong_vi_pham
        return record
    
    def get_trung_binh_tuan(self, nam_hoc_id: int, tuan: int,
                            lop_hoc_id: int, so_luong_vp: int,
                            so_ngay: int = 5) -> float:
        
        # ✅ Lấy trực tiếp từ bảng vi phạm — giống frontend
        from modules.thi_dua_hoc_sinh.models.tap_the_vi_pham import TapTheViPham
        from modules.thi_dua_hoc_sinh.models.hoc_sinh_vi_pham import HocSinhViPham
        from core.db.models.hoc_sinh import HocSinh
        
        # Vi phạm tập thể
        tap_the = self.session.query(
            func.sum(TapTheViPham.so_diem)
        ).filter(
            TapTheViPham.nam_hoc_id == nam_hoc_id,
            TapTheViPham.tuan == tuan,
            TapTheViPham.lop_hoc_id == lop_hoc_id
        ).scalar() or 0
        
        # Vi phạm cá nhân
        ca_nhan = self.session.query(
            func.sum(HocSinhViPham.so_diem)
        ).join(HocSinh).filter(
            HocSinhViPham.nam_hoc_id == nam_hoc_id,
            HocSinhViPham.tuan == tuan,
            HocSinh.lop_hoc_id == lop_hoc_id
        ).scalar() or 0
        
        tong_diem_thay_doi = tap_the + ca_nhan
        
        diem_mac_dinh = 10 * so_luong_vp * so_ngay
        diem_trung_binh = (diem_mac_dinh + tong_diem_thay_doi) / so_luong_vp / so_ngay
        
        return round(diem_trung_binh, 3)