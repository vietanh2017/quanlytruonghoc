# test_gvcn.py
from core.db.session import SessionLocal
from core.db.models.lop_hoc import LopHoc
from core.db.models.giao_vien import GiaoVien

session = SessionLocal()

# Kiểm tra tất cả lớp
lops = session.query(LopHoc).all()
for lop in lops:
    print(f"📚 Lớp: {lop.ten_lop}")
    print(f"   - giao_vien_cn_id: {lop.giao_vien_cn_id}")
    if lop.giao_vien_cn_id:
        gv = session.query(GiaoVien).filter(GiaoVien.id == lop.giao_vien_cn_id).first()
        if gv and gv.nguoi_dung:
            print(f"   - GVCN: {gv.nguoi_dung.ho_ten}")
        else:
            print(f"   - ❌ Không tìm thấy GV")
    else:
        print(f"   - ❌ Chưa có GVCN")
    print()

session.close()