# modules/timetable/views/class_timetable_tab.py
"""
ClassTimetableTab: TKB theo từng lớp học.
- Layout truyền thống: Hàng = Tiết (1-10), Cột = Thứ (2-7)
- Dữ liệu lấy từ shared_data (dict dùng chung với TeacherTimetableTab)
- Sửa trực tiếp → đồng bộ ngược về shared_data
- Nội dung ô: Mã môn - Tên GV tắt
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QDialogButtonBox, QFrame
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal

DAYS  = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
N_TIET = 10   # 5 sáng + 5 chiều

COLOR_LOCK     = QColor("#C8F0D4")
COLOR_SANG_SEP = QColor("#DCEBFF")   # Dòng phân cách sáng/chiều
COLOR_DISABLED = QColor("#F2F2F2")

BTN_STYLE = """
    QPushButton {
        background:#F5F5F5; border:1px solid #DDD;
        border-radius:5px; padding:5px 12px;
        font-size:12px; color:#333;
    }
    QPushButton:hover { background:#E8F5F0; border-color:#1D9E75; color:#1D9E75; }
"""
BTN_PRIMARY = """
    QPushButton {
        background:#1D9E75; color:white;
        border-radius:5px; padding:5px 14px;
        font-size:12px; font-weight:600; border:none;
    }
    QPushButton:hover { background:#0F6E56; }
"""


class ClassTimetableTab(QWidget):
    # Signal thông báo cho TeacherTimetableTab khi dữ liệu thay đổi
    data_changed = Signal()

    def __init__(self,
                 shared_data: dict,        # tham chiếu dict chung với Tab GV
                 locked_cells: set,        # tham chiếu set chung
                 ds_gv: list,
                 ds_mon: list,
                 ds_lop: list,
                 mon_dict: dict,           # {mon_id: (ma_mon, ten_mon)}
                 gv_dict: dict,            # {gv_id: ten_ngan}
                 lop_dict: dict,           # {lop_id: ten_lop}
                 schedule_config: dict,    # {thu: {sang, chieu}}
                 parent=None):
        super().__init__(parent)

        # Dữ liệu dùng chung — là THAM CHIẾU, không copy
        self._data          = shared_data
        self._locked        = locked_cells
        self._ds_gv         = ds_gv
        self._ds_mon        = ds_mon
        self._ds_lop        = ds_lop
        self._mon_dict      = mon_dict
        self._gv_dict       = gv_dict
        self._lop_dict      = lop_dict
        self._schedule_cfg  = schedule_config

        # lop_id đang xem
        self._cur_lop_id: int | None = None

        self._build_ui()
        self._fill_lop_combo()
        if self._ds_lop:
            self._on_lop_changed()

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Toolbar ───────────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("font-size:12px;color:#555;font-weight:500;")
            return l

        top.addWidget(lbl("Lớp:"))
        self.cmb_lop = QComboBox()
        self.cmb_lop.setMinimumWidth(140)
        self.cmb_lop.currentIndexChanged.connect(self._on_lop_changed)
        top.addWidget(self.cmb_lop)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#DDD;")
        top.addWidget(sep)

        btn_prev = QPushButton("◀")
        btn_prev.setFixedWidth(32)
        btn_prev.setStyleSheet(BTN_STYLE)
        btn_prev.setToolTip("Lớp trước")
        btn_prev.clicked.connect(self._prev_lop)
        top.addWidget(btn_prev)

        btn_next = QPushButton("▶")
        btn_next.setFixedWidth(32)
        btn_next.setStyleSheet(BTN_STYLE)
        btn_next.setToolTip("Lớp tiếp theo")
        btn_next.clicked.connect(self._next_lop)
        top.addWidget(btn_next)

        top.addStretch()

        self.lbl_stat = QLabel("")
        self.lbl_stat.setStyleSheet("font-size:11px;color:#888;")
        top.addWidget(self.lbl_stat)

        btn_xuat = QPushButton("🖨 In / Xuất")
        btn_xuat.setStyleSheet(BTN_STYLE)
        btn_xuat.clicked.connect(self._xuat_tkb)
        top.addWidget(btn_xuat)

        layout.addLayout(top)

        # ── Bảng ──────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setRowCount(N_TIET)
        self.table.setColumnCount(len(DAYS))
        self.table.setHorizontalHeaderLabels(DAYS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setAlternatingRowColors(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._ctx_menu)
        self.table.itemDoubleClicked.connect(self._on_double_click)
        self.table.setWordWrap(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border:1px solid #DDD;
                gridline-color:#E0E0E0;
                font-size:12px;
            }
            QHeaderView::section {
                background:#1D9E75; color:white;
                font-weight:600; font-size:12px;
                padding:6px; border:none;
                border-right:1px solid rgba(255,255,255,0.3);
            }
        """)

        # Vertical header: Tiết 1-10
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.verticalHeader().setStyleSheet(
            "QHeaderView::section { background:#F5F5F5; color:#555;"
            " font-size:11px; padding:4px; border:none;"
            " border-bottom:1px solid #E0E0E0; }")
        for i in range(N_TIET):
            self.table.setVerticalHeaderItem(
                i, QTableWidgetItem(f"Tiết {i+1}"))

        # Chiều rộng cột đều nhau
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        layout.addWidget(self.table)

        note = QLabel(
            "💡 Double-click để sửa  |  "
            "Chuột phải để khóa/mở  |  "
            "🟢 Xanh = đã khóa  |  "
            "🔵 Dòng 5-6 = ranh giới Sáng/Chiều")
        note.setStyleSheet("color:#999;font-size:10px;padding:2px 0;")
        layout.addWidget(note)

    # ── Điền ComboBox lớp ─────────────────────────────────────
    def _fill_lop_combo(self):
        self.cmb_lop.blockSignals(True)
        self.cmb_lop.clear()
        for lop in self._ds_lop:
            ten = self._lop_dict.get(lop.id, str(lop.id))
            self.cmb_lop.addItem(ten, lop.id)
        self.cmb_lop.blockSignals(False)

    # ── Render ────────────────────────────────────────────────
    def refresh(self):
        """Gọi từ bên ngoài khi shared_data thay đổi."""
        self._render()

    def _on_lop_changed(self):
        self._cur_lop_id = self.cmb_lop.currentData()
        self._render()

    def _render(self):
        if not self._cur_lop_id:
            return

        self.table.clearContents()

        # Đếm tiết của lớp này
        n_tiet = 0

        for tiet in range(1, N_TIET + 1):
            for col, thu in enumerate(range(2, 8)):
                # Tìm GV dạy lớp này vào (thu, tiet)
                entry = self._find_entry(thu, tiet, self._cur_lop_id)

                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)

                if entry:
                    thu_v, tiet_v, gv_id = entry
                    mon_id, lop_id = self._data[entry]
                    mon   = self._mon_dict.get(mon_id, ("?", "?"))
                    gv_sh = self._gv_dict.get(gv_id, "?")
                    item.setText(f"{mon[0]}\n{gv_sh}")
                    item.setData(Qt.UserRole, entry)   # lưu key để sửa/khóa

                    if entry in self._locked:
                        item.setBackground(COLOR_LOCK)
                    else:
                        item.setBackground(QColor("#FFFFFF"))

                    n_tiet += 1

                else:
                    # Kiểm tra tiết có được học không
                    if not self._is_valid(thu, tiet):
                        item.setBackground(COLOR_DISABLED)
                        item.setFlags(Qt.NoItemFlags)
                    else:
                        item.setBackground(QColor("#FAFAFA"))

                # Dòng 5 (index 4): ranh giới sáng/chiều
                row = tiet - 1
                if row == 4:
                    item.setBackground(
                        COLOR_SANG_SEP if not entry else COLOR_SANG_SEP)

                f = QFont()
                f.setPointSize(10)
                item.setFont(f)
                self.table.setItem(row, col, item)

        # Thống kê
        ten_lop = self._lop_dict.get(self._cur_lop_id, "?")
        self.lbl_stat.setText(
            f"Lớp {ten_lop}  |  📚 {n_tiet} tiết/tuần")

    def _find_entry(self, thu: int, tiet: int,
                    lop_id: int) -> tuple | None:
        """Tìm key (thu, tiet, gv_id) trong shared_data khớp với lop_id."""
        for key, (mon_id, l_id) in self._data.items():
            if key[0] == thu and key[1] == tiet and l_id == lop_id:
                return key
        return None

    def _is_valid(self, thu: int, tiet: int) -> bool:
        cfg = self._schedule_cfg.get(thu)
        if not cfg:
            return False
        return cfg.get("sang", False) if tiet <= 5 else cfg.get("chieu", False)

    # ── Điều hướng lớp ────────────────────────────────────────
    def _prev_lop(self):
        idx = self.cmb_lop.currentIndex()
        if idx > 0:
            self.cmb_lop.setCurrentIndex(idx - 1)

    def _next_lop(self):
        idx = self.cmb_lop.currentIndex()
        if idx < self.cmb_lop.count() - 1:
            self.cmb_lop.setCurrentIndex(idx + 1)

    # ── Double-click sửa ──────────────────────────────────────
    def _on_double_click(self, item):
        if not item or not (item.flags() & Qt.ItemIsEnabled):
            return
        row = item.row()
        col = item.column()
        thu  = col + 2
        tiet = row + 1
        self._show_edit_dialog(thu, tiet)

    def _show_edit_dialog(self, thu: int, tiet: int):
        # Tìm entry hiện tại
        entry = self._find_entry(thu, tiet, self._cur_lop_id)
        cur_mon_id = self._data[entry][0] if entry else None
        cur_gv_id  = entry[2] if entry else None

        dlg = QDialog(self)
        dlg.setWindowTitle(
            f"Sửa tiết — {DAYS[thu-2]}, Tiết {tiet}, "
            f"Lớp {self._lop_dict.get(self._cur_lop_id, '?')}")
        dlg.setMinimumWidth(360)
        layout = QVBoxLayout(dlg)
        form   = QFormLayout()
        form.setSpacing(10)

        # ComboBox môn
        cmb_mon = QComboBox()
        cmb_mon.addItem("-- Chọn môn --", None)
        for m in self._ds_mon:
            cmb_mon.addItem(f"{m.ma_mon} – {m.ten_mon}", m.id)
        if cur_mon_id:
            idx = cmb_mon.findData(cur_mon_id)
            if idx >= 0:
                cmb_mon.setCurrentIndex(idx)

        # ComboBox GV
        cmb_gv = QComboBox()
        cmb_gv.addItem("-- Chọn GV --", None)
        for gv in self._ds_gv:
            ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
            cmb_gv.addItem(f"{gv.ma_giao_vien} – {ten}", gv.id)
        if cur_gv_id:
            idx = cmb_gv.findData(cur_gv_id)
            if idx >= 0:
                cmb_gv.setCurrentIndex(idx)

        form.addRow("Môn học:", cmb_mon)
        form.addRow("Giáo viên:", cmb_gv)
        layout.addLayout(form)

        # Cảnh báo nếu GV bận
        self.lbl_warn = QLabel("")
        self.lbl_warn.setStyleSheet("color:#C0392B;font-size:11px;")
        self.lbl_warn.setWordWrap(True)
        layout.addWidget(self.lbl_warn)

        def check_conflict():
            gv_id = cmb_gv.currentData()
            if not gv_id:
                self.lbl_warn.setText("")
                return
            # Kiểm tra GV đã có tiết (thu, tiet) chưa
            existing = self._data.get((thu, tiet, gv_id))
            if existing and existing[1] != self._cur_lop_id:
                other_lop = self._lop_dict.get(existing[1], "?")
                self.lbl_warn.setText(
                    f"⚠ GV đang dạy lớp {other_lop} vào tiết này!")
            else:
                self.lbl_warn.setText("")

        cmb_gv.currentIndexChanged.connect(check_conflict)
        check_conflict()

        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel |
            QDialogButtonBox.Reset)
        btn_box.button(QDialogButtonBox.Reset).setText("🗑 Xóa tiết")
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)

        def xoa():
            if entry:
                del self._data[entry]
            dlg.accept()
            self._render()
            self.data_changed.emit()

        btn_box.button(QDialogButtonBox.Reset).clicked.connect(xoa)
        layout.addWidget(btn_box)

        if dlg.exec() == QDialog.Accepted:
            m_id = cmb_mon.currentData()
            g_id = cmb_gv.currentData()
            if m_id and g_id:
                # Xóa entry cũ nếu có
                if entry:
                    del self._data[entry]
                # Ghi entry mới
                new_key = (thu, tiet, g_id)
                self._data[new_key] = (m_id, self._cur_lop_id)
            elif entry:
                del self._data[entry]
            self._render()
            self.data_changed.emit()   # báo Tab GV cập nhật

    # ── Context menu khóa/mở ──────────────────────────────────
    def _ctx_menu(self, pos):
        from PySide6.QtWidgets import QMenu
        item = self.table.itemAt(pos)
        if not item or not item.data(Qt.UserRole):
            return
        key  = item.data(Qt.UserRole)
        menu = QMenu(self)
        if key in self._locked:
            menu.addAction("🔓 Mở khóa tiết này").triggered.connect(
                lambda: self._toggle_lock(key))
        else:
            menu.addAction("🔒 Khóa tiết này").triggered.connect(
                lambda: self._toggle_lock(key))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _toggle_lock(self, key):
        if key in self._locked:
            self._locked.discard(key)
        else:
            self._locked.add(key)
        self._render()
        self.data_changed.emit()

    # ── Xuất / In ─────────────────────────────────────────────
    def _xuat_tkb(self):
        """TODO: Xuất TKB lớp ra Excel hoặc in."""
        QMessageBox.information(
            self, "Thông báo",
            "Tính năng xuất/in TKB lớp đang phát triển 🚧")