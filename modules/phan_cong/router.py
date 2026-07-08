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
    hoc_ky_id: int = Query(...),
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
    hoc_ky_id: int = Query(...),
    svc: PhanCongService = Depends(get_svc),
):
    r = svc.lay_phan_cong_theo_giao_vien(gv_id, nam_hoc_id, hoc_ky_id)
    if not r.ok: raise HTTPException(500, r.error)
    return [
        {
            "id": pc.id,
            "giao_vien_id": pc.giao_vien_id,
            "nam_hoc_id": pc.nam_hoc_id,
            "hoc_ky_id": pc.hoc_ky_id,
            "mon_hoc": {"id": pc.mon_hoc.id, "ten_mon": pc.mon_hoc.ten_mon} if pc.mon_hoc else None,
            "lop_hoc": {"id": pc.lop_hoc.id, "ten_lop": pc.lop_hoc.ten_lop, "khoi": pc.lop_hoc.khoi} if pc.lop_hoc else None,
        }
        for pc in r.data
    ]


@router.get("/meta/nam-hoc", summary="Danh sách năm học")
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
            "kiem_nhiem": gv.kiem_nhiem or "",  # ✅ Thêm
        }
        for gv in svc.lay_ds_giao_vien()
    ]

@router.get("/meta/mon-hoc", summary="Danh sách môn học")
def lay_mon_hoc(svc: PhanCongService = Depends(get_svc)):
    return [
        {"id": m.id, "ma_mon": m.ma_mon, "ten_mon": m.ten_mon}
        for m in svc.lay_ds_mon_hoc()
    ]

@router.get("/phan-mon-gv/{gv_id}", summary="Lấy phân môn của GV")
def lay_phan_mon_gv(
    gv_id: int,
    nam_hoc_id: int = Query(...),
    hoc_ky_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Lấy danh sách môn có phân môn của GV — dùng cho popup"""
    from core.db.models.phan_cong import PhanCongGiangDay
    from core.db.models.mon_hoc import MonHoc, PhanMon

    # Lấy các môn có co_phan_mon=True của GV
    ds_pc = db.query(PhanCongGiangDay).filter(
        PhanCongGiangDay.giao_vien_id == gv_id,
        PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
        PhanCongGiangDay.hoc_ky_id == hoc_ky_id,
    ).all()

    # Gom theo môn có phân môn
    mon_map = {}
    for pc in ds_pc:
        mon = pc.mon_hoc
        if not mon or not mon.co_phan_mon:
            continue
        if mon.id not in mon_map:
            ds_phan_mon = db.query(PhanMon).filter(
                PhanMon.mon_hoc_id == mon.id,
                PhanMon.active == True
            ).order_by(PhanMon.thu_tu).all()
            mon_map[mon.id] = {
                "mon_hoc_id": mon.id,
                "ten_mon": mon.ten_mon,
                "ds_lop": [],
                "ds_phan_mon": [
                    {"id": pm.id, "ten_phan_mon": pm.ten_phan_mon}
                    for pm in ds_phan_mon
                ],
            }
        lop = pc.lop_hoc
        if lop:
            mon_map[mon.id]["ds_lop"].append({
                "pc_id": pc.id,
                "lop_hoc_id": lop.id,
                "ten_lop": lop.ten_lop,
                "phan_mon_id": pc.phan_mon_id,
                "ten_phan_mon": pc.phan_mon.ten_phan_mon if pc.phan_mon else None,
            })

    return list(mon_map.values())


@router.put("/phan-mon-gv", summary="Lưu phân môn cho GV")
def luu_phan_mon_gv(body: dict, db: Session = Depends(get_db)):
    """Lưu phân môn cho từng lớp của GV"""
    from core.db.models.phan_cong import PhanCongGiangDay

    items = body.get("items", [])  # [{pc_id, phan_mon_id}]
    for item in items:
        pc = db.get(PhanCongGiangDay, item["pc_id"])
        if pc:
            pc.phan_mon_id = item.get("phan_mon_id")
    db.commit()
    return {"message": f"Đã lưu {len(items)} phân môn"}

@router.get("/meta/lop-hoc", summary="Danh sách lớp học")
def lay_lop_hoc(svc: PhanCongService = Depends(get_svc)):
    return [
        {
            "id": l.id,
            "ma_lop": l.ma_lop,
            "ten_lop": l.ten_lop,
            "khoi": l.khoi,
            "giao_vien_cn_id": l.giao_vien_cn_id,  # ✅ Thêm
        }
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


# ✅ Sửa lại route xóa nhiều giáo viên
@router.delete("/nhieu-giao-vien", summary="Xóa phân công của nhiều giáo viên")
def delete_nhieu_giao_vien(data: dict, db: Session = Depends(get_db)):
    from core.db.models.phan_cong import PhanCongGiangDay  # ✅ Đúng tên model

    giao_vien_ids = data.get("giao_vien_ids", [])
    nam_hoc_id = data.get("nam_hoc_id")
    hoc_ky_id = data.get("hoc_ky_id")

    if not giao_vien_ids:
        raise HTTPException(400, "Chưa chọn giáo viên")
    if not nam_hoc_id or not hoc_ky_id:
        raise HTTPException(400, "Thiếu năm học hoặc học kỳ")

    deleted = db.query(PhanCongGiangDay).filter(
        PhanCongGiangDay.giao_vien_id.in_(giao_vien_ids),
        PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
        PhanCongGiangDay.hoc_ky_id == hoc_ky_id
    ).delete(synchronize_session=False)

    db.commit()

    return {
        "message": f"Đã xóa {deleted} phân công của {len(giao_vien_ids)} giáo viên",
        "deleted": deleted,
    }


# ── DELETE theo ID — phải đứng SAU các route cụ thể ─────────
@router.delete("/{pc_id}", summary="Xóa phân công theo ID")
def xoa(pc_id: int, svc: PhanCongService = Depends(get_svc)):
    r = svc.xoa(pc_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}