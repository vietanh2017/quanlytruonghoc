# modules\cau_hinh\dialogs\nam_hoc_dialog.py
# TODO: implement
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QCheckBox, QMessageBox)

class NamHocDialog(QDialog):
    def __init__(self, parent=None, nam_hoc=None):
        super().__init__(parent)
        self.nam_hoc = nam_hoc
        self.setWindowTitle("Sửa năm học" if nam_hoc else "Thêm năm học")
        self.setFixedWidth(350)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Tên năm học
        lbl_ten = QLabel("Tên năm học")
        self.inp_ten = QLineEdit()
        self.inp_ten.setPlaceholderText("VD: 2024-2025")
        
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
        layout.addWidget(lbl_ten)
        layout.addWidget(self.inp_ten)
        layout.addWidget(self.chk_active)
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        if self.nam_hoc:
            self.inp_ten.setText(self.nam_hoc.ten_nam_hoc)
            self.chk_active.setChecked(self.nam_hoc.active)
    
    def _on_accept(self):
        if not self.inp_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên năm học")
            return
        self.accept()
    
    def get_data(self):
        return {
            "ten_nam_hoc": self.inp_ten.text().strip(),
            "active": self.chk_active.isChecked()
        }