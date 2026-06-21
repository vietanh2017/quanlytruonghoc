# core/db/session.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Dùng SQLite để test nhanh, đổi sang PostgreSQL sau
DATABASE_URL = "sqlite:///./truonghoc.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Cần thiết cho SQLite
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