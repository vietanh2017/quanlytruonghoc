# D:\QUANLYTRUONGHOC\shared\enums.py
"""
Các enum dùng chung toàn hệ thống EduSchool.
"""

from enum import Enum

class Role(str, Enum):
    ADMIN          = "ADMIN"
    TO_TRUONG      = "TO_TRUONG"
    PHO_TO_TRUONG  = "PHO_TO_TRUONG"  # Sửa thành chữ hoa cho đồng bộ
    TONG_PHU_TRACH = "TONG_PHU_TRACH"
    GIAO_VIEN      = "GIAO_VIEN"
    NHAN_VIEN      = "NHAN_VIEN" 