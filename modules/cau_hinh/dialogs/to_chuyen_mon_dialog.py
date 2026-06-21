# modules\cau_hinh\dialogs\to_chuyen_mon_dialog.py
# TODO: implement
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QTextEdit, QPushButton, QCheckBox, QMessageBox)

class ToChuyenMonDialog(QDialog):
    def __init__(self, parent=None, to=None):
        super().__init__(parent)
        self.to = to
        self.setWindowTitle("Sửa tổ chuyên môn" if to else "Thêm tổ chuyên môn")
        self.setFixedWidth(400)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Mã tổ
        lbl_ma = QLabel("Mã tổ *")
        self.inp_ma = QLineEdit()
        self.inp_ma.setPlaceholderText("VD: TOAN, LY, VAN...")
        
        # Tên tổ
        lbl_ten = QLabel("Tên tổ *")
        self.inp_ten = QLineEdit()
        self.inp_ten.setPlaceholderText("VD: Tổ Toán, Tổ Văn...")
        
        # Mô tả
        lbl_mota = QLabel("Mô tả")
        self.inp_mota = QTextEdit()
        self.inp_mota.setMaximumHeight(80)
        
        # Trạng thái
        self.chk_active = QCheckBox("Hoạt động")
        self.chk_active.setChecked(True)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_ok = QPushButton("Lưu")
        btn_cancel = QPushButton("Hủy")
        btn_ok.clicked.connect(self._on_accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        
        # Add widgets
        layout.addWidget(lbl_ma)
        layout.addWidget(self.inp_ma)
        layout.addWidget(lbl_ten)
        layout.addWidget(self.inp_ten)
        layout.addWidget(lbl_mota)
        layout.addWidget(self.inp_mota)
        layout.addWidget(self.chk_active)
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        if self.to:
            self.inp_ma.setText(self.to.ma_to)
            self.inp_ten.setText(self.to.ten_to)
            self.inp_mota.setText(self.to.mo_ta or "")
            self.chk_active.setChecked(self.to.active)
    
    def _on_accept(self):
        if not self.inp_ma.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã tổ")
            return
        if not self.inp_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên tổ")
            return
        self.accept()
    
    def get_data(self):
        return {
            "ma_to": self.inp_ma.text().strip(),
            "ten_to": self.inp_ten.text().strip(),
            "mo_ta": self.inp_mota.toPlainText().strip(),
            "active": self.chk_active.isChecked()
        }