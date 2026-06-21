# modules/cau_hinh/schemas.py
from typing import Optional
from pydantic import BaseModel, field_validator


# ── Năm học ───────────────────────────────────────────────────

class NamHocCreate(BaseModel):
    ten_nam_hoc: str
    active: Optional[bool] = True

class NamHocUpdate(BaseModel):
    ten_nam_hoc: Optional[str] = None
    active: Optional[bool] = None

class NamHocResponse(BaseModel):
    id: int
    ten_nam_hoc: str
    active: bool
    model_config = {"from_attributes": True}


# ── Học kỳ ────────────────────────────────────────────────────

class HocKyCreate(BaseModel):
    ten_hoc_ky: str
    nam_hoc_id: int
    so_thu_tu: int
    active: Optional[bool] = True

class HocKyUpdate(BaseModel):
    ten_hoc_ky: Optional[str] = None
    nam_hoc_id: Optional[int] = None
    so_thu_tu: Optional[int] = None
    active: Optional[bool] = None

class HocKyResponse(BaseModel):
    id: int
    ten_hoc_ky: str
    nam_hoc_id: int
    so_thu_tu: int
    active: bool
    ten_nam_hoc: Optional[str] = None
    model_config = {"from_attributes": True}


# ── Tổ chuyên môn ─────────────────────────────────────────────

class ToChuyenMonCreate(BaseModel):
    ma_to: str
    ten_to: str
    mo_ta: Optional[str] = ""
    active: Optional[bool] = True

    @field_validator("ma_to", "ten_to")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()

class ToChuyenMonUpdate(BaseModel):
    ma_to: Optional[str] = None
    ten_to: Optional[str] = None
    mo_ta: Optional[str] = None
    active: Optional[bool] = None

class ToChuyenMonResponse(BaseModel):
    id: int
    ma_to: str
    ten_to: str
    mo_ta: Optional[str] = ""
    active: bool
    model_config = {"from_attributes": True}


# ── Môn học ───────────────────────────────────────────────────

class MonHocCreate(BaseModel):
    ma_mon: str
    ten_mon: str
    co_phan_mon: Optional[bool] = False
    to_id: Optional[int] = None
    thu_tu: Optional[int] = 0
    active: Optional[bool] = True

    @field_validator("ma_mon", "ten_mon")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()

class MonHocUpdate(BaseModel):
    ma_mon: Optional[str] = None
    ten_mon: Optional[str] = None
    co_phan_mon: Optional[bool] = None
    to_id: Optional[int] = None
    thu_tu: Optional[int] = None
    active: Optional[bool] = None


# ── Phân môn ───────────────────────────────────────────────────

class PhanMonCreate(BaseModel):
    ma_phan_mon: str
    ten_phan_mon: str
    mon_hoc_id: int
    thu_tu: Optional[int] = 0
    active: Optional[bool] = True

    @field_validator("ma_phan_mon", "ten_phan_mon")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()

class PhanMonUpdate(BaseModel):
    ma_phan_mon: Optional[str] = None
    ten_phan_mon: Optional[str] = None
    mon_hoc_id: Optional[int] = None
    thu_tu: Optional[int] = None
    active: Optional[bool] = None

class PhanMonResponse(BaseModel):
    id: int
    ma_phan_mon: str
    ten_phan_mon: str
    mon_hoc_id: int
    thu_tu: int
    active: bool
    ten_mon_hoc: Optional[str] = None
    model_config = {"from_attributes": True}


# ── Số tiết theo khối ─────────────────────────────────────────

class MonHocKhoiCreate(BaseModel):
    mon_hoc_id: int
    khoi: int
    so_tiet: int

class MonHocKhoiUpdate(BaseModel):
    so_tiet: Optional[int] = None

class MonHocKhoiResponse(BaseModel):
    id: int
    mon_hoc_id: int
    khoi: int
    so_tiet: int
    model_config = {"from_attributes": True}


# ── Cập nhật MonHocResponse ──────────────────────────────────

class MonHocResponse(BaseModel):
    id: int
    ma_mon: str
    ten_mon: str
    co_phan_mon: bool
    to_id: Optional[int] = None
    thu_tu: int
    active: bool
    ten_to: Optional[str] = None
    phan_mon_list: Optional[list[PhanMonResponse]] = None
    khoi_list: Optional[list[MonHocKhoiResponse]] = None
    model_config = {"from_attributes": True}


# ── Tài khoản ─────────────────────────────────────────────────

class NguoiDungCreate(BaseModel):
    ho_ten: str
    email: str
    role: str
    mat_khau: Optional[str] = "eduschool@123"
    active: Optional[bool] = True

class NguoiDungUpdate(BaseModel):
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None

class NguoiDungResponse(BaseModel):
    id: int
    ho_ten: str
    email: str
    role: str
    active: bool
    model_config = {"from_attributes": True}

class ResetMatKhauRequest(BaseModel):
    mat_khau_moi: Optional[str] = "eduschool@123"


# ── Tiết học ──────────────────────────────────────────────────

class TietHocCreate(BaseModel):
    so_thu_tu: int
    ten_tiet: str
    thoi_gian_bat_dau: Optional[str] = ""
    thoi_gian_ket_thuc: Optional[str] = ""
    active: Optional[int] = 1

class TietHocUpdate(BaseModel):
    so_thu_tu: Optional[int] = None
    ten_tiet: Optional[str] = None
    thoi_gian_bat_dau: Optional[str] = None
    thoi_gian_ket_thuc: Optional[str] = None
    active: Optional[int] = None

class TietHocResponse(BaseModel):
    id: int
    so_thu_tu: int
    ten_tiet: str
    thoi_gian_bat_dau: Optional[str] = ""
    thoi_gian_ket_thuc: Optional[str] = ""
    active: int
    model_config = {"from_attributes": True}