# scripts/create_admin.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.nguoi_dung import NguoiDung
from core.auth.password import hash_password
from shared.enums import Role

def create_admin():
    session = SessionLocal()
    email = "admin@school.com"
    
    # Kiểm tra xem đã tồn tại chưa
    exist = session.query(NguoiDung).filter(NguoiDung.email == email).first()
    if exist:
        print(f"✅ Tài khoản {email} đã tồn tại!")
        return
    
    admin = NguoiDung(
        ho_ten="Quản trị viên",
        email=email,
        mat_khau_hash=hash_password("eduschool@123"),
        role=Role.ADMIN,
        active=True
    )
    session.add(admin)
    session.commit()
    print("✅ Tạo tài khoản admin thành công!")
    print(f"   Email: {email}")
    print("   Mật khẩu: eduschool@123")
    session.close()

if __name__ == "__main__":
    create_admin()