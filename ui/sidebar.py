# D:\QUANLYTRUONGHOC\ui\sidebar.py
"""
Sidebar: menu điều hướng bên trái của MainWindow.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton
from shared.enums import Role
from modules.lop_hoc.page import LopHocPage

MENU_GROUPS = [
    {
        "label": "QUẢN LÝ CHUNG",
        "items": [
            ("👤", "Giáo viên",           "admin.giao_vien",  [Role.ADMIN]),
            ("🏫", "Học sinh",             "admin.lop_hoc",    [Role.ADMIN]),
            ("📅", "Thời khóa biểu",      "timetable",        None),
            ("📋", "Phân công giảng dạy", "phan_cong", [Role.ADMIN, Role.TO_TRUONG]),
            ("⚙️", "Cấu hình hệ thống",   "cau_hinh",         [Role.ADMIN]),
        ]
    },
    {
        "label": "THI ĐUA",
        "items": [
            ("⭐", "Thi đua giáo viên",   "teacher_competition", [Role.ADMIN, Role.TO_TRUONG, Role.PHO_TO_TRUONG]),
            ("🎖️", "Thi đua học sinh",    "student_score", [Role.ADMIN, Role.TONG_PHU_TRACH]),
        ]
    },
    {
        "label": "BÁO CÁO",
        "items": [
            ("📄", "Báo cáo tổng hợp",   "bao_cao.tong_hop", None),
             ("📤", "Xuất báo cáo",        "bao_cao.xuat",     None),
        ]
    },
    {
        "label": "HỆ THỐNG",
        "items": [
            ("💾", "Sao lưu dữ liệu",    "system.backup",    [Role.ADMIN]),
            ("📝", "Nhật ký hệ thống",    "system.log",       [Role.ADMIN]),
        ]
    },
    ]


class Sidebar(QWidget):
    page_changed = Signal(str)

    def __init__(self, role: Role, parent=None):
        super().__init__(parent)
        self._role = role
        self._buttons: dict[str, QPushButton] = {}
        self._active_key: str = ""
        self.setFixedWidth(250)  # Tăng nhẹ từ 220 lên 250
        self.setStyleSheet("""
            QWidget { background: #1A1F2E; }  /* Đổi màu nền tối hơn */
        """)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────
        logo_frame = QFrame()
        logo_frame.setFixedHeight(70)
        logo_frame.setStyleSheet("""
            background: #1D9E75;
            border: none;
        """)  # ← Bỏ border-bottom
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 12, 20, 12)
        logo_layout.setAlignment(Qt.AlignVCenter)

        logo_lbl = QLabel("🏫  EduSchool Suite")
        logo_lbl.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            letter-spacing: 1px;
        """)
        logo_layout.addWidget(logo_lbl)

        sub_lbl = QLabel("Quản lý trường học")
        sub_lbl.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 11px;
            background: transparent;
            margin-top: 2px;
        """)
        logo_layout.addWidget(sub_lbl)
        outer.addWidget(logo_frame)

        # ── Scroll menu ───────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #1A1F2E;
            }
            QScrollBar:vertical {
                width: 5px;
                background: #2A2F3E;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #1D9E75;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0F6E56;
            }
        """)

        menu_widget = QWidget()
        menu_widget.setStyleSheet("background: #1A1F2E;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 16, 0, 16)
        menu_layout.setSpacing(4)

        for group in MENU_GROUPS:
            visible = [
                item for item in group["items"]
                if item[3] is None or self._role in item[3]
            ]
            if not visible:
                continue

            grp_lbl = QLabel(group["label"])
            grp_lbl.setStyleSheet("""
                color: #6B7280;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding: 12px 20px 4px 20px;
                background: transparent;
            """)
            menu_layout.addWidget(grp_lbl)

            for icon, label, key, roles in visible:
                btn = self._make_btn(icon, label, key)
                menu_layout.addWidget(btn)
                self._buttons[key] = btn

        menu_layout.addStretch()
        scroll.setWidget(menu_widget)
        outer.addWidget(scroll)

    def _make_btn(self, icon: str, label: str, key: str) -> QPushButton:
        btn = QPushButton(f"{icon}  {label}")
        btn.setFixedHeight(42)
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                color: #A0A5B5;
                background: transparent;
                border: none;
                text-align: left;
                padding-left: 24px;
                font-size: 13px;
                font-weight: 500;
                margin: 2px 8px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #2A2F3E;
                color: white;
            }
            QPushButton:checked {
                background: #1D9E75;
                color: white;
                font-weight: 600;
            }
        """)
        btn.clicked.connect(lambda _, k=key: self._on_click(k))
        return btn

    def _on_click(self, key: str):
        if self._active_key == key:
            return
        if self._active_key and self._active_key in self._buttons:
            self._buttons[self._active_key].setChecked(False)
        self._active_key = key
        self._buttons[key].setChecked(True)
        self.page_changed.emit(key)

    def set_active(self, key: str):
        if key in self._buttons:
            self._on_click(key)