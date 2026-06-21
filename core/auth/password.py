# D:\QUANLYTRUONGHOC\core\auth\password.py
"""
Hàm hash và verify mật khẩu dùng bcrypt.
"""

import bcrypt


def hash_password(plain: str) -> str:
    """Hash mật khẩu plain text → bcrypt hash string."""
    return bcrypt.hashpw(plain.encode("utf-8"),
                         bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra plain text có khớp với hash không."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"),
                              hashed.encode("utf-8"))
    except Exception:
        return False
