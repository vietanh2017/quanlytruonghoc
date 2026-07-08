# scripts/add_kiem_nhiem.py
import sys
sys.path.append('.')

from core.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE giao_vien ADD COLUMN kiem_nhiem VARCHAR(200) DEFAULT ''"))
        conn.commit()
        print("✅ Thêm cột kiem_nhiem thành công!")
    except Exception as e:
        print(f"⚠️ {e}")  # Có thể cột đã tồn tại