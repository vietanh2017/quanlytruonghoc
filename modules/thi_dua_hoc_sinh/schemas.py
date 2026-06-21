# modules/thi_dua_hoc_sinh/schemas.py
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, field_validator


# ══ LOẠI VI PHẠM ═════════════════════════════════════════════

class LoaiViPhamCreate(BaseModel):
    ma_loi:   str
    ten_loi:  str
    loai:     str   # "vi_pham" | "thanh_tich"
    nhom:     Optional[str]  = ""
    so_diem:  float          = 0
    mo_ta:    Optional[str]  = ""
    thu_tu:   Optional[int]  = 0

    @field_validator("loai")
    @classmethod
    def check_loai(cls, v):
        if v not in ("vi_pham", "thanh_tich"):
            raise ValueError("loai phải là 'vi_pham' hoặc 'thanh_tich'")
        return v

class LoaiViPhamUpdate(BaseModel):
    ten_loi:  Optional[str]   = None
    loai:     Optional[str]   = None
    nhom:     Optional[str]   = None
    so_diem:  Optional[float] = None
    mo_ta:    Optional[str]   = None
    thu_tu:   Optional[int]   = None
    is_active: Optional[bool] = None

class LoaiViPhamResponse(BaseModel):
    id:       int
    ma_loi:   str
    ten_loi:  str
    loai:     str
    nhom:     Optional[str]  = ""
    so_diem:  float
    mo_ta:    Optional[str]  = ""
    thu_tu:   int
    is_active: bool
    model_config = {"from_attributes": True}


# ══ VI PHẠM CÁ NHÂN ══════════════════════════════════════════

class ThemViPhamCaNhan(BaseModel):
    hoc_sinh_id:     int
    loai_vi_pham_id: int
    nam_hoc_id:      int
    tuan:            int
    ngay_xay_ra:     date
    tiet:            Optional[int] = None
    mo_ta:           Optional[str] = ""
    nguoi_ghi_nhan:  Optional[str] = ""

class ViPhamCaNhanResponse(BaseModel):
    id:              int
    hoc_sinh_id:     int
    loai_vi_pham_id: int
    nam_hoc_id:      int
    tuan:            int
    so_diem:         float
    ngay_xay_ra:     date
    tiet:            Optional[int] = None
    mo_ta:           Optional[str] = ""
    nguoi_ghi_nhan:  Optional[str] = ""
    da_anh_huong_lop: bool = True
    model_config = {"from_attributes": True}


# ══ VI PHẠM TẬP THỂ ══════════════════════════════════════════

class ThemViPhamTapThe(BaseModel):
    lop_hoc_id:      int
    loai_vi_pham_id: int
    nam_hoc_id:      int
    tuan:            int
    ngay_xay_ra:     date
    tiet:            Optional[int] = None
    mo_ta:           Optional[str] = ""
    nguoi_ghi_nhan:  Optional[str] = ""

class ViPhamTapTheResponse(BaseModel):
    id:              int
    lop_hoc_id:      int
    loai_vi_pham_id: int
    nam_hoc_id:      int
    tuan:            int
    thu:             int
    so_diem:         float
    ngay_xay_ra:     date
    tiet:            Optional[int] = None
    mo_ta:           Optional[str] = ""
    nguoi_ghi_nhan:  Optional[str] = ""
    model_config = {"from_attributes": True}


# ══ ĐIỂM HỌC TẬP ═════════════════════════════════════════════

class DiemHocTapItem(BaseModel):
    lop_hoc_id:   int
    diem_hoc_tap: float
    ghi_chu:      Optional[str] = ""

class LuuDiemHocTapRequest(BaseModel):
    nam_hoc_id:   int
    tuan:         int
    nguoi_nhap:   Optional[str] = ""
    data:         List[DiemHocTapItem]
