# D:\QUANLYTRUONGHOC\ui\router.py
"""
Router: quản lý việc chuyển trang giữa các module.
Dùng QStackedWidget — lazy init, chỉ tạo page khi lần đầu được gọi.
"""

from PySide6.QtWidgets import QStackedWidget, QLabel
from PySide6.QtCore import Qt
from core.db.models import NguoiDung
from modules.giao_vien_thi_dua import ThiDuaGVWidget

class Router(QStackedWidget):
    def __init__(self, nguoi_dung: NguoiDung,
                 to_id: int = None, parent=None):
        super().__init__(parent)
        self._nd    = nguoi_dung
        self._to_id = to_id
        self._pages: dict[str, int] = {}

        self.addWidget(self._placeholder("Chọn chức năng từ menu bên trái"))

    def navigate(self, page_key: str):
        if page_key not in self._pages:
            widget = self._create_page(page_key)
            if widget is None:
                return
            idx = self.addWidget(widget)
            self._pages[page_key] = idx
        self.setCurrentIndex(self._pages[page_key])

    def _create_page(self, key: str):

            # ── Giáo viên ─────────────────────────────────────────
        if key == "admin.giao_vien":
            from modules.giao_vien.page import GiaoVienPage
            return GiaoVienPage()

        # ── Lớp học ───────────────────────────────────────────
        if key == "admin.lop_hoc":
            from modules.lop_hoc.page import LopHocPage
            return LopHocPage()
        # ── Phân công giảng dạy ───────────────────────────────
        if key == "phan_cong":  # Thêm vào đây
            from modules.phan_cong.page import PhanCongPage
            return PhanCongPage()
        # ── Cấu hình hệ thống ─────────────────────────────────
        if key == "cau_hinh":  # Giữ nguyên "cau_hinh" cho khớp với sidebar
            try:
                from modules.cau_hinh.page import CauHinhPage
                return CauHinhPage()
            except ImportError as e:
                return self._placeholder(f"Module 'Cấu hình' đang phát triển 🚧\nLỗi: {e}")

        # ── Thi đua giáo viên ─────────────────────────────────
        if key == "teacher_competition":
            try:
                return ThiDuaGVWidget(nguoi_dung=self._nd)
            except ImportError as e:
                return self._placeholder(f"Module 'Thi đua giáo viên' đang phát triển 🚧\nLỗi: {e}")

        # ── Thi đua học sinh ────────── ĐÃ THAY THẾ BẰNG THI ĐUA TẬP THỂ LỚP ───
        if key == "student_score":
            try:
                # Thay vì module cũ, dùng module mới (Thi đua tập thể lớp - Điểm Đội)
                from modules.competition.views.tap_the_tab import TapTheTab
                return TapTheTab()
            except ImportError as e:
                return self._placeholder(f"Module 'Thi đua tập thể lớp' đang phát triển 🚧\nLỗi: {e}")

        # ── Thời khóa biểu ────────────────────────────────────
        if key == "timetable":
            from modules.timetable.page import TimetablePage
            return TimetablePage()

        # ── Báo cáo ───────────────────────────────────────────
        if key == "bao_cao.tong_hop":
            from modules.reports.views.bao_cao_tab import BaoCaoTab
            return BaoCaoTab()
        # ── Xuất báo cáo ─────────────────────────────────────────────
        if key == "bao_cao.xuat":
            try:
                from modules.reports.views.export_report_tab import ExportReportTab
                return ExportReportTab()
            except ImportError as e:
                return self._placeholder(f"Module 'Xuất báo cáo' đang phát triển 🚧\nLỗi: {e}")

        # ── Hệ thống ──────────────────────────────────────────────
        if key == "system.backup":
            from modules.system.views.backup_tab import BackupTab
            return BackupTab()

        if key == "system.log":
            from modules.system.views.log_tab import LogTab
            return LogTab()
        
    def _placeholder(self, msg: str) -> QLabel:
        lbl = QLabel(msg)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #aaa; font-size: 15px;")
        return lbl