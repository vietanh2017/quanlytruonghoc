# scripts/check_giao_vien.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db.models.giao_vien import GiaoVien

DATABASE_URL = "sqlite:///truonghoc.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# ⭐ Kiểm tra tất cả giáo viên (cả active và inactive)
giao_viens = session.query(GiaoVien).all()
print(f"📊 Tổng số giáo viên trong DB: {len(giao_viens)}")
for gv in giao_viens:
    print(f"  - ID: {gv.id}, Mã: {gv.ma_giao_vien}, Active: {gv.active}, Tên: {gv.nguoi_dung.ho_ten if gv.nguoi_dung else 'N/A'}")

session.close()