# modules/thi_dua_hoc_sinh/repository/hoc_sinh_vi_pham_repository.py
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from modules.thi_dua_hoc_sinh.models.hoc_sinh_vi_pham import HocSinhViPham
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class HocSinhViPhamRepository(BaseRepository[HocSinhViPham]):
    def __init__(self, session: Session):
        super().__init__(session, HocSinhViPham)
    
    def get_by_lop(self, lop_hoc_id: int, nam_hoc_id: int, tuan: Optional[int] = None):
        query = self.session.query(HocSinhViPham).options(
            joinedload(HocSinhViPham.hoc_sinh),
            joinedload(HocSinhViPham.loai_vi_pham)
        ).filter(
            HocSinhViPham.nam_hoc_id == nam_hoc_id
        )
        
        # Join với hoc_sinh để lọc theo lớp
        query = query.join(HocSinhViPham.hoc_sinh).filter(
            HocSinhViPham.hoc_sinh.has(lop_hoc_id=lop_hoc_id)
        )
        
        if tuan:
            query = query.filter(HocSinhViPham.tuan == tuan)
        
        return query.all()
    
    def get_by_hoc_sinh(self, hoc_sinh_id: int, nam_hoc_id: int, tuan: Optional[int] = None):
        query = self.session.query(HocSinhViPham).filter(
            HocSinhViPham.hoc_sinh_id == hoc_sinh_id,
            HocSinhViPham.nam_hoc_id == nam_hoc_id
        )
        if tuan:
            query = query.filter(HocSinhViPham.tuan == tuan)
        return query.all()