from core.db.session import SessionLocal, engine
from core.db.base import Base

# Xóa bảng cũ và tạo lại (CHỈ DÙNG KHI PHÁT TRIỂN)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Đã reset database!")