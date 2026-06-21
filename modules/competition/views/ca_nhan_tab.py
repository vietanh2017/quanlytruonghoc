# modules/competition/views/ca_nhan_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox, QLabel,
    QPushButton, QFrame, QSplitter, QDialog, QFormLayout, QDialogButtonBox,
    QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QSizePolicy, QMenu,
    QTabWidget, QLineEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont

from modules.competition.service.diem_ca_nhan_service import DiemCaNhanService
from modules.lop_hoc.hoc_sinh_repository import HocSinhRepository
from modules.competition.models.loai_vi_pham import LoaiViPham

TABLE_STYLE = """
    QTableWidget {
        border: 1px solid #DDD;
        gridline-color: #E8E8E8;
        font-size: 12px;
    }
    QHeaderView::section {
        background: #1D9E75; color: white;
        font-weight: 600; font-size: 12px;
        padding: 5px; border: none;
    }
    QTableWidget::item:alternate { background: #F9F9F9; }
    QTableWidget::item:selected { background: #D0EDE4; color: #000; }
"""
BTN_PRIMARY = """
    QPushButton {
        background: #1D9E75; color: white;
        border-radius: 4px; padding: 4px 12px;
        font-size: 12px; font-weight: 600; border: none;
    }
    QPushButton:hover { background: #0F6E56; }
"""
BTN_STYLE = """
    QPushButton {
        background: #F5F5F5; border: 1px solid #DDD;
        border-radius: 4px; padding: 4px 10px;
        font-size: 12px; color: #333;
    }
    QPushButton:hover { background: #E8F5F0; border-color: #1D9E75; color: #1D9E75; }
"""
BTN_DANGER = """
    QPushButton {
        background: #F5F5F5; border: 1px solid #DDD;
        border-radius: 4px; padding: 4px 10px;
        font-size: 12px; color: #E53935;
    }
    QPushButton:hover { background: #FFEBEE; border-color: #E53935; }
"""
BTN_TOGGLE_ACTIVE = """
    QPushButton {
        background: #1D9E75; color: white;
        border: 1px solid #1D9E75; border-radius: 4px;
        padding: 4px 12px; font-size: 12px; font-weight: 600;
    }
"""
BTN_TOGGLE_INACTIVE = """
    QPushButton {
        background: #F5F5F5; color: #555;
        border: 1px solid #CCC; border-radius: 4px;
        padding: 4px 12px; font-size: 12px;
    }
    QPushButton:hover { background: #E8F5F0; border-color: #1D9E75; color: #1D9E75; }
"""

VIEW_CA_NHAN  = "ca_nhan"
VIEW_TOAN_LOP = "toan_lop"


# ══════════════════════════════════════════════════════════════
# DIALOG THÊM / SỬA DANH MỤC (nhỏ gọn, dùng trong Tab 2)
# ══════════════════════════════════════════════════════════════
class DanhMucDialog(QDialog):
    """Dialog nhỏ thêm/sửa một loại vi phạm hoặc thành tích"""

    def __init__(self, parent=None, loai_vp=None, loai_mac_dinh="vi_pham"):
        super().__init__(parent)
        self._loai_vp = loai_vp
        self.setWindowTitle("Sửa danh mục" if loai_vp else "Thêm danh mục mới")
        self.setMinimumWidth(400)
        self._build_ui(loai_mac_dinh)
        if loai_vp:
            self._fill(loai_vp)

    def _build_ui(self, loai_mac_dinh):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.cmb_loai = QComboBox()
        self.cmb_loai.addItem("Vi phạm", "vi_pham")
        self.cmb_loai.addItem("Thành tích", "thanh_tich")
        if loai_mac_dinh == "thanh_tich":
            self.cmb_loai.setCurrentIndex(1)
        self.cmb_loai.currentIndexChanged.connect(self._on_loai_changed)
        form.addRow("Loại:", self.cmb_loai)

        self.cmb_nhom = QComboBox()
        self.cmb_nhom.setEditable(True)
        self._refresh_nhom("vi_pham")
        form.addRow("Nhóm:", self.cmb_nhom)

        self.txt_ten = QLineEdit()
        self.txt_ten.setPlaceholderText("Tên vi phạm / thành tích...")
        form.addRow("Tên:", self.txt_ten)

        self.spin_diem = QDoubleSpinBox()
        self.spin_diem.setRange(-100, 100)
        self.spin_diem.setDecimals(1)
        self.spin_diem.setSuffix(" điểm")
        self.spin_diem.setValue(-2)
        form.addRow("Số điểm:", self.spin_diem)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_ok)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self._on_loai_changed()

    def _refresh_nhom(self, loai):
        self.cmb_nhom.clear()
        if loai == "vi_pham":
            for n in ["Nề nếp", "ATGT", "Đạo đức", "Vệ sinh", "Khác"]:
                self.cmb_nhom.addItem(n)
        else:
            for n in ["Văn nghệ", "Thể thao", "Học tập", "Phong trào", "Khác"]:
                self.cmb_nhom.addItem(n)

    def _on_loai_changed(self):
        loai = self.cmb_loai.currentData()
        self._refresh_nhom(loai)
        if loai == "vi_pham" and self.spin_diem.value() > 0:
            self.spin_diem.setValue(-2)
        elif loai == "thanh_tich" and self.spin_diem.value() < 0:
            self.spin_diem.setValue(5)

    def _fill(self, obj):
        idx = self.cmb_loai.findData(obj.loai)
        if idx >= 0:
            self.cmb_loai.setCurrentIndex(idx)
        idx_n = self.cmb_nhom.findText(obj.nhom or "")
        if idx_n >= 0:
            self.cmb_nhom.setCurrentIndex(idx_n)
        else:
            self.cmb_nhom.setCurrentText(obj.nhom or "")
        self.txt_ten.setText(obj.ten_loi or "")
        self.spin_diem.setValue(float(obj.so_diem or 0))

    def _on_ok(self):
        if not self.txt_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên!")
            return
        self.accept()

    def get_data(self):
        return {
            "loai":    self.cmb_loai.currentData(),
            "nhom":    self.cmb_nhom.currentText().strip(),
            "ten_loi": self.txt_ten.text().strip(),
            "so_diem": self.spin_diem.value(),
        }


# ══════════════════════════════════════════════════════════════
# DIALOG CHÍNH: THÊM VI PHẠM / THÀNH TÍCH  (2 tab)
# ══════════════════════════════════════════════════════════════
class ThemViPhamDialog(QDialog):
    """Dialog thêm vi phạm/thành tích — Tab 1: Ghi nhận | Tab 2: Danh mục"""

    def __init__(self, hoc_sinh, loai_vp_list, session, parent=None):
        super().__init__(parent)
        self.hoc_sinh     = hoc_sinh
        self.loai_vp_list = list(loai_vp_list)   # copy để có thể append
        self._session     = session
        self.setWindowTitle(f"Vi phạm/thành tích — {hoc_sinh.ho_ten}")
        self.setMinimumWidth(520)
        self.setMinimumHeight(480)
        self._build_ui()

    # ── Build UI ─────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_ghi_nhan(), "📝 Ghi nhận")
        self.tabs.addTab(self._build_tab_danh_muc(), "⚙️ Danh mục")
        layout.addWidget(self.tabs)

        # Nút OK/Cancel chỉ hoạt động ở Tab Ghi nhận
        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)

        self.tabs.currentChanged.connect(self._on_tab_changed)
        self._load_loai_vp()
        self._on_loai_changed()

    def _build_tab_ghi_nhan(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(5, 8, 5, 0)
        form = QFormLayout()
        form.setSpacing(10)

        lbl_hs = QLabel(f"{self.hoc_sinh.ho_ten} ({self.hoc_sinh.ma_hoc_sinh})")
        lbl_hs.setStyleSheet("font-weight:bold; color:#1D9E75;")
        form.addRow("Học sinh:", lbl_hs)

        self.cmb_loai = QComboBox()
        self.cmb_loai.addItem("Vi phạm", "vi_pham")
        self.cmb_loai.addItem("Thành tích", "thanh_tich")
        self.cmb_loai.currentIndexChanged.connect(self._on_loai_changed)
        form.addRow("Loại:", self.cmb_loai)

        self.cmb_loi = QComboBox()
        self.cmb_loi.setEditable(True)
        self.cmb_loi.currentIndexChanged.connect(self._on_loi_changed)
        form.addRow("Lỗi/Thành tích:", self.cmb_loi)

        self.spin_diem = QSpinBox()
        self.spin_diem.setRange(-100, 100)
        self.spin_diem.setSuffix(" điểm")
        form.addRow("Số điểm:", self.spin_diem)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form.addRow("Ngày:", self.date_edit)

        self.cmb_tiet = QComboBox()
        for i in range(1, 9):
            buoi    = "Sáng" if i <= 5 else "Chiều"
            tiet_hien = i if i <= 5 else i - 5
            self.cmb_tiet.addItem(f"Tiết {tiet_hien} ({buoi})", i)
        self.cmb_tiet.addItem("Ngoài giờ", 0)
        form.addRow("Tiết:", self.cmb_tiet)

        self.txt_nguoi_ghi = QTextEdit()
        self.txt_nguoi_ghi.setMaximumHeight(55)
        self.txt_nguoi_ghi.setPlaceholderText("Ví dụ: Cô giáo chủ nhiệm, Sao đỏ, Tổng phụ trách...")
        form.addRow("Người ghi nhận:", self.txt_nguoi_ghi)

        self.txt_ghi_chu = QTextEdit()
        self.txt_ghi_chu.setMaximumHeight(70)
        self.txt_ghi_chu.setPlaceholderText("Mô tả chi tiết sự việc...")
        form.addRow("Mô tả:", self.txt_ghi_chu)

        layout.addLayout(form)
        layout.addStretch()
        return w

    def _build_tab_danh_muc(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(5, 8, 5, 0)
        layout.setSpacing(6)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(6)

        self.cmb_dm_filter = QComboBox()
        self.cmb_dm_filter.addItem("Tất cả", "all")
        self.cmb_dm_filter.addItem("Vi phạm", "vi_pham")
        self.cmb_dm_filter.addItem("Thành tích", "thanh_tich")
        self.cmb_dm_filter.currentIndexChanged.connect(self._render_danh_muc)
        tb.addWidget(self.cmb_dm_filter)
        tb.addStretch()

        btn_them_vp = QPushButton("➕ Vi phạm")
        btn_them_vp.setStyleSheet(BTN_STYLE)
        btn_them_vp.setFixedHeight(28)
        btn_them_vp.clicked.connect(lambda: self._dm_them("vi_pham"))

        btn_them_tt = QPushButton("⭐ Thành tích")
        btn_them_tt.setStyleSheet(BTN_PRIMARY)
        btn_them_tt.setFixedHeight(28)
        btn_them_tt.clicked.connect(lambda: self._dm_them("thanh_tich"))

        self.btn_dm_sua = QPushButton("✏️ Sửa")
        self.btn_dm_sua.setStyleSheet(BTN_STYLE)
        self.btn_dm_sua.setFixedHeight(28)
        self.btn_dm_sua.setEnabled(False)
        self.btn_dm_sua.clicked.connect(self._dm_sua)

        self.btn_dm_an = QPushButton("🙈 Ẩn")
        self.btn_dm_an.setStyleSheet(BTN_DANGER)
        self.btn_dm_an.setFixedHeight(28)
        self.btn_dm_an.setEnabled(False)
        self.btn_dm_an.clicked.connect(self._dm_an)

        tb.addWidget(btn_them_vp)
        tb.addWidget(btn_them_tt)
        tb.addWidget(self.btn_dm_sua)
        tb.addWidget(self.btn_dm_an)
        layout.addLayout(tb)

        # Bảng danh mục
        self.tbl_dm = QTableWidget()
        headers = ["Nhóm", "Tên vi phạm / thành tích", "Điểm", "Loại", ""]
        self.tbl_dm.setColumnCount(len(headers))
        self.tbl_dm.setHorizontalHeaderLabels(headers)
        self.tbl_dm.setColumnWidth(0, 90)
        self.tbl_dm.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_dm.setColumnWidth(2, 60)
        self.tbl_dm.setColumnWidth(3, 75)
        self.tbl_dm.setColumnWidth(4, 35)
        self.tbl_dm.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_dm.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_dm.setAlternatingRowColors(True)
        self.tbl_dm.verticalHeader().setVisible(False)
        self.tbl_dm.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tbl_dm.setStyleSheet(TABLE_STYLE)
        self.tbl_dm.itemSelectionChanged.connect(self._dm_on_selection)
        self.tbl_dm.doubleClicked.connect(self._dm_sua)
        layout.addWidget(self.tbl_dm, stretch=1)

        self.lbl_dm_status = QLabel("")
        self.lbl_dm_status.setStyleSheet("color:#666; font-size:11px;")
        layout.addWidget(self.lbl_dm_status)

        return w

    # ── Tab Ghi nhận ─────────────────────────────
    def _load_loai_vp(self):
        self.cmb_loi.blockSignals(True)
        self.cmb_loi.clear()
        loai = self.cmb_loai.currentData()
        for item in self.loai_vp_list:
            if item.loai == loai and item.is_active:
                display = f"{item.ten_loi} ({'+' if item.so_diem > 0 else ''}{item.so_diem:.1f} điểm)"
                self.cmb_loi.addItem(display, item.id)
        self.cmb_loi.blockSignals(False)
        self._on_loi_changed()

    def _on_loai_changed(self):
        self._load_loai_vp()

    def _on_loi_changed(self):
        loai_id = self.cmb_loi.currentData()
        for item in self.loai_vp_list:
            if item.id == loai_id:
                self.spin_diem.setValue(int(item.so_diem))
                break

    def _on_tab_changed(self, idx):
        # Nút OK chỉ hiện ở Tab Ghi nhận
        self.btn_box.setVisible(idx == 0)

    def get_data(self):
        loai_vp_id = self.cmb_loi.currentData()
        loai_vp = next((x for x in self.loai_vp_list if x.id == loai_vp_id), None)
        return {
            'loai_vi_pham_id': loai_vp_id,
            'loai':            self.cmb_loai.currentData(),
            'ten_loi':         loai_vp.ten_loi if loai_vp else "",
            'so_diem':         self.spin_diem.value(),
            'ngay_xay_ra':     self.date_edit.date().toPython(),
            'tiet':            self.cmb_tiet.currentData(),
            'nguoi_ghi_nhan':  self.txt_nguoi_ghi.toPlainText(),
            'mo_ta':           self.txt_ghi_chu.toPlainText(),
        }

    # ── Tab Danh mục ─────────────────────────────
    def _render_danh_muc(self):
        loai = self.cmb_dm_filter.currentData()
        ds = [
            x for x in self.loai_vp_list
            if loai == "all" or x.loai == loai
        ]
        ds.sort(key=lambda x: (x.nhom or "", x.thu_tu or 0))

        self.tbl_dm.setRowCount(len(ds))
        COLOR_VP = QColor("#FFE5E5")
        COLOR_TT = QColor("#E8F5E9")
        COLOR_OFF = QColor("#F5F5F5")

        for row, item in enumerate(ds):
            bg = COLOR_OFF if not item.is_active else (
                COLOR_VP if item.loai == "vi_pham" else COLOR_TT
            )

            def cell(text, align=Qt.AlignCenter, obj=item):
                c = QTableWidgetItem(str(text))
                c.setTextAlignment(align)
                c.setData(Qt.UserRole, obj.id)
                if not obj.is_active:
                    c.setForeground(QColor("#AAAAAA"))
                return c

            self.tbl_dm.setItem(row, 0, cell(item.nhom or ""))
            ten = cell(item.ten_loi or "", Qt.AlignLeft | Qt.AlignVCenter)
            if not item.is_active:
                f = QFont(); f.setItalic(True); ten.setFont(f)
            self.tbl_dm.setItem(row, 1, ten)

            diem = item.so_diem or 0
            d = cell(f"{'+' if diem > 0 else ''}{diem:.1f}")
            if item.is_active:
                d.setForeground(QColor("#CC0000") if diem < 0 else QColor("#2E7D32"))
            self.tbl_dm.setItem(row, 2, d)

            self.tbl_dm.setItem(row, 3, cell(
                "Vi phạm" if item.loai == "vi_pham" else "Thành tích"
            ))
            self.tbl_dm.setItem(row, 4, cell("✅" if item.is_active else "🙈"))

            for col in range(self.tbl_dm.columnCount()):
                c = self.tbl_dm.item(row, col)
                if c:
                    c.setBackground(bg)

        vp = sum(1 for x in ds if x.loai == "vi_pham")
        tt = sum(1 for x in ds if x.loai == "thanh_tich")
        self.lbl_dm_status.setText(f"{len(ds)} mục  |  🔴 VP: {vp}  |  🟢 TT: {tt}")
        self._dm_update_buttons()

    def _dm_on_selection(self):
        self._dm_update_buttons()

    def _dm_update_buttons(self):
        row = self.tbl_dm.currentRow()
        has = row >= 0 and len(self.tbl_dm.selectedItems()) > 0
        self.btn_dm_sua.setEnabled(has)
        self.btn_dm_an.setEnabled(has)
        if has:
            obj = self._dm_get_selected()
            self.btn_dm_an.setText("👁 Hiện" if obj and not obj.is_active else "🙈 Ẩn")

    def _dm_get_selected(self):
        row = self.tbl_dm.currentRow()
        item = self.tbl_dm.item(row, 0)
        if not item:
            return None
        obj_id = item.data(Qt.UserRole)
        return next((x for x in self.loai_vp_list if x.id == obj_id), None)

    def _gen_ma(self, loai: str) -> str:
        """Sinh mã tự động VP hoặc TT + số tiếp theo chưa dùng"""
        prefix = "VP" if loai == "vi_pham" else "TT"
        
        # Lấy tất cả mã hiện có
        all_codes = self._session.query(LoaiViPham.ma_loi).all()
        existing_numbers = []
        
        for (code,) in all_codes:
            if code and code.startswith(prefix):
                try:
                    num = int(code[len(prefix):])
                    existing_numbers.append(num)
                except:
                    pass
        
        # Tìm số nhỏ nhất còn trống
        num = 1
        while num in existing_numbers:
            num += 1
        
        return f"{prefix}{num:03d}"

    def _dm_them(self, loai_mac_dinh):
        dlg = DanhMucDialog(self, loai_mac_dinh=loai_mac_dinh)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            from modules.competition.models.loai_vi_pham import LoaiViPham
            obj = LoaiViPham(
                ma_loi    = self._gen_ma(data["loai"]),
                ten_loi   = data["ten_loi"],
                loai      = data["loai"],
                nhom      = data["nhom"],
                so_diem   = data["so_diem"],
                thu_tu    = len(self.loai_vp_list),
                is_active = True,
            )
            self._session.add(obj)
            self._session.commit()
            self._session.refresh(obj)
            self.loai_vp_list.append(obj)
            self._render_danh_muc()
            # Cập nhật lại combobox Tab 1
            self._load_loai_vp()
            QMessageBox.information(self, "Thành công", f"Đã thêm: {obj.ten_loi}")
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def _dm_sua(self):
        obj = self._dm_get_selected()
        if not obj:
            return
        dlg = DanhMucDialog(self, loai_vp=obj)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            obj.loai    = data["loai"]
            obj.nhom    = data["nhom"]
            obj.ten_loi = data["ten_loi"]
            obj.so_diem = data["so_diem"]
            self._session.commit()
            self._render_danh_muc()
            self._load_loai_vp()
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def _dm_an(self):
        obj = self._dm_get_selected()
        if not obj:
            return
        new_state = not obj.is_active
        action = "hiện" if new_state else "ẩn"
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn muốn {action} mục «{obj.ten_loi}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            obj.is_active = new_state
            self._session.commit()
            self._render_danh_muc()
            self._load_loai_vp()
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def showEvent(self, event):
        """Render danh mục lần đầu khi dialog mở"""
        super().showEvent(event)
        self._render_danh_muc()


# ══════════════════════════════════════════════════════════════
# CaNhanTab — giữ nguyên, chỉ sửa chỗ gọi ThemViPhamDialog
# ══════════════════════════════════════════════════════════════
class CaNhanTab(QWidget):
    COLOR_TOP1     = QColor("#FFD700")
    COLOR_TOP2     = QColor("#C0C0C0")
    COLOR_TOP3     = QColor("#CD7F32")
    COLOR_NEGATIVE = QColor("#FFE5E5")
    COLOR_POSITIVE = QColor("#E8F5E9")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc      = DiemCaNhanService()
        self.hs_repo  = HocSinhRepository(self.svc.session)
        # Thêm biến flag vào __init__
        self._cell_clicked_connected = False
        self._current_nam_hoc_id = None
        self._current_lop_id     = None
        self._current_tuan       = None
        self._ds_hoc_sinh        = []
        self._view_mode          = VIEW_CA_NHAN

        self._build_ui()
        self._load_nam_hoc()
        self._load_loai_vi_pham()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc)
        filter_layout.addWidget(QLabel("Tuần:"))
        self.cmb_tuan = QComboBox()
        self.cmb_tuan.setMinimumWidth(100)
        for i in range(1, 36):
            self.cmb_tuan.addItem(f"Tuần {i}", i)
        filter_layout.addWidget(self.cmb_tuan)
        filter_layout.addWidget(QLabel("Lớp:"))
        self.cmb_lop = QComboBox()
        self.cmb_lop.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_lop)
        self.btn_load = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(self.btn_load)
        filter_layout.addStretch()
        self.btn_add = QPushButton("➕ Thêm vi phạm/thành tích")
        self.btn_add.setStyleSheet("background:#1D9E75; color:white; font-weight:bold;")
        filter_layout.addWidget(self.btn_add)
        layout.addLayout(filter_layout)
        # Trong filter_layout, sau nút btn_add
        self.btn_tap_the = QPushButton("🏫 Vi phạm tập thể")
        self.btn_tap_the.setStyleSheet(BTN_STYLE)
        self.btn_tap_the.clicked.connect(self._on_tap_the)
        filter_layout.addWidget(self.btn_tap_the)

        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        self.status_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(self.status_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #E0E0E0; width: 1px; }")

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        left_layout.setSpacing(5)
        lbl_left_title = QLabel("📋 DANH SÁCH HỌC SINH")
        lbl_left_title.setStyleSheet("font-weight:bold; color:#1D9E75; padding:5px 0;")
        left_layout.addWidget(lbl_left_title)
        self.table = QTableWidget()
        self._setup_table()
        left_layout.addWidget(self.table)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(6)

        right_header = QHBoxLayout()
        right_header.setSpacing(8)
        lbl_stats_title = QLabel("📊 THỐNG KÊ VI PHẠM / THÀNH TÍCH")
        lbl_stats_title.setStyleSheet("font-weight:bold; color:#1D9E75; padding:5px 0;")
        right_header.addWidget(lbl_stats_title)
        right_header.addStretch()
        self.btn_view_ca_nhan = QPushButton("👤 Cá nhân")
        self.btn_view_ca_nhan.setFixedHeight(26)
        self.btn_view_ca_nhan.clicked.connect(lambda: self._switch_view(VIEW_CA_NHAN))
        self.btn_view_toan_lop = QPushButton("📋 Toàn lớp")
        self.btn_view_toan_lop.setFixedHeight(26)
        self.btn_view_toan_lop.clicked.connect(lambda: self._switch_view(VIEW_TOAN_LOP))
        right_header.addWidget(self.btn_view_ca_nhan)
        right_header.addWidget(self.btn_view_toan_lop)
        right_layout.addLayout(right_header)

        self.lbl_hs_info = QLabel("🏠 Chọn học sinh để xem chi tiết")
        self.lbl_hs_info.setStyleSheet("font-weight:bold; font-size:12px; color:#1D9E75; padding:3px 0;")
        right_layout.addWidget(self.lbl_hs_info)

        self.lbl_detail_title = QLabel("📜 LỊCH SỬ VI PHẠM / THÀNH TÍCH")
        self.lbl_detail_title.setStyleSheet("font-weight:bold; color:#555; margin-top:2px;")
        right_layout.addWidget(self.lbl_detail_title)

        self.table_detail = QTableWidget()
        self._setup_detail_table_ca_nhan()
        self.table_detail.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_detail.customContextMenuRequested.connect(self._show_detail_context_menu)
        right_layout.addWidget(self.table_detail, stretch=1)

        self.lbl_tong_diem = QLabel("🏆 Tổng điểm: 0  |  📉 Vi phạm: 0  |  📈 Thành tích: 0")
        self.lbl_tong_diem.setStyleSheet("font-weight:bold; font-size:12px; padding:4px 0; color:#333;")
        self.lbl_tong_diem.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.lbl_tong_diem)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([520, 400])
        layout.addWidget(splitter, stretch=1)

        self.btn_load.clicked.connect(self._on_load)
        self.btn_add.clicked.connect(self._on_add)
        self.table.itemSelectionChanged.connect(self._on_select_hoc_sinh)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._load_lop)
        self._refresh_toggle_style()

    def _setup_table(self):
        headers = ["STT", "Mã HS", "Họ tên", "Điểm TD", "Số lần VP", "Số lần TT", "Xếp thứ"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 138)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 70)
        self.table.setColumnWidth(6, 65)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setStyleSheet(TABLE_STYLE)

    def _setup_detail_table_ca_nhan(self):
        headers = ["STT", "Ngày", "Lỗi/TT", "Điểm", "Người ghi nhận"]
        self.table_detail.setColumnCount(len(headers))
        self.table_detail.setHorizontalHeaderLabels(headers)
        self.table_detail.setColumnWidth(0, 40)
        self.table_detail.setColumnWidth(1, 90)
        self.table_detail.setColumnWidth(2, 200)
        self.table_detail.setColumnWidth(3, 60)
        self.table_detail.setColumnWidth(4, 150)
        self._apply_detail_table_base()

    def _setup_detail_table_toan_lop(self):
        self._apply_detail_table_base()   # ← gọi trước

        headers = ["STT", "Học sinh", "Ngày", "Lỗi/TT", "Điểm", ""]
        self.table_detail.setColumnCount(len(headers))
        self.table_detail.setHorizontalHeaderLabels(headers)

        header = self.table_detail.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # ← Lỗi/TT co giãn
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setStretchLastSection(False)                   # ← tắt stretch cột cuối

        self.table_detail.setColumnWidth(0, 35)
        self.table_detail.setColumnWidth(1, 140)
        self.table_detail.setColumnWidth(2, 85)
        self.table_detail.setColumnWidth(4, 50)
        self.table_detail.setColumnWidth(5, 30)   # ← cột X nhỏ gọn
        try:
            self.table_detail.cellClicked.disconnect(self._on_cell_clicked)
        except (RuntimeError, TypeError):
            pass
        self.table_detail.cellClicked.connect(self._on_cell_clicked)
        # Trong _setup_detail_table_toan_lop
        if self._cell_clicked_connected:
            self.table_detail.cellClicked.disconnect(self._on_cell_clicked)
        self.table_detail.cellClicked.connect(self._on_cell_clicked)
        self._cell_clicked_connected = True
    def _apply_detail_table_base(self):
        self.table_detail.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_detail.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_detail.setAlternatingRowColors(True)
        self.table_detail.verticalHeader().setVisible(False)
        self.table_detail.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        # ← bỏ setStretchLastSection(True)
        self.table_detail.setStyleSheet(TABLE_STYLE)

    def _switch_view(self, mode):
        if self._view_mode == mode:
            return
        self._view_mode = mode
        self._refresh_toggle_style()
        if mode == VIEW_CA_NHAN:
            self._setup_detail_table_ca_nhan()
            self.lbl_hs_info.setText("🏠 Chọn học sinh để xem chi tiết")
            self.lbl_tong_diem.setText("🏆 Tổng điểm: 0  |  📉 Vi phạm: 0  |  📈 Thành tích: 0")
            self.table_detail.setRowCount(0)
        else:
            self._setup_detail_table_toan_lop()
            self._render_detail_toan_lop()

    def _refresh_toggle_style(self):
        if self._view_mode == VIEW_CA_NHAN:
            self.btn_view_ca_nhan.setStyleSheet(BTN_TOGGLE_ACTIVE)
            self.btn_view_toan_lop.setStyleSheet(BTN_TOGGLE_INACTIVE)
        else:
            self.btn_view_ca_nhan.setStyleSheet(BTN_TOGGLE_INACTIVE)
            self.btn_view_toan_lop.setStyleSheet(BTN_TOGGLE_ACTIVE)

    def _load_nam_hoc(self):
        try:
            from core.db.models.nam_hoc import NamHoc
            from core.db.session import SessionLocal
            session = SessionLocal()
            nam_hocs = session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all()
            for nh in nam_hocs:
                self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
            session.close()
            if self.cmb_nam_hoc.count() > 0:
                self.cmb_nam_hoc.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải năm học: {e}")

    def _load_lop(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if not nam_hoc_id:
            return
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if result.ok:
            self.cmb_lop.clear()
            self.cmb_lop.addItem("-- Chọn lớp --", None)
            for lop in result.data:
                self.cmb_lop.addItem(lop.ten_lop, lop.id)

    def _load_loai_vi_pham(self):
        self.loai_vp_list = self.svc.get_loai_vi_pham()

    def _on_load(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        lop_id     = self.cmb_lop.currentData()
        tuan       = self.cmb_tuan.currentData()
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        if not lop_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn lớp!")
            return
        self._current_nam_hoc_id = nam_hoc_id
        self._current_lop_id     = lop_id
        self._current_tuan       = tuan
        result = self.svc.get_ds_hoc_sinh_theo_lop(lop_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        self._ds_hoc_sinh = result.data or []
        self.table_detail.setRowCount(0)
        self.lbl_hs_info.setText("🏠 Chọn học sinh để xem chi tiết")
        self.lbl_tong_diem.setText("🏆 Tổng điểm: 0  |  📉 Vi phạm: 0  |  📈 Thành tích: 0")
        if not self._ds_hoc_sinh:
            QMessageBox.warning(self, "Thông báo", "Lớp không có học sinh nào!")
            self.table.setRowCount(0)
            self.status_label.setText(f"📚 Lớp: {self.cmb_lop.currentText()} | Tuần {tuan} | 0 học sinh")
            return
        self._render_table()
        self.status_label.setText(f"📚 Lớp: {self.cmb_lop.currentText()} | Tuần {tuan} | {len(self._ds_hoc_sinh)} học sinh")
        if self._view_mode == VIEW_TOAN_LOP:
            self._render_detail_toan_lop()

    def _render_table(self):
        self.table.setRowCount(len(self._ds_hoc_sinh))
        diem_dict = {}
        for hs in self._ds_hoc_sinh:
            result = self.svc.get_tong_diem_ca_nhan(hs.id, self._current_nam_hoc_id, self._current_tuan)
            diem_dict[hs.id] = result.data if result.ok else 0
        sorted_hs = sorted(self._ds_hoc_sinh, key=lambda x: diem_dict.get(x.id, 0), reverse=True)
        rank_map = {}
        rank = 1
        for i, hs in enumerate(sorted_hs):
            if i > 0 and diem_dict.get(hs.id, 0) < diem_dict.get(sorted_hs[i-1].id, 0):
                rank = i + 1
            rank_map[hs.id] = rank
        for row, hs in enumerate(self._ds_hoc_sinh):
            diem = diem_dict.get(hs.id, 0)
            rank = rank_map.get(hs.id, 0)
            item = QTableWidgetItem(str(row + 1)); item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)
            item = QTableWidgetItem(hs.ma_hoc_sinh or ""); item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item)
            self.table.setItem(row, 2, QTableWidgetItem(hs.ho_ten or ""))
            item = QTableWidgetItem(f"{diem:.1f}"); item.setTextAlignment(Qt.AlignCenter)
            if diem < 0:
                item.setBackground(self.COLOR_NEGATIVE); item.setForeground(QColor("#CC0000"))
            elif diem > 0:
                item.setBackground(self.COLOR_POSITIVE); item.setForeground(QColor("#2E7D32"))
            self.table.setItem(row, 3, item)
            result_ct = self.svc.get_chi_tiet_vi_pham(hs.id, self._current_nam_hoc_id, self._current_tuan)
            ds_vp = result_ct.data if result_ct.ok else []
            so_vp = sum(1 for vp in ds_vp if vp.so_diem < 0)
            so_tt = sum(1 for vp in ds_vp if vp.so_diem >= 0)
            item = QTableWidgetItem(str(so_vp)); item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item)
            item = QTableWidgetItem(str(so_tt)); item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, item)
            item = QTableWidgetItem(str(rank) if rank > 0 else "---"); item.setTextAlignment(Qt.AlignCenter)
            if rank == 1:
                item.setBackground(self.COLOR_TOP1); item.setFont(QFont("Arial", 9, QFont.Bold))
            elif rank == 2:
                item.setBackground(self.COLOR_TOP2); item.setFont(QFont("Arial", 9, QFont.Bold))
            elif rank == 3:
                item.setBackground(self.COLOR_TOP3); item.setFont(QFont("Arial", 9, QFont.Bold))
            self.table.setItem(row, 6, item)

    def _on_select_hoc_sinh(self):
        if self._view_mode != VIEW_CA_NHAN:
            return
        row = self.table.currentRow()
        if row < 0 or row >= len(self._ds_hoc_sinh):
            return
        hs = self._ds_hoc_sinh[row]
        self.lbl_hs_info.setText(f"👤 {hs.ho_ten} ({hs.ma_hoc_sinh})")
        result = self.svc.get_chi_tiet_vi_pham(hs.id, self._current_nam_hoc_id, self._current_tuan)
        if not result.ok:
            self.table_detail.setRowCount(0)
            self.lbl_tong_diem.setText("🏆 Tổng điểm: 0  |  📉 Vi phạm: 0  |  📈 Thành tích: 0")
            return
        ds_vp = result.data or []
        self._fill_detail_ca_nhan(ds_vp)
        so_vp = sum(1 for vp in ds_vp if vp.so_diem < 0)
        so_tt = sum(1 for vp in ds_vp if vp.so_diem >= 0)
        for col, val in ((4, so_vp), (5, so_tt)):
            item = self.table.item(row, col)
            if item:
                item.setText(str(val))

    def _fill_detail_ca_nhan(self, ds_vp):
        self.table_detail.setRowCount(len(ds_vp))
        tong_diem = so_vp = so_tt = 0
        for idx, vp in enumerate(ds_vp):
            item = QTableWidgetItem(str(idx + 1)); item.setTextAlignment(Qt.AlignCenter)
            item.setData(Qt.UserRole, vp.id); self.table_detail.setItem(idx, 0, item)
            ngay = vp.ngay_xay_ra.strftime("%d/%m/%Y") if vp.ngay_xay_ra else ""
            item = QTableWidgetItem(ngay); item.setTextAlignment(Qt.AlignCenter)
            self.table_detail.setItem(idx, 1, item)
            ten_loi = vp.loai_vi_pham.ten_loi if vp.loai_vi_pham else ""
            self.table_detail.setItem(idx, 2, QTableWidgetItem(ten_loi))
            diem = vp.so_diem
            item = QTableWidgetItem(f"{diem:.1f}"); item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(self.COLOR_NEGATIVE if diem < 0 else self.COLOR_POSITIVE)
            item.setForeground(QColor("#CC0000") if diem < 0 else QColor("#2E7D32"))
            self.table_detail.setItem(idx, 3, item)
            self.table_detail.setItem(idx, 4, QTableWidgetItem(vp.nguoi_ghi_nhan or ""))
            tong_diem += diem
            if diem < 0: so_vp += 1
            else:         so_tt += 1
        self.lbl_tong_diem.setText(
            f"🏆 Tổng điểm: {tong_diem:.1f}  |  📉 Vi phạm: {so_vp}  |  📈 Thành tích: {so_tt}"
        )

    def _render_detail_toan_lop(self):
        """Hiển thị tất cả vi phạm của lớp (cá nhân + tập thể)"""
        if not self._current_lop_id or not self._current_nam_hoc_id:
            return
        
        all_rows = []
        
        # 1. Vi phạm cá nhân
        for hs in self._ds_hoc_sinh:
            result = self.svc.get_chi_tiet_vi_pham(hs.id, self._current_nam_hoc_id, self._current_tuan)
            if result.ok and result.data:
                for vp in result.data:
                    all_rows.append({
                        'id': vp.id,
                        'type': 'ca_nhan',
                        'hoc_sinh': hs.ho_ten,
                        'ngay': vp.ngay_xay_ra,
                        'ten_loi': vp.loai_vi_pham.ten_loi if vp.loai_vi_pham else "",
                        'so_diem': vp.so_diem,
                        'nguoi_ghi': vp.nguoi_ghi_nhan or ""
                    })
        
        # 2. Vi phạm tập thể
        result = self.svc.get_tap_the_vi_pham(self._current_nam_hoc_id, self._current_tuan, self._current_lop_id)
        if result.ok and result.data:
            for vp in result.data:
                all_rows.append({
                    'id': vp.id,
                    'type': 'tap_the',
                    'hoc_sinh': "🏫 TẬP THỂ",
                    'ngay': vp.ngay_xay_ra,
                    'ten_loi': vp.loai_vi_pham.ten_loi if vp.loai_vi_pham else "",
                    'so_diem': vp.so_diem,
                    'nguoi_ghi': vp.nguoi_ghi_nhan or ""
                })
        
        # Sắp xếp theo ngày giảm dần
        all_rows.sort(key=lambda x: x['ngay'], reverse=True)
        
        self.table_detail.setRowCount(len(all_rows))
        tong_vp = 0
        tong_tt = 0
        
        for idx, row in enumerate(all_rows):
            # STT
            item = QTableWidgetItem(str(idx + 1))
            item.setTextAlignment(Qt.AlignCenter)
            item.setData(Qt.UserRole, row['id'])
            item.setData(Qt.UserRole + 1, row['type'])
            self.table_detail.setItem(idx, 0, item)
            
            # Học sinh
            item = QTableWidgetItem(row['hoc_sinh'])
            self.table_detail.setItem(idx, 1, item)
            
            # Ngày
            ngay = row['ngay'].strftime("%d/%m/%Y") if row['ngay'] else ""
            item = QTableWidgetItem(ngay)
            item.setTextAlignment(Qt.AlignCenter)
            self.table_detail.setItem(idx, 2, item)
            
            # Lỗi/TT
            self.table_detail.setItem(idx, 3, QTableWidgetItem(row['ten_loi']))
            
            # Điểm
            diem = row['so_diem']
            item = QTableWidgetItem(f"{diem:.1f}")
            item.setTextAlignment(Qt.AlignCenter)
            if diem < 0:
                item.setBackground(self.COLOR_NEGATIVE)
                item.setForeground(QColor("#CC0000"))
                tong_vp += 1
            else:
                item.setBackground(self.COLOR_POSITIVE)
                item.setForeground(QColor("#2E7D32"))
                tong_tt += 1
            self.table_detail.setItem(idx, 4, item)
  
            # Nút xóa — wrap trong container để căn giữa
            container = QWidget()
            container.setStyleSheet("background: transparent;")  # ← thêm dòng này
            layout = QHBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setAlignment(Qt.AlignCenter)

            # Thay toàn bộ phần nút xóa bằng:
            btn_item = QTableWidgetItem("✖")
            btn_item.setTextAlignment(Qt.AlignCenter)
            btn_item.setForeground(QColor("#E53935"))
            btn_item.setData(Qt.UserRole, row['id'])
            btn_item.setData(Qt.UserRole + 1, row['type'])
            btn_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_detail.setItem(idx, 5, btn_item)
                    
        ten_lop = self.cmb_lop.currentText()
        self.lbl_hs_info.setText(f"🏫 Lớp {ten_lop} — Tuần {self._current_tuan}")
        self.lbl_tong_diem.setText(
            f"📋 Tổng {len(all_rows)} bản ghi  |  📉 Vi phạm: {tong_vp}  |  📈 Thành tích: {tong_tt}"
        )

    def _on_add(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._ds_hoc_sinh):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn học sinh!")
            return
        hs = self._ds_hoc_sinh[row]
        # ← truyền thêm session để Tab Danh mục có thể ghi DB
        dlg = ThemViPhamDialog(hs, self.loai_vp_list, self.svc.session, self)
        if dlg.exec() != QDialog.Accepted:
            # Sau khi đóng, đồng bộ lại danh mục phòng trường hợp người dùng đã thêm mới
            self.loai_vp_list = self.svc.get_loai_vi_pham()
            return
        # Đồng bộ danh mục (có thể đã thêm mới ở Tab 2)
        self.loai_vp_list = self.svc.get_loai_vi_pham()
        data   = dlg.get_data()
        result = self.svc.them_vi_pham(
            hoc_sinh_id      = hs.id,
            loai_vi_pham_id  = data['loai_vi_pham_id'],
            nam_hoc_id       = self._current_nam_hoc_id,
            tuan             = self._current_tuan,
            so_diem          = data['so_diem'],
            ngay_xay_ra      = data['ngay_xay_ra'],
            tiet             = data['tiet'],
            mo_ta            = data['mo_ta'],
            nguoi_ghi_nhan   = data['nguoi_ghi_nhan']
        )
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã thêm thành công!")
            self._on_load()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _show_detail_context_menu(self, pos):
        row = self.table_detail.currentRow()
        if row < 0:
            return
        vp_id = self._get_selected_vp_id(row)
        if not vp_id:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("🗑️ Xóa vi phạm/thành tích này")
        delete_action.triggered.connect(lambda: self._on_delete_vi_pham(vp_id))
        menu.exec(self.table_detail.viewport().mapToGlobal(pos))

    def _get_selected_vp_id(self, row):
        item = self.table_detail.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _on_delete_vi_pham(self, vp_id):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            "Bạn có chắc muốn xóa vi phạm/thành tích này?\nĐiểm Đội của lớp sẽ được hoàn trả!",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        result = self.svc.xoa_vi_pham(vp_id)
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã xóa!")
            self._on_load()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)
    
    def _on_cell_clicked(self, row, col):
        if col != 5:
            return
        item = self.table_detail.item(row, 0)
        if not item:
            return
        vp_id   = item.data(Qt.UserRole)
        vp_type = item.data(Qt.UserRole + 1)
        ho_ten  = self.table_detail.item(row, 1).text() if self.table_detail.item(row, 1) else ""
        ten_loi = self.table_detail.item(row, 3).text() if self.table_detail.item(row, 3) else ""
        so_diem = float(self.table_detail.item(row, 4).text()) if self.table_detail.item(row, 4) else 0
        self._on_delete_row({
            'id':       vp_id,
            'type':     vp_type,
            'hoc_sinh': ho_ten,
            'ten_loi':  ten_loi,
            'so_diem':  so_diem,
            'ngay':     None,
        })

    def _on_tap_the(self):
        """Thêm vi phạm tập thể cho lớp"""
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        tuan = self.cmb_tuan.currentData()
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        if not tuan:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn tuần!")
            return
        
        # Lấy danh sách lớp
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_lop = result.data or []
        
        if not ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return
        
        dlg = ThemTapTheViPhamDialog(ds_lop, self.loai_vp_list, self)
        if dlg.exec() != QDialog.Accepted:
            return
        
        data = dlg.get_data()
        data['nam_hoc_id'] = nam_hoc_id
        data['tuan'] = tuan
        
        result = self.svc.them_tap_the_vi_pham(
            lop_hoc_id=data['lop_hoc_id'],
            loai_vi_pham_id=data['loai_vi_pham_id'],
            nam_hoc_id=nam_hoc_id,
            tuan=tuan,
            so_diem=data['so_diem'],
            ngay_xay_ra=data['ngay_xay_ra'],
            tiet=data['tiet'],
            mo_ta=data['mo_ta'],
            nguoi_ghi_nhan=data['nguoi_ghi_nhan']
        )
        
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã thêm vi phạm tập thể!")
            # Reload lại tab "Theo tuần" để cập nhật điểm Đội
            self._refresh_week_tab()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _refresh_week_tab(self):
        """Làm mới tab Theo tuần"""
        # Tìm tab "Theo tuần" và reload
        parent = self.parent()
        if parent and hasattr(parent, 'tab_widget'):
            for i in range(parent.tab_widget.count()):
                tab = parent.tab_widget.widget(i)
                if hasattr(tab, '_on_load_week'):
                    tab._on_load_week()
                    break
    def _on_delete_row(self, row_data):
        """Xóa vi phạm/thành tích từ dòng trong bảng toàn lớp"""
        vp_id = row_data['id']
        vp_type = row_data['type']
        
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa vi phạm/thành tích này?\n"
            f"Học sinh: {row_data['hoc_sinh']}\n"
            f"Nội dung: {row_data['ten_loi']}\n"
            f"Điểm: {row_data['so_diem']:.1f}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        if vp_type == 'ca_nhan':
            result = self.svc.xoa_vi_pham(vp_id)
        else:
            result = self.svc.xoa_tap_the_vi_pham(vp_id)
        
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã xóa!")
            self._on_load()  # Reload lại dữ liệu
        else:
            QMessageBox.critical(self, "Lỗi", result.error)
            
    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)
class ThemTapTheViPhamDialog(QDialog):
    """Dialog thêm vi phạm tập thể cho lớp"""
    
    def __init__(self, lop_list, loai_vp_list, parent=None):
        super().__init__(parent)
        self.lop_list = lop_list
        self.loai_vp_list = loai_vp_list
        self.setWindowTitle("Thêm vi phạm tập thể")
        self.setMinimumWidth(450)
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        
        # Chọn lớp
        self.cmb_lop = QComboBox()
        for lop in self.lop_list:
            self.cmb_lop.addItem(lop.ten_lop, lop.id)
        form.addRow("Lớp:", self.cmb_lop)
        
        # Chọn lỗi
        self.cmb_loi = QComboBox()
        self._load_loi()
        form.addRow("Lỗi vi phạm:", self.cmb_loi)
        
        # Số điểm
        self.spin_diem = QSpinBox()
        self.spin_diem.setRange(-100, 0)
        self.spin_diem.setSuffix(" điểm")
        form.addRow("Số điểm trừ:", self.spin_diem)
        
        # Ngày
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form.addRow("Ngày:", self.date_edit)
        
        # Tiết
        self.cmb_tiet = QComboBox()
        for i in range(1, 9):
            buoi = "Sáng" if i <= 5 else "Chiều"
            tiet_hien = i if i <= 5 else i - 5
            self.cmb_tiet.addItem(f"Tiết {tiet_hien} ({buoi})", i)
        self.cmb_tiet.addItem("Ngoài giờ", 0)
        form.addRow("Tiết:", self.cmb_tiet)
        
        # Người ghi nhận
        self.txt_nguoi_ghi = QTextEdit()
        self.txt_nguoi_ghi.setMaximumHeight(60)
        form.addRow("Người ghi nhận:", self.txt_nguoi_ghi)
        
        # Mô tả
        self.txt_mo_ta = QTextEdit()
        self.txt_mo_ta.setMaximumHeight(80)
        form.addRow("Mô tả:", self.txt_mo_ta)
        
        layout.addLayout(form)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.cmb_loi.currentIndexChanged.connect(self._on_loi_changed)
        self._load_loi()
    
    def _load_loi(self):
        """Load danh sách lỗi vi phạm (chỉ loại vi_pham)"""
        self.cmb_loi.clear()
        for item in self.loai_vp_list:
            if item.loai == "vi_pham" and item.is_active:
                display = f"{item.ten_loi} ({item.so_diem} điểm)"
                self.cmb_loi.addItem(display, item.id)
    
    def _on_loi_changed(self):
        loai_id = self.cmb_loi.currentData()
        for item in self.loai_vp_list:
            if item.id == loai_id:
                self.spin_diem.setValue(int(item.so_diem))
                break
    
    def get_data(self):
        loai_id = self.cmb_loi.currentData()
        return {
            'lop_hoc_id': self.cmb_lop.currentData(),
            'loai_vi_pham_id': loai_id,
            'so_diem': self.spin_diem.value(),
            'ngay_xay_ra': self.date_edit.date().toPython(),
            'tiet': self.cmb_tiet.currentData(),
            'nguoi_ghi_nhan': self.txt_nguoi_ghi.toPlainText(),
            'mo_ta': self.txt_mo_ta.toPlainText()
        }
