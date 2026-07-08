# modules/reports/schemas.py
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# ══ FILTERS ════════════════════════════════════════════════════

class ReportFilter(BaseModel):
    loai: str  # tuan, thang, hoc_ky, nam_hoc, ca_nhan, giao_vien
    nam_hoc_id: Optional[int] = None
    hoc_ky_id: Optional[int] = None
    thang_id: Optional[int] = None
    tuan: Optional[int] = None
    lop_hoc_id: Optional[int] = None
    khoi: Optional[int] = None

# ══ RESPONSE ═══════════════════════════════════════════════════

class ReportStats(BaseModel):
    tong_lop: int = 0
    tong_hs: int = 0
    tong_gv: int = 0
    tong_vi_pham: int = 0
    tong_thanh_tich: int = 0
    diem_cao_nhat: float = 0
    diem_thap_nhat: float = 0
    diem_trung_binh: float = 0

class ReportItem(BaseModel):
    lop_hoc_id: int
    ten_lop: str
    khoi: int
    si_so: Optional[int] = 0
    ten_gvcn: Optional[str] = None
    diem_doi: Optional[float] = 0
    diem_hoc_tap: Optional[float] = 0
    trung_binh: float = 0
    xep_hang: Optional[int] = None
    so_vi_pham: Optional[int] = 0
    so_thanh_tich: Optional[int] = 0
    chi_tiet: Optional[dict] = None

class ReportResponse(BaseModel):
    loai: str
    ten_bao_cao: str
    nam_hoc: Optional[str] = None
    hoc_ky: Optional[str] = None
    thang: Optional[str] = None
    tuan: Optional[int] = None
    ngay_tao: str = datetime.now().strftime("%d/%m/%Y %H:%M")
    stats: ReportStats
    data: List[ReportItem]