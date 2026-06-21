import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.nguoi_dung import NguoiDung
from core.auth.password import hash_password

session = SessionLocal()

# Kiểm tra và tạo admin nếu chưa có
admin = session.query(NguoiDung).filter_by(email="admin@eduschool.vn").first()
if not admin:
    admin = NguoiDung(
        email="admin@eduschool.vn",
        mat_khau_hash=hash_password("admin123"),
        ho_ten="Quản trị viên hệ thống",
        role="admin",
        active=True
    )
    session.add(admin)
    session.commit()
    print("✅ Đã tạo tài khoản admin thành công!")
    print("   Email: admin@eduschool.vn")
    print("   Mật khẩu: admin123")
else:
    print("✅ Tài khoản admin đã tồn tại")

session.close()