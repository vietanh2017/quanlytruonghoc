# scripts/tao_diem_cho_lop_moi.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.lop_hoc import LopHoc
from core.db.models.nam_hoc import NamHoc
from modules.thi_dua_hoc_sinh.models.diem_doi_ngay import DiemDoiNgay
from datetime import datetime

def tao_diem_cho_lop_moi():
    session = SessionLocal()
    
    # Lấy năm học hiện tại
    nam_hoc = session.query(NamHoc).filter(NamHoc.active == True).first()
    if not nam_hoc:
        print("❌ Không tìm thấy năm học hiện tại")
        return
    
    # Lấy tất cả lớp
    ds_lop = session.query(LopHoc).filter(LopHoc.active == True).all()
    
    # ⭐ Lấy ngày hiện tại để fill vào cột ngay
    now = datetime.now()
    
    for lop in ds_lop:
        # Kiểm tra lớp đã có bản ghi điểm chưa
        existing = session.query(DiemDoiNgay).filter(
            DiemDoiNgay.nam_hoc_id == nam_hoc.id,
            DiemDoiNgay.lop_hoc_id == lop.id
        ).first()
        
        if existing:
            print(f"⏭ Lớp {lop.ten_lop} đã có điểm")
            continue
        
        # Tạo bản ghi điểm cho 52 tuần
        count = 0
        for tuan in range(1, 53):
            for thu in range(1, 8):
                diem = DiemDoiNgay(
                    nam_hoc_id=nam_hoc.id,
                    lop_hoc_id=lop.id,
                    tuan=tuan,
                    thu=thu,
                    diem_thay_doi=0,
                    so_luong_vi_pham=0,
                    ngay=now,  # ⭐ THÊM DÒNG NÀY
                    updated_at=now  # ⭐ THÊM DÒNG NÀY (nếu có)
                )
                session.add(diem)
                count += 1
        
        session.flush()
        print(f"✅ Đã tạo {count} bản ghi điểm cho lớp {lop.ten_lop}")
    
    session.commit()
    print("🎉 Hoàn thành!")
    session.close()

if __name__ == "__main__":
    tao_diem_cho_lop_moi()