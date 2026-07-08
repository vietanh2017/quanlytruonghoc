# modules/thi_dua_hoc_sinh/repository/loai_vi_pham_repository.py
from sqlalchemy.orm import Session
from modules.thi_dua_hoc_sinh.models.loai_vi_pham import LoaiViPham
from modules.thi_dua_hoc_sinh.repository.base_repository import BaseRepository

class LoaiViPhamRepository(BaseRepository[LoaiViPham]):
    def __init__(self, session: Session):
        super().__init__(session, LoaiViPham)
    
    def get_by_ma(self, ma_loi: str) -> LoaiViPham:
        return self.session.query(LoaiViPham).filter(
            LoaiViPham.ma_loi == ma_loi
        ).first()
    def get_all(self, loai: str = None):
        query = self.session.query(LoaiViPham)
        if loai:
            query = query.filter(LoaiViPham.loai == loai)
        return query.order_by(LoaiViPham.thu_tu).all()  # ⭐ Sắp xếp theo thu_tu