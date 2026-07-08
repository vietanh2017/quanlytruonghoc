# scripts/tao_diem_tap_the_cho_lop_moi.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.lop_hoc import LopHoc
from core.db.models.nam_hoc import NamHoc
from modules.thi_dua_hoc_sinh.models.diem_tap_the import DiemTapThe

def tao_diem_tap_the_cho_lop_moi():
    session = SessionLocal()
    
    nam_hoc = session.query(NamHoc).filter(NamHoc.active == True).first()
    if not nam_hoc:
        print("❌ Không tìm thấy năm học")
        return
    
    # Lấy các lớp từ 12 trở đi (lớp mới)
    ds_lop = session.query(LopHoc).filter(
        LopHoc.active == True,
        LopHoc.id >= 12
    ).all()
    
    print(f"📊 Tìm thấy {len(ds_lop)} lớp mới")
    
    for lop in ds_lop:
        # Kiểm tra đã có bản ghi chưa
        existing = session.query(DiemTapThe).filter(
            DiemTapThe.nam_hoc_id == nam_hoc.id,
            DiemTapThe.lop_hoc_id == lop.id
        ).first()
        
        if existing:
            print(f"⏭ Lớp {lop.ten_lop} đã có bản ghi")
            continue
        
        count = 0
        for tuan in range(1, 53):
            diem = DiemTapThe(
                nam_hoc_id=nam_hoc.id,
                tuan=tuan,
                lop_hoc_id=lop.id,
                diem_hoc_tap=0,
                diem_doi=0,
                ghi_chu="",
                nguoi_nhap="Hệ thống",
                da_khoa=False
            )
            session.add(diem)
            count += 1
        
        session.flush()
        print(f"✅ Đã tạo {count} bản ghi cho lớp {lop.ten_lop}")
    
    session.commit()
    print("🎉 Hoàn thành!")
    session.close()

if __name__ == "__main__":
    tao_diem_tap_the_cho_lop_moi()