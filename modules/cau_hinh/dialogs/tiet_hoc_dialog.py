from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QSpinBox, QLabel
)
from PySide6.QtCore import Qt


class TietHocDialog(QDialog):
    def __init__(self, parent=None, tiet_hoc=None):
        super().__init__(parent)
        self.tiet_hoc = tiet_hoc
        self.setWindowTitle("Sửa tiết học" if tiet_hoc else "Thêm tiết học")
        self.setMinimumWidth(350)
        self.setModal(True)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        
        # Thứ tự
        self.spin_stt = QSpinBox()
        self.spin_stt.setRange(1, 15)
        self.spin_stt.setValue(1)
        form.addRow("Thứ tự:", self.spin_stt)
        
        # Tên tiết
        self.inp_ten = QLineEdit()
        self.inp_ten.setPlaceholderText("VD: Tiết 1")
        form.addRow("Tên tiết:", self.inp_ten)
        
        # Thời gian bắt đầu
        self.inp_bat_dau = QLineEdit()
        self.inp_bat_dau.setPlaceholderText("VD: 7:00")
        form.addRow("Thời gian bắt đầu:", self.inp_bat_dau)
        
        # Thời gian kết thúc
        self.inp_ket_thuc = QLineEdit()
        self.inp_ket_thuc.setPlaceholderText("VD: 7:45")
        form.addRow("Thời gian kết thúc:", self.inp_ket_thuc)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton("💾 Lưu")
        self.btn_ok.setStyleSheet("background: #1D9E75; color: white; padding: 6px 20px; border-radius: 5px;")
        self.btn_ok.clicked.connect(self._on_accept)
        
        self.btn_cancel = QPushButton("❌ Hủy")
        self.btn_cancel.setStyleSheet("background: #ccc; padding: 6px 20px; border-radius: 5px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        if self.tiet_hoc:
            self.spin_stt.setValue(self.tiet_hoc.so_thu_tu)
            self.inp_ten.setText(self.tiet_hoc.ten_tiet)
            self.inp_bat_dau.setText(self.tiet_hoc.thoi_gian_bat_dau or "")
            self.inp_ket_thuc.setText(self.tiet_hoc.thoi_gian_ket_thuc or "")
    
    def _on_accept(self):
        if not self.inp_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên tiết học")
            return
        self.accept()
    
    def get_data(self):
        return {
            "so_thu_tu": self.spin_stt.value(),
            "ten_tiet": self.inp_ten.text().strip(),
            "thoi_gian_bat_dau": self.inp_bat_dau.text().strip(),
            "thoi_gian_ket_thuc": self.inp_ket_thuc.text().strip()
        }