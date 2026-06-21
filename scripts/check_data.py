# scripts/check_data.py
import sys
import os

# Thêm đường dẫn gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.models.mon_hoc import MonHoc, PhanMon
from core.db.models.mon_hoc_khoi import MonHocKhoi

# Kết nối database SQLite
DATABASE_URL = "sqlite:///truonghoc.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Kiểm tra phân môn
    phan_mons = session.query(PhanMon).all()
    print(f"📊 Số phân môn: {len(phan_mons)}")
    for pm in phan_mons:
        mon = session.query(MonHoc).filter(MonHoc.id == pm.mon_hoc_id).first()
        ten_mon = mon.ten_mon if mon else "Không xác định"
        print(f"  - {pm.ma_phan_mon}: {pm.ten_phan_mon} (Môn: {ten_mon})")

    # Kiểm tra số tiết
    so_tiets = session.query(MonHocKhoi).all()
    print(f"\n📊 Số tiết theo khối: {len(so_tiets)}")
    for st in so_tiets:
        mon = session.query(MonHoc).filter(MonHoc.id == st.mon_hoc_id).first()
        ten_mon = mon.ten_mon if mon else "Không xác định"
        print(f"  - {ten_mon} - Khối {st.khoi}: {st.so_tiet} tiết")

except Exception as e:
    print(f"❌ Lỗi: {e}")
finally:
    session.close()