# scripts/seed_mon_hoc_data.py
"""
Script tạo dữ liệu phân môn và số tiết theo khối cho các môn học
Chạy: python scripts/seed_mon_hoc_data.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.models.mon_hoc import MonHoc, PhanMon
from core.db.models.mon_hoc_khoi import MonHocKhoi

# ⭐ Kết nối SQLite - file truonghoc.db trong thư mục gốc
DATABASE_URL = "sqlite:///truonghoc.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def seed_data():
    try:
        # Lấy danh sách môn học
        mon_hocs = session.query(MonHoc).all()
        mon_hoc_dict = {m.ma_mon: m for m in mon_hocs}

        print("📋 Danh sách môn học:", [m.ma_mon for m in mon_hocs])
        print(f"📊 Tổng số môn học: {len(mon_hocs)}")

        # Dữ liệu phân môn
        phan_mon_data = {
            'LSĐL': [
                {'ma_phan_mon': 'LS', 'ten_phan_mon': 'Lịch sử', 'thu_tu': 1},
                {'ma_phan_mon': 'DL', 'ten_phan_mon': 'Địa lý', 'thu_tu': 2},
            ],
            'KHTN': [
                {'ma_phan_mon': 'SINH', 'ten_phan_mon': 'Sinh học', 'thu_tu': 1},
                {'ma_phan_mon': 'LY', 'ten_phan_mon': 'Vật lí', 'thu_tu': 2},
                {'ma_phan_mon': 'HOA', 'ten_phan_mon': 'Hoá học', 'thu_tu': 3},
            ],
            'NT': [
                {'ma_phan_mon': 'AN', 'ten_phan_mon': 'Âm nhạc', 'thu_tu': 1},
                {'ma_phan_mon': 'MT', 'ten_phan_mon': 'Mỹ thuật', 'thu_tu': 2},
            ],
        }

        # Dữ liệu số tiết theo khối (mặc định)
        so_tiet_data = {
            'TOAN': {6: 4, 7: 4, 8: 4, 9: 4,},
            'VAN': {6: 4, 7: 4, 8: 4, 9: 4, },
            'ANH': {6: 3, 7: 3, 8: 3, 9: 3, },
            'LSĐL': {6: 2, 7: 2, 8: 2, 9: 2, },
            'KHTN': {6: 2, 7: 2, 8: 2, 9: 2, },
            'TIN': {6: 1, 7: 1, 8: 1, 9: 1, },
            'CN': {6: 1, 7: 1, 8: 1, 9: 1, },
            'GDTC': {6: 2, 7: 2, 8: 2, 9: 2, },
            'NT': {6: 1, 7: 1, 8: 1, 9: 1, },
            'GDĐP': {6: 1, 7: 1, 8: 1, 9: 1, },
            'HĐTN': {6: 2, 7: 2, 8: 2, 9: 2, },
        }

        # ===== TẠO PHÂN MÔN =====
        print("\n📝 Tạo phân môn...")
        for ma_mon, phan_mons in phan_mon_data.items():
            mon = mon_hoc_dict.get(ma_mon)
            if not mon:
                print(f"  ⚠️ Không tìm thấy môn {ma_mon}, bỏ qua")
                continue
            
            # Cập nhật co_phan_mon = True
            mon.co_phan_mon = True
            
            for pm_data in phan_mons:
                # Kiểm tra phân môn đã tồn tại chưa
                existing = session.query(PhanMon).filter(
                    PhanMon.mon_hoc_id == mon.id,
                    PhanMon.ma_phan_mon == pm_data['ma_phan_mon']
                ).first()
                
                if existing:
                    print(f"  ⏭️ Phân môn {pm_data['ma_phan_mon']} đã tồn tại, bỏ qua")
                else:
                    phan_mon = PhanMon(
                        mon_hoc_id=mon.id,
                        ma_phan_mon=pm_data['ma_phan_mon'],
                        ten_phan_mon=pm_data['ten_phan_mon'],
                        thu_tu=pm_data['thu_tu'],
                        active=True
                    )
                    session.add(phan_mon)
                    print(f"  ✅ Đã tạo phân môn: {pm_data['ma_phan_mon']} - {pm_data['ten_phan_mon']}")

        # ===== TẠO SỐ TIẾT THEO KHỐI =====
        print("\n📝 Tạo số tiết theo khối...")
        for ma_mon, khoi_data in so_tiet_data.items():
            mon = mon_hoc_dict.get(ma_mon)
            if not mon:
                print(f"  ⚠️ Không tìm thấy môn {ma_mon}, bỏ qua")
                continue
            
            for khoi, so_tiet in khoi_data.items():
                # Kiểm tra đã tồn tại chưa
                existing = session.query(MonHocKhoi).filter(
                    MonHocKhoi.mon_hoc_id == mon.id,
                    MonHocKhoi.khoi == khoi
                ).first()
                
                if existing:
                    # Cập nhật nếu đã tồn tại
                    existing.so_tiet = so_tiet
                    print(f"  🔄 Cập nhật {ma_mon} - Khối {khoi}: {so_tiet} tiết")
                else:
                    mon_khoi = MonHocKhoi(
                        mon_hoc_id=mon.id,
                        khoi=khoi,
                        so_tiet=so_tiet
                    )
                    session.add(mon_khoi)
                    print(f"  ✅ Tạo {ma_mon} - Khối {khoi}: {so_tiet} tiết")

        # Commit
        session.commit()
        print("\n🎉 Hoàn thành tạo dữ liệu!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu seed dữ liệu phân môn và số tiết theo khối...")
    print(f"📁 Database: truonghoc.db")
    seed_data()