# modules/lop_hoc/schemas.py
from typing import Optional
from datetime import date
from pydantic import BaseModel, field_validator


# ── Giáo viên chủ nhiệm (brief) ───────────────────────────────

class GiaoVienBrief(BaseModel):
    id: int
    ma_giao_vien: str
    nguoi_dung: Optional[dict] = None

    model_config = {"from_attributes": True}


# ── Lớp học ───────────────────────────────────────────────────

class LopHocCreate(BaseModel):
    ma_lop: str
    ten_lop: str
    khoi: int
    si_so: Optional[int] = 0
    giao_vien_cn_id: Optional[int] = None
    nam_hoc_id: Optional[int] = None
    active: Optional[bool] = True

    @field_validator("ma_lop", "ten_lop")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()


class LopHocUpdate(BaseModel):
    ma_lop: Optional[str] = None
    ten_lop: Optional[str] = None
    khoi: Optional[int] = None
    si_so: Optional[int] = None
    giao_vien_cn_id: Optional[int] = None
    nam_hoc_id: Optional[int] = None
    active: Optional[bool] = None


class LopHocResponse(BaseModel):
    id: int
    ma_lop: str
    ten_lop: str
    khoi: int
    si_so: int
    active: bool
    giao_vien_cn_id: Optional[int] = None
    nam_hoc_id: Optional[int] = None
    ten_gvcn: Optional[str] = None   # computed field

    model_config = {"from_attributes": True}


class LopHocListResponse(BaseModel):
    total: int
    items: list[LopHocResponse]


# ── Học sinh ──────────────────────────────────────────────────

class HocSinhCreate(BaseModel):
    ma_hoc_sinh: str
    ho_ten: str
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[bool] = True   # True = Nam, False = Nữ
    so_dien_thoai: Optional[str] = None
    lop_hoc_id: int

    @field_validator("ma_hoc_sinh", "ho_ten")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()


class HocSinhUpdate(BaseModel):
    ma_hoc_sinh: Optional[str] = None
    ho_ten: Optional[str] = None
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[bool] = None
    so_dien_thoai: Optional[str] = None
    active: Optional[bool] = None


class HocSinhResponse(BaseModel):
    id: int
    ma_hoc_sinh: str
    ho_ten: str
    ngay_sinh: Optional[date] = None
    gioi_tinh: bool
    so_dien_thoai: Optional[str] = None
    lop_hoc_id: int
    active: bool

    model_config = {"from_attributes": True}
