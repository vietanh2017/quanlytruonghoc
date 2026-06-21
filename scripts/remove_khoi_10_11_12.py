# scripts/remove_khoi_10_11_12_sqlite.py
import sqlite3
import os

# Đường dẫn đến file database
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'truonghoc.db')
print(f"📁 Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Kiểm tra bảng mon_hoc_khoi có tồn tại không
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mon_hoc_khoi'")
    if not cursor.fetchone():
        print("⚠️ Bảng mon_hoc_khoi chưa tồn tại!")
    else:
        # Xóa dữ liệu khối 10, 11, 12
        cursor.execute("DELETE FROM mon_hoc_khoi WHERE khoi IN (10, 11, 12)")
        conn.commit()
        print(f"✅ Đã xóa {cursor.rowcount} bản ghi khối 10, 11, 12")
        
        # Kiểm tra dữ liệu còn lại
        cursor.execute("SELECT khoi, so_tiet, mon_hoc_id FROM mon_hoc_khoi ORDER BY khoi")
        rows = cursor.fetchall()
        print(f"📊 Số bản ghi còn lại: {len(rows)}")
        for row in rows:
            print(f"  - Khối {row[0]}: {row[1]} tiết (mon_hoc_id: {row[2]})")
        
except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
finally:
    conn.close()