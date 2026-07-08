# modules/phan_cong/schemas.py
from typing import Optional
from pydantic import BaseModel


# ── Brief models ──────────────────────────────────────────────

class GiaoVienBrief(BaseModel):
    id: int
    ma_giao_vien: str
    nguoi_dung: Optional[dict] = None
    model_config = {"from_attributes": True}

class MonHocBrief(BaseModel):
    id: int
    ma_mon: str
    ten_mon: str
    model_config = {"from_attributes": True}

class LopHocBrief(BaseModel):
    id: int
    ma_lop: str
    ten_lop: str
    khoi: int
    model_config = {"from_attributes": True}

class NamHocBrief(BaseModel):
    id: int
    ten_nam_hoc: str
    model_config = {"from_attributes": True}

class HocKyBrief(BaseModel):
    id: int
    ten_hoc_ky: str
    so_thu_tu: int
    model_config = {"from_attributes": True}


# ── Phân công ─────────────────────────────────────────────────

class PhanCongItem(BaseModel):
    """Một mục phân công (môn + lớp)"""
    mon_hoc_id: int
    lop_hoc_id: int

class PhanCongCreate(BaseModel):
    """Tạo phân công cho 1 giáo viên trong 1 học kỳ"""
    giao_vien_id: int
    nam_hoc_id: int
    hoc_ky_id: int
    phan_cong_list: list[PhanCongItem]
    clear_old: Optional[bool] = False

class PhanCongXoaCuThe(BaseModel):
    """Xóa 1 phân công cụ thể"""
    giao_vien_id: int
    nam_hoc_id: int
    hoc_ky_id: int
    mon_hoc_id: int
    lop_hoc_id: int

class PhanCongXoaTatCa(BaseModel):
    """Xóa tất cả phân công của GV trong học kỳ"""
    giao_vien_id: int
    nam_hoc_id: int
    hoc_ky_id: int

class PhanCongResponse(BaseModel):
    """Response cho 1 bản ghi phân công"""
    id: int
    giao_vien_id: int
    nam_hoc_id: int
    hoc_ky_id: int
    mon_hoc_id: int
    lop_hoc_id: int
    giao_vien: Optional[GiaoVienBrief] = None
    mon_hoc: Optional[MonHocBrief] = None
    lop_hoc: Optional[LopHocBrief] = None
    model_config = {"from_attributes": True}

class PhanCongTongHopItem(BaseModel):
    """Response tổng hợp theo giáo viên"""
    giao_vien_id: int
    ho_ten: str
    phan_cong: list[dict]
    # ⭐ Thêm các field breakdown tiết dạy / tiết chủ nhiệm
    # (nếu thiếu các field này, response_model của FastAPI sẽ tự lọc bỏ
    #  mọi field không khai báo ở đây, dù service đã trả về đủ)
    tiet_day: int = 0
    lop_chu_nhiem: list[str] = []
    tiet_cn: int = 0
    tong_tiet: int