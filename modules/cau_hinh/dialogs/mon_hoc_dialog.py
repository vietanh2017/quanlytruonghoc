# modules/cau_hinh/dialogs/mon_hoc_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QCheckBox,
    QMessageBox, QGroupBox, QRadioButton, QSpinBox
)
from PySide6.QtCore import Qt


class MonHocDialog(QDialog):
    def __init__(self, parent=None, mon_hoc=None, ds_to=None):
        super().__init__(parent)
        self.mon_hoc = mon_hoc
        self.ds_to = ds_to or []
        self.setWindowTitle("Sửa môn học" if mon_hoc else "Thêm môn học")
        self.setMinimumWidth(450)
        self.setModal(True)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        # Mã môn
        self.inp_ma_mon = QLineEdit()
        self.inp_ma_mon.setPlaceholderText("VD: TOAN, VAN, LS_DL...")
        form.addRow("Mã môn *:", self.inp_ma_mon)
        
        # Tên môn
        self.inp_ten_mon = QLineEdit()
        self.inp_ten_mon.setPlaceholderText("VD: Toán, Ngữ văn...")
        form.addRow("Tên môn *:", self.inp_ten_mon)
        
        # Tổ chuyên môn
        self.cmb_to = QComboBox()
        self.cmb_to.addItem("-- Chọn tổ --", None)
        for to in self.ds_to:
            self.cmb_to.addItem(to.ten_to, to.id)
        form.addRow("Tổ chuyên môn:", self.cmb_to)
        
        # Loại môn
        self.group_loai = QGroupBox("Loại môn")
        loai_layout = QHBoxLayout()
        self.radio_doc_lap = QRadioButton("Môn độc lập")
        self.radio_co_phan_mon = QRadioButton("Có phân môn")
        self.radio_doc_lap.setChecked(True)
        
        loai_layout.addWidget(self.radio_doc_lap)
        loai_layout.addWidget(self.radio_co_phan_mon)
        self.group_loai.setLayout(loai_layout)
        form.addRow(self.group_loai)
        
        # Thứ tự
        self.inp_thu_tu = QSpinBox()
        self.inp_thu_tu.setRange(0, 100)
        self.inp_thu_tu.setValue(0)
        form.addRow("Thứ tự:", self.inp_thu_tu)
        
        # Trạng thái
        self.chk_active = QCheckBox("Hoạt động")
        self.chk_active.setChecked(True)
        form.addRow("", self.chk_active)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton("Lưu")
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background: #1D9E75; color: white;
                border-radius: 5px; padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: #0F6E56; }
        """)
        self.btn_ok.clicked.connect(self._on_accept)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ccc; color: #333;
                border-radius: 5px; padding: 8px 20px;
            }
            QPushButton:hover { background: #bbb; }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        if self.mon_hoc:
            self.inp_ma_mon.setText(self.mon_hoc.ma_mon or "")
            self.inp_ten_mon.setText(self.mon_hoc.ten_mon or "")
            self.inp_thu_tu.setValue(self.mon_hoc.thu_tu or 0)
            
            if self.mon_hoc.co_phan_mon:
                self.radio_co_phan_mon.setChecked(True)
            else:
                self.radio_doc_lap.setChecked(True)
            
            # Chọn tổ
            if self.mon_hoc.to_id:
                idx = self.cmb_to.findData(self.mon_hoc.to_id)
                if idx >= 0:
                    self.cmb_to.setCurrentIndex(idx)
            
            self.chk_active.setChecked(self.mon_hoc.active)
    
    def _on_accept(self):
        if not self.inp_ma_mon.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã môn")
            return
        if not self.inp_ten_mon.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên môn")
            return
        self.accept()
    
    def get_data(self):
        return {
            "ma_mon": self.inp_ma_mon.text().strip(),
            "ten_mon": self.inp_ten_mon.text().strip(),
            "co_phan_mon": self.radio_co_phan_mon.isChecked(),
            "to_id": self.cmb_to.currentData(),
            "thu_tu": self.inp_thu_tu.value(),
            "active": self.chk_active.isChecked()
        }