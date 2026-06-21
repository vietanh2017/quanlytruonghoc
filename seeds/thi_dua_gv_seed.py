# seeds/thi_dua_gv_seed.py

from core.db.session import SessionLocal
from core.db.models.tieu_chi import TieuChi  # ← SỬA ĐƯỜNG DẪN


def seed_tieu_chi():
    session = SessionLocal()
    
    # Danh sách tiêu chí cộng
    tieu_chi_cong = [
        {"ma_tieu_chi": "TC01", "ten_tieu_chi": "Soạn bài đầy đủ, đúng phân phối", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC02", "ten_tieu_chi": "Lên lớp đúng giờ, đầy đủ", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC03", "ten_tieu_chi": "Thực hiện đúng chương trình", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC04", "ten_tieu_chi": "Chấm trả bài đúng hạn", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC05", "ten_tieu_chi": "Tham gia sinh hoạt tổ chuyên môn", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC06", "ten_tieu_chi": "Dự giờ, thao giảng (mỗi tiết)", "diem_toi_da": 5, "loai": "cong"},
        {"ma_tieu_chi": "TC07", "ten_tieu_chi": "Làm hồ sơ sổ sách đầy đủ", "diem_toi_da": 10, "loai": "cong"},
        {"ma_tieu_chi": "TC08", "ten_tieu_chi": "Tham gia hoạt động ngoại khóa", "diem_toi_da": 5, "loai": "cong"},
        {"ma_tieu_chi": "TC09", "ten_tieu_chi": "Có sáng kiến kinh nghiệm", "diem_toi_da": 15, "loai": "cong"},
        {"ma_tieu_chi": "TC10", "ten_tieu_chi": "Học sinh đạt giải (cấp trường/quận/tỉnh)", "diem_toi_da": 15, "loai": "cong"},
    ]
    
    # Danh sách tiêu chí trừ
    tieu_chi_tru = [
        {"ma_tieu_chi": "TC11", "ten_tieu_chi": "Đi muộn/ về sớm (mỗi lần)", "diem_toi_da": 5, "loai": "tru"},
        {"ma_tieu_chi": "TC12", "ten_tieu_chi": "Bỏ tiết, dạy thay không phép", "diem_toi_da": 10, "loai": "tru"},
        {"ma_tieu_chi": "TC13", "ten_tieu_chi": "Soạn bài không đầy đủ", "diem_toi_da": 5, "loai": "tru"},
        {"ma_tieu_chi": "TC14", "ten_tieu_chi": "Chấm bài chậm, trả bài muộn", "diem_toi_da": 5, "loai": "tru"},
        {"ma_tieu_chi": "TC15", "ten_tieu_chi": "Không tham gia sinh hoạt tổ", "diem_toi_da": 10, "loai": "tru"},
        {"ma_tieu_chi": "TC16", "ten_tieu_chi": "Hồ sơ sổ sách thiếu/ không đúng", "diem_toi_da": 5, "loai": "tru"},
        {"ma_tieu_chi": "TC17", "ten_tieu_chi": "Vi phạm quy chế chuyên môn", "diem_toi_da": 10, "loai": "tru"},
    ]
    
    added = 0
    for tc in tieu_chi_cong + tieu_chi_tru:
        exists = session.query(TieuChi).filter(TieuChi.ma_tieu_chi == tc["ma_tieu_chi"]).first()
        if not exists:
            session.add(TieuChi(
                ma_tieu_chi=tc["ma_tieu_chi"],
                ten_tieu_chi=tc["ten_tieu_chi"],
                diem_toi_da=tc["diem_toi_da"],
                loai=tc["loai"],
                active=True
            ))
            added += 1
    
    session.commit()
    session.close()
    print(f"✅ Đã thêm {added} tiêu chí mới!")


if __name__ == "__main__":
    seed_tieu_chi()