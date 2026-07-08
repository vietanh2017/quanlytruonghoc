# modules/thi_dua_hoc_sinh/repository/diem_tap_the_repository.py
from sqlalchemy.orm import Session
from typing import Optional
from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class DiemTapTheRepository(BaseRepository[DiemTapThe]):
    def __init__(self, session: Session):
        super().__init__(session, DiemTapThe)
    
    def get_by_nam_hoc_tuan_lop(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int):
        """Lấy bản ghi điểm tập thể theo năm học, tuần, lớp"""
        from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe
        
        # ⭐ LOG để debug
        print(f"🔍 get_by_nam_hoc_tuan_lop: nam_hoc={nam_hoc_id}, tuan={tuan}, lop={lop_hoc_id}")
        
        record = self.session.query(DiemTapThe).filter(
            DiemTapThe.nam_hoc_id == nam_hoc_id,
            DiemTapThe.tuan == tuan,
            DiemTapThe.lop_hoc_id == lop_hoc_id
        ).first()
        
        if record:
            print(f"   ✅ Tìm thấy ID={record.id}, diem_hoc_tap={record.diem_hoc_tap}")
        else:
            print(f"   ❌ KHÔNG TÌM THẤY bản ghi cho lop={lop_hoc_id}, tuan={tuan}")
        
        return record

    def create_or_update(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int,
                        diem_hoc_tap: float = 0, diem_doi: float = 0,
                        ghi_chu: str = "", nguoi_nhap: str = ""):
        """Tạo hoặc cập nhật điểm tập thể"""
        from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe
        
        # ⭐ Tìm bản ghi
        record = self.session.query(DiemTapThe).filter(
            DiemTapThe.nam_hoc_id == nam_hoc_id,
            DiemTapThe.tuan == tuan,
            DiemTapThe.lop_hoc_id == lop_hoc_id
        ).first()
        
        if record:
            # ⭐ Cập nhật
            record.diem_hoc_tap = float(diem_hoc_tap) if diem_hoc_tap is not None else 0
            record.diem_doi = float(diem_doi) if diem_doi is not None else 0
            record.ghi_chu = ghi_chu
            record.nguoi_nhap = nguoi_nhap
            print(f"   ✅ Cập nhật diem_tap_the ID={record.id}: diem_hoc_tap={record.diem_hoc_tap}")
            return record
        else:
            # ⭐ Tạo mới
            new_record = DiemTapThe(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                lop_hoc_id=lop_hoc_id,
                diem_hoc_tap=float(diem_hoc_tap) if diem_hoc_tap is not None else 0,
                diem_doi=float(diem_doi) if diem_doi is not None else 0,
                ghi_chu=ghi_chu,
                nguoi_nhap=nguoi_nhap,
                da_khoa=False
            )
            self.session.add(new_record)
            self.session.flush()
            print(f"   ✅ Tạo mới diem_tap_the ID={new_record.id}: diem_hoc_tap={new_record.diem_hoc_tap}")
            return new_record