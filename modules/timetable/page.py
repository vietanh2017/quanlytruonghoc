# modules/timetable/page.py
"""
TimetablePage: trang Thời khóa biểu gồm 2 tab.
  Tab 1 — Theo giáo viên : sinh TKB tự động, chỉnh thủ công
  Tab 2 — Theo lớp       : xem + sửa trực tiếp, đồng bộ về Tab 1

Dữ liệu dùng chung qua tham chiếu dict/set:
  _shared_data   = {(thu, tiet, gv_id): (mon_id, lop_id)}
  _locked_cells  = {(thu, tiet, gv_id)}
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from core.db.models import NguoiDung


class TimetablePage(QWidget):
    def __init__(self, nguoi_dung: NguoiDung = None, parent=None):
        super().__init__(parent)
        self._nd = nguoi_dung

        # ── Dữ liệu dùng chung giữa 2 tab ────────────────────
        self._shared_data  = {}   # {(thu, tiet, gv_id): (mon_id, lop_id)}
        self._locked_cells = set()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 22px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                font-weight: 600;
                border-bottom: 2px solid #1D9E75;
                color: #1D9E75;
            }
        """)
        layout.addWidget(self.tabs)

        # ── Tab 1: Theo giáo viên ─────────────────────────────
        from modules.timetable.views.teacher_timetable_tab import TeacherTimetableTab
        self.tab_gv = TeacherTimetableTab(parent=self)

        # Gắn shared_data vào tab GV
        # (TeacherTimetableTab dùng self._current_data nội bộ,
        #  ta sync sau khi load xong)
        self.tab_gv._current_data = self._shared_data
        self.tab_gv._locked_cells = self._locked_cells

        self.tabs.addTab(self.tab_gv, "👨‍🏫  Theo giáo viên")

        # ── Tab 2: Theo lớp ───────────────────────────────────
        from modules.timetable.views.class_timetable_tab import ClassTimetableTab
        self.tab_lop = ClassTimetableTab(
            shared_data    = self._shared_data,
            locked_cells   = self._locked_cells,
            ds_gv          = self.tab_gv._ds_gv,
            ds_mon         = self.tab_gv._ds_mon,
            ds_lop         = self.tab_gv._ds_lop,
            mon_dict       = self.tab_gv._mon_dict,
            gv_dict        = self.tab_gv._gv_dict,
            lop_dict       = self.tab_gv._lop_dict,
            schedule_config= self.tab_gv._schedule_config,
            parent=self,
        )
        self.tabs.addTab(self.tab_lop, "🏫  Theo lớp")

        # ── Đồng bộ 2 chiều ───────────────────────────────────
        # Tab lớp sửa → báo Tab GV refresh
        self.tab_lop.data_changed.connect(self._on_class_data_changed)

        # Khi chuyển sang Tab lớp → refresh
        self.tabs.currentChanged.connect(self._on_tab_changed)

    # ── Đồng bộ ───────────────────────────────────────────────
    def _on_class_data_changed(self):
        """Tab lớp vừa sửa dữ liệu → cập nhật Tab GV."""
        self.tab_gv._render_table()

    def _on_tab_changed(self, idx: int):
        """Chuyển sang Tab lớp → refresh để lấy dữ liệu mới nhất."""
        if idx == 1:
            self.tab_lop.refresh()