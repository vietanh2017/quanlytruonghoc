# modules/dashboard/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db.session import get_db
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
@router.get("/recent-activities")
def get_recent_activities(db: Session = Depends(get_db)):
    """Lấy hoạt động gần đây từ các module"""
    activities = []
    
    # 1. Lấy học sinh mới thêm
    from core.db.models.hoc_sinh import HocSinh
    hs_moi = db.query(HocSinh).order_by(HocSinh.created_at.desc()).limit(3).all()
    for hs in hs_moi:
        activities.append({
            "user": "Hệ thống",
            "action": f"Thêm học sinh {hs.ho_ten}",
            "time": hs.created_at.strftime("%H:%M %d/%m"),
            "type": "student"
        })
    
    # 2. Lấy giáo viên mới thêm
    from core.db.models.giao_vien import GiaoVien
    gv_moi = db.query(GiaoVien).order_by(GiaoVien.created_at.desc()).limit(3).all()
    for gv in gv_moi:
        activities.append({
            "user": "Hệ thống",
            "action": f"Thêm giáo viên {gv.nguoi_dung.ho_ten if gv.nguoi_dung else ''}",
            "time": gv.created_at.strftime("%H:%M %d/%m"),
            "type": "teacher"
        })
    
    # 3. Lấy TKB mới tạo
    from modules.tkb.models import ThoiKhoaBieu
    tkb_moi = db.query(ThoiKhoaBieu).order_by(ThoiKhoaBieu.id.desc()).limit(3).all()
    for tkb in tkb_moi:
        mon = tkb.mon_hoc
        lop = tkb.lop_hoc
        activities.append({
            "user": "Hệ thống",
            "action": f"Xếp TKB: {mon.ten_mon if mon else ''} - {lop.ten_lop if lop else ''}",
            "time": "Vừa xong",
            "type": "timetable"
        })
    
    # 4. Sắp xếp theo thời gian (mới nhất trước)
    activities.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    return activities[:10]  # Lấy 10 hoạt động gần nhất