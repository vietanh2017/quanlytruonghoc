# modules/giao_vien_thi_dua/__init__.py
from .router import router
from .service import ThiDuaGVServiceWeb  # ⭐ Import từ service.py

__all__ = ['router', 'ThiDuaGVServiceWeb']