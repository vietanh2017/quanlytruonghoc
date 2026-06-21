"""
MainWindow: cửa sổ chính của EduSchool Suite.
Layout: Sidebar (trái) + phần phải gồm Topbar (trên) + Router/content (dưới).
Nhận nguoi_dung từ LoginPage sau khi xác thực thành công.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent

from core.db.models import NguoiDung
from ui.sidebar import Sidebar
from ui.topbar import Topbar
from ui.router import Router
from shared.enums import Role

# Trang mặc định theo role
DEFAULT_PAGE = {
    Role.ADMIN:          "admin.giao_vien",
    Role.TO_TRUONG:      "teacher_competition",
    Role.PHO_TO_TRUONG:  "teacher_competition",
    Role.TONG_PHU_TRACH: "student_score",
    Role.GIAO_VIEN:      "timetable",
    Role.NHAN_VIEN:      "timetable",
}


class MainWindow(QMainWindow):
    def __init__(self, nguoi_dung: NguoiDung,
                 to_id: int = None, parent=None):
        super().__init__(parent)
        self._nd    = nguoi_dung
        self._to_id = to_id
        self.setWindowTitle("EduSchool Suite")
        self.setMinimumSize(1100, 660)
        self.resize(1280, 760)
        self._build_ui()
        self._navigate_default()

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(role=self._nd.role)
        self.sidebar.page_changed.connect(self._on_navigate)
        root.addWidget(self.sidebar)

        # Phần phải: Topbar + Content
        right = QWidget()
        right.setStyleSheet("background: #F7F8FA;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Topbar - hiển thị thông tin người dùng
        self.topbar = Topbar()
        self.topbar.set_user_name(self._nd.ho_ten)
        self.topbar.logout_requested.connect(self._on_logout)
        right_layout.addWidget(self.topbar)

        # Router
        self.router = Router(nguoi_dung=self._nd, to_id=self._to_id)
        right_layout.addWidget(self.router)

        root.addWidget(right)

        # Status bar
        self.statusBar().showMessage(
            f"  Người dùng: {self._nd.ho_ten}   |   "
            f"Máy trạm: LOCALHOST   |   CSDL: eduschool.db   |   Sẵn sàng ✓"
        )
        self.statusBar().setStyleSheet(
            "QStatusBar { font-size: 11px; color: #888;"
            " border-top: 1px solid #E0E0E0; background: white; }")

    # ── Navigation ────────────────────────────────────────────
    def _navigate_default(self):
        default_key = DEFAULT_PAGE.get(self._nd.role, "teacher_score")
        self.router.navigate(default_key)
        self.sidebar.set_active(default_key)

    def _on_navigate(self, page_key: str):
        try:
            self.router.navigate(page_key)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # ── Logout ────────────────────────────────────────────────
    def _on_logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from ui.login_page import LoginPage
            self.login = LoginPage()
            self.login.show()
            self.close()

    # ── Close ─────────────────────────────────────────────────
    def closeEvent(self, event: QCloseEvent):
        for i in range(self.router.count()):
            w = self.router.widget(i)
            if hasattr(w, "svc") and hasattr(w.svc, "close"):
                w.svc.close()
        super().closeEvent(event)