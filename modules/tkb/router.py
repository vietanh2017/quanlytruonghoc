# modules/tkb/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from core.db.session import get_db
from .service import TKBService
from .schemas import (
    CauHinhNgayRequest, CauHinhTietRequest, CauHinhMonRequest,
    RangBuocGVRequest
)

router = APIRouter(prefix="/tkb", tags=["Thời Khóa Biểu"])


def get_svc(db: Session = Depends(get_db)) -> TKBService:
    return TKBService(session=db)


# ══ CẤU HÌNH NGÀY ══════════════════════════════════════════

@router.get("/cau-hinh-ngay")
def get_cau_hinh_ngay(
    nam_hoc_id: int = Query(...),
    svc: TKBService = Depends(get_svc)
):
    r = svc.get_cau_hinh_ngay(nam_hoc_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


@router.post("/cau-hinh-ngay")
def save_cau_hinh_ngay(
    body: CauHinhNgayRequest,
    svc: TKBService = Depends(get_svc)
):
    r = svc.save_cau_hinh_ngay(
        body.nam_hoc_id,
        [item.model_dump() for item in body.items]
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ CẤU HÌNH TIẾT ══════════════════════════════════════════

@router.get("/cau-hinh-tiet")
def get_cau_hinh_tiet(svc: TKBService = Depends(get_svc)):
    r = svc.get_cau_hinh_tiet()
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


@router.post("/cau-hinh-tiet")
def save_cau_hinh_tiet(
    body: CauHinhTietRequest,
    svc: TKBService = Depends(get_svc)
):
    r = svc.save_cau_hinh_tiet(
        [item.model_dump() for item in body.items]
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ CẤU HÌNH MÔN ══════════════════════════════════════════

@router.get("/cau-hinh-mon")
def get_cau_hinh_mon(
    nam_hoc_id: int = Query(...),
    svc: TKBService = Depends(get_svc)
):
    r = svc.get_cau_hinh_mon(nam_hoc_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


@router.post("/cau-hinh-mon")
def save_cau_hinh_mon(
    body: CauHinhMonRequest,
    svc: TKBService = Depends(get_svc)
):
    r = svc.save_cau_hinh_mon(
        body.nam_hoc_id,
        [item.model_dump() for item in body.items]
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ META ═══════════════════════════════════════════════════

@router.get("/meta/mon-hoc")
def get_mon_hoc(db: Session = Depends(get_db)):
    from core.db.models.mon_hoc import MonHoc
    data = db.query(MonHoc).filter(MonHoc.active == True).order_by(MonHoc.thu_tu).all()
    return [{"id": m.id, "ma_mon": m.ma_mon, "ten_mon": m.ten_mon} for m in data]


# ══ RÀNG BUỘC GIÁO VIÊN ════════════════════════════════════

@router.get("/rang-buoc-gv")
def get_rang_buoc_gv(
    nam_hoc_id: int = Query(...),
    svc: TKBService = Depends(get_svc)
):
    r = svc.get_rang_buoc_gv(nam_hoc_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


@router.post("/rang-buoc-gv")
def save_rang_buoc_gv(
    body: RangBuocGVRequest,
    svc: TKBService = Depends(get_svc)
):
    r = svc.save_rang_buoc_gv(
        body.nam_hoc_id,
        [item.model_dump() for item in body.items]
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ LẤY TKB ════════════════════════════════════════════════

@router.get("/theo-lop/{lop_hoc_id}")
def lay_tkb_lop(
    lop_hoc_id: int,
    nam_hoc_id: int = Query(...),
    hoc_ky_id: Optional[int] = Query(None),
    svc: TKBService = Depends(get_svc)
):
    r = svc.lay_tkb_theo_lop(nam_hoc_id, lop_hoc_id, hoc_ky_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


@router.get("/theo-gv/{giao_vien_id}")
def lay_tkb_gv(
    giao_vien_id: int,
    nam_hoc_id: int = Query(...),
    hoc_ky_id: Optional[int] = Query(None),
    svc: TKBService = Depends(get_svc)
):
    r = svc.lay_tkb_theo_gv(nam_hoc_id, giao_vien_id, hoc_ky_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


# ══ CRUD Ô TKB ═════════════════════════════════════════════

@router.post("/o-tkb")
def luu_o_tkb(body: dict, svc: TKBService = Depends(get_svc)):
    r = svc.luu_o_tkb(**body)
    if not r.ok:
        raise HTTPException(400, r.error)
    return r.data


@router.delete("/o-tkb/{tkb_id}")
def xoa_o_tkb(tkb_id: int, svc: TKBService = Depends(get_svc)):
    r = svc.xoa_o_tkb(tkb_id)
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.error}


# ══ PHÂN CÔNG ══════════════════════════════════════════════

@router.get("/phan-cong-lop/{lop_hoc_id}")
def lay_phan_cong_lop(
    lop_hoc_id: int,
    nam_hoc_id: int = Query(...),
    hoc_ky_id: int = Query(...),
    svc: TKBService = Depends(get_svc)
):
    r = svc.lay_phan_cong_theo_lop(nam_hoc_id, hoc_ky_id, lop_hoc_id)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


# ══ DEBUG ═══════════════════════════════════════════════════

@router.get("/debug-hocky")
def debug_hocky(db: Session = Depends(get_db)):
    from core.db.models.hoc_ky import HocKy
    from core.db.models.phan_cong import PhanCongGiangDay
    from sqlalchemy import func

    hoc_ky = db.query(HocKy).all()
    pc_hocky = db.query(
        PhanCongGiangDay.hoc_ky_id,
        func.count(PhanCongGiangDay.id).label("so_ban_ghi")
    ).group_by(PhanCongGiangDay.hoc_ky_id).all()

    return {
        "hoc_ky_list": [{"id": h.id, "ten": h.ten_hoc_ky, "nam_hoc_id": h.nam_hoc_id} for h in hoc_ky],
        "phan_cong_theo_hoc_ky": [{"hoc_ky_id": r.hoc_ky_id, "so_ban_ghi": r.so_ban_ghi} for r in pc_hocky],
    }


# ══ SINH TKB TỰ ĐỘNG ══════════════════════════════════════

@router.post("/sinh-tu-dong")
def sinh_tkb_tu_dong(body: dict, svc: TKBService = Depends(get_svc)):
    nam_hoc_id = body.get("nam_hoc_id")
    hoc_ky_id = body.get("hoc_ky_id")
    clear_old = body.get("clear_old", False)
    off_slots = body.get("off_slots", [])  # ⭐ Nhận từ frontend
    if not nam_hoc_id or not hoc_ky_id:
        raise HTTPException(400, "Thiếu năm học hoặc học kỳ")
    r = svc.sinh_tkb_tu_dong(nam_hoc_id, hoc_ky_id, clear_old, off_slots)
    if not r.ok:
        raise HTTPException(500, r.error)
    return r.data


# ══ SWAP ═══════════════════════════════════════════════════

@router.post("/swap-o-tkb")
def swap_o_tkb(body: dict, svc: TKBService = Depends(get_svc)):
    id1 = body.get("id1")
    id2 = body.get("id2")
    if not id1 or not id2:
        raise HTTPException(400, "Thiếu id1 hoặc id2")
    r = svc.swap_o_tkb(id1, id2)
    if not r.ok:
        raise HTTPException(400, r.error)
    return {"message": r.data}


# ══ TKB TẠI VỊ TRÍ ════════════════════════════════════════

@router.get("/tai-vi-tri")
def get_tkb_tai_vi_tri(
    nam_hoc_id: int = Query(...),
    hoc_ky_id: int = Query(...),
    thu: int = Query(...),
    buoi: str = Query(...),
    tiet: int = Query(...),
    svc: TKBService = Depends(get_svc)
):
    result = svc.get_tkb_at_position(nam_hoc_id, hoc_ky_id, thu, buoi, tiet)
    if not result.ok:
        raise HTTPException(400, detail=result.error)
    return result.data


# ══ MOVE / SWAP ════════════════════════════════════════════

# router.py - check-move
@router.post("/check-move")
def check_move(body: dict, svc: TKBService = Depends(get_svc)):
    print(f"📥 /check-move body: {body}")  # ⭐ LOG
    r = svc.check_move_tkb(
        source_id=body["source_id"],
        target_thu=body["target_thu"],
        target_buoi=body["target_buoi"],
        target_tiet=body["target_tiet"],
        target_lop_hoc_id=body.get("target_lop_hoc_id"),
    )
    print(f"📤 /check-move result: ok={r.ok}, data={r.data if r.ok else r.error}")  # ⭐ LOG
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return r.data

@router.post("/confirm-move")
def confirm_move(body: dict, svc: TKBService = Depends(get_svc)):
    r = svc.confirm_move_tkb(
        source_id=body["source_id"],
        target_thu=body["target_thu"],
        target_buoi=body["target_buoi"],
        target_tiet=body["target_tiet"],
        target_lop_hoc_id=body["target_lop_hoc_id"],
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return r.data


# router.py
@router.post("/confirm-swap")
def confirm_swap(body: dict, svc: TKBService = Depends(get_svc)):
    print(f"📥 /confirm-swap body: {body}")  # ⭐ LOG
    r = svc.confirm_swap_tkb(
        item_a_id=body["item_a_id"],
        item_b_id=body["item_b_id"],
    )
    print(f"📤 /confirm-swap result: ok={r.ok}")  # ⭐ LOG
    if not r.ok:
        raise HTTPException(400, r.error)
    return r.data


@router.post("/resolve-conflict")
def resolve_conflict(body: dict, svc: TKBService = Depends(get_svc)):
    r = svc.resolve_conflict_auto(
        item_a_id=body["item_a_id"],
        item_b_id=body["item_b_id"],
        target_thu=body["target_thu"],
        target_buoi=body["target_buoi"],
        target_tiet=body["target_tiet"],
        target_lop_hoc_id=body["target_lop_hoc_id"],
    )
    if not r.ok:
        raise HTTPException(400, r.error)
    return r.data

@router.get("/export")
def export_tkb(
    nam_hoc_id: int = Query(...),
    hoc_ky_id: int = Query(...),
    db: Session = Depends(get_db)
):
    from modules.tkb.export_service import TKBExportService
    svc = TKBExportService(db)
    output = svc.export_tkb(nam_hoc_id, hoc_ky_id)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=TKB_{nam_hoc_id}_{hoc_ky_id}.xlsx"}
    )
@router.post("/cascade-confirm")
def cascade_confirm(body: dict, svc: TKBService = Depends(get_svc)):
    moves = body.get("moves", [])
    if not moves:
        raise HTTPException(400, "Thiếu danh sách di chuyển")
    r = svc.cascade_confirm_move(moves)
    if not r.ok:
        raise HTTPException(400, r.error)
    return r.data