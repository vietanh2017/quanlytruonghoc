# modules/thi_dua_giao_vien/schemas.py
from typing import Optional, List
from pydantic import BaseModel, field_validator


# ══ TIÊU CHÍ ══════════════════════════════════════════════════

class TieuChiCreate(BaseModel):
    ten_tieu_chi: str
    diem_toi_da:  float
    loai:         str   # "cong" | "tru"
    mo_ta:        Optional[str] = ""
    to_chuyen_mon_id: Optional[int] = None

    @field_validator("loai")
    @classmethod
    def check_loai(cls, v):
        if v not in ("cong", "tru"):
            raise ValueError("loai phải là 'cong' hoặc 'tru'")
        return v

class TieuChiUpdate(BaseModel):
    ten_tieu_chi:     Optional[str]   = None
    diem_toi_da:      Optional[float] = None
    loai:             Optional[str]   = None
    mo_ta:            Optional[str]   = None
    to_chuyen_mon_id: Optional[int]   = None
    active:           Optional[bool]  = None

class TieuChiResponse(BaseModel):
    id:           int
    ma_tieu_chi:  str
    ten_tieu_chi: str
    diem_toi_da:  float
    loai:         str
    mo_ta:        Optional[str] = ""
    active:       bool
    model_config = {"from_attributes": True}


# ══ CHẤM ĐIỂM ════════════════════════════════════════════════

class NhapDiemItem(BaseModel):
    tieu_chi_id: int
    diem:        float
    ghi_chu:     Optional[str] = ""

class NhapDiemRequest(BaseModel):
    giao_vien_id:  int
    thang:         int
    nam_hoc_id:    int
    nguoi_cham_id: Optional[int] = 1
    diem_list:     List[NhapDiemItem]

class DiemResponse(BaseModel):
    id:           int
    giao_vien_id: int
    tieu_chi_id:  int
    thang:        int
    nam_hoc_id:   int
    diem:         float
    ghi_chu:      Optional[str] = ""
    model_config = {"from_attributes": True}


# ══ KẾT QUẢ XẾP HẠNG ════════════════════════════════════════

class XepHangItem(BaseModel):
    giao_vien_id: int
    ma_giao_vien: str
    ho_ten:       str
    diem:         float
    xep_loai:     str
    hang:         int