# scripts/add_phan_mon_id.py
import sys
sys.path.append('.')
from core.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE phan_cong_giang_day ADD COLUMN phan_mon_id INTEGER REFERENCES phan_mon(id)"))
        conn.commit()
        print("✅ Thêm cột phan_mon_id thành công!")
    except Exception as e:
        print(f"⚠️ {e}")