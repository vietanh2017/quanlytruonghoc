# modules/tkb/schemas.py
from typing import Optional, List
from pydantic import BaseModel


class CauHinhNgayItem(BaseModel):
    thu: int
    co_buoi_sang: bool = True
    co_buoi_chieu: bool = False


class CauHinhNgayRequest(BaseModel):
    nam_hoc_id: int
    items: List[CauHinhNgayItem]


class CauHinhNgayResponse(BaseModel):
    id: int
    thu: int
    co_buoi_sang: bool
    co_buoi_chieu: bool
    model_config = {"from_attributes": True}


class CauHinhTietItem(BaseModel):
    buoi: str
    tiet_so: int
    gio_bat_dau: Optional[str] = None
    gio_ket_thuc: Optional[str] = None


class CauHinhTietRequest(BaseModel):
    items: List[CauHinhTietItem]


class CauHinhTietResponse(BaseModel):
    id: int
    buoi: str
    tiet_so: int
    gio_bat_dau: Optional[str]
    gio_ket_thuc: Optional[str]
    model_config = {"from_attributes": True}


class CauHinhMonItem(BaseModel):
    mon_hoc_id: int
    chi_buoi_sang: bool = False
    chi_buoi_chieu: bool = False
    khong_lien_tiet: bool = False
    so_tiet_toi_da_ngay: int = 0


class CauHinhMonRequest(BaseModel):
    nam_hoc_id: int
    items: List[CauHinhMonItem]


class CauHinhMonResponse(BaseModel):
    id: int
    mon_hoc_id: int
    ten_mon: Optional[str] = None
    chi_buoi_sang: bool
    chi_buoi_chieu: bool
    khong_lien_tiet: bool
    so_tiet_toi_da_ngay: int
    model_config = {"from_attributes": True}

class RangBuocGVItem(BaseModel):
    giao_vien_id: int
    chi_buoi_sang: bool = False
    chi_buoi_chieu: bool = False
    so_tiet_toi_da_ngay: int = 0
    so_tiet_toi_thieu_ngay: int = 0
    gom_tiet: bool = False
    so_ngay_nghi: int = 0
    ngay_nghi_list: List[int] = []  # [2, 4] = nghỉ thứ 2, thứ 4


class RangBuocGVRequest(BaseModel):
    nam_hoc_id: int
    items: List[RangBuocGVItem]


class RangBuocGVResponse(BaseModel):
    id: int
    giao_vien_id: int
    ho_ten: Optional[str] = None
    chi_buoi_sang: bool
    chi_buoi_chieu: bool
    so_tiet_toi_da_ngay: int
    so_tiet_toi_thieu_ngay: int
    gom_tiet: bool
    so_ngay_nghi: int
    ngay_nghi_list: List[int] = []
    model_config = {"from_attributes": True}