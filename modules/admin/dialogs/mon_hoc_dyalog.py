# D:\QUANLYTRUONGHOC\modules\admin\dialogs\mon_hoc_dialog.py
"""
MonHocDialog: dialog thêm / sửa môn học.
Hỗ trợ khai báo phân môn (Lý, Hoá, Sinh...) nếu môn có phân môn.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QLabel, QDialogButtonBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from typing import Optional


class MonHocDialog(QDialog):
    def __init__(self, parent=None, mon=None, ds_to: list = None):
        super().__init__(parent)
        self._mon = mon
        self._ds_to = ds_to or []
        self.setWindowTitle("Sửa môn học" if mon else "Thêm môn học")
        self.setMinimumWidth(480)
        self.setMinimumHeight(400)
        self.setModal(True)
        self._build_ui()
        if mon:
            self._fill(mon)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Thêm môn học" if not self._mon else "Sửa môn học")
        title.setStyleSheet("font-size:15px; font-weight:700;")
        layout.addWidget(title)

        # Form thông tin môn
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.inp_ma = QLineEdit()
        self.inp_ma.setPlaceholderText("VD: TOAN, LY, HOA")
        self.inp_ma.setMaxLength(20)
        form.addRow("Mã môn *", self.inp_ma)

        self.inp_ten = QLineEdit()
        self.inp_ten.setPlaceholderText("VD: Toán, Vật lý")
        form.addRow("Tên môn *", self.inp_ten)

        self.cmb_to = QComboBox()
        self.cmb_to.addItem("-- Chưa phân tổ --", None)
        for to in self._ds_to:
            self.cmb_to.addItem(to.ten_to, to.id)
        form.addRow("Tổ chuyên môn", self.cmb_to)

        self.spn_thu_tu = QSpinBox()
        self.spn_thu_tu.setRange(0, 100)
        self.spn_thu_tu.setValue(0)
        form.addRow("Thứ tự hiển thị", self.spn_thu_tu)

        self.chk_phan_mon = QCheckBox("Môn này có phân môn")
        self.chk_phan_mon.toggled.connect(self._on_toggle_phan_mon)
        form.addRow("", self.chk_phan_mon)

        layout.addLayout(form)

        # Bảng phân môn (hiện khi tích checkbox)
        self.lbl_pm = QLabel("Danh sách phân môn:")
        self.lbl_pm.setStyleSheet("font-weight:600;")
        self.lbl_pm.setVisible(False)
        layout.addWidget(self.lbl_pm)

        self.tbl_pm = QTableWidget(0, 2)
        self.tbl_pm.setHorizontalHeaderLabels(["Mã phân môn", "Tên phân môn"])
        self.tbl_pm.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_pm.setColumnWidth(0, 110)
        self.tbl_pm.setVisible(False)
        self.tbl_pm.setMaximumHeight(160)
        layout.addWidget(self.tbl_pm)

        btn_pm_row = QHBoxLayout()
        self.btn_them_pm = QPushButton("＋  Thêm phân môn")
        self.btn_them_pm.setVisible(False)
        self.btn_them_pm.clicked.connect(self._on_them_phan_mon)
        self.btn_xoa_pm = QPushButton("🗑  Xoá")
        self.btn_xoa_pm.setVisible(False)
        self.btn_xoa_pm.setObjectName("btn_danger")
        self.btn_xoa_pm.clicked.connect(self._on_xoa_phan_mon)
        btn_pm_row.addWidget(self.btn_them_pm)
        btn_pm_row.addWidget(self.btn_xoa_pm)
        btn_pm_row.addStretch()
        layout.addLayout(btn_pm_row)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Lưu")
        btns.button(QDialogButtonBox.Cancel).setText("Huỷ")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_toggle_phan_mon(self, checked: bool):
        self.lbl_pm.setVisible(checked)
        self.tbl_pm.setVisible(checked)
        self.btn_them_pm.setVisible(checked)
        self.btn_xoa_pm.setVisible(checked)

    def _on_them_phan_mon(self):
        row = self.tbl_pm.rowCount()
        self.tbl_pm.insertRow(row)
        self.tbl_pm.setItem(row, 0, QTableWidgetItem(""))
        self.tbl_pm.setItem(row, 1, QTableWidgetItem(""))
        self.tbl_pm.editItem(self.tbl_pm.item(row, 0))

    def _on_xoa_phan_mon(self):
        row = self.tbl_pm.currentRow()
        if row >= 0:
            self.tbl_pm.removeRow(row)

    def _fill(self, mon):
        self.inp_ma.setText(mon.ma_mon)
        self.inp_ten.setText(mon.ten_mon)
        self.spn_thu_tu.setValue(mon.thu_tu or 0)

        for i in range(self.cmb_to.count()):
            if self.cmb_to.itemData(i) == mon.to_id:
                self.cmb_to.setCurrentIndex(i)
                break

        if mon.co_phan_mon:
            self.chk_phan_mon.setChecked(True)
            for pm in mon.phan_mon_list:
                row = self.tbl_pm.rowCount()
                self.tbl_pm.insertRow(row)
                self.tbl_pm.setItem(row, 0, QTableWidgetItem(pm.ma_phan_mon))
                self.tbl_pm.setItem(row, 1, QTableWidgetItem(pm.ten_phan_mon))

    def _on_accept(self):
        if not self.inp_ma.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã môn.")
            return
        if not self.inp_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên môn.")
            return
        if self.chk_phan_mon.isChecked() and self.tbl_pm.rowCount() == 0:
            QMessageBox.warning(self, "Lỗi",
                                "Môn có phân môn phải có ít nhất 1 phân môn.")
            return
        self.accept()

    def get_data(self) -> dict:
        phan_mon_list = []
        for row in range(self.tbl_pm.rowCount()):
            ma  = self.tbl_pm.item(row, 0)
            ten = self.tbl_pm.item(row, 1)
            if ma and ten:
                phan_mon_list.append({
                    "ma": ma.text().strip().upper(),
                    "ten": ten.text().strip()
                })
        return {
            "ma_mon": self.inp_ma.text().strip().upper(),
            "ten_mon": self.inp_ten.text().strip(),
            "co_phan_mon": self.chk_phan_mon.isChecked(),
            "to_id": self.cmb_to.currentData(),
            "thu_tu": self.spn_thu_tu.value(),
            "phan_mon_list": phan_mon_list,
        }