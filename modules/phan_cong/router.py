# modules/phan_cong/router.py
# Fix: đặt các route DELETE cụ thể LÊN TRÊN route DELETE /{pc_id}

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.db.session import get_db
from modules.phan_cong.service import PhanCongService
from modules.phan_cong.schemas import (
    PhanCongCreate, PhanCongXoaCuThe, PhanCongXoaTatCa,
    PhanCongResponse, PhanCongTongHopItem,
)

router = APIRouter(prefix="/phan-cong", tags=["Phân Công Giảng Dạy"])


def get_svc(db: Session = Depends(get_db)) -> PhanCongService:
    return PhanCongService(session=db)


@router.get("/", summary="Danh sách phân công")
def lay_ds(svc: PhanCongService = Depends(get_svc)):
    r = svc.lay_ds()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.get("/hoc-ky", summary="Phân công theo học kỳ")
def lay_ds_theo_hoc_ky(
    nam_hoc_id: int = Query(...),
    hoc_ky_id:  int = Query(...),
    svc: PhanCongService = Depends(get_svc),
):
    r = svc.lay_ds_theo_hoc_ky(nam_hoc_id, hoc_ky_id)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.get("/tong-hop", response_model=list[PhanCongTongHopItem],
            summary="Tổng hợp theo giáo viên")
def lay_tong_hop(svc: PhanCongService = Depends(get_svc)):
    r = svc.lay_ds_phan_cong_tong_hop()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.get("/giao-vien/{gv_id}", summary="Phân công của giáo viên")
def lay_theo_giao_vien(
    gv_id: int,
    nam_hoc_id: int = Query(...),
    hoc_ky_id:  int = Query(...),
    svc: PhanCongService = Depends(get_svc),
):
    r = svc.lay_phan_cong_theo_giao_vien(gv_id, nam_hoc_id, hoc_ky_id)
    if not r.ok: raise HTTPException(500, r.error)
    return [
        {
            "id": pc.id,
            "giao_vien_id": pc.giao_vien_id,
            "nam_hoc_id":   pc.nam_hoc_id,
            "hoc_ky_id":    pc.hoc_ky_id,
            "mon_hoc": {"id": pc.mon_hoc.id, "ten_mon": pc.mon_hoc.ten_mon} if pc.mon_hoc else None,
            "lop_hoc": {"id": pc.lop_hoc.id, "ten_lop": pc.lop_hoc.ten_lop, "khoi": pc.lop_hoc.khoi} if pc.lop_hoc else None,
        }
        for pc in r.data
    ]


@router.get("/meta/nam-hoc",  summary="Danh sách năm học")
def lay_nam_hoc(svc: PhanCongService = Depends(get_svc)):
    return [{"id": n.id, "ten_nam_hoc": n.ten_nam_hoc} for n in svc.lay_ds_nam_hoc()]

@router.get("/meta/hoc-ky", summary="Danh sách học kỳ")
def lay_hoc_ky(
    nam_hoc_id: Optional[int] = Query(None),
    svc: PhanCongService = Depends(get_svc),
):
    return [{"id": h.id, "ten_hoc_ky": h.ten_hoc_ky} for h in svc.lay_ds_hoc_ky(nam_hoc_id)]

@router.get("/meta/giao-vien", summary="Danh sách giáo viên")
def lay_giao_vien(svc: PhanCongService = Depends(get_svc)):
    return [
        {
            "id": gv.id,
            "ma_giao_vien": gv.ma_giao_vien,
            "ho_ten": gv.nguoi_dung.ho_ten if gv.nguoi_dung else "",
            "mon_day": gv.mon_day,
        }
        for gv in svc.lay_ds_giao_vien()
    ]

@router.get("/meta/mon-hoc", summary="Danh sách môn học")
def lay_mon_hoc(svc: PhanCongService = Depends(get_svc)):
    return [
        {"id": m.id, "ma_mon": m.ma_mon, "ten_mon": m.ten_mon}
        for m in svc.lay_ds_mon_hoc()
    ]

@router.get("/meta/lop-hoc", summary="Danh sách lớp học")
def lay_lop_hoc(svc: PhanCongService = Depends(get_svc)):
    return [
        {"id": l.id, "ma_lop": l.ma_lop, "ten_lop": l.ten_lop, "khoi": l.khoi}
        for l in svc.lay_ds_lop_hoc()
    ]


# ── POST ──────────────────────────────────────────────────────
@router.post("/", status_code=201, summary="Thêm phân công")
def them_phan_cong(body: PhanCongCreate, svc: PhanCongService = Depends(get_svc)):
    r = svc.them(
        giao_vien_id=body.giao_vien_id,
        nam_hoc_id=body.nam_hoc_id,
        hoc_ky_id=body.hoc_ky_id,
        phan_cong_list=[pc.model_dump() for pc in body.phan_cong_list],
        clear_old=body.clear_old,
    )
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ── DELETE cụ thể — phải đứng TRÊN DELETE /{pc_id} ──────────
@router.delete("/chi-tiet/xoa", summary="Xóa phân công cụ thể")
def xoa_cu_the(body: PhanCongXoaCuThe, svc: PhanCongService = Depends(get_svc)):
    r = svc.xoa_phan_cong(
        giao_vien_id=body.giao_vien_id,
        nam_hoc_id=body.nam_hoc_id,
        hoc_ky_id=body.hoc_ky_id,
        mon_hoc_id=body.mon_hoc_id,
        lop_hoc_id=body.lop_hoc_id,
    )
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


@router.delete("/tat-ca/xoa", summary="Xóa tất cả phân công của GV")
def xoa_tat_ca(body: PhanCongXoaTatCa, svc: PhanCongService = Depends(get_svc)):
    r = svc.xoa_tat_ca_phan_cong(
        giao_vien_id=body.giao_vien_id,
        nam_hoc_id=body.nam_hoc_id,
        hoc_ky_id=body.hoc_ky_id,
    )
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ── DELETE theo ID — phải đứng SAU các route cụ thể ─────────
@router.delete("/{pc_id}", summary="Xóa phân công theo ID")
def xoa(pc_id: int, svc: PhanCongService = Depends(get_svc)):
    r = svc.xoa(pc_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}