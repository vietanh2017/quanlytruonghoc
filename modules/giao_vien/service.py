# modules/giao_vien/service.py
"""
GiaoVienService: logic nghiệp vụ module Giáo viên.

Thay đổi so với bản desktop:
- Nhận session từ bên ngoài (dependency injection) thay vì tự tạo
- Bỏ hàm them_giao_vien() trùng lặp với them(), gộp thành 1
- Bỏ close() vì session do FastAPI quản lý vòng đời
"""

from typing import Optional
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
import re

from core.auth.password import hash_password
from modules.giao_vien.repository import GiaoVienRepository
from shared.dto.result import ServiceResult
from shared.enums import Role
# KHÔNG cần import NguoiDung vì đã có trong repository
# KHÔNG cần import GiaoVien vì đã có trong repository


class GiaoVienService:
    def __init__(self, session: Session):
        """
        Nhận session từ FastAPI Depends(get_db).
        Không tự tạo session như bản desktop.
        """
        self.session = session
        self.repo = GiaoVienRepository(session)

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()

    # ── Danh sách ─────────────────────────────────────────────

    def lay_ds(self, include_inactive: bool = False) -> ServiceResult:
        try:
            data = self.repo.get_all(include_inactive=include_inactive)
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_to(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.repo.get_all_to())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_theo_to(self, to_id: int) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.repo.get_by_to(to_id))
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_chi_tiet(self, gv_id: int) -> ServiceResult:
        try:
            gv = self.repo.get_by_id(gv_id)
            if not gv:
                return ServiceResult(ok=False, error="Không tìm thấy giáo viên.")
            return ServiceResult(ok=True, data=gv)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    # ── Thêm ──────────────────────────────────────────────────

    def them(
        self,
        ho_ten: str,
        email: str,
        mat_khau: str,
        ma_gv: str,
        mon_day: str = "",
        to_id: Optional[int] = None,
        so_dien_thoai: str = "",
        role: Role = Role.GIAO_VIEN,
        active: bool = True,
    ) -> ServiceResult:
        # Validation
        if not str(ho_ten or '').strip():
            return ServiceResult(ok=False, error="Họ tên không được để trống.")
        if not str(email or '').strip() or "@" not in str(email):
            return ServiceResult(ok=False, error="Email không hợp lệ.")
        if not str(ma_gv or '').strip():
            return ServiceResult(ok=False, error="Mã GV không được để trống.")

        # ⭐ Kiểm tra email đã tồn tại
        if self.repo.get_nguoi_dung_by_email(email.strip().lower()):
            return ServiceResult(ok=False, error="Email đã tồn tại trong hệ thống.")

        # ⭐ Kiểm tra mã GV đã tồn tại và đang hoạt động (active = True)
        existing_gv = self.repo.get_by_ma(ma_gv.strip().upper())
        if existing_gv and existing_gv.active:
            return ServiceResult(ok=False, error=f"Mã giáo viên '{ma_gv}' đã tồn tại và đang hoạt động.")

        try:
            nd = self.repo.create_nguoi_dung(
                ho_ten=ho_ten.strip(),
                email=email.strip().lower(),
                mat_khau_hash=hash_password(mat_khau or "eduschool@123"),
                role=role,
                active=active,
            )
            gv = self.repo.create(
                nguoi_dung_id=nd.id,
                ma_gv=ma_gv.strip().upper(),
                mon_day=str(mon_day or '').strip(),
                to_id=to_id,
                so_dien_thoai=str(so_dien_thoai or '').strip(),
                active=active,
            )
            self._commit()
            return ServiceResult(ok=True, data=gv, error="Thêm giáo viên thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=f"Lỗi: {e}")

    # ── Sửa ───────────────────────────────────────────────────

    def sua(
        self,
        gv_id: int,
        ma_gv: Optional[str] = None,
        ho_ten: Optional[str] = None,
        email: Optional[str] = None,
        mat_khau: Optional[str] = None,
        mon_day: Optional[str] = None,
        to_id: Optional[int] = None,
        so_dien_thoai: Optional[str] = None,
        active: Optional[bool] = None,
        role: Optional[Role] = None,
    ) -> ServiceResult:
        try:
            gv = self.repo.get_by_id(gv_id)
            if not gv:
                return ServiceResult(ok=False, error="Không tìm thấy giáo viên.")

            # Kiểm tra mã trùng
            if ma_gv:
                exist = self.repo.get_by_ma(ma_gv.strip().upper())
                if exist and exist.id != gv_id:
                    return ServiceResult(ok=False, error="Mã giáo viên đã tồn tại.")
                gv.ma_giao_vien = ma_gv.strip().upper()

            if mon_day is not None:
                gv.mon_day = mon_day.strip()
            if to_id is not None:
                gv.to_id = to_id
            if so_dien_thoai is not None:
                gv.so_dien_thoai = str(so_dien_thoai).strip()
            if active is not None:
                gv.active = active

            if gv.nguoi_dung:
                if ho_ten:
                    gv.nguoi_dung.ho_ten = ho_ten.strip()
                if email:
                    gv.nguoi_dung.email = email.strip().lower()
                if role is not None:
                    gv.nguoi_dung.role = role
                if mat_khau and mat_khau.strip():
                    gv.nguoi_dung.mat_khau_hash = hash_password(mat_khau)

            self._commit()
            return ServiceResult(ok=True, data=gv, error="Cập nhật giáo viên thành công.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ── Xóa ───────────────────────────────────────────────────

    def xoa(self, gv_id: int) -> ServiceResult:
        try:
            gv = self.repo.get_by_id(gv_id)
            if not gv:
                return ServiceResult(ok=False, error="Không tìm thấy giáo viên.")
            if gv.nguoi_dung.role == Role.ADMIN:
                return ServiceResult(ok=False, error="Không thể xóa tài khoản Admin.")

            ten = gv.nguoi_dung.ho_ten
            if self.repo.delete(gv_id):
                self._commit()
                return ServiceResult(ok=True, error=f"Đã xóa giáo viên {ten}.")
            return ServiceResult(ok=False, error="Xóa thất bại.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=f"Lỗi: {e}")

    # ── Đổi trạng thái ────────────────────────────────────────

    def doi_trang_thai(self, gv_id: int) -> ServiceResult:
        try:
            gv = self.repo.toggle_active(gv_id)
            if not gv:
                return ServiceResult(ok=False, error="Không tìm thấy giáo viên.")
            self.repo.toggle_active_nguoi_dung(gv.nguoi_dung_id)
            self._commit()
            tt = "kích hoạt" if gv.active else "vô hiệu hóa"
            return ServiceResult(ok=True, data=gv, error=f"Đã {tt} giáo viên.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ── Đặt lại mật khẩu ─────────────────────────────────────

    def dat_lai_mat_khau(
        self, gv_id: int, mat_khau_moi: str = "eduschool@123"
    ) -> ServiceResult:
        try:
            gv = self.repo.get_by_id(gv_id)
            if not gv:
                return ServiceResult(ok=False, error="Không tìm thấy giáo viên.")
            self.repo.update_nguoi_dung(
                gv.nguoi_dung_id,
                mat_khau_hash=hash_password(mat_khau_moi),
            )
            self._commit()
            return ServiceResult(ok=True, error=f"Đã đặt lại mật khẩu: {mat_khau_moi}")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
        
    # ── Import từ Excel ────────────────────────────────────────

    def import_from_excel(self, file_content: bytes, filename: str = None) -> ServiceResult:
        """
        Import danh sách giáo viên từ file Excel.
        Hỗ trợ .xlsx, .xls
        """
        try:
            # Đọc file Excel
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            
            # Chuẩn hóa tên cột (bỏ khoảng trắng, viết thường)
            df.columns = df.columns.str.strip().str.lower()
            
            # Map cột tiếng Việt sang field trong database
            column_mapping = {
                'mã giáo viên': 'ma_giao_vien',
                'mã gv': 'ma_giao_vien',
                'họ tên': 'ho_ten',
                'họ và tên': 'ho_ten',
                'tên': 'ho_ten',
                'email': 'email',
                'mật khẩu': 'mat_khau',
                'môn dạy': 'mon_day',
                'môn': 'mon_day',
                'số điện thoại': 'so_dien_thoai',
                'sđt': 'so_dien_thoai',
                'tổ id': 'to_id',
                'mã tổ': 'to_id',
                'tổ chuyên môn': 'to_ten',
                'trạng thái': 'active',
                'active': 'active'
            }
            
            # Đổi tên cột
            df.rename(columns=column_mapping, inplace=True)
            
            # Kiểm tra các cột bắt buộc
            required_cols = ['ho_ten', 'email', 'ma_giao_vien']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return ServiceResult(
                    ok=False, 
                    error=f"Thiếu cột bắt buộc: {', '.join(missing_cols)}. "
                          f"Các cột hiện có: {list(df.columns)}"
                )
            
            # Xử lý từng dòng
            ket_qua = {
                'tong_so': 0,
                'thanh_cong': 0,
                'that_bai': 0,
                'chi_tiet': [],
                'da_them': []
            }
            
            for idx, row in df.iterrows():
                ket_qua['tong_so'] += 1
                row_num = idx + 2  # Excel row number (1-based + header)
                errors = []
                
                # Lấy dữ liệu
                ho_ten = self._get_value(row, 'ho_ten', '')
                email = self._get_value(row, 'email', '')
                ma_giao_vien = self._get_value(row, 'ma_giao_vien', '')
                mat_khau = self._get_value(row, 'mat_khau', 'eduschool@123')
                mon_day = self._get_value(row, 'mon_day', '')
                so_dien_thoai = self._get_value(row, 'so_dien_thoai', '')
                to_id = self._get_value(row, 'to_id', None)
                to_ten = self._get_value(row, 'to_ten', '')
                active = self._get_value(row, 'active', True)
                
                # ── Validate ──
                # 1. Họ tên
                if not ho_ten or not ho_ten.strip():
                    errors.append("Họ tên không được để trống")
                else:
                    ho_ten = ho_ten.strip()
                
                # 2. Email
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not email or not re.match(email_pattern, email):
                    errors.append("Email không hợp lệ")
                else:
                    # Kiểm tra email đã tồn tại chưa
                    existing = self.repo.get_nguoi_dung_by_email(email)
                    if existing:
                        errors.append(f"Email '{email}' đã được sử dụng")
                
                # 3. Mã giáo viên
                if not ma_giao_vien or not ma_giao_vien.strip():
                    errors.append("Mã giáo viên không được để trống")
                else:
                    ma_giao_vien = ma_giao_vien.strip().upper()
                    existing = self.repo.get_by_ma(ma_giao_vien)
                    if existing:
                        errors.append(f"Mã giáo viên '{ma_giao_vien}' đã tồn tại")
                
                # 4. Tổ chuyên môn (nếu có)
                if to_ten:
                    # Tìm tổ theo tên - dùng repository
                    to = self.repo.get_to_by_ten(to_ten)
                    if to:
                        to_id = to.id
                    else:
                        errors.append(f"Tổ chuyên môn '{to_ten}' không tồn tại")
                elif to_id and isinstance(to_id, (int, float)):
                    to_id = int(to_id)
                    to = self.repo.get_to_by_id(to_id)
                    if not to:
                        errors.append(f"Tổ ID '{to_id}' không tồn tại")
                
                # 5. Active
                if isinstance(active, str):
                    active = active.lower() in ['true', '1', 'active', 'hoạt động', 'yes', 'y']
                elif isinstance(active, (int, float)):
                    active = bool(active)
                
                # ── Lưu ──
                if errors:
                    ket_qua['that_bai'] += 1
                    ket_qua['chi_tiet'].append({
                        'row': row_num,
                        'data': row.to_dict(),
                        'errors': errors
                    })
                else:
                    try:
                        # Sử dụng service để thêm (tận dụng validation)
                        result = self.them(
                            ho_ten=ho_ten,
                            email=email,
                            mat_khau=mat_khau,
                            ma_gv=ma_giao_vien,
                            mon_day=mon_day,
                            to_id=to_id,
                            so_dien_thoai=so_dien_thoai,
                            active=active
                        )
                        
                        if result.ok:
                            ket_qua['thanh_cong'] += 1
                            ket_qua['da_them'].append({
                                'ma_giao_vien': ma_giao_vien,
                                'ho_ten': ho_ten,
                                'email': email
                            })
                        else:
                            ket_qua['that_bai'] += 1
                            ket_qua['chi_tiet'].append({
                                'row': row_num,
                                'data': row.to_dict(),
                                'errors': [result.error]
                            })
                            
                    except Exception as e:
                        self._rollback()
                        ket_qua['that_bai'] += 1
                        ket_qua['chi_tiet'].append({
                            'row': row_num,
                            'data': row.to_dict(),
                            'errors': [f"Lỗi hệ thống: {str(e)}"]
                        })
            
            return ServiceResult(ok=True, data=ket_qua, error="Import hoàn tất")
                
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=f"Lỗi đọc file Excel: {str(e)}")
        
    # Thay toàn bộ hàm cũ
    def _get_value(self, row, key, default=None):
        import pandas as pd
        value = row.get(key, default)
        if value is None:
            return default
        try:
            if pd.isna(value):
                return default
        except (TypeError, ValueError):
            pass
        return value