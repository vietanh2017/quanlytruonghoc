# scripts/create_loai_vi_pham.py
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'truonghoc.db')
print(f"📁 Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # ⭐ Kiểm tra bảng đã tồn tại chưa
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='loai_vi_pham'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("📝 Đang tạo bảng loai_vi_pham...")
        cursor.execute("""
            CREATE TABLE loai_vi_pham (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_loi VARCHAR(20) UNIQUE NOT NULL,
                ten_loi VARCHAR(200) NOT NULL,
                loai VARCHAR(20) NOT NULL,
                doi_tuong VARCHAR(20) DEFAULT 'tap_the',
                loai_diem VARCHAR(20) DEFAULT 'tru',
                nhom VARCHAR(50),
                so_diem FLOAT DEFAULT 0,
                mo_ta TEXT,
                thu_tu INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Đã tạo bảng loai_vi_pham")
    else:
        # ⭐ Kiểm tra và thêm cột nếu chưa có
        cursor.execute("PRAGMA table_info(loai_vi_pham)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'doi_tuong' not in columns:
            cursor.execute("ALTER TABLE loai_vi_pham ADD COLUMN doi_tuong VARCHAR(20) DEFAULT 'tap_the'")
            print("✅ Đã thêm cột doi_tuong")
        
        if 'loai_diem' not in columns:
            cursor.execute("ALTER TABLE loai_vi_pham ADD COLUMN loai_diem VARCHAR(20) DEFAULT 'tru'")
            print("✅ Đã thêm cột loai_diem")
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE loai_vi_pham ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("✅ Đã thêm cột is_active")
    
    # ⭐ Thêm dữ liệu mẫu
    cursor.execute("SELECT COUNT(*) FROM loai_vi_pham")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📝 Đang thêm dữ liệu mẫu...")
        sample_data = [
            ('VP001', 'Đi học muộn', 'vi_pham', 'ca_nhan', 'tru', 'Nề nếp', 1),
            ('VP002', 'Không làm bài tập', 'vi_pham', 'ca_nhan', 'tru', 'Học tập', 2),
            ('VP003', 'Mất trật tự trong lớp', 'vi_pham', 'tap_the', 'tru', 'Nề nếp', 2),
            ('VP004', 'Vệ sinh lớp kém', 'vi_pham', 'tap_the', 'tru', 'Vệ sinh', 1),
            ('TT001', 'Đạt điểm cao', 'thanh_tich', 'ca_nhan', 'cong', 'Học tập', 3),
            ('TT002', 'Lớp đạt danh hiệu', 'thanh_tich', 'tap_the', 'cong', 'Thi đua', 5),
        ]
        
        for item in sample_data:
            cursor.execute("""
                INSERT INTO loai_vi_pham 
                (ma_loi, ten_loi, loai, doi_tuong, loai_diem, nhom, so_diem, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, item)
        
        print(f"✅ Đã thêm {len(sample_data)} dòng dữ liệu mẫu")
    
    conn.commit()
    print("🎉 Hoàn thành!")
    
    # Kiểm tra kết quả
    cursor.execute("SELECT ma_loi, ten_loi, loai, doi_tuong, loai_diem, so_diem FROM loai_vi_pham")
    rows = cursor.fetchall()
    print("\n📋 Danh sách loại vi phạm:")
    for row in rows:
        print(f"  - {row[0]}: {row[1]} ({row[2]}) - Đối tượng: {row[3]}, Loại điểm: {row[4]}, Điểm: {row[5]}")

except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()