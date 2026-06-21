from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
    QLineEdit, QSplitter, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt
from modules.lop_hoc.views.lop_hoc_table import LopHocTable
from modules.lop_hoc.service import LopHocService
from modules.lop_hoc.dialogs.lop_hoc_dialog import LopHocDialog
from modules.lop_hoc.views.hoc_sinh_panel import HocSinhPanel
from core.utils.logger import logger
BTN_STYLE = """
    QPushButton {
        background:#F5F5F5; border:1px solid #DDD;
        border-radius:5px; padding:5px 12px;
        font-size:12px; color:#333;
    }
    QPushButton:hover { background:#E8F5F0; border-color:#1D9E75; color:#1D9E75; }
    QPushButton:disabled { color:#BBB; background:#F5F5F5; }
"""
BTN_PRIMARY = """
    QPushButton {
        background:#1D9E75; color:white;
        border-radius:5px; padding:5px 12px;
        font-size:12px; font-weight:600; border:none;
    }
    QPushButton:hover { background:#0F6E56; }
"""
BTN_WARNING = """
    QPushButton {
        background:#FF9800; color:white; border:none;
        border-radius:5px; padding:5px 12px;
        font-size:12px; font-weight:600;
    }
    QPushButton:hover { background:#FB8C00; }
    QPushButton:disabled { background:#FFB74D; color:#FFF3E0; }
"""
BTN_DANGER = """
    QPushButton {
        background:#DC3545; color:white; border:none;
        border-radius:5px; padding:5px 12px;
        font-size:12px; font-weight:600;
    }
    QPushButton:hover { background:#C82333; }
    QPushButton:disabled { background:#EF9A9A; color:#FFEBEE; }
"""
BTN_GRAY = """
    QPushButton {
        background:#6C757D; color:white; border:none;
        border-radius:5px; padding:5px 12px;
        font-size:12px; font-weight:600;
    }
    QPushButton:hover { background:#5A6268; }
    QPushButton:disabled { background:#BDBDBD; color:#EEE; }
"""


class LopHocPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.svc = LopHocService()
        self._all = []
        self._build_ui()
        self._load()

    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # ── Header ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        lbl = QLabel("Danh sách lớp học")
        lbl.setStyleSheet("font-size:17px; font-weight:600;")
        hdr.addWidget(lbl)
        hdr.addStretch()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔍 Tìm lớp...")
        self.inp_search.setFixedWidth(220)
        self.inp_search.setStyleSheet("""
            QLineEdit {
                border:1px solid #ccc; border-radius:5px;
                padding:5px 10px; font-size:13px;
            }
            QLineEdit:focus { border-color:#1D9E75; }
        """)
        self.inp_search.textChanged.connect(self._filter)
        hdr.addWidget(self.inp_search)
        layout.addLayout(hdr)

        # ── Toolbar chung ────────────────────────────────────────
        tb = QHBoxLayout()
        tb.setSpacing(6)

        # Nút lớp học
        self.btn_them = QPushButton("＋ Thêm lớp")
        self.btn_them.setStyleSheet(BTN_PRIMARY)
        self.btn_them.setFixedHeight(30)
        self.btn_them.clicked.connect(self._on_them)

        self.btn_sua = QPushButton("✏ Sửa lớp")
        self.btn_sua.setStyleSheet(BTN_WARNING)
        self.btn_sua.setFixedHeight(30)
        self.btn_sua.setEnabled(False)
        self.btn_sua.clicked.connect(self._on_sua)

        self.btn_xoa = QPushButton("🗑 Xóa lớp")
        self.btn_xoa.setStyleSheet(BTN_DANGER)
        self.btn_xoa.setFixedHeight(30)
        self.btn_xoa.setEnabled(False)
        self.btn_xoa.clicked.connect(self._on_xoa)

        self.btn_tt = QPushButton("⏸ Vô hiệu/KH")
        self.btn_tt.setStyleSheet(BTN_GRAY)
        self.btn_tt.setFixedHeight(30)
        self.btn_tt.setEnabled(False)
        self.btn_tt.clicked.connect(self._on_tt)

        tb.addWidget(self.btn_them)
        tb.addWidget(self.btn_sua)
        tb.addWidget(self.btn_xoa)
        tb.addWidget(self.btn_tt)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#DDD;")
        sep.setFixedHeight(24)
        tb.addWidget(sep)

        # Nút học sinh
        self.lbl_lop_hs = QLabel("👨‍🎓 Chọn lớp để xem học sinh")
        self.lbl_lop_hs.setStyleSheet("color:#888; font-size:12px; font-weight:500;")
        tb.addWidget(self.lbl_lop_hs)

        self.btn_them_hs = QPushButton("＋ Thêm HS")
        self.btn_them_hs.setStyleSheet(BTN_PRIMARY)
        self.btn_them_hs.setFixedHeight(30)
        self.btn_them_hs.setEnabled(False)

        self.btn_sua_hs = QPushButton("✏ Sửa HS")
        self.btn_sua_hs.setStyleSheet(BTN_STYLE)
        self.btn_sua_hs.setFixedHeight(30)
        self.btn_sua_hs.setEnabled(False)

        self.btn_xoa_hs = QPushButton("🗑 Xóa HS")
        self.btn_xoa_hs.setStyleSheet(BTN_STYLE)
        self.btn_xoa_hs.setFixedHeight(30)
        self.btn_xoa_hs.setEnabled(False)

        self.btn_excel_hs = QPushButton("📥 Excel")
        self.btn_excel_hs.setStyleSheet(BTN_STYLE)
        self.btn_excel_hs.setFixedHeight(30)
        self.btn_excel_hs.setEnabled(False)
        tb.addWidget(self.btn_excel_hs)
        tb.addWidget(self.btn_them_hs)
        tb.addWidget(self.btn_sua_hs)
        tb.addWidget(self.btn_xoa_hs)
        tb.addStretch()

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color:#666; font-size:12px;")
        tb.addWidget(self.lbl_count)

        self.lbl_count_hs = QLabel()
        self.lbl_count_hs.setStyleSheet("color:#666; font-size:12px;")
        tb.addWidget(self.lbl_count_hs)

        layout.addLayout(tb)

        # ── Splitter ─────────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background:#E0E0E0; width:2px; }")

        self.table = LopHocTable()
        self.table.selection_changed.connect(self._on_selection)
        self.table.double_clicked.connect(self._on_sua)
        splitter.addWidget(self.table)

        self.hs_panel = HocSinhPanel(self.svc)
        self.hs_panel.set_external_buttons(
            self.btn_them_hs,
            self.btn_sua_hs,
            self.btn_xoa_hs,
            self.btn_excel_hs,
            self.lbl_lop_hs,
            self.lbl_count_hs,
        )
        splitter.addWidget(self.hs_panel)

        splitter.setSizes([600, 500])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)

    # ── Load / Render ────────────────────────────────────────────
    def _load(self):
        r = self.svc.lay_ds()
        if not r.ok:
            QMessageBox.critical(self, "Lỗi", r.error)
            return
        self._all = r.data or []
        self._render(self._all)

    def _render(self, ds):
        self.table.load_data(ds)
        self.lbl_count.setText(f"{len(ds)} lớp")

    def _filter(self, text):
        kw = text.lower().strip()
        ds = [l for l in self._all if kw in l.ma_lop.lower() or kw in l.ten_lop.lower()]
        self._render(ds)

    # ── Selection ────────────────────────────────────────────────
    def _on_selection(self, selected_id):
        if selected_id is not None:
            try:
                selected_id = int(selected_id)
            except:
                selected_id = None

        has = selected_id is not None
        self.btn_sua.setEnabled(has)
        self.btn_xoa.setEnabled(has)
        self.btn_tt.setEnabled(has)

        if selected_id:
            lop = self.svc.repo.get_by_id(selected_id)
            if lop:
                self.hs_panel.load_lop(selected_id, lop.ten_lop)
                self.lbl_lop_hs.setText(f"👨‍🎓 Lớp: {lop.ten_lop}")
                self.lbl_lop_hs.setStyleSheet("color:#1D9E75; font-size:12px; font-weight:600;")
                self.btn_them_hs.setEnabled(True)
                self.btn_excel_hs.setEnabled(True)

    def _sel_id(self):
        lop_id = self.table.get_selected_id()
        if lop_id is not None:
            try:
                return int(lop_id)
            except:
                return None
        return None

    # ── CRUD Lớp ────────────────────────────────────────────────
    def _on_them(self):
        ds_gv = self.svc.lay_ds_giao_vien().data
        ds_nh = self.svc.lay_ds_nam_hoc().data
        dlg = LopHocDialog(self, ds_gv=ds_gv, ds_nam_hoc=ds_nh)
        if dlg.exec() != LopHocDialog.Accepted:
            return
        r = self.svc.them(**dlg.get_data())
        if r.ok:
            self._load()
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)
        logger.log_action(
                user=self._nd.ho_ten,
                action="Thêm lớp học",
                details=f"Mã lớp: {ma_lop}, Tên: {ten_lop}"
            )
    def _on_sua(self, lop_id=None):
        if not lop_id:
            lop_id = self._sel_id()
        if lop_id:
            try:
                lop_id = int(lop_id)
            except:
                lop_id = None
        if not lop_id:
            QMessageBox.warning(self, "Lỗi", "Chưa chọn lớp nào để sửa.")
            return
        lop = self.svc.repo.get_by_id(lop_id)
        if not lop:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy lớp học.")
            return
        ds_gv = self.svc.lay_ds_giao_vien().data or []
        ds_nh = self.svc.lay_ds_nam_hoc().data or []
        dlg = LopHocDialog(self, lop=lop, ds_gv=ds_gv, ds_nam_hoc=ds_nh)
        if dlg.exec() != LopHocDialog.Accepted:
            return
        r = self.svc.sua(lop_id, **dlg.get_data())
        if r.ok:
            self._load()
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)

    def _on_xoa(self):
        lop_id = self._sel_id()
        if not lop_id:
            return
        reply = QMessageBox.question(self, "Xác nhận", "Xóa lớp học?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        r = self.svc.xoa(lop_id)
        if r.ok:
            self._load()
        else:
            QMessageBox.warning(self, "Lỗi", r.error)

    def _on_tt(self):
        lop_id = self._sel_id()
        if not lop_id:
            return
        r = self.svc.doi_trang_thai(lop_id)
        if r.ok:
            self._load()
        else:
            QMessageBox.warning(self, "Lỗi", r.error)