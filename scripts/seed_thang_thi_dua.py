# scripts/seed_thang_thi_dua.py
import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'truonghoc.db')
print(f"📁 Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # ⭐ Kiểm tra bảng đã tồn tại chưa
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thang_thi_dua'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("📝 Đang tạo bảng thang_thi_dua...")
        cursor.execute("""
            CREATE TABLE thang_thi_dua (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_thang VARCHAR(100) NOT NULL,
                nam_hoc_id INTEGER NOT NULL,
                tuan_list TEXT NOT NULL,
                so_tuan INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (nam_hoc_id) REFERENCES nam_hoc(id)
            )
        """)
        print("✅ Đã tạo bảng thang_thi_dua")
    else:
        print("✅ Bảng thang_thi_dua đã tồn tại")
    
    # ⭐ Kiểm tra dữ liệu
    cursor.execute("SELECT COUNT(*) FROM thang_thi_dua")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📝 Đang thêm dữ liệu mẫu...")
        
        # Lấy nam_hoc_id đầu tiên
        cursor.execute("SELECT id FROM nam_hoc ORDER BY id LIMIT 1")
        nam_hoc_row = cursor.fetchone()
        nam_hoc_id = nam_hoc_row[0] if nam_hoc_row else 2
        
        # Dữ liệu mẫu
        sample_data = [
            ('Tháng 9', nam_hoc_id, json.dumps([1, 2, 3, 4]), 4, 1),
            ('Tháng 10', nam_hoc_id, json.dumps([5, 6, 7, 8]), 4, 1),
            ('Tháng 11', nam_hoc_id, json.dumps([9, 10, 11, 12]), 4, 1),
            ('Tháng 12', nam_hoc_id, json.dumps([13, 14, 15, 16]), 4, 1),
            ('Tháng 1', nam_hoc_id, json.dumps([17, 18, 19, 20]), 4, 1),
            ('Tháng 2', nam_hoc_id, json.dumps([21, 22, 23, 24]), 4, 1),
            ('Tháng 3', nam_hoc_id, json.dumps([25, 26, 27, 28]), 4, 1),
            ('Tháng 4', nam_hoc_id, json.dumps([29, 30, 31, 32]), 4, 1),
            ('Tháng 5', nam_hoc_id, json.dumps([33, 34, 35]), 3, 1),
        ]
        
        for item in sample_data:
            cursor.execute("""
                INSERT INTO thang_thi_dua (ten_thang, nam_hoc_id, tuan_list, so_tuan, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, item)
        
        print(f"✅ Đã thêm {len(sample_data)} dòng dữ liệu mẫu")
    else:
        print(f"📊 Đã có {count} dòng dữ liệu")
    
    conn.commit()
    print("🎉 Hoàn thành!")
    
    # Kiểm tra kết quả
    cursor.execute("SELECT id, ten_thang, so_tuan, is_active FROM thang_thi_dua")
    rows = cursor.fetchall()
    print("\n📋 Danh sách tháng thi đua:")
    for row in rows:
        print(f"  - {row[0]}: {row[1]} ({row[2]} tuần) - {'Đang áp dụng' if row[3] else 'Đã kết thúc'}")

except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()