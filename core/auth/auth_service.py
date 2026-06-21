# D:\QUANLYTRUONGHOC\core\auth\auth_service.py
"""
AuthService: xử lý đăng nhập và đổi mật khẩu.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from core.db.models import NguoiDung, GiaoVien
from core.auth.password import verify_password
from shared.enums import Role
from core.db.session import SessionLocal

@dataclass
class LoginResult:
    success: bool
    user:    Optional[NguoiDung] = None
    to_id:   Optional[int] = None
    error:   str = ""


class AuthService:
    def __init__(self, session: Session = None):
        if session is None:
            self.session = SessionLocal()
            self._own_session = True
        else:
            self.session = session
            self._own_session = False
    def close(self):
        if self._own_session and self.session:
            self.session.close()

    def login(self, email: str, mat_khau: str) -> LoginResult:
        user = (self.session.query(NguoiDung)
                .filter_by(email=email.strip().lower(), active=True)
                .first())
        if not user:
            return LoginResult(success=False,
                               error="Email không tồn tại hoặc đã bị vô hiệu.")
        if not verify_password(mat_khau, user.mat_khau_hash):
            return LoginResult(success=False, error="Mật khẩu không đúng.")

        # Lấy to_id nếu là Tổ trưởng
        to_id = None
        if user.role == Role.TO_TRUONG:
            gv = (self.session.query(GiaoVien)
                  .filter_by(nguoi_dung_id=user.id)
                  .first())
            if gv:
                to_id = gv.to_id

        return LoginResult(success=True, user=user, to_id=to_id)

    def doi_mat_khau(self, user_id: int,
                     cu: str, moi: str) -> tuple[bool, str]:
        from core.auth.password import hash_password
        user = self.session.get(NguoiDung, user_id)
        if not user:
            return False, "Không tìm thấy tài khoản."
        if not verify_password(cu, user.mat_khau_hash):
            return False, "Mật khẩu cũ không đúng."
        user.mat_khau_hash = hash_password(moi)
        self.session.commit()
        return True, "Đổi mật khẩu thành công."
