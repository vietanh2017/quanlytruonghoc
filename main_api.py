# main_api.py
"""
Điểm khởi động EduSchool Suite - Phiên bản Web (FastAPI).
Thay thế main.py (PySide6 desktop).

Cài đặt:
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic[email]

Chạy development:
    uvicorn main_api:app --reload --port 8000

Sau khi chạy, mở trình duyệt:
    http://localhost:8000/docs   ← Swagger UI để test API
    http://localhost:8000/redoc  ← Tài liệu API dạng đẹp hơn
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.utils.logger import logger
from core.db.session import init_db

# ── Import routers ────────────────────────────────────────────
# Thêm dần các module khác vào đây khi chuyển đổi xong
from modules.dashboard.router import router as dashboard_router
from modules.giao_vien.router import router as giao_vien_router
from modules.lop_hoc.router import router as lop_hoc_router
from modules.thi_dua_giao_vien.router import router as thi_dua_gv_router
from modules.thi_dua_hoc_sinh.router import router as thi_dua_hs_router
from modules.thi_dua_hoc_sinh.models.thi_dua_cau_hinh import ThiDuaCauHinh
from modules.phan_cong.router import router as phan_cong_router
from modules.tkb.models import TKBCauHinhNgay, TKBCauHinhTiet, TKBCauHinhMon, ThoiKhoaBieu
from modules.tkb.models import TKBRangBuocGV
from modules.tkb.router import router as tkb_router
from modules.reports.router import router as reports_router 
from modules.cau_hinh.router import router as cau_hinh_router
from core.auth.router import router as auth_router

# ── Tạo thư mục cần thiết ─────────────────────────────────────
REQUIRED_DIRS = ["logs", "backups", "uploads", "temp", "data/exports", "data/imports"]
for dir_name in REQUIRED_DIRS:
    os.makedirs(dir_name, exist_ok=True)


# ── Lifespan (khởi động / tắt app) ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động
    logger.info("=" * 50)
    logger.info("🚀 EduSchool Suite API khởi động")
    logger.info(f"📅 Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 50)

    init_db()  # Tạo bảng nếu chưa có
    logger.info("✅ Kết nối database thành công")

    yield  # App đang chạy

    # Tắt app
    logger.info("🛑 EduSchool Suite API đóng")
    logger.info("=" * 50)


# ── Khởi tạo FastAPI ──────────────────────────────────────────
app = FastAPI(
    title="EduSchool Suite API",
    description="HỆ THỐNG QUẢN LÝ TRƯỜNG HỌC - LƯU HÀNH NỘI BỘ",
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS (cho phép frontend React kết nối) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
        "https://quanlytruonghoc-amber.vercel.app/login"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# ── Đăng ký routers ───────────────────────────────────────────
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(giao_vien_router, prefix="/api/v1")
app.include_router(lop_hoc_router,      prefix="/api/v1")
app.include_router(thi_dua_gv_router, prefix="/api/v1")
app.include_router(thi_dua_hs_router, prefix="/api/v1")
app.include_router(phan_cong_router,    prefix="/api/v1")
app.include_router(tkb_router, prefix="/api/v1")
app.include_router(reports_router,      prefix="/api/v1")
app.include_router(cau_hinh_router,     prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────
@app.get("/", tags=["System"])
def root():
    return {
        "app": "EduSchool Suite API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}
