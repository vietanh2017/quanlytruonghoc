from sqlalchemy.orm import joinedload
from core.db.models.hoc_sinh import HocSinh


class HocSinhRepository:
    def __init__(self, session):
        self.db = session

    def get_by_lop(self, lop_hoc_id: int):
        return (
            self.db.query(HocSinh)
            .filter(HocSinh.lop_hoc_id == lop_hoc_id)
            .order_by(HocSinh.ho_ten)
            .all()
        )

    def get_by_id(self, hs_id: int):
        return self.db.query(HocSinh).filter(HocSinh.id == hs_id).first()

    def get_by_ma(self, ma: str):
        return self.db.query(HocSinh).filter(HocSinh.ma_hoc_sinh == ma).first()

    def create(self, **data):
        obj = HocSinh(**data)
        self.db.add(obj)
        return obj

    def update(self, hs_id: int, **data):
        obj = self.get_by_id(hs_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        return obj

    def delete(self, hs_id: int):
        obj = self.get_by_id(hs_id)
        if not obj:
            return False
        self.db.delete(obj)
        return True
    def get_next_ma(self):
        """Sinh mã học sinh tự động HS001, HS002..."""
        from sqlalchemy import func
        last = self.db.query(HocSinh).order_by(HocSinh.id.desc()).first()
        if not last or not last.ma_hoc_sinh:
            return "HS001"
        # Lấy số cuối cùng
        try:
            so = int(last.ma_hoc_sinh.replace("HS", ""))
            return f"HS{so + 1:03d}"
        except:
            count = self.db.query(func.count(HocSinh.id)).scalar() or 0
            return f"HS{count + 1:03d}"

    def get_by_ten_ngaysinh(self, ho_ten: str, ngay_sinh, lop_hoc_id: int):
        """Kiểm tra trùng tên + ngày sinh trong lớp"""
        return self.db.query(HocSinh).filter(
            HocSinh.ho_ten.like(f"{ho_ten}%"),
            HocSinh.ngay_sinh == ngay_sinh,
            HocSinh.lop_hoc_id == lop_hoc_id
        ).all()
    # ==================== THÊM METHOD NÀY ====================
    def delete_by_lop(self, lop_hoc_id: int):
        """
        Xóa tất cả học sinh thuộc một lớp
        Dùng khi import Excel với chế độ REPLACE
        """
        deleted_count = self.db.query(HocSinh).filter(
            HocSinh.lop_hoc_id == lop_hoc_id
        ).delete(synchronize_session=False)
        
        self.db.commit()
        return deleted_count
    def count_by_lop(self, lop_hoc_id: int):
        """Đếm số học sinh trong lớp"""
        from sqlalchemy import func
        return self.db.query(func.count(HocSinh.id)).filter(
            HocSinh.lop_hoc_id == lop_hoc_id
        ).scalar() or 0