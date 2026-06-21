# modules/giao_vien/schemas.py
"""
Pydantic schemas cho module Giáo viên.
Dùng để validate request/response trong FastAPI.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Tổ chuyên môn (dùng trong response) ──────────────────────

class ToChuyenMonBrief(BaseModel):
    id: int
    ten_to: str

    model_config = {"from_attributes": True}


# ── Người dùng (dùng trong response) ─────────────────────────

class NguoiDungBrief(BaseModel):
    id: int
    ho_ten: str
    email: str
    active: bool

    model_config = {"from_attributes": True}


# ── Giáo viên ─────────────────────────────────────────────────

class GiaoVienCreate(BaseModel):
    """Dùng cho POST /giao-vien/ — tạo mới"""
    ho_ten: str
    email: EmailStr
    mat_khau: Optional[str] = "eduschool@123"
    ma_giao_vien: str
    mon_day: Optional[str] = ""
    to_id: Optional[int] = None
    so_dien_thoai: Optional[str] = ""
    active: Optional[bool] = True

    @field_validator("ho_ten", "ma_giao_vien")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Không được để trống.")
        return v.strip()


class GiaoVienUpdate(BaseModel):
    """Dùng cho PUT /giao-vien/{id} — cập nhật"""
    ho_ten: Optional[str] = None
    email: Optional[EmailStr] = None
    mat_khau: Optional[str] = None
    ma_giao_vien: Optional[str] = None
    mon_day: Optional[str] = None
    to_id: Optional[int] = None
    so_dien_thoai: Optional[str] = None
    active: Optional[bool] = None


class GiaoVienResponse(BaseModel):
    """Dùng cho tất cả response trả về"""
    id: int
    ma_giao_vien: str
    mon_day: str
    so_dien_thoai: str
    active: bool
    nguoi_dung: Optional[NguoiDungBrief] = None
    to_chuyen_mon: Optional[ToChuyenMonBrief] = None

    model_config = {"from_attributes": True}


class GiaoVienListResponse(BaseModel):
    """Dùng cho GET /giao-vien/ — danh sách"""
    total: int
    items: list[GiaoVienResponse]


# ── Password reset ────────────────────────────────────────────

class DatLaiMatKhauRequest(BaseModel):
    mat_khau_moi: Optional[str] = "abc@123"

class ImportGiaoVienResult(BaseModel):
    """Kết quả import từ Excel"""
    tong_so: int = 0
    thanh_cong: int = 0
    that_bai: int = 0
    chi_tiet: list[dict] = []  # Mỗi item: {row: int, errors: list[str]}
    da_them: list[dict] = []   # Thông tin các giáo viên đã thêm