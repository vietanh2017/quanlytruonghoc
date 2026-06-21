from core.db.models.diem_giao_vien import DiemGiaoVien  # ← SỬA
from sqlalchemy.orm import joinedload


class DiemGiaoVienRepository:
    def __init__(self, session):
        self.db = session

    def get_by_gv_thang(self, gv_id: int, thang: int, nam_hoc_id: int):
        """Lấy tất cả điểm của GV trong tháng"""
        return (
            self.db.query(DiemGiaoVien)
            .options(joinedload(DiemGiaoVien.tieu_chi))
            .filter(
                DiemGiaoVien.giao_vien_id == gv_id,
                DiemGiaoVien.thang == thang,
                DiemGiaoVien.nam_hoc_id == nam_hoc_id,
            )
            .all()
        )

    def get_by_tieu_chi_gv_thang(self, gv_id: int, tieu_chi_id: int, thang: int, nam_hoc_id: int):
        """Kiểm tra xem đã có điểm cho tiêu chí này không"""
        return (
            self.db.query(DiemGiaoVien)
            .filter(
                DiemGiaoVien.giao_vien_id == gv_id,
                DiemGiaoVien.tieu_chi_id == tieu_chi_id,
                DiemGiaoVien.thang == thang,
                DiemGiaoVien.nam_hoc_id == nam_hoc_id,
            )
            .first()
        )

    def get_by_id(self, diem_id: int):
        return self.db.query(DiemGiaoVien).filter(DiemGiaoVien.id == diem_id).first()

    def create(self, **data):
        obj = DiemGiaoVien(**data)
        self.db.add(obj)
        return obj

    def update(self, diem_id: int, **data):
        obj = self.get_by_id(diem_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        return obj

    def delete(self, diem_id: int):
        obj = self.get_by_id(diem_id)
        if not obj:
            return False
        self.db.delete(obj)
        return True

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()