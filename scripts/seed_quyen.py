import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.phan_quyen import Quyen

session = SessionLocal()

# Danh sách quyền
quyen_list = [
    # Module Giáo viên
    ("giao_vien.xem", "Xem danh sách giáo viên", "giao_vien"),
    ("giao_vien.them", "Thêm giáo viên mới", "giao_vien"),
    ("giao_vien.sua", "Sửa thông tin giáo viên", "giao_vien"),
    ("giao_vien.xoa", "Xóa giáo viên", "giao_vien"),
    
    # Module Lớp học
    ("lop_hoc.xem", "Xem danh sách lớp học", "lop_hoc"),
    ("lop_hoc.them", "Thêm lớp học mới", "lop_hoc"),
    ("lop_hoc.sua", "Sửa thông tin lớp học", "lop_hoc"),
    ("lop_hoc.xoa", "Xóa lớp học", "lop_hoc"),
    
    # Module Cấu hình
    ("cau_hinh.xem", "Xem cấu hình hệ thống", "cau_hinh"),
    ("cau_hinh.sua", "Sửa cấu hình hệ thống", "cau_hinh"),
    
    # Module Thi đua
    ("thi_dua.nhap_diem", "Nhập điểm thi đua", "thi_dua"),
    ("thi_dua.xem", "Xem bảng thi đua", "thi_dua"),
    ("thi_dua.xuat", "Xuất báo cáo thi đua", "thi_dua"),
    
    # Module Tài khoản
    ("tai_khoan.xem", "Xem danh sách tài khoản", "tai_khoan"),
    ("tai_khoan.them", "Thêm tài khoản mới", "tai_khoan"),
    ("tai_khoan.sua", "Sửa tài khoản", "tai_khoan"),
    ("tai_khoan.xoa", "Xóa tài khoản", "tai_khoan"),
]

count = 0
for ma, ten, module in quyen_list:
    exist = session.query(Quyen).filter(Quyen.ma_quyen == ma).first()
    if not exist:
        q = Quyen(ma_quyen=ma, ten_quyen=ten, module=module, active=True)
        session.add(q)
        count += 1
        print(f"✅ Thêm quyền: {ma} - {ten}")
    else:
        print(f"⚠️ Quyền đã tồn tại: {ma}")

session.commit()
print(f"\n📊 Đã thêm {count} quyền mới")
session.close()