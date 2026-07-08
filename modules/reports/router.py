# modules/reports/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.db.session import get_db
from modules.reports.service import ReportService
from modules.reports.schemas import ReportFilter, ReportResponse


router = APIRouter(prefix="/reports", tags=["Báo Cáo"])


def get_svc(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(session=db)


# ════════════════════════════════════════════════════════════
# ══ LẤY BÁO CÁO ═══════════════════════════════════════════
# ════════════════════════════════════════════════════════════

@router.get("/report", response_model=ReportResponse)
def get_report(
    loai: str = Query(..., description="Loại báo cáo: tuan, thang, hoc_ky, nam_hoc, ca_nhan, giao_vien"),
    nam_hoc_id: Optional[int] = Query(None, description="ID năm học"),
    hoc_ky_id: Optional[int] = Query(None, description="ID học kỳ"),
    thang_id: Optional[int] = Query(None, description="ID tháng"),
    tuan: Optional[int] = Query(None, description="Số tuần (1-52)"),
    lop_hoc_id: Optional[int] = Query(None, description="ID lớp học"),
    khoi: Optional[int] = Query(None, description="Khối lớp (6-12)"),
    svc: ReportService = Depends(get_svc)
):
    """Lấy báo cáo theo loại và bộ lọc"""
    filter_data = ReportFilter(
        loai=loai,
        nam_hoc_id=nam_hoc_id,
        hoc_ky_id=hoc_ky_id,
        thang_id=thang_id,
        tuan=tuan,
        lop_hoc_id=lop_hoc_id,
        khoi=khoi,
    )
    
    result = svc.get_report(filter_data)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.error)
    
    return result.data


# ════════════════════════════════════════════════════════════
# ══ XUẤT EXCEL ════════════════════════════════════════════
# ════════════════════════════════════════════════════════════

@router.post("/export-excel")
def export_report_excel(
    filter_data: ReportFilter,
    svc: ReportService = Depends(get_svc)
):
    """Xuất báo cáo ra file Excel"""
    # TODO: Implement export Excel
    return {"message": "Tính năng đang phát triển"}



@router.get("/debug-diem/{nam_hoc_id}/{tuan}/{lop_id}")
def debug_diem(nam_hoc_id: int, tuan: int, lop_id: int, db: Session = Depends(get_db)):
    from modules.thi_dua_hoc_sinh.models.diem_doi_ngay import DiemDoiNgay
    from modules.thi_dua_hoc_sinh.service import ThiDuaHocSinhService
    
    svc = ThiDuaHocSinhService(db)
    
    rows = db.query(DiemDoiNgay).filter(
        DiemDoiNgay.nam_hoc_id == nam_hoc_id,
        DiemDoiNgay.tuan == tuan,
        DiemDoiNgay.lop_hoc_id == lop_id
    ).all()
    raw = [{"thu": r.thu, "diem_thay_doi": r.diem_thay_doi,
            "so_luong_vp": r.so_luong_vi_pham} for r in rows]
    
    so_vp = svc.count_active_violations()
    so_ngay = svc._get_so_ngay_trong_tuan()  # ✅ Thêm dòng này
    diem_doi = svc.doi_ngay_repo.get_trung_binh_tuan(
        nam_hoc_id, tuan, lop_id, so_vp, so_ngay  # ✅ Truyền so_ngay
    )
    
    result = svc.lay_diem_tuan(nam_hoc_id, tuan)
    lop_data = next((i for i in result.data if i['lop_hoc_id'] == lop_id), None)
    
    return {
        "raw_diem_doi_ngay": raw,
        "so_luong_vp_hien_tai": so_vp,
        "so_ngay_hien_tai": so_ngay,  # ✅ Thêm để debug
        "diem_doi_tinh_ra": diem_doi,
        "lay_diem_tuan_result": lop_data,
    }