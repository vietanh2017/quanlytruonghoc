# modules/giao_vien/router.py
"""
FastAPI router cho module Giáo viên.
Đây là file MỚI hoàn toàn — thay thế toàn bộ phần views/ và dialogs/.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.giao_vien.service import GiaoVienService
from modules.giao_vien.schemas import (
    GiaoVienCreate,
    GiaoVienUpdate,
    GiaoVienResponse,
    GiaoVienListResponse,
    DatLaiMatKhauRequest,
    ImportGiaoVienResult,  # THÊM IMPORT NÀY
)

router = APIRouter(prefix="/giao-vien", tags=["Giáo Viên"])


def get_service(db: Session = Depends(get_db)) -> GiaoVienService:
    """Dependency injection — tạo service với session từ FastAPI."""
    return GiaoVienService(session=db)


# ── GET /giao-vien/ ───────────────────────────────────────────

@router.get("/", response_model=GiaoVienListResponse, summary="Danh sách giáo viên")
def lay_danh_sach(
    include_inactive: bool = Query(False, description="Bao gồm giáo viên đã vô hiệu hóa"),
    service: GiaoVienService = Depends(get_service),
):
    result = service.lay_ds(include_inactive=include_inactive)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.error)
    return GiaoVienListResponse(total=len(result.data), items=result.data)


# ── GET /giao-vien/to/{to_id} ─────────────────────────────────

@router.get("/to/{to_id}", response_model=list[GiaoVienResponse], summary="Giáo viên theo tổ")
def lay_theo_to(
    to_id: int,
    service: GiaoVienService = Depends(get_service),
):
    result = service.lay_ds_theo_to(to_id)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


# ── GET /giao-vien/{gv_id} ────────────────────────────────────

@router.get("/{gv_id}", response_model=GiaoVienResponse, summary="Chi tiết giáo viên")
def lay_chi_tiet(
    gv_id: int,
    service: GiaoVienService = Depends(get_service),
):
    result = service.lay_chi_tiet(gv_id)
    if not result.ok:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


# ── POST /giao-vien/ ──────────────────────────────────────────

@router.post("/", response_model=GiaoVienResponse, status_code=201, summary="Thêm giáo viên")
def them_giao_vien(
    body: GiaoVienCreate,
    service: GiaoVienService = Depends(get_service),
):
    result = service.them(
        ho_ten=body.ho_ten,
        email=body.email,
        mat_khau=body.mat_khau,
        ma_gv=body.ma_giao_vien,
        mon_day=body.mon_day or "",
        to_id=body.to_id,
        so_dien_thoai=body.so_dien_thoai or "",
        active=body.active,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


# ── PUT /giao-vien/{gv_id} ────────────────────────────────────

@router.put("/{gv_id}", response_model=GiaoVienResponse, summary="Cập nhật giáo viên")
def sua_giao_vien(
    gv_id: int,
    body: GiaoVienUpdate,
    service: GiaoVienService = Depends(get_service),
):
    result = service.sua(
        gv_id=gv_id,
        ma_gv=body.ma_giao_vien,
        ho_ten=body.ho_ten,
        email=body.email,
        mat_khau=body.mat_khau,
        mon_day=body.mon_day,
        to_id=body.to_id,
        so_dien_thoai=body.so_dien_thoai,
        active=body.active,
    )
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


# ── PATCH /giao-vien/{gv_id}/trang-thai ──────────────────────

@router.patch("/{gv_id}/trang-thai", response_model=GiaoVienResponse, summary="Bật/tắt trạng thái")
def doi_trang_thai(
    gv_id: int,
    service: GiaoVienService = Depends(get_service),
):
    result = service.doi_trang_thai(gv_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


# ── PATCH /giao-vien/{gv_id}/mat-khau ────────────────────────

@router.patch("/{gv_id}/mat-khau", summary="Đặt lại mật khẩu")
def dat_lai_mat_khau(
    gv_id: int,
    body: DatLaiMatKhauRequest,
    service: GiaoVienService = Depends(get_service),
):
    result = service.dat_lai_mat_khau(gv_id, mat_khau_moi=body.mat_khau_moi)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


# ── DELETE /giao-vien/{gv_id} ─────────────────────────────────

@router.delete("/{gv_id}", summary="Xóa giáo viên")
def xoa_giao_vien(
    gv_id: int,
    service: GiaoVienService = Depends(get_service),
):
    result = service.xoa(gv_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


# ── POST /giao-vien/import-excel ─────────────────────────────

@router.post("/import-excel", response_model=dict, summary="Import giáo viên từ Excel")
async def import_excel(
    file: UploadFile = File(...),
    service: GiaoVienService = Depends(get_service),
):
    """
    Import danh sách giáo viên từ file Excel.
    
    Các cột hỗ trợ:
    - Mã giáo viên (bắt buộc)
    - Họ tên (bắt buộc)
    - Email (bắt buộc)
    - Mật khẩu (mặc định: eduschool@123)
    - Môn dạy
    - Số điện thoại
    - Tổ ID hoặc Tổ chuyên môn (tên)
    - Trạng thái (true/false hoặc active/inactive)
    """
    # Kiểm tra định dạng file
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ file Excel (.xlsx, .xls)"
        )
    
    # Đọc file
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File rỗng")
        
        result = service.import_from_excel(content, file.filename)
        
        if not result.ok:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")