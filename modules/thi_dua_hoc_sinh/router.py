# modules/thi_dua_hoc_sinh/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from typing import Optional, List  # ⭐ Thêm List


from core.db.session import get_db
from modules.thi_dua_hoc_sinh.service import ThiDuaHocSinhService
from modules.thi_dua_hoc_sinh.schemas import (
    LoaiViPhamCreate, LoaiViPhamUpdate, LoaiViPhamResponse,
    ThemViPhamCaNhan, ViPhamCaNhanResponse,
    ThemViPhamTapThe, ViPhamTapTheResponse,
    LuuDiemHocTapRequest, 
    ThangThiDuaCreate, ThangThiDuaUpdate, ThangThiDuaResponse,
    HocKyThiDuaCreate, HocKyThiDuaUpdate, HocKyThiDuaResponse,  # ⭐ Dùng schema mới
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

# modules/thi_dua_hoc_sinh/router.py
# Sửa endpoint thêm vi phạm cá nhân

@router.post("/ca-nhan", status_code=201)
def them_vp_ca_nhan(body: ThemViPhamCaNhan,
                    svc: ThiDuaHocSinhService = Depends(get_svc)):
    # ⭐ In ra để debug
    print(f"📝 Nhận dữ liệu cá nhân: {body.model_dump()}")
    
    r = svc.them_vp_ca_nhan(
        hoc_sinh_id=body.hoc_sinh_id,
        loai_vi_pham_id=body.loai_vi_pham_id,
        nam_hoc_id=body.nam_hoc_id,
        tuan=body.tuan,
        ngay_xay_ra=body.ngay_xay_ra,
        so_diem=body.so_diem,  # ⭐ Truyền điểm từ frontend
        tiet=body.tiet,
        mo_ta=body.mo_ta,
        nguoi_ghi_nhan=body.nguoi_ghi_nhan or "",
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

@router.delete("/ca-nhan/{vp_id}")
def xoa_vp_ca_nhan(vp_id: int, svc: ThiDuaHocSinhService = Depends(get_svc)):
    r = svc.xoa_vp_ca_nhan(vp_id)
    if not r.ok: raise HTTPException(400, r.error)
    return {"message": r.error}
@router.put("/ca-nhan/{vp_id}", status_code=200)
def sua_vp_ca_nhan(
    vp_id: int,
    body: dict,  # Hoặc tạo schema riêng
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    """Cập nhật vi phạm cá nhân"""
    r = svc.sua_vp_ca_nhan(
        vp_id=vp_id,
        loai_vi_pham_id=body.get("loai_vi_pham_id"),
        so_diem=body.get("so_diem"),
        ngay_xay_ra=body.get("ngay_xay_ra"),
        tiet=body.get("tiet"),
        mo_ta=body.get("mo_ta", ""),
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
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
@router.put("/tap-the/{vp_id}", status_code=200)
def sua_vp_tap_the(
    vp_id: int,
    body: dict,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    """Cập nhật vi phạm tập thể"""
    r = svc.sua_vp_tap_the(
        vp_id=vp_id,
        loai_vi_pham_id=body.get("loai_vi_pham_id"),
        so_diem=body.get("so_diem"),
        ngay_xay_ra=body.get("ngay_xay_ra"),
        tiet=body.get("tiet"),
        mo_ta=body.get("mo_ta", ""),
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

# ══ ĐIỂM TẬP THỂ TUẦN ════════════════════════════════════════

@router.get("/diem-tuan")
def lay_diem_tuan(
    nam_hoc_id: int = Query(...),
    tuan: int = Query(...),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_diem_tuan(nam_hoc_id, tuan)
    if not r.ok:
        raise HTTPException(500, detail=r.error)
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
# modules/thi_dua_hoc_sinh/router.py (thêm vào cuối file)

# modules/thi_dua_hoc_sinh/router.py

# ══ THÁNG THI ĐUA ═════════════════════════════════════════════

@router.get("/thang", response_model=list[ThangThiDuaResponse])
def lay_ds_thang(
    nam_hoc_id: Optional[int] = Query(None),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_ds_thang(nam_hoc_id)
    if not r.ok:
        raise HTTPException(500, detail=r.error)
    return r.data

@router.post("/thang", status_code=201)
def them_thang(
    body: ThangThiDuaCreate,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.tao_thang_va_luu_diem(
        ten_thang=body.ten_thang,
        nam_hoc_id=body.nam_hoc_id,
        tuan_list=body.tuan_list,
        is_active=body.is_active
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error, "data": r.data}

@router.put("/thang/{thang_id}")
def sua_thang(
    thang_id: int,
    body: ThangThiDuaUpdate,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.sua_thang_va_cap_nhat_diem(
        thang_id=thang_id,
        ten_thang=body.ten_thang,
        tuan_list=body.tuan_list,
        is_active=body.is_active
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

@router.delete("/thang/{thang_id}")
def xoa_thang(
    thang_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.xoa_thang(thang_id)
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

@router.get("/bao-cao-thang/{thang_id}")
def bao_cao_thang(
    thang_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.get_bao_cao_thang(thang_id)
    if not r.ok:
        raise HTTPException(500, detail=r.error)
    return r.data
@router.post("/thang/{thang_id}/cap-nhat-diem")
def cap_nhat_diem_thang(
    thang_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    """Cập nhật lại điểm cho một tháng"""
    r = svc.cap_nhat_diem_cho_thang(thang_id)
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

# ══ HỌC KỲ THI ĐUA ══════════════════════════════════════════

@router.get("/hoc-ky", response_model=list[HocKyThiDuaResponse])  # ⭐ Dùng schema mới
def lay_ds_hoc_ky(
    nam_hoc_id: Optional[int] = Query(None),
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.lay_ds_hoc_ky(nam_hoc_id)
    if not r.ok:
        raise HTTPException(500, detail=r.error)
    return r.data

@router.post("/hoc-ky", status_code=201)
def tao_hoc_ky(
    body: HocKyThiDuaCreate,  # ⭐ Dùng schema mới
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.tao_hoc_ky_va_luu_diem(
        ten_hoc_ky=body.ten_hoc_ky,
        nam_hoc_id=body.nam_hoc_id,
        thang_list=body.thang_list,
        is_active=body.is_active
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error, "data": r.data}

@router.put("/hoc-ky/{hoc_ky_id}")
def sua_hoc_ky(
    hoc_ky_id: int,
    body: HocKyThiDuaUpdate,  # ⭐ Dùng schema mới
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.sua_hoc_ky(
        hoc_ky_id=hoc_ky_id,
        ten_hoc_ky=body.ten_hoc_ky,
        thang_list=body.thang_list,
        is_active=body.is_active
    )
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

@router.delete("/hoc-ky/{hoc_ky_id}")
def xoa_hoc_ky(
    hoc_ky_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.xoa_hoc_ky(hoc_ky_id)
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}

@router.get("/bao-cao-hoc-ky/{hoc_ky_id}")
def bao_cao_hoc_ky(
    hoc_ky_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    r = svc.get_bao_cao_hoc_ky(hoc_ky_id)
    if not r.ok:
        raise HTTPException(500, detail=r.error)
    return r.data
@router.post("/hoc-ky/{hoc_ky_id}/cap-nhat-diem")
def cap_nhat_diem_hoc_ky(
    hoc_ky_id: int,
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    """Cập nhật lại điểm cho một học kỳ"""
    r = svc.cap_nhat_diem_cho_hoc_ky(hoc_ky_id)
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return {"message": r.error}
# ══ BÁO CÁO NĂM HỌC ══════════════════════════════════════════

@router.post("/bao-cao-nam-hoc")
def bao_cao_nam_hoc(
    body: dict,  # {"hoc_ky_list": [1, 2, 3, 4]}
    svc: ThiDuaHocSinhService = Depends(get_svc)
):
    hoc_ky_list = body.get("hoc_ky_list", [])
    r = svc.get_bao_cao_nam_hoc(hoc_ky_list)
    if not r.ok:
        raise HTTPException(400, detail=r.error)
    return r.data

# ══ CẤU HÌNH THI ĐUA ══════════════════════════════════════════

@router.get("/cau-hinh/so-ngay")
def get_so_ngay(svc: ThiDuaHocSinhService = Depends(get_svc)):
    so_ngay = svc._get_so_ngay_trong_tuan()
    return {"so_ngay": so_ngay}

@router.post("/cau-hinh/so-ngay")
def set_so_ngay(so_ngay: int = Query(...), db: Session = Depends(get_db)):
    try:
        from modules.thi_dua_hoc_sinh.models.thi_dua_cau_hinh import ThiDuaCauHinh
        record = db.query(ThiDuaCauHinh).filter(
            ThiDuaCauHinh.key == 'so_ngay_trong_tuan'
        ).first()
        if record:
            record.value = str(so_ngay)
        else:
            record = ThiDuaCauHinh(key='so_ngay_trong_tuan', value=str(so_ngay))
            db.add(record)
        db.commit()
        return {"so_ngay": so_ngay}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))