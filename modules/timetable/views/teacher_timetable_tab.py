# modules/timetable/views/teacher_timetable_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QDialogButtonBox, QMenu, QFrame,
    QGroupBox, QCheckBox, QSpinBox, QScrollArea, QGridLayout
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QTimer
from core.db.session import SessionLocal
from modules.timetable.service import TimetableService


DAYS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
BUOIS = ["Sáng", "Chiều"]  # Thêm dòng này
TIET_SANG = list(range(1, 6))
TIET_CHIEU = list(range(6, 9))
ALL_TIETS = TIET_SANG + TIET_CHIEU


def tinh_buoi(tiet: int) -> int:
    return 0 if tiet in TIET_SANG else 1


def tinh_tiet_hien_thi(tiet: int) -> int:
    return tiet if tiet <= 5 else tiet - 5


def is_valid_period(schedule_config, thu, tiet):
    cfg = schedule_config.get(thu)
    if not cfg:
        return False
    if tiet <= 5:
        return cfg.get("sang", False)
    if tiet <= 8:
        return cfg.get("chieu", False)
    return False


# Màu sắc
COLOR_LOCK = QColor("#C8F0D4")
COLOR_DAY_BG = QColor("#E8F5F0")
COLOR_BUOI_BG = QColor("#F4FAF7")
COLOR_HOLIDAY = QColor("#FFB3B3")       # Đỏ nhạt - ngày nghỉ
COLOR_MORNING_OFF = QColor("#FFE0B3")   # Cam nhạt - nghỉ sáng
COLOR_AFTERNOON_OFF = QColor("#FFF0B3") # Vàng nhạt - nghỉ chiều
COLOR_DISABLED = QColor("#F2F2F2")      # Xám - không học

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
from PySide6.QtWidgets import QTableWidget, QAbstractItemView
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor

class DraggableTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self._drag_source = None  # (row, col) ô đang kéo

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item and item.text().strip():
                self._drag_source = (item.row(), item.column())
            else:
                self._drag_source = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self._drag_source is None:
            return

        row, col = self._drag_source
        item = self.item(row, col)
        if not item or not item.text().strip():
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(f"{row},{col}")
        drag.setMimeData(mime)

        # Tạo ảnh preview khi kéo
        pix = QPixmap(self.columnWidth(col), self.rowHeight(row))
        pix.fill(QColor("#1D9E75"))
        painter = QPainter(pix)
        painter.setPen(QColor("white"))
        painter.drawText(pix.rect(), Qt.AlignCenter, item.text()[:20])
        painter.end()
        drag.setPixmap(pix)
        drag.setHotSpot(QPoint(pix.width() // 2, pix.height() // 2))

        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            return
        # Chuyển xử lý lên TeacherTimetableTab
        pos = event.position().toPoint()
        target_item = self.itemAt(pos)
        if target_item is None:
            # Thử lấy theo vị trí row/col
            row = self.rowAt(pos.y())
            col = self.columnAt(pos.x())
            if row < 0 or col < 0:
                event.ignore()
                return
        else:
            row = target_item.row()
            col = target_item.column()

        try:
            src_row, src_col = map(int, event.mimeData().text().split(","))
        except Exception:
            event.ignore()
            return

        if (src_row, src_col) == (row, col):
            event.ignore()
            return

        # Phát signal lên parent để xử lý
        if hasattr(self.parent(), '_handle_drop'):
            self.parent()._handle_drop(src_row, src_col, row, col)

        event.acceptProposedAction()

class TeacherTimetableTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.session = SessionLocal()
        self.svc = TimetableService(self.session)

        self._current_data = {}
        self._locked_cells = set()

        self._ds_gv = []
        self._ds_mon = []
        self._ds_lop = []

        self._lop_dict = {}
        self._mon_dict = {}
        self._gv_dict = {}

        self._row_map = {}
        self._col_map = {}

        self._constraint_config = {
            "max_tiet_ngay": 7,
            "max_consecutive": 3,
            "pe_subjects": [],
            "allow_double_subjects": [],
            "tiet_trong_gv": {},
            "no_same_subject_per_day": True,
            "no_consecutive_5_6": False,
            "distribute_evenly": True,
            "sang_4_tiet_neu_co_chieu": True,
        }

        self._schedule_config = {
            2: {"sang": True, "chieu": False},
            3: {"sang": True, "chieu": False},
            4: {"sang": True, "chieu": False},
            5: {"sang": True, "chieu": False},
            6: {"sang": True, "chieu": False},
            7: {"sang": True, "chieu": False},
            
        }
        self._gv_schedule_config = {}  # Lưu lịch riêng cho từng GV
        self._build_ui()
        self._load_filters()

        for mon in self._ds_mon:
            ten = mon.ten_mon.lower()
            if "thể dục" in ten:
                self._constraint_config["pe_subjects"].append(mon.id)
            if "ngữ văn" in ten or ten == "văn":
                self._constraint_config["allow_double_subjects"].append(mon.id)

        QTimer.singleShot(100, self._load_existing_timetable)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("font-size:12px;color:#555;font-weight:500;")
            return l

        filter_row.addWidget(lbl("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setFixedWidth(110)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_nam_hoc_changed)
        filter_row.addWidget(self.cmb_nam_hoc)

        filter_row.addWidget(lbl("Học kỳ:"))
        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.setFixedWidth(100)
        self.cmb_hoc_ky.currentIndexChanged.connect(self._load_existing_timetable)
        filter_row.addWidget(self.cmb_hoc_ky)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#DDD;")
        filter_row.addWidget(sep)

        filter_row.addWidget(lbl("Xem theo GV:"))
        self.cmb_gv = QComboBox()
        self.cmb_gv.setMinimumWidth(220)
        self.cmb_gv.currentIndexChanged.connect(self._render_table)
        filter_row.addWidget(self.cmb_gv)

        filter_row.addStretch()
        layout.addLayout(filter_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        for text, slot, primary in [
            ("🚀 Sinh TKB", self._generate, False),
            ("🔒 Khóa ô", self._lock_selected, False),
            ("🔓 Mở khóa", self._unlock_selected, False),
            ("💾 Lưu TKB", self._save_all, True),
            ("📅 Lịch học", self._show_schedule_dialog, False),
            ("⚙️ Ràng buộc", self._show_constraint_dialog, False),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setStyleSheet(BTN_PRIMARY if primary else BTN_STYLE)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        self.lbl_stat = QLabel("")
        self.lbl_stat.setStyleSheet("font-size:11px;color:#888;")
        btn_row.addWidget(self.lbl_stat)
        layout.addLayout(btn_row)

        self.table = DraggableTable(self)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # Thêm context menu cho header
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self._show_header_context_menu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.itemDoubleClicked.connect(self._on_cell_double_click)
        self.table.setWordWrap(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border:1px solid #DDD;
                gridline-color:#E8E8E8;
                font-size:12px;
            }
            QHeaderView::section {
                background:#1D9E75; color:white;
                font-weight:600; font-size:12px;
                padding:5px; border:none;
                border-right:1px solid rgba(255,255,255,0.3);
            }
        """)
        layout.addWidget(self.table)

        note = QLabel("💡 Double-click để sửa | Chuột phải để khóa/mở | Xanh = đã khóa | Đỏ = nghỉ | Cam = nghỉ sáng | Vàng = nghỉ chiều")
        note.setStyleSheet("color:#999;font-size:10px;padding:2px 0;")
        layout.addWidget(note)

    def _load_filters(self):
        self._ds_gv = self.svc.lay_ds_giao_vien()
        self._ds_mon = self.svc.lay_ds_mon()
        self._ds_lop = self.svc.lay_ds_lop()

        for mon in self._ds_mon:
            self._mon_dict[mon.id] = (mon.ma_mon, mon.ten_mon)
        for lop in self._ds_lop:
            self._lop_dict[lop.id] = lop.ten_lop

        self.cmb_gv.addItem("👨‍🏫 Tất cả giáo viên (theo lớp)", None)
        for gv in self._ds_gv:
            ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
            parts = ten.split()
            self._gv_dict[gv.id] = parts[-1] if parts else ten
            self.cmb_gv.addItem(f"{gv.ma_giao_vien} – {ten}", gv.id)

        from core.db.models.nam_hoc import NamHoc
        for nh in self.session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all():
            self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)

    def _on_nam_hoc_changed(self):
        self.cmb_hoc_ky.clear()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if not nam_hoc_id:
            return
        from core.db.models.hoc_ky import HocKy
        for hk in self.session.query(HocKy).filter_by(nam_hoc_id=nam_hoc_id).order_by(HocKy.so_thu_tu).all():
            self.cmb_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)

    def _build_table_structure_all(self):
        """Xây dựng bảng cho chế độ tất cả giáo viên (theo lớp)"""
        lop_ids = [l.id for l in self._ds_lop]

        # Dùng lịch CHUNG cho bảng tổng hợp
        valid_buois = []
        for thu_idx, thu_name in enumerate(DAYS):
            thu = thu_idx + 2
            if self._schedule_config[thu]["sang"]:
                valid_buois.append((thu_idx, thu_name, "Sáng"))
            if self._schedule_config[thu]["chieu"]:
                valid_buois.append((thu_idx, thu_name, "Chiều"))
        
        n_buoi = len(valid_buois)
        n_tiet = 5
        n_rows = n_buoi * n_tiet
        n_cols = 2 + len(lop_ids)
        
        self.table.setRowCount(n_rows)
        self.table.setColumnCount(n_cols)
        
        self.table.setHorizontalHeaderLabels(["Buổi", "Tiết"] + [self._lop_dict.get(lid, str(lid)) for lid in lop_ids])
        
        self._col_map = {lid: 2 + i for i, lid in enumerate(lop_ids)}
        self._row_map = {}
        
        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 45)
        for i in range(len(lop_ids)):
            self.table.setColumnWidth(2 + i, 110)
        
        row = 0
        for thu_idx, thu_name, buoi_name in valid_buois:
            buoi_start = row
            for tiet_idx in range(n_tiet):
                tiet_hien_thi = tiet_idx + 1
                item = QTableWidgetItem(str(tiet_hien_thi))
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor("#FAFAFA"))
                f = QFont()
                f.setPointSize(10)
                item.setFont(f)
                self.table.setItem(row, 1, item)
                self.table.setRowHeight(row, 46)
                self._row_map[(thu_idx, buoi_name, tiet_idx)] = row
                row += 1
            
            self.table.setSpan(buoi_start, 0, n_tiet, 1)
            bi = QTableWidgetItem(f"{thu_name}\n{buoi_name}")
            bi.setTextAlignment(Qt.AlignCenter)
            bi.setBackground(COLOR_DAY_BG if buoi_name == "Sáng" else COLOR_BUOI_BG)
            f = QFont()
            f.setPointSize(10)
            f.setBold(True)
            bi.setFont(f)
            self.table.setItem(buoi_start, 0, bi)
        
        return lop_ids
    
    def _build_table_structure_single(self):
        n_tiet = 8
        n_thu = len(DAYS)

        self.table.clearSpans()
        self.table.setRowCount(n_tiet)
        self.table.setColumnCount(n_thu)
        self.table.setHorizontalHeaderLabels(DAYS)
        self.table.verticalHeader().setVisible(True)

        for i in range(n_tiet):
            if i < 5:
                item = QTableWidgetItem(f"Tiết {i+1} (Sáng)")
            else:
                item = QTableWidgetItem(f"Tiết {i-4} (Chiều)")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setVerticalHeaderItem(i, item)

        for col in range(n_thu):
            self.table.setColumnWidth(col, 140)
        for row in range(n_tiet):
            self.table.setRowHeight(row, 42)
        self.table.horizontalHeader().setStretchLastSection(True)

    def _render_table(self):
        gv_id = self.cmb_gv.currentData()
        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        if not gv_id:
            self._render_all_teachers_mode()
        else:
            self._render_single_teacher_mode(gv_id)

    def _render_all_teachers_mode(self):
        """Hiển thị TKB tổng hợp - tất cả giáo viên (theo lớp)"""
        lop_ids = self._build_table_structure_all()
        
        # Xóa nội dung cũ
        for row in range(self.table.rowCount()):
            for col in range(2, self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))
        
        # Gom dữ liệu theo (buoi, tiet, lop_id)
        slot_map = {}
        for (thu, tiet, gv), (mon_id, lop_id) in self._current_data.items():
            buoi = "Sáng" if tiet <= 5 else "Chiều"
            tiet_hien_thi = tinh_tiet_hien_thi(tiet)
            
            thu_idx = thu - 2
            row_key = None
            for (t_idx, b, ti_idx), r in self._row_map.items():
                if t_idx == thu_idx and b == buoi and ti_idx == tiet_hien_thi - 1:
                    row_key = r
                    break
            
            if row_key is None:
                continue
            
            col = self._col_map.get(lop_id)
            if col is None:
                continue
            
            mon = self._mon_dict.get(mon_id, ("?", "?"))
            gv_short = self._gv_dict.get(gv, "?")
            text = f"{mon[0]} - {gv_short}"
            
            key = (row_key, col)
            if key not in slot_map:
                slot_map[key] = []
            slot_map[key].append(text)
        
        # Hiển thị dữ liệu
        for (row, col), texts in slot_map.items():
            display = "\n".join(texts[:2])
            if len(texts) > 2:
                display += f"\n... (+{len(texts)-2})"
            item = QTableWidgetItem(display)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, item)
        
        # Tạo đường kẻ đậm sau tiết 5 (cuối buổi sáng) - dùng màu nền
        n_tiet = 5
        total_sang = 0
        last_sang_row = -1
        
        for (t_idx, b, ti_idx), r in self._row_map.items():
            if b == "Sáng" and ti_idx == n_tiet - 1:
                total_sang += 1
                last_sang_row = r
        
        if total_sang > 0 and last_sang_row >= 0 and last_sang_row < self.table.rowCount():
            # Tạo dòng phân cách bằng cách tô màu nền
            for col in range(self.table.columnCount()):
                item = self.table.item(last_sang_row, col)
                if item:
                    item.setBackground(QColor("#D0D0D0"))
                    item.setForeground(QColor("#666"))
                else:
                    new_item = QTableWidgetItem("")
                    new_item.setBackground(QColor("#D0D0D0"))
                    self.table.setItem(last_sang_row, col, new_item)
            
            # Tăng chiều cao dòng phân cách
            self.table.setRowHeight(last_sang_row, 8)
        
        self.lbl_stat.setText(f"📊 Tổng số tiết: {len(self._current_data)}")

    def _render_single_teacher_mode(self, gv_id):
        self._build_table_structure_single()

        gv = next((g for g in self._ds_gv if g.id == gv_id), None)
        if not gv:
            return

        da_xep = sum(1 for (thu, tiet, g) in self._current_data if g == gv_id)
        self.lbl_stat.setText(f"👨‍🏫 {gv.nguoi_dung.ho_ten}  |  📚 Đã xếp: {da_xep} tiết")

        # Xóa nội dung cũ
        for row in range(8):
            for col in range(len(DAYS)):
                self.table.setItem(row, col, QTableWidgetItem(""))

        for i in range(8):
            if i < 5:
                item = QTableWidgetItem(f"Tiết {i+1} (Sáng)")
            else:
                item = QTableWidgetItem(f"Tiết {i-4} (Chiều)")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setVerticalHeaderItem(i, item)

        # Lấy lịch của giáo viên hiện tại
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)

        # Hiển thị dữ liệu
        for (thu, tiet, g), (mon_id, lop_id) in self._current_data.items():
            if g != gv_id:
                continue
            if tiet < 1 or tiet > 8:
                continue
            row = tiet - 1
            col = thu - 2
            mon = self._mon_dict.get(mon_id, ("?", "?"))
            ten_lop = self._lop_dict.get(lop_id, "?")
            text = f"{mon[1]} - {ten_lop}"
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            key = (thu, tiet, gv_id)
            if key in self._locked_cells:
                item.setBackground(COLOR_LOCK)
            self.table.setItem(row, col, item)

        # Tô màu các cột theo lịch của giáo viên
        for col in range(len(DAYS)):
            thu = col + 2
            is_day_off = not (gv_schedule[thu]["sang"] or gv_schedule[thu]["chieu"])
            is_morning_off = not gv_schedule[thu]["sang"] and gv_schedule[thu]["chieu"]
            is_afternoon_off = gv_schedule[thu]["sang"] and not gv_schedule[thu]["chieu"]
            
            for row in range(8):
                tiet = row + 1
                is_sang = tiet <= 5
                
                if is_day_off:
                    item = self.table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem("")
                        self.table.setItem(row, col, item)
                    item.setBackground(COLOR_HOLIDAY)
                    item.setFlags(Qt.NoItemFlags)
                elif is_morning_off and is_sang:
                    item = self.table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem("")
                        self.table.setItem(row, col, item)
                    item.setBackground(COLOR_MORNING_OFF)
                    item.setFlags(Qt.NoItemFlags)
                elif is_afternoon_off and not is_sang:
                    item = self.table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem("")
                        self.table.setItem(row, col, item)
                    item.setBackground(COLOR_AFTERNOON_OFF)
                    item.setFlags(Qt.NoItemFlags)
                elif not self._is_valid_period_for_gv(gv_id, thu, tiet):
                    item = self.table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem("")
                        self.table.setItem(row, col, item)
                    item.setBackground(COLOR_DISABLED)
                    item.setFlags(Qt.NoItemFlags)

    def _check_constraints(self, current_data, assignment, config):
        thu, tiet, gv_id, mon_id, lop_id = assignment

        # ============================================================
        # RÀNG BUỘC CỨNG
        # ============================================================

        # 1. GV không dạy 2 tiết cùng lúc
        for (t, ti, g) in current_data:
            if t == thu and ti == tiet and g == gv_id:
                return False

        # 2. Lớp không học 2 môn cùng lúc
        for (t, ti, g), (m, l) in current_data.items():
            if t == thu and ti == tiet and l == lop_id:
                return False

        # 3. Theo lịch GV (ngày/buổi hợp lệ)
        if not self._is_valid_period_for_gv(gv_id, thu, tiet):
            return False

        # 4. Tiết trống bắt buộc của GV
        if gv_id in config.get("tiet_trong_gv", {}):
            if (thu, tiet) in config["tiet_trong_gv"][gv_id]:
                return False
        # 4b. Ngày có buổi chiều thì buổi sáng chỉ 4 tiết (không xếp tiết 5)
        if config.get("sang_4_tiet_neu_co_chieu", True):
            if tiet == 5 and self._schedule_config.get(thu, {}).get("chieu", False):
                return False
        # ============================================================
        # RÀNG BUỘC MỀM
        # ============================================================

        # 5. Tối đa số tiết/ngày của GV
        max_tiet = config.get("max_tiet_ngay", 5)
        tiet_trong_ngay = sum(
            1 for (t, ti, g) in current_data
            if t == thu and g == gv_id
        )
        if tiet_trong_ngay >= max_tiet:
            return False

        # 6. Tối đa số tiết liên tiếp
        max_consecutive = config.get("max_consecutive", 4)
        consecutive = 0
        for check_tiet in range(max(1, tiet - max_consecutive), tiet):
            if (thu, check_tiet, gv_id) in current_data:
                consecutive += 1
            else:
                consecutive = 0
        if consecutive >= max_consecutive:
            return False

        # 7. Thể dục không xếp tiết 5 (cuối sáng) hoặc tiết 6 (đầu chiều)
        if mon_id in config.get("pe_subjects", []):
            if tiet in (5, 6):
                return False

        # 8. Môn không lặp lại trong cùng ngày với 1 lớp
        if config.get("no_same_subject_per_day", True):
            for (t, ti, g), (m, l) in current_data.items():
                if t == thu and l == lop_id and m == mon_id:
                    return False

        # 9. Môn học đôi - chỉ chặn khi CÙNG môn CÙNG lớp liền kề
        if mon_id not in config.get("allow_double_subjects", []):
            prev_key = (thu, tiet - 1, gv_id)
            if prev_key in current_data:
                prev_mon_id, prev_lop_id = current_data[prev_key]
                if prev_mon_id == mon_id and prev_lop_id == lop_id:
                    return False

            next_key = (thu, tiet + 1, gv_id)
            if next_key in current_data:
                next_mon_id, next_lop_id = current_data[next_key]
                if next_mon_id == mon_id and next_lop_id == lop_id:
                    return False

        # 10. Không dạy tiết 5 rồi tiết 6 liên tục (nghỉ trưa)
        if config.get("no_consecutive_5_6", True):
            if tiet == 6 and (thu, 5, gv_id) in current_data:
                return False
            if tiet == 5 and (thu, 6, gv_id) in current_data:
                return False

        # 11. Phân bổ đều trong tuần
        if config.get("distribute_evenly", True):
            tiet_per_day = {}
            for (t, ti, g) in current_data:
                if g == gv_id:
                    tiet_per_day[t] = tiet_per_day.get(t, 0) + 1
            if tiet_per_day:
                avg = sum(tiet_per_day.values()) / len(tiet_per_day)
                current_day_count = tiet_per_day.get(thu, 0)
                if current_day_count > avg + 2:
                    return False

        return True

    def _on_cell_double_click(self, item):
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            QMessageBox.information(self, "Gợi ý", "Chọn 1 giáo viên để chỉnh sửa tiết dạy.")
            return

        row = item.row()
        col = item.column()
        thu = col + 2
        tiet = row + 1
        key = (thu, tiet, gv_id)
        cur = self._current_data.get(key, (None, None))
        default_lop_id = cur[1] if cur[1] else None
        self._show_edit_dialog(key, cur, default_lop_id)

    def _show_edit_dialog(self, key, current_data, default_lop_id=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Chỉnh sửa tiết dạy")
        dlg.setMinimumWidth(340)
        layout = QVBoxLayout(dlg)
        form = QFormLayout()
        form.setSpacing(10)

        cmb_mon = QComboBox()
        cmb_mon.addItem("-- Chọn môn --", None)
        for m in self._ds_mon:
            cmb_mon.addItem(f"{m.ma_mon} – {m.ten_mon}", m.id)

        cmb_lop = QComboBox()
        cmb_lop.addItem("-- Chọn lớp --", None)
        for l in self._ds_lop:
            cmb_lop.addItem(l.ten_lop, l.id)

        mon_id, lop_id = current_data
        if mon_id:
            idx = cmb_mon.findData(mon_id)
            if idx >= 0:
                cmb_mon.setCurrentIndex(idx)
        cur_lop = lop_id or default_lop_id
        if cur_lop:
            idx = cmb_lop.findData(cur_lop)
            if idx >= 0:
                cmb_lop.setCurrentIndex(idx)

        form.addRow("Môn học:", cmb_mon)
        form.addRow("Lớp:", cmb_lop)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset)
        btn_box.button(QDialogButtonBox.Reset).setText("🗑 Xóa tiết")
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)

        def xoa():
            self._current_data.pop(key, None)
            dlg.accept()
            self._render_table()

        btn_box.button(QDialogButtonBox.Reset).clicked.connect(xoa)
        layout.addWidget(btn_box)

        if dlg.exec() == QDialog.Accepted:
            m_id = cmb_mon.currentData()
            l_id = cmb_lop.currentData()
            if m_id and l_id:
                self._current_data[key] = (m_id, l_id)
            else:
                self._current_data.pop(key, None)
            self._render_table()

    def _show_context_menu(self, pos):
        gv_id = self.cmb_gv.currentData()
        print(f"Click at: {pos.x()}, {pos.y()}")  # Debug
        
        # Lấy vị trí click
        item = self.table.itemAt(pos)
        
        # Lấy header và cột
        header = self.table.horizontalHeader()
        col = header.logicalIndexAt(pos.x())
        print(f"col: {col}, item: {item}, row: {item.row() if item else -1}")  # Debug
        
        # TH1: Click vào header (cột) - khi col >= 0 và không có item hoặc item.row() == -1
        if col >= 0 and (item is None or item.row() == -1):
            if gv_id:
                self._show_header_menu(col, pos)
            else:
                QMessageBox.information(self, "Hướng dẫn", 
                    "Vui lòng chọn 1 giáo viên cụ thể để cài đặt ngày nghỉ")
            return
        
        # TH2: Click vào ô dữ liệu
        if item and item.row() >= 0 and item.column() >= 0:
            if not gv_id:
                QMessageBox.information(self, "Hướng dẫn", 
                    "Vui lòng chọn 1 giáo viên cụ thể để khóa tiết")
                return
            self._show_cell_menu(item.row(), item.column(), gv_id, pos)

    def _show_header_menu(self, col, pos):
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            return
        
        thu = col + 2
        day = DAYS[col]
        
        # Lấy lịch riêng của giáo viên
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        
        menu = QMenu(self)
        
        is_day_off = not (gv_schedule[thu]["sang"] or gv_schedule[thu]["chieu"])
        is_morning_off = not gv_schedule[thu]["sang"] and gv_schedule[thu]["chieu"]
        is_afternoon_off = gv_schedule[thu]["sang"] and not gv_schedule[thu]["chieu"]
        
        if is_day_off:
            menu.addAction(f"✅ Kích hoạt {day}").triggered.connect(
                lambda: self._toggle_gv_day_off(gv_id, thu, False))
        else:
            menu.addAction(f"🚫 Nghỉ cả ngày {day}").triggered.connect(
                lambda: self._toggle_gv_day_off(gv_id, thu, True))
        
        menu.addSeparator()
        
        if is_morning_off:
            menu.addAction(f"🌅 Kích hoạt buổi sáng {day}").triggered.connect(
                lambda: self._toggle_gv_morning(gv_id, thu, True))
        else:
            menu.addAction(f"🌅 Nghỉ buổi sáng {day}").triggered.connect(
                lambda: self._toggle_gv_morning(gv_id, thu, False))
        
        if is_afternoon_off:
            menu.addAction(f"🌙 Kích hoạt buổi chiều {day}").triggered.connect(
                lambda: self._toggle_gv_afternoon(gv_id, thu, True))
        else:
            menu.addAction(f"🌙 Nghỉ buổi chiều {day}").triggered.connect(
                lambda: self._toggle_gv_afternoon(gv_id, thu, False))
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _show_header_context_menu(self, pos):
        """Menu cho header (cột)"""
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            QMessageBox.information(self, "Hướng dẫn", 
                "Vui lòng chọn 1 giáo viên cụ thể để cài đặt ngày nghỉ")
            return
        
        header = self.table.horizontalHeader()
        col = header.logicalIndexAt(pos.x())
        if col >= 0:
            self._show_header_menu(col, pos)
    def _show_cell_menu(self, row, col, gv_id, pos):
        """Hiển thị menu khi click chuột phải vào ô dữ liệu"""
        thu = col + 2
        tiet = row + 1
        key = (thu, tiet, gv_id)
        
        # Lấy lịch của giáo viên hiện tại
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        
        is_day_off = not (gv_schedule[thu]["sang"] or gv_schedule[thu]["chieu"])
        is_morning_off = not gv_schedule[thu]["sang"] and gv_schedule[thu]["chieu"]
        is_afternoon_off = gv_schedule[thu]["sang"] and not gv_schedule[thu]["chieu"]
        
        # Kiểm tra nếu ngày/buổi đang nghỉ
        if is_day_off:
            menu = QMenu(self)
            menu.addAction(f"⚠️ {DAYS[col]} đang nghỉ").setEnabled(False)
            menu.exec(self.table.viewport().mapToGlobal(pos))
            return
        
        if is_morning_off and tiet <= 5:
            menu = QMenu(self)
            menu.addAction(f"⚠️ Buổi sáng {DAYS[col]} đang nghỉ").setEnabled(False)
            menu.exec(self.table.viewport().mapToGlobal(pos))
            return
        
        if is_afternoon_off and tiet >= 6:
            menu = QMenu(self)
            menu.addAction(f"⚠️ Buổi chiều {DAYS[col]} đang nghỉ").setEnabled(False)
            menu.exec(self.table.viewport().mapToGlobal(pos))
            return
        
        menu = QMenu(self)
        
        if key in self._locked_cells:
            menu.addAction("🔓 Mở khóa tiết này").triggered.connect(lambda: self._toggle_lock(key))
        else:
            menu.addAction("🔒 Khóa tiết này").triggered.connect(lambda: self._toggle_lock(key))
        
        if key in self._current_data:
            menu.addSeparator()
            menu.addAction("🗑 Xóa tiết này").triggered.connect(lambda: self._clear_cell(key))
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _toggle_morning_off(self, thu):
        self._schedule_config[thu]["sang"] = False
        keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] <= 5]
        for key in keys_to_remove:
            self._current_data.pop(key, None)
        self._render_table()

    def _toggle_afternoon_off(self, thu):
        self._schedule_config[thu]["chieu"] = False
        keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] >= 6]
        for key in keys_to_remove:
            self._current_data.pop(key, None)
        self._render_table()

    def _toggle_morning_on(self, thu):
        self._schedule_config[thu]["sang"] = True
        self._render_table()
        QMessageBox.information(self, "Thông báo", f"Đã kích hoạt buổi sáng {DAYS[thu-2]}")

    def _toggle_afternoon_on(self, thu):
        self._schedule_config[thu]["chieu"] = True
        self._render_table()
        QMessageBox.information(self, "Thông báo", f"Đã kích hoạt buổi chiều {DAYS[thu-2]}")

    def _clear_cell(self, key):
        if key in self._current_data:
            del self._current_data[key]
        self._render_table()

    def _toggle_lock(self, key):
        if key in self._locked_cells:
            self._locked_cells.discard(key)
        else:
            self._locked_cells.add(key)
        self._render_table()

    def _lock_selected(self):
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            return
        for item in self.table.selectedItems():
            row = item.row()
            col = item.column()
            key = (col + 2, row + 1, gv_id)
            self._locked_cells.add(key)
        self._render_table()

    def _unlock_selected(self):
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            return
        for item in self.table.selectedItems():
            row = item.row()
            col = item.column()
            key = (col + 2, row + 1, gv_id)
            self._locked_cells.discard(key)
        self._render_table()

    def _toggle_day_off(self, gv_id, thu, is_off):
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        if is_off:
            gv_schedule[thu] = {"sang": False, "chieu": False}
        else:
            gv_schedule[thu] = {"sang": True, "chieu": True}
        
        # Xóa dữ liệu cũ của ngày đó cho GV này
        keys_to_remove = [k for k in self._current_data if k[0] == thu and k[2] == gv_id]
        for key in keys_to_remove:
            self._current_data.pop(key, None)
        
        self._render_table()

    def _toggle_morning(self, gv_id, thu, is_on):
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        gv_schedule[thu]["sang"] = is_on
        
        if not is_on:
            keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] <= 5 and k[2] == gv_id]
            for key in keys_to_remove:
                self._current_data.pop(key, None)
        
        self._render_table()

    def _toggle_afternoon(self, gv_id, thu, is_on):
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        gv_schedule[thu]["chieu"] = is_on
        
        if not is_on:
            keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] >= 6 and k[2] == gv_id]
            for key in keys_to_remove:
                self._current_data.pop(key, None)
        
        self._render_table()

    def _show_schedule_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("📅 Cấu hình lịch học")
        dlg.setMinimumSize(560, 440)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        from PySide6.QtWidgets import QTabWidget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 4px; }
            QTabBar::tab {
                padding: 6px 16px; font-size: 12px;
                background: #F5F5F5; border: 1px solid #DDD;
                border-bottom: none; border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected { background: #1D9E75; color: white; font-weight: 600; }
        """)

        # ─── TAB 1: Lịch chung toàn trường ──────────────────────────
        tab1 = QWidget()
        t1 = QVBoxLayout(tab1)
        t1.setContentsMargins(15, 15, 15, 15)
        t1.setSpacing(10)

        btn_row = QHBoxLayout()
        btn_all_sang = QPushButton("☀️ Chọn tất cả buổi sáng")
        btn_all_sang.setStyleSheet(BTN_STYLE)
        btn_clear_chieu = QPushButton("🌙 Bỏ tất cả buổi chiều")
        btn_clear_chieu.setStyleSheet(BTN_STYLE)
        btn_row.addWidget(btn_all_sang)
        btn_row.addWidget(btn_clear_chieu)
        btn_row.addStretch()
        t1.addLayout(btn_row)

        tbl_chung = QTableWidget()
        tbl_chung.setRowCount(len(DAYS))
        tbl_chung.setColumnCount(3)
        tbl_chung.setHorizontalHeaderLabels(["Thứ", "Sáng", "Chiều"])
        tbl_chung.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl_chung.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tbl_chung.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tbl_chung.verticalHeader().setVisible(False)
        tbl_chung.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl_chung.setSelectionMode(QAbstractItemView.NoSelection)

        for row, day in enumerate(DAYS):
            thu = row + 2
            item = QTableWidgetItem(day)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            tbl_chung.setItem(row, 0, item)

            chk_sang = QTableWidgetItem()
            chk_sang.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_sang.setCheckState(Qt.Checked if self._schedule_config[thu]["sang"] else Qt.Unchecked)
            chk_sang.setTextAlignment(Qt.AlignCenter)
            tbl_chung.setItem(row, 1, chk_sang)

            chk_chieu = QTableWidgetItem()
            chk_chieu.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_chieu.setCheckState(Qt.Checked if self._schedule_config[thu]["chieu"] else Qt.Unchecked)
            chk_chieu.setTextAlignment(Qt.AlignCenter)
            tbl_chung.setItem(row, 2, chk_chieu)

        t1.addWidget(tbl_chung)

        def set_all_sang():
            for row in range(len(DAYS)):
                tbl_chung.item(row, 1).setCheckState(Qt.Checked)

        def clear_all_chieu():
            for row in range(len(DAYS)):
                tbl_chung.item(row, 2).setCheckState(Qt.Unchecked)

        btn_all_sang.clicked.connect(set_all_sang)
        btn_clear_chieu.clicked.connect(clear_all_chieu)
        tabs.addTab(tab1, "🏫 Lịch chung")

        # ─── TAB 2: Lịch từng GV ────────────────────────────────────
        tab2 = QWidget()
        t2 = QVBoxLayout(tab2)
        t2.setContentsMargins(15, 15, 15, 15)
        t2.setSpacing(10)

        gv_row = QHBoxLayout()
        gv_row.addWidget(QLabel("Chọn giáo viên:"))
        cmb_gv_lich = QComboBox()
        cmb_gv_lich.setMinimumWidth(250)
        for gv in self._ds_gv:
            ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
            cmb_gv_lich.addItem(f"{gv.ma_giao_vien} – {ten}", gv.id)

        btn_apply_chung = QPushButton("🔄 Áp dụng lịch chung")
        btn_apply_chung.setStyleSheet(BTN_STYLE)
        btn_apply_chung.setFixedHeight(28)

        btn_apply_all = QPushButton("⚡ Áp dụng cho tất cả GV")
        btn_apply_all.setStyleSheet(BTN_STYLE)
        btn_apply_all.setFixedHeight(28)

        gv_row.addWidget(cmb_gv_lich)
        gv_row.addWidget(btn_apply_chung)
        gv_row.addWidget(btn_apply_all)
        gv_row.addStretch()
        t2.addLayout(gv_row)

        tbl_gv = QTableWidget()
        tbl_gv.setRowCount(len(DAYS))
        tbl_gv.setColumnCount(3)
        tbl_gv.setHorizontalHeaderLabels(["Thứ", "Sáng", "Chiều"])
        tbl_gv.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl_gv.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tbl_gv.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tbl_gv.verticalHeader().setVisible(False)
        tbl_gv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl_gv.setSelectionMode(QAbstractItemView.NoSelection)

        # Khởi tạo các dòng bảng GV
        for row, day in enumerate(DAYS):
            item = QTableWidgetItem(day)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            tbl_gv.setItem(row, 0, item)
            for col in [1, 2]:
                chk = QTableWidgetItem()
                chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                chk.setCheckState(Qt.Unchecked)
                chk.setTextAlignment(Qt.AlignCenter)
                tbl_gv.setItem(row, col, chk)

        # Track GV đang xem để lưu khi chuyển
        current_gv_id = [self._ds_gv[0].id if self._ds_gv else None]

        def _load_gv_lich(gv_id):
            gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
            for row in range(len(DAYS)):
                thu = row + 2
                tbl_gv.item(row, 1).setCheckState(
                    Qt.Checked if gv_schedule[thu]["sang"] else Qt.Unchecked
                )
                tbl_gv.item(row, 2).setCheckState(
                    Qt.Checked if gv_schedule[thu]["chieu"] else Qt.Unchecked
                )

        def _save_current_gv_lich():
            """Lưu lịch GV đang xem vào _gv_schedule_config"""
            gv_id = current_gv_id[0]
            if not gv_id:
                return
            gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
            for row in range(len(DAYS)):
                thu = row + 2
                gv_schedule[thu] = {
                    "sang": tbl_gv.item(row, 1).checkState() == Qt.Checked,
                    "chieu": tbl_gv.item(row, 2).checkState() == Qt.Checked
                }

        def _on_gv_changed():
            # Lưu lịch GV cũ trước khi chuyển
            _save_current_gv_lich()
            # Load lịch GV mới
            new_gv_id = cmb_gv_lich.currentData()
            current_gv_id[0] = new_gv_id
            if new_gv_id:
                _load_gv_lich(new_gv_id)

        def _apply_lich_chung_cho_gv():
            for row in range(len(DAYS)):
                tbl_gv.item(row, 1).setCheckState(tbl_chung.item(row, 1).checkState())
                tbl_gv.item(row, 2).setCheckState(tbl_chung.item(row, 2).checkState())

        def _apply_lich_chung_cho_tat_ca():
            reply = QMessageBox.question(dlg, "Xác nhận",
                "Áp dụng lịch chung cho TẤT CẢ giáo viên?\n"
                "Lịch riêng của từng GV sẽ bị ghi đè!",
                QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            for gv in self._ds_gv:
                self._gv_schedule_config[gv.id] = {
                    thu: {
                        "sang": tbl_chung.item(thu - 2, 1).checkState() == Qt.Checked,
                        "chieu": tbl_chung.item(thu - 2, 2).checkState() == Qt.Checked
                    }
                    for thu in range(2, 8)
                }
            _load_gv_lich(current_gv_id[0])
            QMessageBox.information(dlg, "Thành công", "✅ Đã áp dụng lịch chung cho tất cả GV!")

        cmb_gv_lich.currentIndexChanged.connect(_on_gv_changed)
        btn_apply_chung.clicked.connect(_apply_lich_chung_cho_gv)
        btn_apply_all.clicked.connect(_apply_lich_chung_cho_tat_ca)

        # Load GV đầu tiên
        if self._ds_gv:
            _load_gv_lich(self._ds_gv[0].id)

        t2.addWidget(tbl_gv)

        note = QLabel("🔴 Nghỉ cả ngày  🟠 Nghỉ sáng  🟡 Nghỉ chiều")
        note.setStyleSheet("color:#888; font-size:11px;")
        t2.addWidget(note)

        tabs.addTab(tab2, "👤 Lịch từng GV")
        layout.addWidget(tabs)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setStyleSheet(BTN_PRIMARY)
        btn_box.button(QDialogButtonBox.Cancel).setStyleSheet(BTN_STYLE)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        if dlg.exec() == QDialog.Accepted:
            # Lưu lịch chung
            for row in range(len(DAYS)):
                thu = row + 2
                self._schedule_config[thu] = {
                    "sang": tbl_chung.item(row, 1).checkState() == Qt.Checked,
                    "chieu": tbl_chung.item(row, 2).checkState() == Qt.Checked
                }

            # Lưu lịch GV đang xem cuối cùng
            _save_current_gv_lich()

            self._render_table()
    def _show_constraint_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("⚙️ Cấu hình ràng buộc xếp TKB")
        dlg.setFixedSize(720, 560)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        from PySide6.QtWidgets import QTabWidget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 4px; }
            QTabBar::tab {
                padding: 6px 16px; font-size: 12px;
                background: #F5F5F5; border: 1px solid #DDD;
                border-bottom: none; border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected { background: #1D9E75; color: white; font-weight: 600; }
        """)

        # ─── TAB 1: Giới hạn ───────────────────────────────────────
        tab1 = QWidget()
        t1 = QVBoxLayout(tab1)
        t1.setSpacing(12)
        t1.setContentsMargins(15, 15, 15, 15)

        # Tối đa tiết/ngày
        grp1 = QGroupBox("📊 Số tiết mỗi ngày")
        f1 = QFormLayout(grp1)
        f1.setSpacing(8)
        spin_max_tiet = QSpinBox()
        spin_max_tiet.setRange(1, 10)
        spin_max_tiet.setValue(self._constraint_config.get("max_tiet_ngay", 4))
        spin_max_tiet.setFixedWidth(80)
        f1.addRow("Tối đa số tiết/ngày của 1 GV:", spin_max_tiet)
        t1.addWidget(grp1)

        # Tối đa tiết liên tiếp
        grp2 = QGroupBox("⏱️ Số tiết liên tiếp")
        f2 = QFormLayout(grp2)
        f2.setSpacing(8)
        spin_max_consecutive = QSpinBox()
        spin_max_consecutive.setRange(1, 6)
        spin_max_consecutive.setValue(self._constraint_config.get("max_consecutive", 3))
        spin_max_consecutive.setFixedWidth(80)
        f2.addRow("Tối đa số tiết liên tiếp:", spin_max_consecutive)
        t1.addWidget(grp2)

        # Ràng buộc khác
        grp3 = QGroupBox("🔧 Ràng buộc khác")
        v3 = QVBoxLayout(grp3)
        v3.setSpacing(8)
        chk_no_same = QCheckBox("Môn không lặp lại trong cùng ngày với 1 lớp")
        chk_no_same.setChecked(self._constraint_config.get("no_same_subject_per_day", True))
        chk_no_56 = QCheckBox("Không xếp GV dạy liên tiếp tiết 5 (sáng) → tiết 6 (chiều)")
        chk_no_56.setChecked(self._constraint_config.get("no_consecutive_5_6", True))
        chk_even = QCheckBox("Phân bổ đều số tiết trong tuần")
        chk_even.setChecked(self._constraint_config.get("distribute_evenly", True))

        chk_sang_4 = QCheckBox("Ngày có buổi chiều thì buổi sáng chỉ học 4 tiết (không xếp tiết 5)")
        chk_sang_4.setChecked(self._constraint_config.get("sang_4_tiet_neu_co_chieu", True))

        v3.addWidget(chk_no_same)
        v3.addWidget(chk_no_56)
        v3.addWidget(chk_even)
        v3.addWidget(chk_sang_4)  # ← thêm vào đây
        t1.addWidget(grp3)
        t1.addStretch()
        tabs.addTab(tab1, "📊 Giới hạn")

        # ─── TAB 2: Môn học ────────────────────────────────────────
        tab2 = QWidget()
        t2 = QVBoxLayout(tab2)
        t2.setSpacing(12)
        t2.setContentsMargins(15, 15, 15, 15)

        # Môn học đôi
        grp4 = QGroupBox("✅ Môn được phép học đôi (2 tiết liên tiếp)")
        v4 = QVBoxLayout(grp4)
        scroll4 = QScrollArea()
        scroll4.setWidgetResizable(True)
        scroll4.setFixedHeight(160)
        scroll4.setStyleSheet("QScrollArea { border: none; }")
        w4 = QWidget()
        g4 = QGridLayout(w4)
        g4.setSpacing(6)
        self._double_subject_checkboxes = {}
        for i, mon in enumerate(self._ds_mon):
            cb = QCheckBox(f"{mon.ma_mon} – {mon.ten_mon}")
            cb.setChecked(mon.id in self._constraint_config.get("allow_double_subjects", []))
            self._double_subject_checkboxes[mon.id] = cb
            g4.addWidget(cb, i // 2, i % 2)
        scroll4.setWidget(w4)
        v4.addWidget(scroll4)
        t2.addWidget(grp4)

        # Môn thể dục
        grp5 = QGroupBox("🏃 Môn tránh tiết 5 (buổi sáng) và tiết 1 (buổi chiều)")
        v5 = QVBoxLayout(grp5)
        scroll5 = QScrollArea()
        scroll5.setWidgetResizable(True)
        scroll5.setFixedHeight(130)
        scroll5.setStyleSheet("QScrollArea { border: none; }")
        w5 = QWidget()
        g5 = QGridLayout(w5)
        g5.setSpacing(6)
        self._pe_subject_checkboxes = {}
        pe_mons = self._ds_mon
        if pe_mons:
            for i, mon in enumerate(pe_mons):
                cb = QCheckBox(f"{mon.ma_mon} – {mon.ten_mon}")
                cb.setChecked(mon.id in self._constraint_config.get("pe_subjects", []))
                self._pe_subject_checkboxes[mon.id] = cb
                g5.addWidget(cb, i // 2, i % 2)
        else:
            g5.addWidget(QLabel("Không có môn thể dục trong danh sách"), 0, 0)
        scroll5.setWidget(w5)
        v5.addWidget(scroll5)
        t2.addWidget(grp5)
        t2.addStretch()
        tabs.addTab(tab2, "📚 Môn học")

        # ─── TAB 3: Tiết trống GV ──────────────────────────────────
        tab3 = QWidget()
        t3 = QVBoxLayout(tab3)
        t3.setSpacing(10)
        t3.setContentsMargins(15, 15, 15, 15)

        # Dòng chọn GV + thứ + tiết
        row_add = QHBoxLayout()
        row_add.setSpacing(6)

        cmb_gv = QComboBox()
        cmb_gv.setMinimumWidth(180)
        cmb_gv.addItem("-- Chọn GV --", None)
        for gv in self._ds_gv:
            ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
            cmb_gv.addItem(f"{gv.ma_giao_vien} – {ten}", gv.id)

        cmb_thu = QComboBox()
        cmb_thu.setFixedWidth(80)
        for i, day in enumerate(DAYS):
            cmb_thu.addItem(day, i + 2)

        cmb_tiet = QComboBox()
        cmb_tiet.setFixedWidth(120)
        for t in range(1, 9):
            buoi = "Sáng" if t <= 5 else "Chiều"
            tiet_hien = t if t <= 5 else t - 5
            cmb_tiet.addItem(f"Tiết {tiet_hien} ({buoi})", t)

        btn_add = QPushButton("➕ Thêm")
        btn_add.setStyleSheet(BTN_PRIMARY)
        btn_add.setFixedHeight(28)

        row_add.addWidget(QLabel("GV:"))
        row_add.addWidget(cmb_gv)
        row_add.addWidget(QLabel("Thứ:"))
        row_add.addWidget(cmb_thu)
        row_add.addWidget(QLabel("Tiết:"))
        row_add.addWidget(cmb_tiet)
        row_add.addWidget(btn_add)
        row_add.addStretch()
        t3.addLayout(row_add)

        # Bảng danh sách tiết trống
        self._free_slots_list = QTableWidget()
        self._free_slots_list.setColumnCount(4)
        self._free_slots_list.setHorizontalHeaderLabels(["Giáo viên", "Thứ", "Tiết", ""])
        self._free_slots_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._free_slots_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._free_slots_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._free_slots_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._free_slots_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._free_slots_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._free_slots_list.verticalHeader().setVisible(False)
        self._free_slots_list.setStyleSheet("font-size:12px;")
        self._load_free_slots_to_table()
        t3.addWidget(self._free_slots_list)
        tabs.addTab(tab3, "🚫 Tiết trống GV")

        layout.addWidget(tabs)

        # Nút OK / Cancel
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setStyleSheet(BTN_PRIMARY)
        btn_box.button(QDialogButtonBox.Cancel).setStyleSheet(BTN_STYLE)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        def add_free_slot():
            gv_id = cmb_gv.currentData()
            if not gv_id:
                QMessageBox.warning(dlg, "Lỗi", "Vui lòng chọn giáo viên!")
                return
            thu = cmb_thu.currentData()
            tiet = cmb_tiet.currentData()
            if gv_id not in self._constraint_config["tiet_trong_gv"]:
                self._constraint_config["tiet_trong_gv"][gv_id] = []
            if (thu, tiet) not in self._constraint_config["tiet_trong_gv"][gv_id]:
                self._constraint_config["tiet_trong_gv"][gv_id].append((thu, tiet))
            self._load_free_slots_to_table()

        btn_add.clicked.connect(add_free_slot)

        if dlg.exec() == QDialog.Accepted:
            self._constraint_config["max_tiet_ngay"] = spin_max_tiet.value()
            self._constraint_config["max_consecutive"] = spin_max_consecutive.value()
            self._constraint_config["allow_double_subjects"] = [
                mid for mid, cb in self._double_subject_checkboxes.items() if cb.isChecked()
            ]
            self._constraint_config["pe_subjects"] = [
                mid for mid, cb in self._pe_subject_checkboxes.items() if cb.isChecked()
            ]
            self._constraint_config["no_same_subject_per_day"] = chk_no_same.isChecked()
            self._constraint_config["no_consecutive_5_6"] = chk_no_56.isChecked()
            self._constraint_config["distribute_evenly"] = chk_even.isChecked()
            self._constraint_config["sang_4_tiet_neu_co_chieu"] = chk_sang_4.isChecked()
            QMessageBox.information(self, "Thành công", "✅ Đã cập nhật ràng buộc!")

    def _load_free_slots_to_table(self):
        """Load danh sách tiết trống lên bảng"""
        self._free_slots_list.setRowCount(0)
        row = 0
        for gv_id, slots in self._constraint_config.get("tiet_trong_gv", {}).items():
            gv = next((g for g in self._ds_gv if g.id == gv_id), None)
            gv_name = gv.nguoi_dung.ho_ten if gv and gv.nguoi_dung else "?"
            
            for thu, tiet in slots:
                self._free_slots_list.insertRow(row)
                self._free_slots_list.setItem(row, 0, QTableWidgetItem(gv_name))
                self._free_slots_list.setItem(row, 1, QTableWidgetItem(DAYS[thu - 2]))
                buoi = "Sáng" if tiet <= 5 else "Chiều"
                tiet_hien = tiet if tiet <= 5 else tiet - 5
                self._free_slots_list.setItem(row, 2, QTableWidgetItem(f"Tiết {tiet_hien} ({buoi})"))
                
                btn_del = QPushButton("🗑 Xóa")
                btn_del.clicked.connect(lambda checked, g=gv_id, t=thu, ti=tiet: self._remove_free_slot(g, t, ti))
                self._free_slots_list.setCellWidget(row, 3, btn_del)
                row += 1

    def _remove_free_slot(self, gv_id, thu, tiet):
        """Xóa tiết trống"""
        if gv_id in self._constraint_config["tiet_trong_gv"]:
            if (thu, tiet) in self._constraint_config["tiet_trong_gv"][gv_id]:
                self._constraint_config["tiet_trong_gv"][gv_id].remove((thu, tiet))
            if not self._constraint_config["tiet_trong_gv"][gv_id]:
                del self._constraint_config["tiet_trong_gv"][gv_id]
        self._load_free_slots_to_table()
        self._render_table()

    def _generate(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()
        if not nam_hoc_id or not hoc_ky_id:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn năm học và học kỳ!")
            return

        reply = QMessageBox.question(
            self, "Xác nhận",
            "Sinh TKB sẽ xóa dữ liệu cũ (trừ ô đã khóa). Tiếp tục?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        from core.db.models.phan_cong import PhanCongGiangDay
        from core.db.models.mon_hoc_khoi import MonHocKhoi
        import random

        # Giữ lại dữ liệu đã khóa
        self._current_data = {
            k: v for k, v in self._current_data.items()
            if k in self._locked_cells
        }

        used_gv_slots = set()
        used_lop_slots = set()

        # Khởi tạo used_slots từ dữ liệu đã khóa
        for (thu, tiet, gv_id) in self._current_data:
            used_gv_slots.add((thu, tiet, gv_id))
            lop_id = self._current_data[(thu, tiet, gv_id)][1]
            used_lop_slots.add((thu, tiet, lop_id))

        so_tiet_khong_xep = 0

        for gv in self._ds_gv:
            # Lấy danh sách phân công của GV
            pc_list = self.session.query(PhanCongGiangDay).filter_by(
                giao_vien_id=gv.id,
                nam_hoc_id=nam_hoc_id,
                hoc_ky_id=hoc_ky_id
            ).all()
            if not pc_list:
                continue

            # Xây dựng danh sách (mon_id, lop_id) theo số tiết/tuần
            mon_lop_list = []
            for pc in pc_list:
                lop = pc.lop_hoc
                khoi = lop.khoi if lop else 6
                so_tiet_mon = self.session.query(MonHocKhoi).filter(
                    MonHocKhoi.mon_hoc_id == pc.mon_hoc_id,
                    MonHocKhoi.khoi == khoi
                ).first()
                so_tiet = so_tiet_mon.so_tiet if so_tiet_mon else 1
                for _ in range(so_tiet):
                    mon_lop_list.append((pc.mon_hoc_id, pc.lop_hoc_id))

            random.shuffle(mon_lop_list)

            # Tạo danh sách slot hợp lệ theo lịch của GV
            all_slots = [
                (thu, tiet)
                for thu in range(2, 8)
                for tiet in range(1, 9)
                if self._is_valid_period_for_gv(gv.id, thu, tiet)
            ]

            # Xếp từng tiết
            for mon_id, lop_id in mon_lop_list:
                random.shuffle(all_slots)
                xep_duoc = False
                ly_do_bi_chan = {}

                for thu, tiet in all_slots:
                    gv_key = (thu, tiet, gv.id)
                    lop_key = (thu, tiet, lop_id)

                    if gv_key in used_gv_slots:
                        ly_do_bi_chan["trung_gv"] = ly_do_bi_chan.get("trung_gv", 0) + 1
                        continue
                    if lop_key in used_lop_slots:
                        ly_do_bi_chan["trung_lop"] = ly_do_bi_chan.get("trung_lop", 0) + 1
                        continue

                    assignment = (thu, tiet, gv.id, mon_id, lop_id)
                    if not self._check_constraints(
                        self._current_data, assignment, self._constraint_config
                    ):
                        ly_do_bi_chan["rang_buoc"] = ly_do_bi_chan.get("rang_buoc", 0) + 1
                        continue

                    self._current_data[gv_key] = (mon_id, lop_id)
                    used_gv_slots.add(gv_key)
                    used_lop_slots.add(lop_key)
                    xep_duoc = True
                    break

                if not xep_duoc:
                    mon_name = self._mon_dict.get(mon_id, ("?", "?"))[1]
                    lop_name = self._lop_dict.get(lop_id, "?")
                    gv_name = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
                    print(f"❌ Không xếp được: GV={gv_name} | Môn={mon_name} | Lớp={lop_name} | Lý do: {ly_do_bi_chan}")
                    so_tiet_khong_xep += 1

        self._render_table()

        msg = f"✅ Đã sinh TKB — {len(self._current_data)} tiết."
        if so_tiet_khong_xep > 0:
            msg += f"\n⚠️ Không xếp được {so_tiet_khong_xep} tiết do ràng buộc quá chặt."
        QMessageBox.information(self, "Hoàn tất", msg)

    def _load_existing_timetable(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()
        if not nam_hoc_id or not hoc_ky_id:
            self._render_table()
            return

        from core.db.models.thoi_khoa_bieu import ThoiKhoaBieu
        self._current_data.clear()
        
        for tkb in self.session.query(ThoiKhoaBieu).filter_by(
                nam_hoc_id=nam_hoc_id, hoc_ky_id=hoc_ky_id).all():
            if tkb.tiet_bat_dau <= 8:
                key = (tkb.thu, tkb.tiet_bat_dau, tkb.giao_vien_id)
                self._current_data[key] = (tkb.mon_hoc_id, tkb.lop_hoc_id)

        # Đồng bộ _schedule_config theo dữ liệu thực tế
        for (thu, tiet, gv) in self._current_data:
            if tiet <= 5:
                self._schedule_config[thu]["sang"] = True
            else:
                self._schedule_config[thu]["chieu"] = True

        # Reset lịch riêng GV để khởi tạo lại từ _schedule_config mới
        self._gv_schedule_config.clear()

        self._render_table()

    def _save_all(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()
        if not nam_hoc_id or not hoc_ky_id:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn năm học và học kỳ!")
            return

        from core.db.models.thoi_khoa_bieu import ThoiKhoaBieu
        self.session.query(ThoiKhoaBieu).filter_by(
            nam_hoc_id=nam_hoc_id, hoc_ky_id=hoc_ky_id).delete()

        for (thu, tiet, gv_id), (mon_id, lop_id) in self._current_data.items():
            self.session.add(ThoiKhoaBieu(
                nam_hoc_id=nam_hoc_id, hoc_ky_id=hoc_ky_id,
                giao_vien_id=gv_id, mon_hoc_id=mon_id, lop_hoc_id=lop_id,
                thu=thu, tiet_bat_dau=tiet, so_tiet=1, phong_hoc="",
            ))

        self.session.commit()
        QMessageBox.information(self, "Thành công", f"Đã lưu {len(self._current_data)} tiết.")
    
     # ==================== LỊCH HỌC THEO GIÁO VIÊN ====================
    
    def _load_lich_hoc_cho_gv(self, gv_id):
        """Load lịch học riêng cho 1 giáo viên (ưu tiên lịch riêng, nếu không thì dùng lịch chung)"""
        if gv_id not in self._gv_schedule_config:
            # Khởi tạo từ lịch chung
            self._gv_schedule_config[gv_id] = {
                thu: {"sang": self._schedule_config[thu]["sang"], 
                    "chieu": self._schedule_config[thu]["chieu"]} 
                for thu in range(2, 8)
            }
        return self._gv_schedule_config[gv_id]
    
    def _is_valid_period_for_gv(self, gv_id, thu, tiet):
        """Kiểm tra ngày/thời điểm có học cho 1 giáo viên cụ thể"""
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        cfg = gv_schedule.get(thu)
        if not cfg:
            return False
        if tiet <= 5:
            return cfg.get("sang", False)
        if tiet <= 8:
            return cfg.get("chieu", False)
        return False

    def _toggle_gv_day_off(self, gv_id, thu, is_off):
        """Bật/tắt nghỉ cả ngày cho 1 giáo viên"""
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        if is_off:
            gv_schedule[thu] = {"sang": False, "chieu": False}
        else:
            gv_schedule[thu] = {"sang": True, "chieu": True}
        
        keys_to_remove = [k for k in self._current_data if k[0] == thu and k[2] == gv_id]
        for key in keys_to_remove:
            self._current_data.pop(key, None)
        
        self._render_table()

    def _toggle_gv_morning(self, gv_id, thu, is_on):
        """Bật/tắt buổi sáng cho 1 giáo viên"""
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        gv_schedule[thu]["sang"] = is_on
        
        if not is_on:
            keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] <= 5 and k[2] == gv_id]
            for key in keys_to_remove:
                self._current_data.pop(key, None)
        
        self._render_table()

    def _toggle_gv_afternoon(self, gv_id, thu, is_on):
        """Bật/tắt buổi chiều cho 1 giáo viên"""
        gv_schedule = self._load_lich_hoc_cho_gv(gv_id)
        gv_schedule[thu]["chieu"] = is_on
        
        if not is_on:
            keys_to_remove = [k for k in self._current_data if k[0] == thu and k[1] >= 6 and k[2] == gv_id]
            for key in keys_to_remove:
                self._current_data.pop(key, None)
        
        self._render_table()
    
    def showEvent(self, event):
        """Khi tab được hiển thị, reload dữ liệu từ database"""
        self._load_existing_timetable()
        super().showEvent(event)
    def _find_empty_slot(self, gv_id, exclude_keys=None):
        """Tìm ô trống phù hợp cho GV, tránh các key trong exclude_keys"""
        exclude_keys = exclude_keys or set()
        for thu in range(2, 8):
            for tiet in range(1, 9):
                key = (thu, tiet, gv_id)
                if key in exclude_keys:
                    continue
                if key in self._locked_cells:
                    continue
                if not self._is_valid_period_for_gv(gv_id, thu, tiet):
                    continue
                if key not in self._current_data:
                    return key
        return None

    def _handle_drop(self, src_row, src_col, dst_row, dst_col):
        gv_id = self.cmb_gv.currentData()
        if not gv_id:
            return

        src_thu = src_col + 2
        src_tiet = src_row + 1
        dst_thu = dst_col + 2
        dst_tiet = dst_row + 1

        src_key = (src_thu, src_tiet, gv_id)
        dst_key = (dst_thu, dst_tiet, gv_id)

        if src_key not in self._current_data:
            return

        # 1. Ô đích bị khóa
        if dst_key in self._locked_cells:
            QMessageBox.warning(self, "Không thể di chuyển",
                f"⛔ Ô {DAYS[dst_col]} - Tiết {dst_tiet} đang bị khóa!")
            return

        # 2. Ô đích là ngày/buổi nghỉ
        if not self._is_valid_period_for_gv(gv_id, dst_thu, dst_tiet):
            QMessageBox.warning(self, "Không thể di chuyển",
                f"⛔ {DAYS[dst_col]} không có lịch dạy cho giáo viên này!")
            return

        src_data = self._current_data[src_key]
        src_mon = self._mon_dict.get(src_data[0], ("?", "?"))
        src_lop = self._lop_dict.get(src_data[1], "?")

        # ← THÊM MỚI: 3. Kiểm tra lớp đích có bị trùng với GV khác không
        dst_lop_id = src_data[1]  # Lớp của tiết đang kéo
        conflict_gv_key = None
        for (t, ti, g), (m, l) in self._current_data.items():
            if t == dst_thu and ti == dst_tiet and l == dst_lop_id and g != gv_id:
                conflict_gv_key = (t, ti, g)
                conflict_mon = self._mon_dict.get(m, ("?", "?"))
                conflict_gv = next((gv for gv in self._ds_gv if gv.id == g), None)
                conflict_gv_name = conflict_gv.nguoi_dung.ho_ten if conflict_gv and conflict_gv.nguoi_dung else "?"
                break

        if conflict_gv_key:
            conflict_thu, conflict_tiet, conflict_gv_id = conflict_gv_key
            conflict_lop_id = self._current_data[conflict_gv_key][1]
            
            # Tìm ô trống cho GV kia trước
            empty_for_conflict = self._find_empty_slot(
                conflict_gv_id, 
                exclude_keys={src_key, dst_key, conflict_gv_key}
            )
            
            if not empty_for_conflict:
                QMessageBox.warning(self, "Không thể di chuyển",
                    f"⛔ Không tìm được ô trống cho GV {conflict_gv_name}!\n"
                    f"   Không thể di chuyển tiết này.")
                return
            
            empty_thu, empty_tiet, _ = empty_for_conflict
            
            reply = QMessageBox.question(self, "⚠️ Trùng lịch lớp!",
                f"Lớp {src_lop} vào {DAYS[dst_col]} - Tiết {dst_tiet} đang có:\n"
                f"   👨‍🏫 GV: {conflict_gv_name}\n"
                f"   📚 Môn: {conflict_mon[1]}\n\n"
                f"Tiết của {conflict_gv_name} sẽ được chuyển tự động sang:\n"
                f"   📅 {DAYS[empty_thu-2]} - Tiết {empty_tiet}\n\n"
                f"Bạn có muốn tiếp tục không?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Đẩy GV kia sang ô trống, không xóa
            self._current_data[empty_for_conflict] = self._current_data[conflict_gv_key]
            del self._current_data[conflict_gv_key]

        # --- Ô đích trống: di chuyển thẳng ---
        if dst_key not in self._current_data:
            self._current_data[dst_key] = src_data
            del self._current_data[src_key]
            self._render_table()
            return

        # --- Ô đích có dữ liệu (cùng GV): hỏi xử lý ---
        dst_data = self._current_data[dst_key]
        dst_mon = self._mon_dict.get(dst_data[0], ("?", "?"))
        dst_lop = self._lop_dict.get(dst_data[1], "?")

        gv = next((g for g in self._ds_gv if g.id == gv_id), None)
        gv_name = gv.nguoi_dung.ho_ten if gv and gv.nguoi_dung else "?"

        msg = (
            f"⚠️ Ô đích đang có:\n"
            f"   👨‍🏫 GV: {gv_name}\n"
            f"   📚 Môn: {dst_mon[1]} — Lớp: {dst_lop}\n"
            f"   📅 {DAYS[dst_col]} - Tiết {dst_tiet}\n\n"
            f"Tiết này sẽ được tìm ô trống tự động.\n"
            f"Bạn có muốn tiếp tục không?"
        )

        reply = QMessageBox.question(self, "Xác nhận di chuyển", msg,
                                    QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        empty_slot = self._find_empty_slot(gv_id, exclude_keys={src_key, dst_key})

        if empty_slot:
            self._current_data[empty_slot] = dst_data
            self._current_data[dst_key] = src_data
            del self._current_data[src_key]
            self._render_table()

            empty_thu, empty_tiet, _ = empty_slot
            QMessageBox.information(self, "Hoàn tất",
                f"✅ Đã di chuyển!\n"
                f"   📚 {dst_mon[1]} - {dst_lop} → {DAYS[empty_thu-2]} Tiết {empty_tiet}")
        else:
            reply2 = QMessageBox.question(self, "Không tìm được ô trống",
                f"⚠️ Không tìm được ô trống cho:\n"
                f"   📚 {dst_mon[1]} — Lớp: {dst_lop}\n\n"
                f"Bạn có muốn ghi đè (xóa tiết cũ) không?",
                QMessageBox.Yes | QMessageBox.No)
            if reply2 == QMessageBox.Yes:
                self._current_data[dst_key] = src_data
                del self._current_data[src_key]
                self._render_table()
    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)