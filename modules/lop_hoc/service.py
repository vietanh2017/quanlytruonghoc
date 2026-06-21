# modules/lop_hoc/service.py
"""
LopHocService: logic nghiệp vụ module Lớp học.
"""
import pandas as pd
from io import BytesIO
import re
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from modules.lop_hoc.repository import LopHocRepository
from modules.giao_vien.repository import GiaoVienRepository
from modules.lop_hoc.hoc_sinh_repository import HocSinhRepository
from shared.dto.result import ServiceResult

MODE_MERGE   = "merge"
MODE_REPLACE = "replace"


class LopHocService:
    def __init__(self, session: Session):
        self.session  = session
        self.repo     = LopHocRepository(session)
        self.gv_repo  = GiaoVienRepository(session)
        self.hs_repo  = HocSinhRepository(session)

    def _commit(self):
        self.session.commit()

    def _rollback(self):
        self.session.rollback()

    # ── Lớp học ───────────────────────────────────────────────

    def lay_ds(self, include_inactive: bool = False) -> ServiceResult:
        try:
            data = self.repo.get_all()
            if not include_inactive:
                data = [l for l in data if l.active]
            return ServiceResult(ok=True, data=data)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_chi_tiet(self, lop_id: int) -> ServiceResult:
        try:
            lop = self.repo.get_by_id(lop_id)
            if not lop:
                return ServiceResult(ok=False, error="Không tìm thấy lớp.")
            return ServiceResult(ok=True, data=lop)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_giao_vien(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.gv_repo.get_all())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def lay_ds_nam_hoc(self) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.repo.get_all_nam_hoc())
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them(self, ma_lop: str, ten_lop: str, khoi: int,
             si_so: int = 0, giao_vien_cn_id: Optional[int] = None,
             nam_hoc_id: Optional[int] = None, active: bool = True) -> ServiceResult:
        try:
            if not ma_lop.strip():
                return ServiceResult(ok=False, error="Mã lớp không được để trống.")
            if not ten_lop.strip():
                return ServiceResult(ok=False, error="Tên lớp không được để trống.")
            if self.repo.get_by_ma(ma_lop.strip()):
                return ServiceResult(ok=False, error="Mã lớp đã tồn tại.")

            self.repo.create(
                ma_lop=ma_lop.strip(),
                ten_lop=ten_lop.strip(),
                khoi=khoi,
                si_so=si_so,
                giao_vien_cn_id=giao_vien_cn_id,
                nam_hoc_id=nam_hoc_id,
                active=active,
            )
            self._commit()
            return ServiceResult(ok=True, error="Đã thêm lớp học.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua(self, lop_id: int, ma_lop: Optional[str] = None,
            ten_lop: Optional[str] = None, khoi: Optional[int] = None,
            si_so: Optional[int] = None, giao_vien_cn_id: Optional[int] = None,
            nam_hoc_id: Optional[int] = None, active: Optional[bool] = None) -> ServiceResult:
        try:
            if ma_lop:
                other = self.repo.get_by_ma(ma_lop.strip())
                if other and other.id != lop_id:
                    return ServiceResult(ok=False, error="Mã lớp đã tồn tại.")

            data = {}
            if ma_lop      is not None: data["ma_lop"]          = ma_lop.strip()
            if ten_lop     is not None: data["ten_lop"]         = ten_lop.strip()
            if khoi        is not None: data["khoi"]            = khoi
            if si_so       is not None: data["si_so"]           = si_so
            if giao_vien_cn_id is not None: data["giao_vien_cn_id"] = giao_vien_cn_id
            if nam_hoc_id  is not None: data["nam_hoc_id"]      = nam_hoc_id
            if active      is not None: data["active"]          = active

            self.repo.update(lop_id, **data)
            self._commit()
            return ServiceResult(ok=True, error="Đã cập nhật lớp.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa(self, lop_id: int) -> ServiceResult:
        try:
            if not self.repo.delete(lop_id):
                return ServiceResult(ok=False, error="Không tìm thấy lớp.")
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa lớp.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def doi_trang_thai(self, lop_id: int) -> ServiceResult:
        try:
            obj = self.repo.get_by_id(lop_id)
            if not obj:
                return ServiceResult(ok=False, error="Không tìm thấy lớp.")
            obj.active = not obj.active
            self._commit()
            tt = "kích hoạt" if obj.active else "vô hiệu hóa"
            return ServiceResult(ok=True, data=obj, error=f"Đã {tt} lớp.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    # ── Học sinh ──────────────────────────────────────────────

    def lay_ds_hoc_sinh(self, lop_id: int) -> ServiceResult:
        try:
            return ServiceResult(ok=True, data=self.hs_repo.get_by_lop(lop_id))
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))

    def them_hoc_sinh(self, ma_hoc_sinh, ho_ten, ngay_sinh=None,
                    gioi_tinh=True, so_dien_thoai=None, lop_hoc_id=None):
        try:
            if self.hs_repo.get_by_ma(ma_hoc_sinh):
                return ServiceResult(ok=False, error="Mã học sinh đã tồn tại.")
            hs = self.hs_repo.create(
                ma_hoc_sinh=ma_hoc_sinh.strip(),
                ho_ten=ho_ten.strip(),
                ngay_sinh=ngay_sinh,
                gioi_tinh=gioi_tinh,
                so_dien_thoai=so_dien_thoai,
                lop_hoc_id=lop_hoc_id,
                active=True,
            )
            self._commit()
            return ServiceResult(ok=True, data=hs, error="Đã thêm học sinh.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def sua_hoc_sinh(self, hs_id: int, **data) -> ServiceResult:
        try:
            if "ma_hoc_sinh" in data:
                other = self.hs_repo.get_by_ma(data["ma_hoc_sinh"])
                if other and other.id != hs_id:
                    return ServiceResult(ok=False, error="Mã học sinh đã tồn tại.")
            
            # Cập nhật
            self.hs_repo.update(hs_id, **data)
            self._commit()
            
            # ⭐ Lấy lại dữ liệu sau khi update để trả về
            updated_hs = self.hs_repo.get_by_id(hs_id)
            if not updated_hs:
                return ServiceResult(ok=False, error="Không tìm thấy học sinh sau khi cập nhật.")
            
            return ServiceResult(ok=True, data=updated_hs, error="Đã cập nhật học sinh.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_hoc_sinh(self, hs_id: int) -> ServiceResult:
        try:
            if not self.hs_repo.delete(hs_id):
                return ServiceResult(ok=False, error="Không tìm thấy học sinh.")
            self._commit()
            return ServiceResult(ok=True, error="Đã xóa học sinh.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def doi_trang_thai_hoc_sinh(self, hs_id: int) -> ServiceResult:
        try:
            obj = self.hs_repo.get_by_id(hs_id)
            if not obj:
                return ServiceResult(ok=False, error="Không tìm thấy học sinh.")
            obj.active = not obj.active
            self._commit()
            return ServiceResult(ok=True, data=obj)
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))

    def xoa_toan_bo_hoc_sinh(self, lop_id: int) -> ServiceResult:
        try:
            count = self.hs_repo.count_by_lop(lop_id)
            if count == 0:
                return ServiceResult(ok=True, error="Không có học sinh nào để xóa.")
            deleted = self.hs_repo.delete_by_lop(lop_id)
            self._commit()
            return ServiceResult(ok=True, error=f"Đã xóa {deleted} học sinh.")
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=str(e))
    # modules/lop_hoc/service.py (thêm vào cuối file)

    # ── Import Excel ──────────────────────────────────────────────

    def import_hoc_sinh_from_excel(self, file_content: bytes, lop_hoc_id: int) -> ServiceResult:
        """
        Import danh sách học sinh từ file Excel.
        """
        try:
            # Đọc file Excel
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            
            # Chuẩn hóa tên cột
            df.columns = df.columns.str.strip().str.lower()
            
            # Map cột tiếng Việt sang field
            column_mapping = {
                'mã học sinh': 'ma_hoc_sinh',
                'mã hs': 'ma_hoc_sinh',
                'họ tên': 'ho_ten',
                'họ và tên': 'ho_ten',
                'tên': 'ho_ten',
                'giới tính': 'gioi_tinh',
                'ngày sinh': 'ngay_sinh',
                'số điện thoại': 'so_dien_thoai',
                'sđt': 'so_dien_thoai',
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Kiểm tra cột bắt buộc
            required_cols = ['ma_hoc_sinh', 'ho_ten']
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
                row_num = idx + 2
                errors = []
                
                # Lấy dữ liệu
                ma_hoc_sinh = self._get_value(row, 'ma_hoc_sinh', '')
                ho_ten = self._get_value(row, 'ho_ten', '')
                gioi_tinh = self._get_value(row, 'gioi_tinh', True)
                ngay_sinh = self._get_value(row, 'ngay_sinh', None)
                so_dien_thoai = self._get_value(row, 'so_dien_thoai', '')
                
                # ── Validate ──
                # 1. Mã học sinh
                if not ma_hoc_sinh or not str(ma_hoc_sinh).strip():
                    errors.append("Mã học sinh không được để trống")
                else:
                    ma_hoc_sinh = str(ma_hoc_sinh).strip().upper()
                    existing = self.hs_repo.get_by_ma(ma_hoc_sinh)
                    if existing:
                        errors.append(f"Mã học sinh '{ma_hoc_sinh}' đã tồn tại")
                
                # 2. Họ tên
                if not ho_ten or not str(ho_ten).strip():
                    errors.append("Họ tên không được để trống")
                else:
                    ho_ten = str(ho_ten).strip()
                
                # 3. Giới tính
                if isinstance(gioi_tinh, str):
                    gioi_tinh = gioi_tinh.lower() in ['nam', 'true', '1', 'male', 'm']
                elif isinstance(gioi_tinh, (int, float)):
                    gioi_tinh = bool(gioi_tinh)
                else:
                    gioi_tinh = True
                
                # 4. Ngày sinh
                if ngay_sinh:
                    try:
                        if isinstance(ngay_sinh, pd.Timestamp):
                            ngay_sinh = ngay_sinh.date()
                        elif isinstance(ngay_sinh, datetime):
                            ngay_sinh = ngay_sinh.date()
                        elif isinstance(ngay_sinh, str):
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']:
                                try:
                                    ngay_sinh = datetime.strptime(ngay_sinh, fmt).date()  # ← .date() thay vì .strftime()
                                    break
                                except ValueError:
                                    continue
                    except Exception:
                        errors.append("Ngày sinh không đúng định dạng")
                else:
                    ngay_sinh = None
                
                # 5. Số điện thoại
                if so_dien_thoai:
                    so_dien_thoai = str(so_dien_thoai).strip().replace(' ', '').replace('-', '')
                    
                    # Tự thêm số 0 nếu Excel bị mất
                    if so_dien_thoai and not so_dien_thoai.startswith('0'):
                        so_dien_thoai = '0' + so_dien_thoai
                    
                    if not re.match(r'^[0-9]{10,11}$', so_dien_thoai):
                        errors.append("Số điện thoại không hợp lệ (phải có 10-11 chữ số)")
                else:
                    so_dien_thoai = None
                
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
                        hs = self.hs_repo.create(
                            ma_hoc_sinh=ma_hoc_sinh,
                            ho_ten=ho_ten,
                            ngay_sinh=ngay_sinh,
                            gioi_tinh=gioi_tinh,
                            so_dien_thoai=so_dien_thoai,
                            lop_hoc_id=lop_hoc_id,
                            active=True,
                        )
                        self._commit()
                        
                        ket_qua['thanh_cong'] += 1
                        ket_qua['da_them'].append({
                            'ma_hoc_sinh': ma_hoc_sinh,
                            'ho_ten': ho_ten,
                            'ngay_sinh': ngay_sinh,
                            'gioi_tinh': 'Nam' if gioi_tinh else 'Nữ',
                            'so_dien_thoai': so_dien_thoai,
                        })
                        
                    except Exception as e:
                        self._rollback()
                        ket_qua['that_bai'] += 1
                        ket_qua['chi_tiet'].append({
                            'row': row_num,
                            'data': row.to_dict(),
                            'errors': [f"Lỗi hệ thống: {str(e)}"]
                        })
            
            # Cập nhật sĩ số lớp
            if ket_qua['thanh_cong'] > 0:
                lop = self.repo.get_by_id(lop_hoc_id)
                if lop:
                    lop.si_so = (lop.si_so or 0) + ket_qua['thanh_cong']
                    self._commit()
            
            return ServiceResult(ok=True, data=ket_qua, error="Import hoàn tất")
                
        except Exception as e:
            self._rollback()
            return ServiceResult(ok=False, error=f"Lỗi đọc file Excel: {str(e)}")

    def _get_value(self, row, key, default=None):
        value = row.get(key, default)
        try:
            if pd.isna(value):
                return default
        except (TypeError, ValueError):
            pass
        return value