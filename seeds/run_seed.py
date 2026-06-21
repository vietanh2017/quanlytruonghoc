# seeds/run_seed.py

"""
Script chạy seed dữ liệu cho database
Chạy lệnh: python -m seeds.run_seed
"""

import sys
import os

# Thêm đường dẫn gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from seeds.thi_dua_ca_nhan_seed import seed_loai_vi_pham


def run_all_seeds():
    """Chạy tất cả seed"""
    session = SessionLocal()
    
    print("=" * 50)
    print("Bắt đầu seed dữ liệu...")
    print("=" * 50)
    
    # Seed danh mục vi phạm
    print("\n1. Seed danh mục vi phạm/thành tích...")
    seed_loai_vi_pham(session)
    
    print("\n" + "=" * 50)
    print("Hoàn thành seed dữ liệu!")
    print("=" * 50)
    
    session.close()


if __name__ == "__main__":
    run_all_seeds()