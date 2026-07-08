# scripts/add_columns_loai_vi_pham.py
import sqlite3

conn = sqlite3.connect('truonghoc.db')
cursor = conn.cursor()

try:
    # Kiểm tra cột đã tồn tại chưa
    cursor.execute("PRAGMA table_info(loai_vi_pham)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'doi_tuong' not in columns:
        cursor.execute("ALTER TABLE loai_vi_pham ADD COLUMN doi_tuong VARCHAR(20) DEFAULT 'tap_the'")
        print("✅ Đã thêm cột doi_tuong")
    
    if 'loai_diem' not in columns:
        cursor.execute("ALTER TABLE loai_vi_pham ADD COLUMN loai_diem VARCHAR(20) DEFAULT 'tru'")
        print("✅ Đã thêm cột loai_diem")
    
    conn.commit()
    print("🎉 Cập nhật database thành công!")
except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
finally:
    conn.close()