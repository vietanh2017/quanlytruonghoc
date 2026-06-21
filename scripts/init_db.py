# D:\QUANLYTRUONGHOC\scripts\init_db.py
"""
Khởi tạo database và seed dữ liệu mặc định.
Chạy 1 lần: py -3.11 scripts\init_db.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import engine, SessionLocal, init_db
from core.auth.password import hash_password
from shared.enums import Role


def seed_admin(session):
    from core.db.models import NguoiDung
    if session.query(NguoiDung).filter_by(email="admin@eduschool.vn").first():
        print("   ℹ  Admin đã tồn tại — bỏ qua")
        return
    admin = NguoiDung(
        ho_ten="Quản trị viên",
        email="admin@eduschool.vn",
        mat_khau_hash=hash_password("admin123"),
        role=Role.ADMIN,
        active=True,
    )
    session.add(admin)
    session.flush()
    print(f"   ✓ Tạo admin id={admin.id}")


def seed_to_chuyen_mon(session):
    from core.db.models import ToCHuyenMon
    if session.query(ToCHuyenMon).count() > 0:
        print("   ℹ  Đã có tổ chuyên môn — bỏ qua")
        return
    ds = [
        ("Tổ Toán",             "TOAN"),
        ("Tổ Văn",              "VAN"),
        ("Tổ Ngoại ngữ",        "NN"),
        ("Tổ Lý – Hóa – Sinh",  "LHS"),
        ("Tổ Sử – Địa – GDCD",  "SDG"),
        ("Tổ Tin – CN – TD",    "TCT"),
        ("Tổ Nghệ thuật",       "NT"),
    ]
    for ten, ma in ds:
        session.add(ToCHuyenMon(ten_to=ten, ma_to=ma, active=True))
    session.flush()
    print(f"   ✓ Tạo {len(ds)} tổ chuyên môn")


def seed_mon_hoc(session):
    from core.db.models import MonHoc, PhanMon, MonHocKhoi
    if session.query(MonHoc).count() > 0:
        print("   ℹ  Đã có môn học — bỏ qua")
        return

    DS_MON = [
        ("NV",   "Ngữ văn",                              False, []),
        ("TOAN", "Toán",                                  False, []),
        ("NN1",  "Ngoại ngữ 1",                          False, []),
        ("GDCD", "Giáo dục công dân",                    False, []),
        ("LSDC", "Lịch sử và Địa lí",                    True,
            [("LS", "Lịch sử"), ("DL", "Địa lí")]),
        ("KHTN", "Khoa học tự nhiên",                    True,
            [("SH", "Sinh học"), ("HOA", "Hoá học"), ("LY", "Vật lý")]),
        ("TH",   "Tin học",                               False, []),
        ("CN",   "Công nghệ",                             False, []),
        ("GDTC", "Giáo dục thể chất",                    False, []),
        ("NT",   "Nghệ thuật",                            True,
            [("AN", "Âm nhạc"), ("MT", "Mỹ thuật")]),
        ("HDTN", "Hoạt động trải nghiệm, hướng nghiệp",  False, []),
        ("GDDP", "Nội dung giáo dục địa phương",         False, []),
    ]

    for thu_tu, (ma, ten, co_pm, phan_mon_list) in enumerate(DS_MON):
        mon = MonHoc(ma_mon=ma, ten_mon=ten, co_phan_mon=co_pm,
                     thu_tu=thu_tu, active=True)
        session.add(mon)
        session.flush()
        for i, (ma_pm, ten_pm) in enumerate(phan_mon_list):
            session.add(PhanMon(mon_hoc_id=mon.id, ma_phan_mon=ma_pm,
                                ten_phan_mon=ten_pm, thu_tu=i, active=True))
        for khoi in [6, 7, 8, 9]:
            session.add(MonHocKhoi(mon_hoc_id=mon.id, khoi=khoi, so_tiet=0))

    session.flush()
    print(f"   ✓ Tạo {len(DS_MON)} môn học THCS")


def main():
    print("\n🚀 Khởi tạo EduSchool Database\n" + "─" * 36)

    print("📦 Tạo bảng...")
    init_db()
    print("   ✓ Xong")

    session = SessionLocal()
    try:
        print("\n👤 Seed tài khoản...")
        seed_admin(session)

        print("\n🏫 Seed tổ chuyên môn...")
        seed_to_chuyen_mon(session)

        print("\n📚 Seed môn học...")
        seed_mon_hoc(session)

        session.commit()
        print("\n✅ Hoàn tất!\n" + "─" * 36)
        print("  Email   : admin@eduschool.vn")
        print("  Mật khẩu: admin123")
        print("─" * 36 + "\n")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Lỗi: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
