# modules/competition/repository/diem_doi_ngay_repository.py

from sqlalchemy.orm import Session
from modules.competition.models.diem_doi_ngay import DiemDoiNgay
from datetime import datetime


class DiemDoiNgayRepository:
    def __init__(self, session: Session):
        self.db = session

    def get_by_id(self, id: int):
        return self.db.query(DiemDoiNgay).filter(DiemDoiNgay.id == id).first()

    def get_by_ngay(self, nam_hoc_id: int, tuan: int, thu: int, lop_hoc_id: int):
        """Lấy bản ghi điểm của 1 lớp trong 1 ngày cụ thể"""
        return self.db.query(DiemDoiNgay).filter(
            DiemDoiNgay.nam_hoc_id == nam_hoc_id,
            DiemDoiNgay.tuan == tuan,
            DiemDoiNgay.thu == thu,
            DiemDoiNgay.lop_hoc_id == lop_hoc_id
        ).first()

    def get_all_by_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int = None):
        """Lấy tất cả điểm trong tuần của 1 lớp hoặc tất cả lớp"""
        query = self.db.query(DiemDoiNgay).filter(
            DiemDoiNgay.nam_hoc_id == nam_hoc_id,
            DiemDoiNgay.tuan == tuan
        )
        if lop_hoc_id:
            query = query.filter(DiemDoiNgay.lop_hoc_id == lop_hoc_id)
        return query.order_by(DiemDoiNgay.thu).all()

    def get_tong_diem_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int):
        """Tính tổng điểm đội của cả tuần (tổng 5 ngày)"""
        records = self.get_all_by_tuan(nam_hoc_id, tuan, lop_hoc_id)
        if not records:
            return 0
        return sum(r.diem_con_lai for r in records)

    def get_trung_binh_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int, so_luong_vi_pham: int):
        """Tính điểm trung bình tuần"""
        records = self.get_all_by_tuan(nam_hoc_id, tuan, lop_hoc_id)
        
        # Tạo map các ngày có dữ liệu
        diem_map = {r.thu: r for r in records}
        
        tong_tb_ngay = 0
        for thu in range(2, 7):
            if thu in diem_map:
                r = diem_map[thu]
                # === THÊM DEBUG Ở ĐÂY ===
                # =========================
                tb_ngay = (10 * so_luong_vi_pham + r.tong_diem_cong - r.tong_diem_tru) / so_luong_vi_pham

            else:
                tb_ngay = 10.0
            tong_tb_ngay += tb_ngay
        
        ket_qua = tong_tb_ngay / 5

        return ket_qua

    def create_or_update(self, nam_hoc_id: int, tuan: int, thu: int, 
                     lop_hoc_id: int, diem_thay_doi: float, 
                     so_luong_vi_pham: int,
                     ngay: datetime = None):
        """Tạo mới hoặc cập nhật điểm khi có vi phạm (âm) hoặc thành tích (dương)"""
        record = self.get_by_ngay(nam_hoc_id, tuan, thu, lop_hoc_id)
        
        if record:
            # Cập nhật: cộng thêm điểm thay đổi (có thể âm hoặc dương)
            if diem_thay_doi < 0:
                # Vi phạm: cộng điểm trừ
                record.tong_diem_tru += abs(diem_thay_doi)
            else:
                # Thành tích: cộng điểm cộng (làm tăng điểm)
                record.tong_diem_cong += diem_thay_doi
            
            # Tính lại điểm còn lại
            record.diem_con_lai = max(0, (10 * so_luong_vi_pham + record.tong_diem_cong - record.tong_diem_tru))
            record.updated_at = datetime.now()
        else:
            # Tạo mới
            diem_toi_da = so_luong_vi_pham * 10
            tong_diem_tru = abs(diem_thay_doi) if diem_thay_doi < 0 else 0
            tong_diem_cong = diem_thay_doi if diem_thay_doi > 0 else 0
            diem_con_lai = max(0, diem_toi_da + tong_diem_cong - tong_diem_tru)
            
            record = DiemDoiNgay(
                nam_hoc_id=nam_hoc_id,
                tuan=tuan,
                thu=thu,
                lop_hoc_id=lop_hoc_id,
                so_luong_vi_pham=so_luong_vi_pham,
                diem_toi_da=diem_toi_da,
                tong_diem_tru=tong_diem_tru,
                tong_diem_cong=tong_diem_cong,
                diem_con_lai=diem_con_lai,
                ngay=ngay or datetime.now(),
                ghi_chu=f"Tự động từ thi đua cá nhân"
            )
            self.db.add(record)
        
        self.db.flush()
        return record

    def rollback_diem_tru(self, nam_hoc_id: int, tuan: int, thu: int, 
                        lop_hoc_id: int, diem_thay_doi: float,
                        so_luong_vi_pham: int):
        """Hoàn tác điểm (khi xóa vi phạm hoặc thành tích)"""
        record = self.get_by_ngay(nam_hoc_id, tuan, thu, lop_hoc_id)
        if record:

            if diem_thay_doi < 0:
                record.tru_diem_tru(diem_thay_doi)
            else:
                record.tru_diem_cong(diem_thay_doi)
            record.cap_nhat_diem_toi_da(so_luong_vi_pham)
            record.updated_at = datetime.now()
            self.db.flush()
        else:
            return record

    def update_so_luong_vi_pham(self, nam_hoc_id: int, tuan: int, 
                                lop_hoc_id: int, so_luong_moi: int):
        """Cập nhật số lượng vi phạm cho tất cả các ngày trong tuần"""
        records = self.get_all_by_tuan(nam_hoc_id, tuan, lop_hoc_id)
        for record in records:
            record.cap_nhat_diem_toi_da(so_luong_moi)
        self.db.flush()
        return len(records)

    def delete_by_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: int = None):
        """Xóa tất cả điểm của tuần (dùng khi reset)"""
        query = self.db.query(DiemDoiNgay).filter(
            DiemDoiNgay.nam_hoc_id == nam_hoc_id,
            DiemDoiNgay.tuan == tuan
        )
        if lop_hoc_id:
            query = query.filter(DiemDoiNgay.lop_hoc_id == lop_hoc_id)
        return query.delete(synchronize_session=False)