# modules/cau_hinh/schemas.py
from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import date, datetime


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


# ═══════════════════════════════════════════════════════════════
# ⭐ THÊM SCHEMAS CHO THÔNG TIN TRƯỜNG
# ═══════════════════════════════════════════════════════════════

class ThongTinTruongCreate(BaseModel):
    ten_truong: str
    ten_truong_tieng_anh: Optional[str] = ""
    dia_chi: Optional[str] = ""
    dien_thoai: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    ma_so_truong: Optional[str] = ""
    logo: Optional[str] = ""
    
    nam_hoc_id: Optional[int] = None
    hoc_ky_id: Optional[int] = None
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None
    
    hieu_truong: Optional[str] = ""
    hieu_pho: Optional[str] = ""
    to_truong_cm: Optional[str] = ""
    nguoi_lap: Optional[str] = ""
    is_active: Optional[bool] = True

    @field_validator("ten_truong")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tên trường không được để trống.")
        return v.strip()


class ThongTinTruongUpdate(BaseModel):
    ten_truong: Optional[str] = None
    ten_truong_tieng_anh: Optional[str] = None
    dia_chi: Optional[str] = None
    dien_thoai: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    ma_so_truong: Optional[str] = None
    logo: Optional[str] = None
    
    nam_hoc_id: Optional[int] = None
    hoc_ky_id: Optional[int] = None
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None
    
    hieu_truong: Optional[str] = None
    hieu_pho: Optional[str] = None
    to_truong_cm: Optional[str] = None
    nguoi_lap: Optional[str] = None
    is_active: Optional[bool] = None


class ThongTinTruongResponse(BaseModel):
    id: int
    ten_truong: str
    ten_truong_tieng_anh: Optional[str] = ""
    dia_chi: Optional[str] = ""
    dien_thoai: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    ma_so_truong: Optional[str] = ""
    logo: Optional[str] = ""
    
    nam_hoc_id: Optional[int] = None
    hoc_ky_id: Optional[int] = None
    ten_nam_hoc: Optional[str] = ""
    ten_hoc_ky: Optional[str] = ""
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None
    
    hieu_truong: Optional[str] = ""
    hieu_pho: Optional[str] = ""
    to_truong_cm: Optional[str] = ""
    nguoi_lap: Optional[str] = ""
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# ── Cấu hình chung (Key-Value) ──────────────────────────────

class CauHinhChungCreate(BaseModel):
    key: str
    value: str
    ghi_chu: Optional[str] = ""

    @field_validator("key")
    @classmethod
    def key_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Key không được để trống.")
        return v.strip()


class CauHinhChungUpdate(BaseModel):
    value: Optional[str] = None
    ghi_chu: Optional[str] = None


class CauHinhChungResponse(BaseModel):
    id: int
    key: str
    value: Optional[str] = ""
    ghi_chu: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}