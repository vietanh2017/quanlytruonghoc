# D:\QUANLYTRUONGHOC\core\db\base.py
"""
Base class cho tất cả ORM model trong EduSchool.
Tự động sinh __tablename__ (snake_case) và thêm created_at, updated_at.
"""

import re
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime, func


class Base(DeclarativeBase):

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Tự động: NguoiDung → nguoi_dung, ToCHuyenMon → to_chuyen_mon
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return name

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), nullable=False)
