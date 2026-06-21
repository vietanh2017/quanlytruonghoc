# modules/giao_vien/dialogs/phan_cong_dialog.py
"""
PhanCongDialog: phân công giảng dạy cho giáo viên.
Cho phép gán GV dạy môn nào, lớp nào, học kỳ nào.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QDialogButtonBox, QMessageBox,
    QHeaderView, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class PhanCongDialog(QDialog):
    """
    Dialog phân công giảng dạy.
    Hiển thị danh sách phân công hiện tại của GV,
    cho phép thêm / xoá phân công.
    """

    def __init__(self, parent=None, giao_vien=None,
                 ds_lop: list = None,
                 ds_mon: list = None,
                 ds_hoc_ky: list = None,
                 ds_phan_cong: list = None):
        super().__init__(parent)
        self._gv        = giao_vien
        self._ds_lop    = ds_lop or []
        self._ds_mon    = ds_mon or []
        self._ds_hk     = ds_hoc_ky or []
        self._phan_cong = list(ds_phan_cong or [])   # copy để edit
        self._deleted   = []                          # id cần xoá

        ten = giao_vien.nguoi_dung.ho_ten if giao_vien else ""
        self.setWindowTitle(f"Phân công giảng dạy — {ten}")
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)
        self.setModal(True)
        self._build_ui()
        self._render()

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Tiêu đề
        if self._gv:
            nd  = self._gv.nguoi_dung
            ten = nd.ho_ten
            ma  = self._gv.ma_giao_vien
        else:
            ten, ma = "—", "—"

        hdr = QHBoxLayout()
        lbl = QLabel(f"👤  <b>{ten}</b>  <span style='color:#7A8BAD'>({ma})</span>")
        lbl.setStyleSheet("font-size:14px;")
        hdr.addWidget(lbl)
        hdr.addStretch()
        layout.addLayout(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#E4E8F0; max-height:1px;")
        layout.addWidget(sep)

        # Form thêm phân công mới
        lbl_add = QLabel("Thêm phân công:")
        lbl_add.setStyleSheet("font-weight:600; font-size:13px;")
        layout.addWidget(lbl_add)

        form = QHBoxLayout()
        form.setSpacing(8)

        self.cmb_hk = QComboBox()
        self.cmb_hk.setMinimumWidth(130)
        self.cmb_hk.addItem("-- Học kỳ --", None)
        for hk in self._ds_hk:
            label = f"{hk.ten_hoc_ky} {hk.nam_hoc}" if hasattr(hk, 'ten_hoc_ky') \
                else str(hk)
            self.cmb_hk.addItem(label, hk.id if hasattr(hk, 'id') else hk)

        self.cmb_mon = QComboBox()
        self.cmb_mon.setMinimumWidth(160)
        self.cmb_mon.addItem("-- Môn học --", None)
        for mon in self._ds_mon:
            self.cmb_mon.addItem(mon.ten_mon, mon.id)

        self.cmb_lop = QComboBox()
        self.cmb_lop.setMinimumWidth(100)
        self.cmb_lop.addItem("-- Lớp --", None)
        for lop in self._ds_lop:
            self.cmb_lop.addItem(lop.ten_lop, lop.id)

        btn_add = QPushButton("＋  Thêm")
        btn_add.setStyleSheet(
            "QPushButton{background:#1D9E75;color:white;border-radius:6px;"
            "padding:6px 14px;font-weight:600;}"
            "QPushButton:hover{background:#0F6E56;}")
        btn_add.clicked.connect(self._on_them_dong)

        for w in [QLabel("Học kỳ:"), self.cmb_hk,
                  QLabel("Môn:"), self.cmb_mon,
                  QLabel("Lớp:"), self.cmb_lop,
                  btn_add]:
            form.addWidget(w)
        form.addStretch()
        layout.addLayout(form)

        # Bảng phân công hiện tại
        lbl_tbl = QLabel("Phân công hiện tại:")
        lbl_tbl.setStyleSheet("font-weight:600; font-size:13px;")
        layout.addWidget(lbl_tbl)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Học kỳ", "Môn học", "Lớp", ""])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 60)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color:#7A8BAD; font-size:12px;")
        layout.addWidget(self.lbl_count)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Lưu")
        btns.button(QDialogButtonBox.Cancel).setText("Huỷ")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    # ── Render bảng ───────────────────────────────────────────
    def _render(self):
        self.table.setRowCount(0)
        for i, pc in enumerate(self._phan_cong):
            self.table.insertRow(i)

            # Học kỳ
            ten_hk = pc.get("ten_hk", "") if isinstance(pc, dict) else \
                getattr(pc, "ten_hk", "")
            self.table.setItem(i, 0, QTableWidgetItem(str(ten_hk)))

            # Môn
            ten_mon = pc.get("ten_mon", "") if isinstance(pc, dict) else \
                getattr(pc, "ten_mon", "")
            self.table.setItem(i, 1, QTableWidgetItem(str(ten_mon)))

            # Lớp
            ten_lop = pc.get("ten_lop", "") if isinstance(pc, dict) else \
                getattr(pc, "ten_lop", "")
            item_lop = QTableWidgetItem(str(ten_lop))
            item_lop.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, item_lop)

            # Nút xoá
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(28, 28)
            btn_del.setStyleSheet(
                "QPushButton{color:#C0392B;border:none;font-size:14px;"
                "border-radius:4px;background:transparent;}"
                "QPushButton:hover{background:#FDEEEC;}")
            btn_del.clicked.connect(lambda _, row=i: self._on_xoa_dong(row))
            self.table.setCellWidget(i, 3, btn_del)

            # Lưu data vào row
            self.table.item(i, 0).setData(Qt.UserRole, i)

        self.lbl_count.setText(f"{len(self._phan_cong)} phân công")

    # ── Actions ───────────────────────────────────────────────
    def _on_them_dong(self):
        hk_id  = self.cmb_hk.currentData()
        mon_id = self.cmb_mon.currentData()
        lop_id = self.cmb_lop.currentData()

        if not hk_id or not mon_id or not lop_id:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng chọn đầy đủ Học kỳ, Môn và Lớp.")
            return

        # Kiểm tra trùng
        for pc in self._phan_cong:
            if isinstance(pc, dict):
                if (pc.get("hk_id") == hk_id and
                        pc.get("mon_id") == mon_id and
                        pc.get("lop_id") == lop_id):
                    QMessageBox.warning(self, "Trùng",
                                        "Phân công này đã tồn tại.")
                    return

        ten_hk  = self.cmb_hk.currentText().replace("-- Học kỳ --", "")
        ten_mon = self.cmb_mon.currentText().replace("-- Môn học --", "")
        ten_lop = self.cmb_lop.currentText().replace("-- Lớp --", "")

        self._phan_cong.append({
            "hk_id":   hk_id,  "ten_hk":  ten_hk,
            "mon_id":  mon_id, "ten_mon": ten_mon,
            "lop_id":  lop_id, "ten_lop": ten_lop,
            "is_new":  True,
        })
        self._render()

    def _on_xoa_dong(self, row: int):
        if row >= len(self._phan_cong):
            return
        pc = self._phan_cong[row]
        # Nếu là bản ghi đã có trong DB thì đánh dấu xoá
        if isinstance(pc, dict) and pc.get("id"):
            self._deleted.append(pc["id"])
        self._phan_cong.pop(row)
        self._render()

    # ── Lấy kết quả ───────────────────────────────────────────
    def get_data(self) -> dict:
        """
        Trả về dict gồm:
          - them_moi: list phân công mới cần INSERT
          - xoa_id:   list id cần DELETE
        """
        them_moi = [pc for pc in self._phan_cong
                    if isinstance(pc, dict) and pc.get("is_new")]
        return {
            "them_moi": them_moi,
            "xoa_id":   self._deleted,
        }
