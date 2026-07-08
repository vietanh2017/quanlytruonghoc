# scripts/seed_quyen.py
"""
Script khởi tạo dữ liệu quyền cho hệ thống
"""
import sys
import os

# ⭐ THÊM ĐƯỜNG DẪN GỐC CỦA PROJECT
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.phan_quyen import Quyen
from core.db.models.vai_tro_quyen import VaiTroQuyenModel
from shared.enums import Role


def seed_quyen():
    session = SessionLocal()
    
    # ⭐ DANH SÁCH QUYỀN THEO MODULE
    quyen_list = [
        # ── Cấu hình hệ thống ──
        {"ma_quyen": "cau_hinh.xem", "ten_quyen": "Xem cấu hình hệ thống", "module": "Cấu hình"},
        {"ma_quyen": "cau_hinh.them", "ten_quyen": "Thêm cấu hình", "module": "Cấu hình"},
        {"ma_quyen": "cau_hinh.sua", "ten_quyen": "Sửa cấu hình", "module": "Cấu hình"},
        {"ma_quyen": "cau_hinh.xoa", "ten_quyen": "Xóa cấu hình", "module": "Cấu hình"},
        
        # ── Giáo viên ──
        {"ma_quyen": "giao_vien.xem", "ten_quyen": "Xem danh sách giáo viên", "module": "Giáo viên"},
        {"ma_quyen": "giao_vien.them", "ten_quyen": "Thêm giáo viên", "module": "Giáo viên"},
        {"ma_quyen": "giao_vien.sua", "ten_quyen": "Sửa giáo viên", "module": "Giáo viên"},
        {"ma_quyen": "giao_vien.xoa", "ten_quyen": "Xóa giáo viên", "module": "Giáo viên"},
        {"ma_quyen": "giao_vien.import", "ten_quyen": "Import giáo viên từ Excel", "module": "Giáo viên"},
        
        # ── Phân công ──
        {"ma_quyen": "phan_cong.xem", "ten_quyen": "Xem phân công giảng dạy", "module": "Phân công"},
        {"ma_quyen": "phan_cong.them", "ten_quyen": "Thêm phân công", "module": "Phân công"},
        {"ma_quyen": "phan_cong.sua", "ten_quyen": "Sửa phân công", "module": "Phân công"},
        {"ma_quyen": "phan_cong.xoa", "ten_quyen": "Xóa phân công", "module": "Phân công"},
        {"ma_quyen": "phan_cong.import", "ten_quyen": "Import phân công từ Excel", "module": "Phân công"},
        
        # ── TKB ──
        {"ma_quyen": "tkb.xem", "ten_quyen": "Xem TKB", "module": "Thời khóa biểu"},
        {"ma_quyen": "tkb.them", "ten_quyen": "Thêm tiết TKB", "module": "Thời khóa biểu"},
        {"ma_quyen": "tkb.sua", "ten_quyen": "Sửa TKB", "module": "Thời khóa biểu"},
        {"ma_quyen": "tkb.xoa", "ten_quyen": "Xóa tiết TKB", "module": "Thời khóa biểu"},
        {"ma_quyen": "tkb.sinh_tu_dong", "ten_quyen": "Sinh TKB tự động", "module": "Thời khóa biểu"},
        {"ma_quyen": "tkb.export", "ten_quyen": "Xuất TKB Excel", "module": "Thời khóa biểu"},
        
        # ── Học sinh ──
        {"ma_quyen": "hoc_sinh.xem", "ten_quyen": "Xem danh sách học sinh", "module": "Học sinh"},
        {"ma_quyen": "hoc_sinh.them", "ten_quyen": "Thêm học sinh", "module": "Học sinh"},
        {"ma_quyen": "hoc_sinh.sua", "ten_quyen": "Sửa học sinh", "module": "Học sinh"},
        {"ma_quyen": "hoc_sinh.xoa", "ten_quyen": "Xóa học sinh", "module": "Học sinh"},
        
        # ── Thi đua ──
        {"ma_quyen": "thi_dua.xem", "ten_quyen": "Xem thi đua", "module": "Thi đua"},
        {"ma_quyen": "thi_dua.them", "ten_quyen": "Thêm thi đua", "module": "Thi đua"},
        {"ma_quyen": "thi_dua.sua", "ten_quyen": "Sửa thi đua", "module": "Thi đua"},
        {"ma_quyen": "thi_dua.xoa", "ten_quyen": "Xóa thi đua", "module": "Thi đua"},
    ]
    
    try:
        for q in quyen_list:
            exist = session.query(Quyen).filter(Quyen.ma_quyen == q["ma_quyen"]).first()
            if not exist:
                quyen = Quyen(
                    ma_quyen=q["ma_quyen"],
                    ten_quyen=q["ten_quyen"],
                    module=q["module"],
                    active=True
                )
                session.add(quyen)
                print(f"✅ Đã thêm quyền: {q['ma_quyen']}")
            else:
                print(f"⏭ Quyền đã tồn tại: {q['ma_quyen']}")
        
        session.commit()
        print("\n🎉 Seed dữ liệu quyền thành công!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        session.close()


def seed_vai_tro_quyen():
    """Gán quyền cho các vai trò"""
    session = SessionLocal()
    
    # ⭐ Cấu hình quyền cho từng vai trò
    role_permissions = {
        Role.ADMIN: [
            "cau_hinh.xem", "cau_hinh.them", "cau_hinh.sua", "cau_hinh.xoa",
            "giao_vien.xem", "giao_vien.them", "giao_vien.sua", "giao_vien.xoa", "giao_vien.import",
            "phan_cong.xem", "phan_cong.them", "phan_cong.sua", "phan_cong.xoa", "phan_cong.import",
            "tkb.xem", "tkb.them", "tkb.sua", "tkb.xoa", "tkb.sinh_tu_dong", "tkb.export",
            "hoc_sinh.xem", "hoc_sinh.them", "hoc_sinh.sua", "hoc_sinh.xoa",
            "thi_dua.xem", "thi_dua.them", "thi_dua.sua", "thi_dua.xoa",
        ],
        Role.TO_TRUONG: [
            "cau_hinh.xem",
            "giao_vien.xem", "giao_vien.sua",
            "phan_cong.xem", "phan_cong.them", "phan_cong.sua", "phan_cong.xoa",
            "tkb.xem", "tkb.them", "tkb.sua", "tkb.xoa",
            "hoc_sinh.xem",
            "thi_dua.xem",
        ],
        Role.GIAO_VIEN: [
            "tkb.xem",
            "hoc_sinh.xem",
            "thi_dua.xem",
        ],
    }
    
    try:
        for role, ma_quyens in role_permissions.items():
            # Xóa quyền cũ của vai trò
            session.query(VaiTroQuyenModel).filter(VaiTroQuyenModel.vai_tro == role).delete()
            
            # Thêm quyền mới
            count = 0
            for ma_quyen in ma_quyens:
                quyen = session.query(Quyen).filter(Quyen.ma_quyen == ma_quyen).first()
                if quyen:
                    vtq = VaiTroQuyenModel(vai_tro=role, quyen_id=quyen.id)
                    session.add(vtq)
                    count += 1
                    print(f"✅ Gán quyền {ma_quyen} cho {role}")
                else:
                    print(f"⚠️ Không tìm thấy quyền: {ma_quyen}")
            print(f"📊 Đã gán {count} quyền cho {role}")
        
        session.commit()
        print("\n🎉 Gán quyền cho vai trò thành công!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 BẮT ĐẦU SEED DỮ LIỆU QUYỀN")
    print("=" * 50)
    seed_quyen()
    print("\n" + "=" * 50)
    print("🚀 BẮT ĐẦU GÁN QUYỀN CHO VAI TRÒ")
    print("=" * 50)
    seed_vai_tro_quyen()