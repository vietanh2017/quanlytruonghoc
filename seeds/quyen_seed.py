# seeds/quyen_seed.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.session import SessionLocal
from core.db.models.quyen import QuyenModel
from core.db.models.vai_tro_quyen import VaiTroQuyenModel
from shared.enums import Role


def seed_quyen():
    session = SessionLocal()
    
    # seeds/quyen_seed.py

    quyen_list = [
        # === THI ĐUA GIÁO VIÊN ===
        {"ma_quyen": "Q001", "module": "thi_dua_giao_vien", "ten_quyen": "Xem danh sách GV", "mo_ta": "Xem danh sách giáo viên trong tổ"},
        {"ma_quyen": "Q002", "module": "thi_dua_giao_vien", "ten_quyen": "Chấm điểm", "mo_ta": "Nhập điểm cho giáo viên trong tổ"},
        {"ma_quyen": "Q003", "module": "thi_dua_giao_vien", "ten_quyen": "Quản lý tiêu chí", "mo_ta": "Thêm/sửa/xóa tiêu chí chấm điểm"},
        {"ma_quyen": "Q004", "module": "thi_dua_giao_vien", "ten_quyen": "Xem báo cáo tháng", "mo_ta": "Xem bảng xếp hạng theo tháng"},
        {"ma_quyen": "Q005", "module": "thi_dua_giao_vien", "ten_quyen": "Xem báo cáo học kỳ", "mo_ta": "Xem bảng xếp hạng học kỳ"},
        {"ma_quyen": "Q006", "module": "thi_dua_giao_vien", "ten_quyen": "Xem báo cáo năm", "mo_ta": "Xem bảng xếp hạng cả năm"},
        
        # === THI ĐUA HỌC SINH ===
        {"ma_quyen": "Q101", "module": "thi_dua_hoc_sinh", "ten_quyen": "Xem điểm tập thể", "mo_ta": "Xem điểm thi đua tập thể lớp"},
        {"ma_quyen": "Q102", "module": "thi_dua_hoc_sinh", "ten_quyen": "Nhập điểm đội", "mo_ta": "Nhập điểm Đội cho lớp"},
        {"ma_quyen": "Q103", "module": "thi_dua_hoc_sinh", "ten_quyen": "Xem điểm cá nhân", "mo_ta": "Xem vi phạm/thành tích học sinh"},
        {"ma_quyen": "Q104", "module": "thi_dua_hoc_sinh", "ten_quyen": "Nhập vi phạm", "mo_ta": "Thêm vi phạm/thành tích học sinh"},
        {"ma_quyen": "Q105", "module": "thi_dua_hoc_sinh", "ten_quyen": "Xóa vi phạm", "mo_ta": "Xóa vi phạm/thành tích học sinh"},
        {"ma_quyen": "Q106", "module": "thi_dua_hoc_sinh", "ten_quyen": "Quản lý danh mục", "mo_ta": "Thêm/sửa/xóa loại vi phạm"},
        {"ma_quyen": "Q107", "module": "thi_dua_hoc_sinh", "ten_quyen": "Xuất báo cáo", "mo_ta": "Xuất báo cáo thi đua"},
        
        # === THỜI KHÓA BIỂU ===
        {"ma_quyen": "Q201", "module": "thoi_khoa_bieu", "ten_quyen": "Xem TKB", "mo_ta": "Xem thời khóa biểu"},
        {"ma_quyen": "Q202", "module": "thoi_khoa_bieu", "ten_quyen": "Sửa TKB", "mo_ta": "Sửa thời khóa biểu"},
        
        # === PHÂN CÔNG ===
        {"ma_quyen": "Q301", "module": "phan_cong", "ten_quyen": "Xem phân công", "mo_ta": "Xem phân công giảng dạy"},
        {"ma_quyen": "Q302", "module": "phan_cong", "ten_quyen": "Sửa phân công", "mo_ta": "Sửa phân công giảng dạy"},
        
        # === BÁO CÁO ===
        {"ma_quyen": "Q401", "module": "bao_cao", "ten_quyen": "Xem báo cáo", "mo_ta": "Xem báo cáo tổng hợp"},
        {"ma_quyen": "Q402", "module": "bao_cao", "ten_quyen": "Xuất báo cáo", "mo_ta": "Xuất báo cáo Excel/PDF"},
    ]
    
    quyen_map = {}
    added = 0
    
    for q in quyen_list:
        exists = session.query(QuyenModel).filter(
            QuyenModel.module == q["module"],
            QuyenModel.ten_quyen == q["ten_quyen"]
        ).first()
        if not exists:
            quyen = QuyenModel(**q)
            session.add(quyen)
            session.flush()
            quyen_map[(q["module"], q["ten_quyen"])] = quyen.id
            added += 1
        else:
            quyen_map[(q["module"], q["ten_quyen"])] = exists.id
    
    session.commit()
    print(f"✅ Đã thêm {added} quyền mới")
    
    role_quyen_map = {
        Role.ADMIN: [
            ("thi_dua_giao_vien", "Xem danh sách GV"),
            ("thi_dua_giao_vien", "Chấm điểm"),
            ("thi_dua_giao_vien", "Quản lý tiêu chí"),
            ("thi_dua_giao_vien", "Xem báo cáo tháng"),
            ("thi_dua_giao_vien", "Xem báo cáo học kỳ"),
            ("thi_dua_giao_vien", "Xem báo cáo năm"),
            ("thi_dua_hoc_sinh", "Xem điểm tập thể"),
            ("thi_dua_hoc_sinh", "Nhập điểm đội"),
            ("thi_dua_hoc_sinh", "Xem điểm cá nhân"),
            ("thi_dua_hoc_sinh", "Nhập vi phạm"),
            ("thi_dua_hoc_sinh", "Xóa vi phạm"),
            ("thi_dua_hoc_sinh", "Quản lý danh mục"),
            ("thi_dua_hoc_sinh", "Xuất báo cáo"),
            ("thoi_khoa_bieu", "Xem TKB"),
            ("thoi_khoa_bieu", "Sửa TKB"),
            ("phan_cong", "Xem phân công"),
            ("phan_cong", "Sửa phân công"),
            ("bao_cao", "Xem báo cáo"),
            ("bao_cao", "Xuất báo cáo"),
        ],
        Role.TO_TRUONG: [
            ("thi_dua_giao_vien", "Xem danh sách GV"),
            ("thi_dua_giao_vien", "Chấm điểm"),
            ("thi_dua_giao_vien", "Xem báo cáo tháng"),
            ("thi_dua_giao_vien", "Xem báo cáo học kỳ"),
            ("thi_dua_giao_vien", "Xem báo cáo năm"),
            ("thi_dua_hoc_sinh", "Xem điểm tập thể"),
            ("thi_dua_hoc_sinh", "Xem điểm cá nhân"),
            ("thoi_khoa_bieu", "Xem TKB"),
            ("phan_cong", "Xem phân công"),
            ("bao_cao", "Xem báo cáo"),
            ("bao_cao", "Xuất báo cáo"),
        ],
        Role.PHO_TO_TRUONG: [
            ("thi_dua_giao_vien", "Xem danh sách GV"),
            ("thi_dua_giao_vien", "Chấm điểm"),
            ("thi_dua_giao_vien", "Xem báo cáo tháng"),
            ("thi_dua_giao_vien", "Xem báo cáo học kỳ"),
            ("thi_dua_giao_vien", "Xem báo cáo năm"),
            ("thi_dua_hoc_sinh", "Xem điểm tập thể"),
            ("thi_dua_hoc_sinh", "Xem điểm cá nhân"),
            ("thoi_khoa_bieu", "Xem TKB"),
            ("phan_cong", "Xem phân công"),
            ("bao_cao", "Xem báo cáo"),
            ("bao_cao", "Xuất báo cáo"),
        ],
        Role.TONG_PHU_TRACH: [
            ("thi_dua_hoc_sinh", "Xem điểm tập thể"),
            ("thi_dua_hoc_sinh", "Nhập điểm đội"),
            ("thi_dua_hoc_sinh", "Xem điểm cá nhân"),
            ("thi_dua_hoc_sinh", "Nhập vi phạm"),
            ("thi_dua_hoc_sinh", "Xóa vi phạm"),
            ("thi_dua_hoc_sinh", "Xuất báo cáo"),
            ("thoi_khoa_bieu", "Xem TKB"),
            ("bao_cao", "Xem báo cáo"),
            ("bao_cao", "Xuất báo cáo"),
        ],
        Role.GIAO_VIEN: [
            ("thi_dua_hoc_sinh", "Xem điểm tập thể"),
            ("thi_dua_hoc_sinh", "Xem điểm cá nhân"),
            ("thoi_khoa_bieu", "Xem TKB"),
            ("bao_cao", "Xem báo cáo"),
        ],
    }

    for role in role_quyen_map.keys():
        session.query(VaiTroQuyenModel).filter(VaiTroQuyenModel.vai_tro == role.value).delete()
        added_role_quyen = 0
    for role, quyen_list_role in role_quyen_map.items():
        for module, ten_quyen in quyen_list_role:
            key = (module, ten_quyen)
            if key in quyen_map:
                vtq = VaiTroQuyenModel(
                    vai_tro=role.value,
                    quyen_id=quyen_map[key]
                )
                session.add(vtq)
                added_role_quyen += 1
    
    session.commit()
    print(f"✅ Đã gán {added_role_quyen} quyền cho các vai trò")
    
    session.close()


if __name__ == "__main__":
    seed_quyen()