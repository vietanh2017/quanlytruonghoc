# modules/competition/views/quan_ly_loai_vi_pham.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox, QLabel,
    QPushButton, QDialog, QFormLayout, QDialogButtonBox, QTextEdit,
    QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


BTN_PRIMARY = """
    QPushButton {
        background: #1D9E75; color: white;
        border-radius: 5px; padding: 5px 14px;
        font-size: 12px; font-weight: 600; border: none;
    }
    QPushButton:hover { background: #0F6E56; }
    QPushButton:disabled { background: #A5D6C5; }
"""
BTN_STYLE = """
    QPushButton {
        background: #F5F5F5; border: 1px solid #DDD;
        border-radius: 5px; padding: 5px 12px;
        font-size: 12px; color: #333;
    }
    QPushButton:hover { background: #E8F5F0; border-color: #1D9E75; color: #1D9E75; }
"""
BTN_DANGER = """
    QPushButton {
        background: #F5F5F5; border: 1px solid #DDD;
        border-radius: 5px; padding: 5px 12px;
        font-size: 12px; color: #E53935;
    }
    QPushButton:hover { background: #FFEBEE; border-color: #E53935; }
"""
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


class LoaiViPhamDialog(QDialog):
    """Dialog thêm / sửa loại vi phạm hoặc thành tích"""

    def __init__(self, parent=None, loai_vp=None, loai_mac_dinh="vi_pham"):
        super().__init__(parent)
        self._loai_vp = loai_vp  # None = thêm mới
        self._loai_mac_dinh = loai_mac_dinh
        title = "Sửa loại vi phạm/thành tích" if loai_vp else "Thêm loại vi phạm/thành tích"
        self.setWindowTitle(title)
        self.setMinimumWidth(460)
        self._build_ui()
        if loai_vp:
            self._fill(loai_vp)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        form = QFormLayout()
        form.setSpacing(10)

        # Loại
        self.cmb_loai = QComboBox()
        self.cmb_loai.addItem("Vi phạm", "vi_pham")
        self.cmb_loai.addItem("Thành tích", "thanh_tich")
        if self._loai_mac_dinh == "thanh_tich":
            self.cmb_loai.setCurrentIndex(1)
        self.cmb_loai.currentIndexChanged.connect(self._on_loai_changed)
        form.addRow("Loại:", self.cmb_loai)

        # Mã lỗi (tự động, cho sửa)
        self.txt_ma = QLineEdit()
        self.txt_ma.setPlaceholderText("Tự động sinh nếu để trống")
        form.addRow("Mã:", self.txt_ma)

        # Nhóm
        self.cmb_nhom = QComboBox()
        self.cmb_nhom.setEditable(True)
        self._load_nhom("vi_pham")
        form.addRow("Nhóm:", self.cmb_nhom)

        # Tên lỗi
        self.txt_ten = QLineEdit()
        self.txt_ten.setPlaceholderText("Ví dụ: Đi học muộn, Đạt giải văn nghệ...")
        form.addRow("Tên:", self.txt_ten)

        # Số điểm
        self.spin_diem = QDoubleSpinBox()
        self.spin_diem.setRange(-100, 100)
        self.spin_diem.setDecimals(1)
        self.spin_diem.setSuffix(" điểm")
        self.spin_diem.setValue(-2)
        form.addRow("Số điểm:", self.spin_diem)

        # Thứ tự
        self.spin_thu_tu = QSpinBox()
        self.spin_thu_tu.setRange(0, 999)
        form.addRow("Thứ tự:", self.spin_thu_tu)

        # Mô tả
        self.txt_mo_ta = QTextEdit()
        self.txt_mo_ta.setMaximumHeight(70)
        self.txt_mo_ta.setPlaceholderText("Mô tả thêm (không bắt buộc)...")
        form.addRow("Mô tả:", self.txt_mo_ta)

        # Kích hoạt
        self.chk_active = QCheckBox("Đang sử dụng")
        self.chk_active.setChecked(True)
        form.addRow("Trạng thái:", self.chk_active)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_ok)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self._on_loai_changed()

    def _load_nhom(self, loai: str):
        self.cmb_nhom.clear()
        if loai == "vi_pham":
            for nhom in ["Nề nếp", "ATGT", "Đạo đức", "Vệ sinh", "Khác"]:
                self.cmb_nhom.addItem(nhom)
        else:
            for nhom in ["Văn nghệ", "Thể thao", "Học tập", "Phong trào", "Khác"]:
                self.cmb_nhom.addItem(nhom)

    def _on_loai_changed(self):
        loai = self.cmb_loai.currentData()
        self._load_nhom(loai)
        # Gợi ý dấu điểm theo loại
        if loai == "vi_pham":
            if self.spin_diem.value() > 0:
                self.spin_diem.setValue(-2)
        else:
            if self.spin_diem.value() < 0:
                self.spin_diem.setValue(5)

    def _fill(self, loai_vp):
        """Điền dữ liệu khi sửa"""
        idx = self.cmb_loai.findData(loai_vp.loai)
        if idx >= 0:
            self.cmb_loai.setCurrentIndex(idx)
        self.txt_ma.setText(loai_vp.ma_loi or "")
        # Set nhóm
        idx_nhom = self.cmb_nhom.findText(loai_vp.nhom or "")
        if idx_nhom >= 0:
            self.cmb_nhom.setCurrentIndex(idx_nhom)
        else:
            self.cmb_nhom.setCurrentText(loai_vp.nhom or "")
        self.txt_ten.setText(loai_vp.ten_loi or "")
        self.spin_diem.setValue(float(loai_vp.so_diem or 0))
        self.spin_thu_tu.setValue(int(loai_vp.thu_tu or 0))
        self.txt_mo_ta.setPlainText(loai_vp.mo_ta or "")
        self.chk_active.setChecked(bool(loai_vp.is_active))

    def _on_ok(self):
        if not self.txt_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên vi phạm/thành tích!")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "loai":      self.cmb_loai.currentData(),
            "ma_loi":    self.txt_ma.text().strip() or None,
            "nhom":      self.cmb_nhom.currentText().strip(),
            "ten_loi":   self.txt_ten.text().strip(),
            "so_diem":   self.spin_diem.value(),
            "thu_tu":    self.spin_thu_tu.value(),
            "mo_ta":     self.txt_mo_ta.toPlainText().strip() or None,
            "is_active": self.chk_active.isChecked(),
        }


class QuanLyLoaiViPhamWidget(QWidget):
    """Màn hình quản lý danh mục vi phạm / thành tích"""

    COLOR_VP = QColor("#FFE5E5")
    COLOR_TT = QColor("#E8F5E9")
    COLOR_INACTIVE = QColor("#F5F5F5")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ds = []          # danh sách hiện tại (theo filter)
        self._all = []         # toàn bộ từ DB
        self._build_ui()
        self._load()

    # ──────────────────────────────────────────────
    # BUILD UI
    # ──────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Tiêu đề
        lbl_title = QLabel("📋 QUẢN LÝ DANH MỤC VI PHẠM / THÀNH TÍCH")
        lbl_title.setStyleSheet("font-weight:bold; color:#1D9E75; font-size:13px; padding:4px 0;")
        layout.addWidget(lbl_title)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)

        # Lọc loại
        tb.addWidget(QLabel("Loại:"))
        self.cmb_filter_loai = QComboBox()
        self.cmb_filter_loai.setMinimumWidth(130)
        self.cmb_filter_loai.addItem("Tất cả", "all")
        self.cmb_filter_loai.addItem("Vi phạm", "vi_pham")
        self.cmb_filter_loai.addItem("Thành tích", "thanh_tich")
        self.cmb_filter_loai.currentIndexChanged.connect(self._on_filter)
        tb.addWidget(self.cmb_filter_loai)

        # Lọc nhóm
        tb.addWidget(QLabel("Nhóm:"))
        self.cmb_filter_nhom = QComboBox()
        self.cmb_filter_nhom.setMinimumWidth(130)
        self.cmb_filter_nhom.addItem("Tất cả", "all")
        self.cmb_filter_nhom.currentIndexChanged.connect(self._on_filter)
        tb.addWidget(self.cmb_filter_nhom)

        # Lọc trạng thái
        self.chk_show_inactive = QCheckBox("Hiện mục đã ẩn")
        self.chk_show_inactive.stateChanged.connect(self._on_filter)
        tb.addWidget(self.chk_show_inactive)

        tb.addStretch()

        btn_them_vp = QPushButton("➕ Thêm vi phạm")
        btn_them_vp.setStyleSheet(BTN_STYLE)
        btn_them_vp.setFixedHeight(30)
        btn_them_vp.clicked.connect(lambda: self._on_them("vi_pham"))

        btn_them_tt = QPushButton("⭐ Thêm thành tích")
        btn_them_tt.setStyleSheet(BTN_PRIMARY)
        btn_them_tt.setFixedHeight(30)
        btn_them_tt.clicked.connect(lambda: self._on_them("thanh_tich"))

        tb.addWidget(btn_them_vp)
        tb.addWidget(btn_them_tt)
        layout.addLayout(tb)

        # Bảng
        self.table = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table, stretch=1)

        # Status + nút action
        bottom = QHBoxLayout()
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color:#666; font-size:11px;")
        bottom.addWidget(self.lbl_status)
        bottom.addStretch()

        self.btn_sua = QPushButton("✏️ Sửa")
        self.btn_sua.setStyleSheet(BTN_STYLE)
        self.btn_sua.setFixedHeight(30)
        self.btn_sua.setEnabled(False)
        self.btn_sua.clicked.connect(self._on_sua)

        self.btn_an = QPushButton("🙈 Ẩn")
        self.btn_an.setStyleSheet(BTN_DANGER)
        self.btn_an.setFixedHeight(30)
        self.btn_an.setEnabled(False)
        self.btn_an.clicked.connect(self._on_an)

        bottom.addWidget(self.btn_sua)
        bottom.addWidget(self.btn_an)
        layout.addLayout(bottom)

    def _setup_table(self):
        headers = ["STT", "Mã", "Nhóm", "Tên vi phạm / thành tích", "Điểm", "Loại", "TT"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 100)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(4, 65)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 55)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._on_sua)

    # ──────────────────────────────────────────────
    # LOAD & RENDER
    # ──────────────────────────────────────────────
    def _load(self):
        try:
            from modules.competition.repository.loai_vi_pham_repository import LoaiViPhamRepository
            from core.db.session import SessionLocal
            self._session = SessionLocal()
            self._repo = LoaiViPhamRepository(self._session)
            self._all = self._repo.get_all()
            self._refresh_nhom_filter()
            self._on_filter()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không tải được danh mục: {e}")

    def _refresh_nhom_filter(self):
        """Cập nhật combobox nhóm theo loại đang lọc"""
        loai = self.cmb_filter_loai.currentData()
        nhom_set = set()
        for item in self._all:
            if loai == "all" or item.loai == loai:
                if item.nhom:
                    nhom_set.add(item.nhom)

        self.cmb_filter_nhom.blockSignals(True)
        cur = self.cmb_filter_nhom.currentData()
        self.cmb_filter_nhom.clear()
        self.cmb_filter_nhom.addItem("Tất cả", "all")
        for nhom in sorted(nhom_set):
            self.cmb_filter_nhom.addItem(nhom, nhom)
        # Giữ lại nhóm đang chọn nếu còn
        idx = self.cmb_filter_nhom.findData(cur)
        if idx >= 0:
            self.cmb_filter_nhom.setCurrentIndex(idx)
        self.cmb_filter_nhom.blockSignals(False)

    def _on_filter(self):
        loai   = self.cmb_filter_loai.currentData()
        nhom   = self.cmb_filter_nhom.currentData()
        show_inactive = self.chk_show_inactive.isChecked()

        self._ds = [
            item for item in self._all
            if (loai == "all" or item.loai == loai)
            and (nhom == "all" or item.nhom == nhom)
            and (show_inactive or item.is_active)
        ]
        # Sort: nhóm → thứ tự
        self._ds.sort(key=lambda x: (x.nhom or "", x.thu_tu or 0))
        self._render()
        self._refresh_nhom_filter()

    def _render(self):
        self.table.setRowCount(len(self._ds))
        for row, item in enumerate(self._ds):
            is_vp = item.loai == "vi_pham"
            bg = self.COLOR_INACTIVE if not item.is_active else (
                self.COLOR_VP if is_vp else self.COLOR_TT
            )

            def cell(text, align=Qt.AlignCenter):
                c = QTableWidgetItem(str(text))
                c.setTextAlignment(align)
                c.setData(Qt.UserRole, item.id)
                if not item.is_active:
                    c.setForeground(QColor("#AAAAAA"))
                return c

            self.table.setItem(row, 0, cell(str(row + 1)))
            self.table.setItem(row, 1, cell(item.ma_loi or ""))
            self.table.setItem(row, 2, cell(item.nhom or ""))

            ten_item = cell(item.ten_loi or "", Qt.AlignLeft | Qt.AlignVCenter)
            if not item.is_active:
                font = QFont()
                font.setItalic(True)
                ten_item.setFont(font)
            self.table.setItem(row, 3, ten_item)

            diem = item.so_diem or 0
            diem_item = cell(f"{'+' if diem > 0 else ''}{diem:.1f}")
            if item.is_active:
                diem_item.setForeground(
                    QColor("#CC0000") if diem < 0 else QColor("#2E7D32")
                )
            self.table.setItem(row, 4, diem_item)

            loai_text = "Vi phạm" if is_vp else "Thành tích"
            self.table.setItem(row, 5, cell(loai_text))

            tt_text = "✅" if item.is_active else "🙈"
            self.table.setItem(row, 6, cell(tt_text))

            # Tô màu cả dòng
            for col in range(self.table.columnCount()):
                c = self.table.item(row, col)
                if c:
                    c.setBackground(bg)

        vp = sum(1 for x in self._ds if x.loai == "vi_pham")
        tt = sum(1 for x in self._ds if x.loai == "thanh_tich")
        self.lbl_status.setText(f"{len(self._ds)} mục  |  🔴 Vi phạm: {vp}  |  🟢 Thành tích: {tt}")
        self._update_buttons()

    # ──────────────────────────────────────────────
    # ACTIONS
    # ──────────────────────────────────────────────
    def _on_selection(self):
        self._update_buttons()

    def _update_buttons(self):
        has = self.table.currentRow() >= 0 and len(self.table.selectedItems()) > 0
        self.btn_sua.setEnabled(has)
        self.btn_an.setEnabled(has)
        if has:
            item = self._get_selected_item()
            self.btn_an.setText("👁 Hiện" if item and not item.is_active else "🙈 Ẩn")

    def _get_selected_item(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._ds):
            return None
        return self._ds[row]

    def _gen_ma(self, loai: str) -> str:
        """Sinh mã tự động VP/TT + số tiếp theo"""
        prefix = "VP" if loai == "vi_pham" else "TT"
        existing = [
            int(x.ma_loi[len(prefix):])
            for x in self._all
            if x.ma_loi and x.ma_loi.startswith(prefix)
            and x.ma_loi[len(prefix):].isdigit()
        ]
        next_num = max(existing, default=0) + 1
        return f"{prefix}{next_num:03d}"

    def _on_them(self, loai_mac_dinh: str):
        dlg = LoaiViPhamDialog(self, loai_mac_dinh=loai_mac_dinh)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data["ma_loi"]:
            data["ma_loi"] = self._gen_ma(data["loai"])
        try:
            from modules.competition.models.loai_vi_pham import LoaiViPham
            obj = LoaiViPham(**data)
            self._session.add(obj)
            self._session.commit()
            self._all.append(obj)
            self._on_filter()
            QMessageBox.information(self, "Thành công", f"Đã thêm: {data['ten_loi']}")
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def _on_sua(self):
        item = self._get_selected_item()
        if not item:
            return
        dlg = LoaiViPhamDialog(self, loai_vp=item)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            item.loai      = data["loai"]
            item.ma_loi    = data["ma_loi"] or item.ma_loi
            item.nhom      = data["nhom"]
            item.ten_loi   = data["ten_loi"]
            item.so_diem   = data["so_diem"]
            item.thu_tu    = data["thu_tu"]
            item.mo_ta     = data["mo_ta"]
            item.is_active = data["is_active"]
            self._session.commit()
            self._on_filter()
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def _on_an(self):
        item = self._get_selected_item()
        if not item:
            return
        new_state = not item.is_active
        action = "hiện" if new_state else "ẩn"
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn muốn {action} mục «{item.ten_loi}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            item.is_active = new_state
            self._session.commit()
            self._on_filter()
        except Exception as e:
            self._session.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

    def closeEvent(self, event):
        if hasattr(self, "_session"):
            self._session.close()
        super().closeEvent(event)
