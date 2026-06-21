# modules/cau_hinh/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.db.session import get_db
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.schemas import (
    NamHocCreate, NamHocUpdate, NamHocResponse,
    HocKyCreate, HocKyUpdate, HocKyResponse,
    ToChuyenMonCreate, ToChuyenMonUpdate, ToChuyenMonResponse,
    MonHocCreate, MonHocUpdate, MonHocResponse,
    NguoiDungCreate, NguoiDungUpdate, NguoiDungResponse, ResetMatKhauRequest,
    TietHocCreate, TietHocUpdate, TietHocResponse, PhanMonCreate, PhanMonUpdate, PhanMonResponse,
    MonHocKhoiCreate, MonHocKhoiUpdate, MonHocKhoiResponse,
)
from core.db.models.quyen import QuyenModel
from core.db.models.vai_tro_quyen import VaiTroQuyenModel
from pydantic import BaseModel as PydanticBase

router = APIRouter(prefix="/cau-hinh", tags=["Cấu Hình"])


def get_svc(db: Session = Depends(get_db)) -> CauHinhService:
    return CauHinhService(session=db)


# ════════════════════════════════════════════════════
#  NĂM HỌC
# ════════════════════════════════════════════════════

@router.get("/nam-hoc", response_model=list[NamHocResponse])
def lay_ds_nam_hoc(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_nam_hoc()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/nam-hoc", response_model=NamHocResponse, status_code=201)
def them_nam_hoc(body: NamHocCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_nam_hoc(body.ten_nam_hoc, body.active)
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/nam-hoc/{id}", response_model=NamHocResponse)
def sua_nam_hoc(id: int, body: NamHocUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_nam_hoc(id, body.ten_nam_hoc, body.active)
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/nam-hoc/{id}")
def xoa_nam_hoc(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_nam_hoc(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  HỌC KỲ
# ════════════════════════════════════════════════════

@router.get("/hoc-ky", response_model=list[HocKyResponse])
def lay_ds_hoc_ky(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_hoc_ky()
    if not r.ok: raise HTTPException(500, r.error)
    items = []
    for hk in r.data:
        items.append(HocKyResponse(
            id=hk.id, ten_hoc_ky=hk.ten_hoc_ky,
            nam_hoc_id=hk.nam_hoc_id, so_thu_tu=hk.so_thu_tu,
            active=hk.active,
            ten_nam_hoc=hk.nam_hoc.ten_nam_hoc if hk.nam_hoc else None,
        ))
    return items

@router.post("/hoc-ky", response_model=HocKyResponse, status_code=201)
def them_hoc_ky(body: HocKyCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_hoc_ky(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    hk = r.data
    return HocKyResponse(
        id=hk.id, ten_hoc_ky=hk.ten_hoc_ky,
        nam_hoc_id=hk.nam_hoc_id, so_thu_tu=hk.so_thu_tu, active=hk.active,
        ten_nam_hoc=hk.nam_hoc.ten_nam_hoc if hk.nam_hoc else None,
    )

@router.put("/hoc-ky/{id}", response_model=HocKyResponse)
def sua_hoc_ky(id: int, body: HocKyUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_hoc_ky(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    hk = r.data
    return HocKyResponse(
        id=hk.id, ten_hoc_ky=hk.ten_hoc_ky,
        nam_hoc_id=hk.nam_hoc_id, so_thu_tu=hk.so_thu_tu, active=hk.active,
        ten_nam_hoc=hk.nam_hoc.ten_nam_hoc if hk.nam_hoc else None,
    )

@router.delete("/hoc-ky/{id}")
def xoa_hoc_ky(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_hoc_ky(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  TỔ CHUYÊN MÔN
# ════════════════════════════════════════════════════

@router.get("/to-chuyen-mon", response_model=list[ToChuyenMonResponse])
def lay_ds_to(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_to_chuyen_mon()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/to-chuyen-mon", response_model=ToChuyenMonResponse, status_code=201)
def them_to(body: ToChuyenMonCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_to_chuyen_mon(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/to-chuyen-mon/{id}", response_model=ToChuyenMonResponse)
def sua_to(id: int, body: ToChuyenMonUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_to_chuyen_mon(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/to-chuyen-mon/{id}")
def xoa_to(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_to_chuyen_mon(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  MÔN HỌC
# ════════════════════════════════════════════════════

@router.get("/mon-hoc", response_model=list[MonHocResponse])
def lay_ds_mon(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_mon_hoc()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/mon-hoc", response_model=MonHocResponse, status_code=201)
def them_mon(body: MonHocCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_mon_hoc(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/mon-hoc/{id}", response_model=MonHocResponse)
def sua_mon(id: int, body: MonHocUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_mon_hoc(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/mon-hoc/{id}")
def xoa_mon(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_mon_hoc(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  PHÂN MÔN
# ════════════════════════════════════════════════════

@router.get("/phan-mon", response_model=list[PhanMonResponse])
def lay_ds_phan_mon(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_phan_mon()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.get("/phan-mon/mon-hoc/{mon_hoc_id}", response_model=list[PhanMonResponse])
def lay_phan_mon_theo_mon(mon_hoc_id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_phan_mon_theo_mon(mon_hoc_id)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.post("/phan-mon", response_model=PhanMonResponse, status_code=201)
def them_phan_mon(body: PhanMonCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_phan_mon(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data


@router.put("/phan-mon/{id}", response_model=PhanMonResponse)
def sua_phan_mon(id: int, body: PhanMonUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_phan_mon(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data


@router.delete("/phan-mon/{id}")
def xoa_phan_mon(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_phan_mon(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ⭐ THÊM ENDPOINT XÓA TẤT CẢ PHÂN MÔN THEO MÔN HỌC
@router.delete("/phan-mon/mon-hoc/{mon_hoc_id}")
def xoa_phan_mon_theo_mon(mon_hoc_id: int, svc: CauHinhService = Depends(get_svc)):
    """
    Xóa tất cả phân môn của một môn học
    """
    try:
        # Lấy danh sách phân môn
        phan_mons = svc.phan_mon_repo.get_by_mon_hoc(mon_hoc_id)
        count = 0
        for pm in phan_mons:
            svc.phan_mon_repo.delete(pm.id)
            count += 1
        svc._commit()
        return {"message": f"Đã xóa {count} phân môn", "count": count}
    except Exception as e:
        svc._rollback()
        raise HTTPException(400, detail=str(e))
from core.db.models.mon_hoc import PhanMon

class PhanMonResponse(PydanticBase):
    id: int
    ma_phan_mon: str
    ten_phan_mon: str
    thu_tu: int
    active: bool
    model_config = {"from_attributes": True}

@router.get("/mon-hoc/{id}/phan-mon", response_model=list[PhanMonResponse])
def lay_phan_mon_cua_mon_hoc(id: int, db: Session = Depends(get_db)):
    """Lấy danh sách phân môn của một môn học."""
    return (db.query(PhanMon)
              .filter(PhanMon.mon_hoc_id == id, PhanMon.active == True)
              .order_by(PhanMon.thu_tu)
              .all())

# ════════════════════════════════════════════════════
#  SỐ TIẾT THEO KHỐI
# ════════════════════════════════════════════════════

@router.get("/mon-hoc/{mon_hoc_id}/so-tiet", response_model=list[MonHocKhoiResponse])
def lay_so_tiet_theo_mon(mon_hoc_id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_so_tiet_theo_khoi(mon_hoc_id)
    if not r.ok: raise HTTPException(500, r.error)
    return r.data


@router.post("/mon-hoc/so-tiet", response_model=MonHocKhoiResponse, status_code=201)
def them_so_tiet(body: MonHocKhoiCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_so_tiet_theo_khoi(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data


@router.put("/mon-hoc/so-tiet/{id}", response_model=MonHocKhoiResponse)
def sua_so_tiet(id: int, body: MonHocKhoiUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_so_tiet_theo_khoi(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data


@router.delete("/mon-hoc/so-tiet/{id}")
def xoa_so_tiet(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_so_tiet_theo_khoi(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


@router.delete("/mon-hoc/{mon_hoc_id}/so-tiet")
def xoa_toan_bo_so_tiet(mon_hoc_id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_toan_bo_so_tiet_theo_khoi(mon_hoc_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  TÀI KHOẢN
# ════════════════════════════════════════════════════

@router.get("/tai-khoan", response_model=list[NguoiDungResponse])
def lay_ds_tai_khoan(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_nguoi_dung()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/tai-khoan", response_model=NguoiDungResponse, status_code=201)
def them_tai_khoan(body: NguoiDungCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_nguoi_dung(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/tai-khoan/{id}", response_model=NguoiDungResponse)
def sua_tai_khoan(id: int, body: NguoiDungUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_nguoi_dung(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/tai-khoan/{id}")
def xoa_tai_khoan(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_nguoi_dung(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}

@router.patch("/tai-khoan/{id}/mat-khau")
def reset_mat_khau(id: int, body: ResetMatKhauRequest,
                   svc: CauHinhService = Depends(get_svc)):
    r = svc.reset_mat_khau(id, body.mat_khau_moi)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  TIẾT HỌC
# ════════════════════════════════════════════════════

@router.get("/tiet-hoc", response_model=list[TietHocResponse])
def lay_ds_tiet(svc: CauHinhService = Depends(get_svc)):
    r = svc.lay_ds_tiet_hoc()
    if not r.ok: raise HTTPException(500, r.error)
    return r.data

@router.post("/tiet-hoc", response_model=TietHocResponse, status_code=201)
def them_tiet(body: TietHocCreate, svc: CauHinhService = Depends(get_svc)):
    r = svc.them_tiet_hoc(**body.model_dump())
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.put("/tiet-hoc/{id}", response_model=TietHocResponse)
def sua_tiet(id: int, body: TietHocUpdate, svc: CauHinhService = Depends(get_svc)):
    r = svc.sua_tiet_hoc(id, **body.model_dump(exclude_none=True))
    if not r.ok: raise HTTPException(400, r.error)
    return r.data

@router.delete("/tiet-hoc/{id}")
def xoa_tiet(id: int, svc: CauHinhService = Depends(get_svc)):
    r = svc.xoa_tiet_hoc(id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}


# ════════════════════════════════════════════════════
#  PHÂN QUYỀN
# ════════════════════════════════════════════════════

class QuyenResponse(PydanticBase):
    id: int
    ma_quyen: str
    ten_quyen: str
    mo_ta: str = ""
    module: str = ""
    model_config = {"from_attributes": True}

class LuuPhanQuyenRequest(PydanticBase):
    quyen_ids: List[int]


# ⚠️ Route cụ thể PHẢI đứng trước route có {vai_tro}
@router.get("/phan-quyen/tat-ca-quyen", response_model=list[QuyenResponse])
def lay_tat_ca_quyen(db: Session = Depends(get_db)):
    return (db.query(QuyenModel)
              .filter(QuyenModel.active == True)
              .order_by(QuyenModel.module, QuyenModel.id)
              .all())


@router.get("/phan-quyen/{vai_tro}", response_model=list[int])
def lay_quyen_cua_vai_tro(vai_tro: str, db: Session = Depends(get_db)):
    rows = db.query(VaiTroQuyenModel).filter(VaiTroQuyenModel.vai_tro == vai_tro).all()
    return [r.quyen_id for r in rows]


@router.post("/phan-quyen/{vai_tro}")
def luu_quyen_cho_vai_tro(vai_tro: str, body: LuuPhanQuyenRequest,
                          db: Session = Depends(get_db)):
    db.query(VaiTroQuyenModel).filter(VaiTroQuyenModel.vai_tro == vai_tro).delete()
    for qid in body.quyen_ids:
        db.add(VaiTroQuyenModel(vai_tro=vai_tro, quyen_id=qid))
    db.commit()
    return {"message": f"Đã cập nhật {len(body.quyen_ids)} quyền cho {vai_tro}"}