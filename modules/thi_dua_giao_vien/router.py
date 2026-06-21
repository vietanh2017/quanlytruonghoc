# modules/thi_dua_giao_vien/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.db.session import get_db
from modules.thi_dua_giao_vien.service import ThiDuaGVServiceWeb  # ⭐ Đúng
from modules.thi_dua_giao_vien.schemas import (
    TieuChiCreate, TieuChiUpdate, TieuChiResponse,
    NhapDiemRequest, XepHangItem,
)

router = APIRouter(prefix="/thi-dua-gv", tags=["Thi Đua Giáo Viên"])


def get_svc(db: Session = Depends(get_db)) -> ThiDuaGVServiceWeb:
    return ThiDuaGVServiceWeb(session=db)


# ══ METADATA ═════════════════════════════════════════════════

@router.get("/meta/nam-hoc")
def lay_nam_hoc(svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    return [{"id": n.id, "ten_nam_hoc": n.ten_nam_hoc}
            for n in svc.lay_ds_nam_hoc()]

@router.get("/meta/hoc-ky")
def lay_hoc_ky(nam_hoc_id: int = Query(...),
               svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    return [{"id": h.id, "ten_hoc_ky": h.ten_hoc_ky, "so_thu_tu": h.so_thu_tu}
            for h in svc.lay_ds_hoc_ky(nam_hoc_id)]

@router.get("/meta/to")
def lay_ds_to(svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    return [{"id": t.id, "ten_to": t.ten_to}
            for t in svc.lay_ds_to()]

@router.get("/meta/giao-vien")
def lay_giao_vien(to_id: Optional[int] = Query(None),
                  svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    return [
        {
            "id": gv.id,
            "ma_giao_vien": gv.ma_giao_vien,
            "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
            "to_id": gv.to_id,
        }
        for gv in svc.lay_ds_giao_vien(to_id)
    ]


# ══ TIÊU CHÍ ═════════════════════════════════════════════════

@router.get("/tieu-chi", response_model=list[TieuChiResponse])
def lay_ds_tieu_chi(
    to_id: Optional[int] = Query(None),
    svc: ThiDuaGVServiceWeb = Depends(get_svc)
):
    r = svc.lay_ds_tieu_chi(to_id)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/tieu-chi", response_model=TieuChiResponse, status_code=201)
def them_tieu_chi(body: TieuChiCreate,
                  svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    r = svc.them_tieu_chi(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/tieu-chi/{tc_id}", response_model=TieuChiResponse)
def sua_tieu_chi(tc_id: int, body: TieuChiUpdate,
                 svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    r = svc.sua_tieu_chi(tc_id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/tieu-chi/{tc_id}")
def xoa_tieu_chi(tc_id: int, svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    r = svc.xoa_tieu_chi(tc_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ CHẤM ĐIỂM ════════════════════════════════════════════════

@router.get("/diem")
def lay_diem_thang(
    giao_vien_id: int = Query(...),
    thang:        int = Query(...),
    nam_hoc_id:   int = Query(...),
    svc: ThiDuaGVServiceWeb = Depends(get_svc)
):
    """Lấy điểm đã chấm của GV trong tháng, kèm thông tin tiêu chí."""
    r = svc.lay_diem_thang(giao_vien_id, thang, nam_hoc_id)
    if not r.ok: raise HTTPException(500, r.error)
    return [
        {
            "id":          d.id,
            "tieu_chi_id": d.tieu_chi_id,
            "ten_tieu_chi": d.tieu_chi.ten_tieu_chi if d.tieu_chi else "",
            "loai":        d.tieu_chi.loai if d.tieu_chi else "",
            "diem_toi_da": d.tieu_chi.diem_toi_da if d.tieu_chi else 0,
            "diem":        d.diem,
            "ghi_chu":     d.ghi_chu or "",
        }
        for d in r.data
    ]

@router.post("/diem")
def nhap_diem(body: NhapDiemRequest,
              svc: ThiDuaGVServiceWeb = Depends(get_svc)):
    r = svc.nhap_diem_hang_loat(
        giao_vien_id=body.giao_vien_id,
        thang=body.thang,
        nam_hoc_id=body.nam_hoc_id,
        diem_list=[item.model_dump() for item in body.diem_list],
        nguoi_cham_id=body.nguoi_cham_id or 1,
    )
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ XẾP HẠNG ══════════════════════════════════════════════════

@router.get("/xep-hang/thang", response_model=list[XepHangItem])
def xep_hang_thang(
    thang:      int = Query(...),
    nam_hoc_id: int = Query(...),
    to_id:      Optional[int] = Query(None),
    svc: ThiDuaGVServiceWeb = Depends(get_svc)
):
    return svc.xep_hang_theo_thang(thang, nam_hoc_id, to_id)

@router.get("/xep-hang/hoc-ky", response_model=list[XepHangItem])
def xep_hang_hoc_ky(
    hoc_ky_so_thu_tu: int = Query(..., description="1 hoặc 2"),
    nam_hoc_id:       int = Query(...),
    to_id:            Optional[int] = Query(None),
    svc: ThiDuaGVServiceWeb = Depends(get_svc)
):
    return svc.xep_hang_theo_hoc_ky(hoc_ky_so_thu_tu, nam_hoc_id, to_id)

@router.get("/xep-hang/ca-nam")
def xep_hang_ca_nam(
    nam_hoc_id: int = Query(...),
    to_id:      Optional[int] = Query(None),
    svc: ThiDuaGVServiceWeb = Depends(get_svc)
):
    return svc.xep_hang_ca_nam(nam_hoc_id, to_id)