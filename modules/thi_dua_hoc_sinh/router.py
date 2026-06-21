# modules/thi_dua_hoc_sinh/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.db.session import get_db
from modules.thi_dua_hoc_sinh.service import ThiDuaHocSinhService
from modules.thi_dua_hoc_sinh.schemas import (
    LoaiViPhamCreate, LoaiViPhamUpdate, LoaiViPhamResponse,
    ThemViPhamCaNhan, ViPhamCaNhanResponse,
    ThemViPhamTapThe, ViPhamTapTheResponse,
    LuuDiemHocTapRequest,
)

router = APIRouter(prefix="/thi-dua-hs", tags=["Thi Đua Học Sinh"])


def get_svc(db: Session = Depends(get_db)) -> ThiDuaHocSinhService:
    return ThiDuaHocSinhService(session=db)


# ══ METADATA ═════════════════════════════════════════════════

@router.get("/meta/nam-hoc")
def lay_nam_hoc(svc: ThiDuaHocSinhService = Depends(get_svc)):
    return [{"id": n.id, "ten_nam_hoc": n.ten_nam_hoc}
            for n in svc.lay_ds_nam_hoc()]

@router.get("/meta/lop")
def lay_ds_lop(
    nam_hoc_id: Optional[int] = Query(None),  # ⭐ Không bắt buộc
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    # ⭐ Gọi hàm lay_ds_lop với tham số optional
    return [{"id": l.id, "ten_lop": l.ten_lop, "khoi": l.khoi}
            for l in svc.lay_ds_lop(nam_hoc_id)]

@router.get("/meta/hoc-sinh")
def lay_ds_hoc_sinh(lop_hoc_id: int = Query(...),
                    svc: ThiDuaHocSinhService = Depends(get_svc)):
    return [{"id": h.id, "ma_hoc_sinh": h.ma_hoc_sinh, "ho_ten": h.ho_ten}
            for h in svc.lay_ds_hoc_sinh(lop_hoc_id)]


# ══ DANH MỤC LOẠI VI PHẠM ════════════════════════════════════

@router.get("/loai-vi-pham", response_model=list[LoaiViPhamResponse])
def lay_ds_loai_vp(
    loai: Optional[str] = Query(None, description="vi_pham | thanh_tich"),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_ds_loai_vp(loai)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/loai-vi-pham", response_model=LoaiViPhamResponse, status_code=201)
def them_loai_vp(body: LoaiViPhamCreate, svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.them_loai_vp(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/loai-vi-pham/{id}", response_model=LoaiViPhamResponse)
def sua_loai_vp(id: int, body: LoaiViPhamUpdate,
                svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.sua_loai_vp(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/loai-vi-pham/{id}")
def xoa_loai_vp(id: int, svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.xoa_loai_vp(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ VI PHẠM CÁ NHÂN ══════════════════════════════════════════

@router.get("/ca-nhan")
def lay_vp_ca_nhan(
    lop_hoc_id: int = Query(...),
    nam_hoc_id: int = Query(...),
    tuan:       Optional[int] = Query(None),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_vp_ca_nhan(lop_hoc_id, nam_hoc_id, tuan)
    if not r.ok: raise HTTPException(500, r.error)
    return [
        {
            "id":              vp.id,
            "hoc_sinh_id":     vp.hoc_sinh_id,
            "ho_ten":          vp.hoc_sinh.ho_ten if vp.hoc_sinh else "",
            "loai_vi_pham_id": vp.loai_vi_pham_id,
            "ten_loi":         vp.loai_vi_pham.ten_loi if vp.loai_vi_pham else "",
            "loai":            vp.loai_vi_pham.loai if vp.loai_vi_pham else "",
            "so_diem":         vp.so_diem,
            "tuan":            vp.tuan,
            "ngay_xay_ra":     str(vp.ngay_xay_ra),
            "tiet":            vp.tiet,
            "mo_ta":           vp.mo_ta,
            "nguoi_ghi_nhan":  vp.nguoi_ghi_nhan,
        }
        for vp in r.data
    ]

@router.post("/ca-nhan", status_code=201)
def them_vp_ca_nhan(body: ThemViPhamCaNhan,
                    svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.them_vp_ca_nhan(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}

@router.delete("/ca-nhan/{vp_id}")
def xoa_vp_ca_nhan(vp_id: int, svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.xoa_vp_ca_nhan(vp_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ VI PHẠM TẬP THỂ ══════════════════════════════════════════

@router.get("/tap-the")
def lay_vp_tap_the(
    nam_hoc_id: int = Query(...),
    tuan:       int = Query(...),
    lop_hoc_id: Optional[int] = Query(None),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_vp_tap_the(nam_hoc_id, tuan, lop_hoc_id)
    if not r.ok: raise HTTPException(500, r.error)
    return [
        {
            "id":              vp.id,
            "lop_hoc_id":      vp.lop_hoc_id,
            "ten_lop":         vp.lop_hoc.ten_lop if vp.lop_hoc else "",
            "loai_vi_pham_id": vp.loai_vi_pham_id,
            "ten_loi":         vp.loai_vi_pham.ten_loi if vp.loai_vi_pham else "",
            "loai":            vp.loai_vi_pham.loai if vp.loai_vi_pham else "",
            "so_diem":         vp.so_diem,
            "tuan":            vp.tuan,
            "thu":             vp.thu,
            "ngay_xay_ra":     str(vp.ngay_xay_ra),
            "tiet":            vp.tiet,
            "mo_ta":           vp.mo_ta,
        }
        for vp in r.data
    ]

@router.post("/tap-the", status_code=201)
def them_vp_tap_the(body: ThemViPhamTapThe,
                    svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.them_vp_tap_the(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}

@router.delete("/tap-the/{vp_id}")
def xoa_vp_tap_the(vp_id: int, svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.xoa_vp_tap_the(vp_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ ĐIỂM TẬP THỂ TUẦN ════════════════════════════════════════

@router.get("/diem-tuan")
def lay_diem_tuan(
    nam_hoc_id: int = Query(...),
    tuan:       int = Query(...),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_diem_tuan(nam_hoc_id, tuan)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/diem-tuan/luu")
def luu_diem_hoc_tap(body: LuuDiemHocTapRequest,
                     svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.luu_diem_hoc_tap(
        nam_hoc_id=body.nam_hoc_id,
        tuan=body.tuan,
        data=[item.model_dump() for item in body.data],
        nguoi_nhap=body.nguoi_nhap or "",
    )
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ BÁO CÁO ══════════════════════════════════════════════════

@router.get("/bao-cao/xep-hang-tuan")
def xep_hang_tuan(
    nam_hoc_id: int = Query(...),
    tuan:       int = Query(...),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.bao_cao_xep_hang_tuan(nam_hoc_id, tuan)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.get("/bao-cao/ca-nhan")
def bao_cao_ca_nhan(
    lop_hoc_id: int = Query(...),
    nam_hoc_id: int = Query(...),
    tuan:       Optional[int] = Query(None),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.bao_cao_ca_nhan_theo_lop(lop_hoc_id, nam_hoc_id, tuan)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data
