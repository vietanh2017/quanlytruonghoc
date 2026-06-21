# D:\QUANLYTRUONGHOC\core\db\models\__init__.py
"""
Export tất cả models để các nơi khác import dễ dàng:
    from core.db.models import NguoiDung, GiaoVien, ...
"""

from core.db.models.nam_hoc import NamHoc
from core.db.models.to_chuyen_mon import ToChuyenMon
from core.db.models.mon_hoc import MonHoc, PhanMon, MonHocKhoi  # ⭐ Import từ mon_hoc
from core.db.models.tiet_hoc import TietHoc
from core.db.models.nguoi_dung import NguoiDung
from core.db.models.giao_vien import GiaoVien
from core.db.models.lop_hoc import LopHoc
from core.db.models.hoc_sinh import HocSinh
from core.db.models.hoc_ky import HocKy

__all__ = ['QuyenModel', 'VaiTroQuyenModel']
__all__ = [
    "NguoiDung",
    "ToChuyenMon",
    "GiaoVien",
    "LopHoc",
    "NamHoc", "HocKy",
    "MonHoc", "PhanMon", "MonHocKhoi", "HocSinh",
]