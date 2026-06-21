# modules/competition/repository/diem_tap_the_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import and_
from modules.competition.models.diem_tap_the import DiemTapTheLop


class DiemTapTheRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, record_id: int):
        """Lấy bản ghi theo ID"""
        return self.db.query(DiemTapTheLop).filter(DiemTapTheLop.id == record_id).first()

    def get_by_nam_hoc_tuan_lop(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int):
        """Lấy điểm của 1 lớp trong 1 tuần cụ thể"""
        return self.db.query(DiemTapTheLop).filter(
            DiemTapTheLop.nam_hoc_id == nam_hoc_id,
            DiemTapTheLop.tuan == tuan,
            DiemTapTheLop.lop_hoc_id == lop_hoc_id
        ).first()

    def get_all_by_nam_hoc_tuan(self, nam_hoc_id: int, tuan: int):
        """Lấy tất cả điểm của các lớp trong 1 tuần"""
        return self.db.query(DiemTapTheLop).filter(
            DiemTapTheLop.nam_hoc_id == nam_hoc_id,
            DiemTapTheLop.tuan == tuan
        ).all()

    def get_weeks_have_data_in_month(self, nam_hoc_id: int, lop_hoc_id: int, weeks: list):
        """Lấy danh sách tuần đã có dữ liệu trong tháng"""
        results = self.db.query(DiemTapTheLop.tuan).filter(
            DiemTapTheLop.nam_hoc_id == nam_hoc_id,
            DiemTapTheLop.lop_hoc_id == lop_hoc_id,
            DiemTapTheLop.tuan.in_(weeks)
        ).all()
        return [r[0] for r in results]

    def get_tb_thang(self, nam_hoc_id: int, lop_hoc_id: int, weeks: list):
        """Tính trung bình tháng từ danh sách tuần"""
        from sqlalchemy import func

        result = self.db.query(
            func.avg(DiemTapTheLop.diem_hoc_tap + DiemTapTheLop.diem_doi)
        ).filter(
            DiemTapTheLop.nam_hoc_id == nam_hoc_id,
            DiemTapTheLop.lop_hoc_id == lop_hoc_id,
            DiemTapTheLop.tuan.in_(weeks)
        ).scalar()

        return result if result else 0

    # modules/competition/repository/diem_tap_the_repository.py

    def create_or_update(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int,
                        diem_hoc_tap: float, diem_doi: float,
                        ghi_chu: str = "", nguoi_nhap: str = ""):
        """Tạo mới hoặc cập nhật điểm cho 1 lớp trong 1 tuần"""
        record = self.get_by_nam_hoc_tuan_lop(nam_hoc_id, tuan, lop_hoc_id)

        if record:
            record.diem_hoc_tap = diem_hoc_tap
            record.diem_doi = diem_doi
            record.ghi_chu = ghi_chu
            record.nguoi_nhap = nguoi_nhap
        else:
            # Tạo mới - diem_doi mặc định là 10.0
            record = DiemTapTheLop(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                lop_hoc_id=lop_hoc_id,
                diem_hoc_tap=diem_hoc_tap,
                diem_doi=diem_doi if diem_doi > 0 else 10.0,  # ← SỬA DÒNG NÀY
                ghi_chu=ghi_chu,
                nguoi_nhap=nguoi_nhap
            )
            self.db.add(record)

        self.db.flush()
        return record

    def delete_by_nam_hoc_tuan(self, nam_hoc_id: int, tuan: int):
        """Xóa tất cả điểm của 1 tuần (dùng khi cần reset)"""
        self.db.query(DiemTapTheLop).filter(
            DiemTapTheLop.nam_hoc_id == nam_hoc_id,
            DiemTapTheLop.tuan == tuan
        ).delete(synchronize_session=False)

    def save_all(self, nam_hoc_id: int, tuan: int, data: list, nguoi_nhap: str = ""):
        """
        Lưu nhiều bản ghi cùng lúc
        data: list of dict {lop_hoc_id, diem_hoc_tap, diem_doi, ghi_chu}
        """
        for item in data:
            self.create_or_update(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                lop_hoc_id=item['lop_hoc_id'],
                diem_hoc_tap=item['diem_hoc_tap'],
                diem_doi=item['diem_doi'],
                ghi_chu=item.get('ghi_chu', ''),
                nguoi_nhap=nguoi_nhap
            )
        self.db.commit()