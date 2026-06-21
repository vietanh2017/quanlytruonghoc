# scripts/add_columns.py
from core.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Kiểm tra và thêm cột nam_hoc_id nếu chưa có
    try:
        conn.execute(text("ALTER TABLE lop_hoc ADD COLUMN nam_hoc_id INTEGER"))
        print("✅ Đã thêm cột nam_hoc_id")
    except:
        print("⚠️ Cột nam_hoc_id đã tồn tại")
    
    # Thêm cột si_so nếu chưa có
    try:
        conn.execute(text("ALTER TABLE lop_hoc ADD COLUMN si_so INTEGER DEFAULT 0"))
        print("✅ Đã thêm cột si_so")
    except:
        print("⚠️ Cột si_so đã tồn tại")
    
    conn.commit()