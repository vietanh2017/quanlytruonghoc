# seeds/thi_dua_ca_nhan_seed.py

def seed_loai_vi_pham(session):
    """Tạo dữ liệu mẫu cho danh mục vi phạm/thành tích"""
    from modules.competition.models.loai_vi_pham import LoaiViPham
    
    data = [
        # === VI PHẠM ===
        # Nề nếp
        ("VP001", "Đi học muộn", "vi_pham", "Nề nếp", -2, 1),
        ("VP002", "Bỏ tiết", "vi_pham", "Nề nếp", -5, 2),
        ("VP003", "Không mặc đồng phục", "vi_pham", "Nề nếp", -2, 3),
        ("VP004", "Không đeo khăn quàng", "vi_pham", "Nề nếp", -1, 4),
        ("VP005", "Mất trật tự trong giờ", "vi_pham", "Nề nếp", -3, 5),
        ("VP006", "Không làm bài tập", "vi_pham", "Nề nếp", -2, 6),
        ("VP007", "Sử dụng điện thoại trong giờ", "vi_pham", "Nề nếp", -5, 7),
        
        # An toàn giao thông
        ("VP101", "Không đội mũ bảo hiểm", "vi_pham", "ATGT", -5, 10),
        ("VP102", "Đi xe dàn hàng ngang", "vi_pham", "ATGT", -3, 11),
        ("VP103", "Vượt đèn đỏ", "vi_pham", "ATGT", -10, 12),
        ("VP104", "Chở quá số người quy định", "vi_pham", "ATGT", -4, 13),
        
        # Đạo đức
        ("VP201", "Nói tục, chửi thề", "vi_pham", "Đạo đức", -4, 20),
        ("VP202", "Đánh nhau", "vi_pham", "Đạo đức", -20, 21),
        ("VP203", "Vô lễ với giáo viên", "vi_pham", "Đạo đức", -15, 22),
        ("VP204", "Bắt nạt bạn bè", "vi_pham", "Đạo đức", -15, 23),
        
        # === THÀNH TÍCH ===
        # Văn nghệ
        ("TT001", "Tham gia văn nghệ", "thanh_tich", "Văn nghệ", 5, 50),
        ("TT002", "Đạt giải văn nghệ cấp trường", "thanh_tich", "Văn nghệ", 10, 51),
        ("TT003", "Đạt giải văn nghệ cấp quận/huyện", "thanh_tich", "Văn nghệ", 15, 52),
        
        # Thể thao
        ("TT101", "Tham gia thể thao", "thanh_tich", "Thể thao", 5, 60),
        ("TT102", "Đạt giải thể thao cấp trường", "thanh_tich", "Thể thao", 10, 61),
        ("TT103", "Đạt giải thể thao cấp quận/huyện", "thanh_tich", "Thể thao", 15, 62),
        
        # Học tập - phong trào
        ("TT201", "Giúp đỡ bạn bè trong học tập", "thanh_tich", "Học tập", 5, 70),
        ("TT202", "Tham gia câu lạc bộ", "thanh_tich", "Học tập", 3, 71),
        ("TT203", "Đạt danh hiệu học sinh giỏi", "thanh_tich", "Học tập", 10, 72),
    ]
    
    for ma, ten, loai, nhom, diem, thu_tu in data:
        exists = session.query(LoaiViPham).filter(LoaiViPham.ma_loi == ma).first()
        if not exists:
            session.add(LoaiViPham(
                ma_loi=ma,
                ten_loi=ten,
                loai=loai,
                nhom=nhom,
                so_diem=diem,
                thu_tu=thu_tu,
                is_active=True
            ))
    
    session.commit()
    print("Đã seed dữ liệu loại vi phạm/thành tích!")