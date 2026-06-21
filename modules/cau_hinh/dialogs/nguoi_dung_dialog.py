# modules\cau_hinh\dialogs\nguoi_dung_dialog.py
# TODO: implement
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QCheckBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from shared.enums import Role

ROLE_CHOICES = {
    Role.ADMIN: "Admin",
    Role.GIAO_VIEN: "Giáo viên",
    Role.TO_TRUONG: "Tổ trưởng",
    Role.PHO_TO_TRUONG: "Phó tổ trưởng",
    Role.TONG_PHU_TRACH: "Tổng phụ trách",
}


class NguoiDungDialog(QDialog):
    def __init__(self, parent=None, nguoi_dung=None):
        super().__init__(parent)
        self.nguoi_dung = nguoi_dung
        self.setWindowTitle("Sửa tài khoản" if nguoi_dung else "Thêm tài khoản")
        self.setMinimumWidth(400)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Họ tên
        self.inp_ho_ten = QLineEdit()
        form.addRow("Họ tên *:", self.inp_ho_ten)
        
        # Email
        self.inp_email = QLineEdit()
        form.addRow("Email *:", self.inp_email)
        
        # Vai trò
        self.cmb_role = QComboBox()
        for role, label in ROLE_CHOICES.items():
            self.cmb_role.addItem(label, role)
        form.addRow("Vai trò:", self.cmb_role)
        
        # Mật khẩu (chỉ hiện khi thêm mới)
        if not self.nguoi_dung:
            self.inp_mat_khau = QLineEdit()
            self.inp_mat_khau.setPlaceholderText("Để trống → dùng mặc định: eduschool@123")
            self.inp_mat_khau.setEchoMode(QLineEdit.Password)
            form.addRow("Mật khẩu:", self.inp_mat_khau)
        
        # Trạng thái
        self.chk_active = QCheckBox("Hoạt động")
        self.chk_active.setChecked(True)
        form.addRow("", self.chk_active)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_ok = QPushButton("Lưu")
        btn_cancel = QPushButton("Hủy")
        btn_ok.clicked.connect(self._on_accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        if self.nguoi_dung:
            self.inp_ho_ten.setText(self.nguoi_dung.ho_ten)
            self.inp_email.setText(self.nguoi_dung.email)
            idx = self.cmb_role.findData(self.nguoi_dung.role)
            if idx >= 0:
                self.cmb_role.setCurrentIndex(idx)
            self.chk_active.setChecked(self.nguoi_dung.active)
    
    def _on_accept(self):
        if not self.inp_ho_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên")
            return
        if not self.inp_email.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email")
            return
        self.accept()
    
    def get_data(self):
        data = {
            "ho_ten": self.inp_ho_ten.text().strip(),
            "email": self.inp_email.text().strip(),
            "role": self.cmb_role.currentData(),
            "active": self.chk_active.isChecked()
        }
        
        if hasattr(self, 'inp_mat_khau') and self.inp_mat_khau:
            data["mat_khau"] = self.inp_mat_khau.text().strip()
        
        return data