# scripts/create_diem_tuan.py
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'truonghoc.db')
print(f"📁 Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Tạo bảng diem_tuan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diem_tuan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lop_hoc_id INTEGER NOT NULL,
            nam_hoc_id INTEGER NOT NULL,
            tuan INTEGER NOT NULL,
            diem_doi REAL DEFAULT 0,
            diem_hoc_tap REAL DEFAULT 0,
            tong_diem REAL DEFAULT 0,
            trung_binh REAL DEFAULT 0,
            ghi_chu TEXT,
            nguoi_nhap TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Đã tạo bảng diem_tuan")
    
    conn.commit()
    
except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
finally:
    conn.close()