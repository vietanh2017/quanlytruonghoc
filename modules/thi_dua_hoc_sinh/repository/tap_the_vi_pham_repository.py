# modules/thi_dua_hoc_sinh/repository/tap_the_vi_pham_repository.py
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from modules.thi_dua_hoc_sinh.models.tap_the_vi_pham import TapTheViPham
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class TapTheViPhamRepository(BaseRepository[TapTheViPham]):
    def __init__(self, session: Session):
        super().__init__(session, TapTheViPham)
    
    def get_by_tuan(self, nam_hoc_id: int, tuan: int, lop_hoc_id: Optional[int] = None):
        query = self.session.query(TapTheViPham).options(
            joinedload(TapTheViPham.lop_hoc),
            joinedload(TapTheViPham.loai_vi_pham)
        ).filter(
            TapTheViPham.nam_hoc_id == nam_hoc_id,
            TapTheViPham.tuan == tuan
        )
        
        if lop_hoc_id:
            query = query.filter(TapTheViPham.lop_hoc_id == lop_hoc_id)
        
        return query.all()