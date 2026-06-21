# modules/cau_hinh/__init__.py
from .router import router
from .service import CauHinhService
from .repository import (
    NamHocRepository,
    HocKyRepository,
    ToChuyenMonRepository,
    MonHocRepository,
    TietHocRepository,
    NguoiDungRepository,
)

__all__ = [
    "router",
    "CauHinhService",
    "NamHocRepository",
    "HocKyRepository",
    "ToChuyenMonRepository",
    "MonHocRepository",
    "TietHocRepository",
    "NguoiDungRepository",
]