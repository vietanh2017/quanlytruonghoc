# seeds/seed_diem_tuan.py
import sqlite3
import os
import random

# ⭐ Đường dẫn đúng tới file database
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'truonghoc.db')
print(f"📁 Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Lấy nam_hoc_id
    cursor.execute("SELECT id FROM nam_hoc WHERE ten_nam_hoc LIKE '%2026%'")
    nam_hoc = cursor.fetchone()
    if not nam_hoc:
        cursor.execute("SELECT id FROM nam_hoc LIMIT 1")
        nam_hoc = cursor.fetchone()
    nam_hoc_id = nam_hoc[0] if nam_hoc else 2
    print(f"📚 nam_hoc_id: {nam_hoc_id}")

    # Lấy danh sách lớp
    cursor.execute("SELECT id FROM lop_hoc")
    lop_hocs = cursor.fetchall()
    print(f"🏫 Số lớp: {len(lop_hocs)}")

    if not lop_hocs:
        print("⚠️ Không có lớp nào trong database!")
        exit()

    # Dữ liệu mẫu cho các lớp và tuần
    data = []
    for lop in lop_hocs:
        for tuan in range(1, 5):  # Tuần 1-4
            trung_binh = round(random.uniform(7.0, 9.5), 2)
            data.append((lop[0], nam_hoc_id, tuan, trung_binh))
            print(f"  - Lớp {lop[0]}, Tuần {tuan}: {trung_binh}")

    # Thêm vào bảng
    count = 0
    for item in data:
        cursor.execute("""
            INSERT OR IGNORE INTO diem_tuan (lop_hoc_id, nam_hoc_id, tuan, diem_doi, diem_hoc_tap, tong_diem, trung_binh)
            VALUES (?, ?, ?, 0, 0, 0, ?)
        """, (item[0], item[1], item[2], item[3]))
        count += 1

    conn.commit()
    print(f"✅ Đã thêm {count} dòng dữ liệu mẫu vào diem_tuan")

    # Kiểm tra
    cursor.execute("SELECT COUNT(*) FROM diem_tuan")
    total = cursor.fetchone()[0]
    print(f"📊 Tổng số dòng trong diem_tuan: {total}")

except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()