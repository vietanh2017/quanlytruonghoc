# core/db/connection.py
# Shim tương thích ngược — giữ file này để code cũ không bị lỗi import.
# Tất cả logic đã chuyển sang core/db/session.py
# KHÔNG xóa file này cho đến khi toàn bộ code cũ đã migrate xong.

from core.db.session import SessionLocal, get_session, init_db  # noqa: F401
