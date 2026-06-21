# modules/lop_hoc/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.lop_hoc.service import LopHocService
from modules.lop_hoc.schemas import (
    LopHocCreate, LopHocUpdate, LopHocResponse, LopHocListResponse,
    HocSinhCreate, HocSinhUpdate, HocSinhResponse,
)

router = APIRouter(prefix="/lop-hoc", tags=["Lớp Học"])


def get_service(db: Session = Depends(get_db)) -> LopHocService:
    return LopHocService(session=db)


# ════════════════════════════════════════════════════
#  LỚP HỌC
# ════════════════════════════════════════════════════

@router.get("/", response_model=LopHocListResponse, summary="Danh sách lớp học")
def lay_danh_sach(
    include_inactive: bool = Query(False),
    service: LopHocService = Depends(get_service),
):
    result = service.lay_ds(include_inactive=include_inactive)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.error)

    items = []
    for lop in result.data:
        ten_gvcn = None
        if lop.giao_vien_cn and lop.giao_vien_cn.nguoi_dung:
            ten_gvcn = lop.giao_vien_cn.nguoi_dung.ho_ten
        items.append(LopHocResponse(
            id=lop.id,
            ma_lop=lop.ma_lop,
            ten_lop=lop.ten_lop,
            khoi=lop.khoi,
            si_so=lop.si_so or 0,
            active=lop.active,
            giao_vien_cn_id=lop.giao_vien_cn_id,
            nam_hoc_id=lop.nam_hoc_id,
            ten_gvcn=ten_gvcn,
        ))
    return LopHocListResponse(total=len(items), items=items)


@router.get("/{lop_id}", response_model=LopHocResponse, summary="Chi tiết lớp học")
def lay_chi_tiet(lop_id: int, service: LopHocService = Depends(get_service)):
    result = service.lay_chi_tiet(lop_id)
    if not result.ok:
        raise HTTPException(status_code=404, detail=result.error)
    lop = result.data
    ten_gvcn = None
    if lop.giao_vien_cn and lop.giao_vien_cn.nguoi_dung:
        ten_gvcn = lop.giao_vien_cn.nguoi_dung.ho_ten
    return LopHocResponse(
        id=lop.id, ma_lop=lop.ma_lop, ten_lop=lop.ten_lop,
        khoi=lop.khoi, si_so=lop.si_so or 0, active=lop.active,
        giao_vien_cn_id=lop.giao_vien_cn_id,
        nam_hoc_id=lop.nam_hoc_id, ten_gvcn=ten_gvcn,
    )


@router.post("/", response_model=LopHocResponse, status_code=201, summary="Thêm lớp học")
def them_lop(body: LopHocCreate, service: LopHocService = Depends(get_service)):
    result = service.them(**body.model_dump())
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    lop = service.repo.get_by_ma(body.ma_lop.strip())
    ten_gvcn = None
    if lop.giao_vien_cn and lop.giao_vien_cn.nguoi_dung:
        ten_gvcn = lop.giao_vien_cn.nguoi_dung.ho_ten
    return LopHocResponse(
        id=lop.id, ma_lop=lop.ma_lop, ten_lop=lop.ten_lop,
        khoi=lop.khoi, si_so=lop.si_so or 0, active=lop.active,
        giao_vien_cn_id=lop.giao_vien_cn_id,
        nam_hoc_id=lop.nam_hoc_id, ten_gvcn=ten_gvcn,
    )


@router.put("/{lop_id}", response_model=LopHocResponse, summary="Cập nhật lớp học")
def sua_lop(lop_id: int, body: LopHocUpdate, service: LopHocService = Depends(get_service)):
    result = service.sua(lop_id, **body.model_dump(exclude_none=True))
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return lay_chi_tiet(lop_id, service)


@router.patch("/{lop_id}/trang-thai", summary="Bật/tắt trạng thái lớp")
def doi_trang_thai(lop_id: int, service: LopHocService = Depends(get_service)):
    result = service.doi_trang_thai(lop_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


@router.delete("/{lop_id}", summary="Xóa lớp học")
def xoa_lop(lop_id: int, service: LopHocService = Depends(get_service)):
    result = service.xoa(lop_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


# ════════════════════════════════════════════════════
#  HỌC SINH
# ════════════════════════════════════════════════════

@router.get("/{lop_id}/hoc-sinh", response_model=list[HocSinhResponse], summary="Danh sách học sinh")
def lay_ds_hoc_sinh(lop_id: int, service: LopHocService = Depends(get_service)):
    result = service.lay_ds_hoc_sinh(lop_id)
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@router.post("/{lop_id}/hoc-sinh", response_model=HocSinhResponse, status_code=201)
def them_hoc_sinh(lop_id: int, body: HocSinhCreate, service: LopHocService = Depends(get_service)):
    body.lop_hoc_id = lop_id
    data = body.model_dump()
    data['lop_hoc_id'] = lop_id
    result = service.them_hoc_sinh(**data)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/hoc-sinh/{hs_id}", response_model=HocSinhResponse, summary="Cập nhật học sinh")
def sua_hoc_sinh(hs_id: int, body: HocSinhUpdate, service: LopHocService = Depends(get_service)):
    result = service.sua_hoc_sinh(hs_id, **body.model_dump(exclude_none=True))
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.delete("/hoc-sinh/{hs_id}", summary="Xóa học sinh")
def xoa_hoc_sinh(hs_id: int, service: LopHocService = Depends(get_service)):
    result = service.xoa_hoc_sinh(hs_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


@router.patch("/hoc-sinh/{hs_id}/trang-thai", summary="Bật/tắt trạng thái học sinh")
def doi_trang_thai_hs(hs_id: int, service: LopHocService = Depends(get_service)):
    result = service.doi_trang_thai_hoc_sinh(hs_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": "Đã cập nhật trạng thái"}


@router.delete("/{lop_id}/hoc-sinh", summary="Xóa toàn bộ học sinh trong lớp")
def xoa_toan_bo_hs(lop_id: int, service: LopHocService = Depends(get_service)):
    result = service.xoa_toan_bo_hoc_sinh(lop_id)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    return {"message": result.error}


# ════════════════════════════════════════════════════
#  IMPORT EXCEL
# ════════════════════════════════════════════════════

@router.post("/import-hoc-sinh", summary="Import học sinh từ Excel")
async def import_hoc_sinh(
    file: UploadFile = File(...),
    lop_hoc_id: int = Form(...),
    service: LopHocService = Depends(get_service),
):
    """
    Import danh sách học sinh từ file Excel.
    
    File Excel cần có các cột:
    - Mã học sinh (bắt buộc)
    - Họ tên (bắt buộc)
    - Giới tính (Nam/Nữ hoặc True/False)
    - Ngày sinh (định dạng YYYY-MM-DD hoặc DD/MM/YYYY)
    - Số điện thoại
    """
    # Kiểm tra định dạng file
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ file Excel (.xlsx, .xls)"
        )
    
    # Kiểm tra lớp học tồn tại
    lop = service.repo.get_by_id(lop_hoc_id)
    if not lop:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File rỗng")
        
        result = service.import_hoc_sinh_from_excel(content, lop_hoc_id)
        
        if not result.ok:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")