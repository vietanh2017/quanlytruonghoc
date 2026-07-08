# core/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.db.session import get_db
from core.auth.password import verify_password
from core.db.models.nguoi_dung import NguoiDung
from core.db.models.phan_quyen import VaiTroQuyen, Quyen
from pydantic import BaseModel
import jwt
import datetime
import os
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Xác thực"])

# ⭐ CẤU HÌNH JWT
# SECRET_KEY BẮT BUỘC lấy từ biến môi trường khi chạy production.
# Local dev không set env var thì dùng key mặc định (chỉ chạy máy mình nên không nguy hiểm).
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    import warnings
    warnings.warn(
        "⚠️  JWT_SECRET_KEY chưa được set trong biến môi trường! "
        "Đang dùng key mặc định KHÔNG AN TOÀN cho production. "
        "Set biến môi trường JWT_SECRET_KEY trước khi deploy thật."
    )
    SECRET_KEY = "dev-only-insecure-key-DO-NOT-USE-IN-PRODUCTION"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8


class LoginRequest(BaseModel):
    email: str
    mat_khau: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    ho_ten: str
    email: str
    role: str


class UserInfo(BaseModel):
    email: str
    role: str
    ho_ten: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not verify_password(request.mat_khau, user.mat_khau_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    if not user.active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa")

    payload = {
        "sub": user.email,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(
        access_token=access_token,
        ho_ten=user.ho_ten,
        email=user.email,
        role=user.role
    )


def get_current_user(token: str = Header(...)) -> UserInfo:
    """
    LƯU Ý: frontend phải gửi header tên chính xác là "token"
    (không phải "Authorization"), vì tên tham số này quyết định
    tên header mà FastAPI sẽ tìm.
    """
    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")

        if not email or not role:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")

        return UserInfo(email=email, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


def get_current_user_optional(token: Optional[str] = Header(None)) -> Optional[UserInfo]:
    if not token:
        return None
    try:
        return get_current_user(token)
    except HTTPException:
        return None


def require_permission(ma_quyen: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if hasattr(arg, "headers"):
                        request = arg
                        break

            if not request:
                raise HTTPException(status_code=401, detail="Không tìm thấy request")

            token = request.headers.get("Authorization")
            if not token:
                raise HTTPException(status_code=401, detail="Chưa đăng nhập")

            user = get_current_user(token)

            if user.role == "ADMIN":
                return func(*args, **kwargs)

            db = next(get_db())
            has_permission = db.query(VaiTroQuyen).join(Quyen).filter(
                VaiTroQuyen.vai_tro == user.role,
                Quyen.ma_quyen == ma_quyen,
                Quyen.active == True
            ).first()

            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Không có quyền '{ma_quyen}'"
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


@router.get("/me")
def get_me(current_user: UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    return {
        "email": user.email,
        "ho_ten": user.ho_ten,
        "role": user.role,
        "active": user.active
    }


@router.get("/my-permissions")
def get_my_permissions(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "ADMIN":
        quyens = db.query(Quyen).filter(Quyen.active == True).all()
        return [q.ma_quyen for q in quyens]

    permissions = db.query(Quyen.ma_quyen).join(VaiTroQuyen).filter(
        VaiTroQuyen.vai_tro == current_user.role,
        Quyen.active == True
    ).all()

    return [p[0] for p in permissions]