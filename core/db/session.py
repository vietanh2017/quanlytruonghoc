# core/db/session.py
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ── Đọc DATABASE_URL từ biến môi trường ────────────────────────
# Local dev: không set gì cả -> tự dùng SQLite (mặc định cũ)
# Production (Render/Railway...): set DATABASE_URL trỏ tới PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./truonghoc.db")

# Render/Railway đôi khi cấp URL dạng "postgres://..." (cũ),
# nhưng SQLAlchemy 1.4+ yêu cầu "postgresql://..." -> tự sửa cho chắc
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args chỉ cần thiết riêng cho SQLite (single-thread check)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # tự kiểm tra connection còn sống trước khi dùng
                         # (quan trọng với Postgres free tier hay bị ngủ/ngắt kết nối)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Tạo tất cả bảng nếu chưa có."""
    from core.db.base import Base
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — cấp phát và giải phóng session tự động."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()