from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt
from typing import Optional

from core.db.models import GiaoVien, ToChuyenMon
from shared.enums import Role

ROLE_LABELS = {
    Role.GIAO_VIEN:      "Giáo viên",
    Role.TO_TRUONG:      "Tổ trưởng",
    Role.TONG_PHU_TRACH: "Tổng phụ trách",
    Role.ADMIN:          "Admin",
    Role.NHAN_VIEN:      "Nhân viên", 
}

BTN_PRIMARY = """
    QPushButton {
        background: #1D9E75; color: white;
        border-radius: 6px; padding: 7px 24px;
        font-size: 13px; font-weight: 600;
    }
    QPushButton:hover   { background: #0F6E56; }
    QPushButton:pressed { background: #0a4f3e; }
"""
BTN_SECONDARY = """
    QPushButton {
        background: #F0F0F0; color: #333;
        border-radius: 6px; padding: 7px 24px;
        font-size: 13px;
    }
    QPushButton:hover { background: #E0E0E0; }
"""


class GiaoVienDialog(QDialog):
    def __init__(self, parent=None,
                 gv: Optional[GiaoVien] = None,
                 ds_to: list[ToChuyenMon] = None):
        super().__init__(parent)
        self._gv    = gv
        self._ds_to = ds_to or []
        self.setWindowTitle("Sửa giáo viên" if gv else "Thêm giáo viên")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()
        if gv:
            self._fill_data(gv)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Thêm giáo viên mới" if not self._gv
                        else "Sửa thông tin giáo viên")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1A1A2E;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #E8E8E8; margin: 10px 0 14px 0;")
        layout.addWidget(line)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setSpacing(10)
        form.setContentsMargins(0, 0, 0, 16)

        def inp(placeholder):
            w = QLineEdit()
            w.setPlaceholderText(placeholder)
            w.setFixedHeight(34)
            w.setStyleSheet("""
                QLineEdit {
                    border: 1.5px solid #D8D8D8; border-radius: 6px;
                    padding: 0 10px; font-size: 13px; background: white;
                }
                QLineEdit:focus { border-color: #1D9E75; }
            """)
            return w

        cmb_style = """
            QComboBox {
                border: 1.5px solid #D8D8D8; border-radius: 6px;
                padding: 0 10px; font-size: 13px;
                background: white; height: 34px;
            }
            QComboBox:focus { border-color: #1D9E75; }
            QComboBox::drop-down { border: none; width: 24px; }
        """

        self.inp_hoten  = inp("Nguyễn Văn A")
        self.inp_email  = inp("giaovien@truong.edu.vn")
        self.inp_magv   = inp("GV001")
        self.inp_monday = inp("Toán, Lý...")
        self.inp_sdt    = inp("0901234567")

        # Tổ chuyên môn
        self.cmb_to = QComboBox()
        self.cmb_to.setStyleSheet(cmb_style)
        self.cmb_to.addItem("-- Chưa phân tổ --", None)
        for to in self._ds_to:
            self.cmb_to.addItem(to.ten_to, to.id)

        # Vai trò
        self.cmb_role = QComboBox()
        self.cmb_role.setStyleSheet(cmb_style)
        for role, label in ROLE_LABELS.items():
            self.cmb_role.addItem(label, role)

        # Trạng thái hoạt động
        self.chk_active = QCheckBox("Hoạt động")
        self.chk_active.setChecked(True)

        lbl_s = "font-size: 13px; font-weight: 500; color: #333;"
        form.addRow(self._lbl("Họ và tên *", lbl_s), self.inp_hoten)
        form.addRow(self._lbl("Email *",     lbl_s), self.inp_email)
        form.addRow(self._lbl("Mã GV *",     lbl_s), self.inp_magv)
        form.addRow(self._lbl("Môn dạy",     lbl_s), self.inp_monday)
        form.addRow(self._lbl("SĐT",         lbl_s), self.inp_sdt)
        form.addRow(self._lbl("Tổ CM",       lbl_s), self.cmb_to)
        form.addRow(self._lbl("Vai trò",     lbl_s), self.cmb_role)
        form.addRow(self._lbl("Trạng thái",  lbl_s), self.chk_active)

        # Mật khẩu chỉ khi thêm mới
        if not self._gv:
            self.inp_matkhau = inp("Để trống → dùng mặc định: eduschool@123")
            self.inp_matkhau.setEchoMode(QLineEdit.Password)
            form.addRow(self._lbl("Mật khẩu", lbl_s), self.inp_matkhau)
        else:
            self.inp_matkhau = None

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_luu = QPushButton("Lưu" if self._gv else "Thêm giáo viên")
        self.btn_luu.setStyleSheet(BTN_PRIMARY)
        self.btn_luu.clicked.connect(self._on_accept)
        btn_row.addWidget(self.btn_luu)
        btn_huy = QPushButton("Huỷ")
        btn_huy.setStyleSheet(BTN_SECONDARY)
        btn_huy.clicked.connect(self.reject)
        btn_row.addWidget(btn_huy)
        layout.addLayout(btn_row)

    def _lbl(self, text, style=""):
        l = QLabel(text)
        l.setStyleSheet(style)
        return l

    def _fill_data(self, gv: GiaoVien):
        self.inp_hoten.setText(gv.nguoi_dung.ho_ten)
        self.inp_email.setText(gv.nguoi_dung.email)
        self.inp_magv.setText(gv.ma_giao_vien)
        self.inp_monday.setText(gv.mon_day or "")
        self.inp_sdt.setText(gv.so_dien_thoai or "")
        self.chk_active.setChecked(gv.active)
        
        for i in range(self.cmb_to.count()):
            if self.cmb_to.itemData(i) == gv.to_id:
                self.cmb_to.setCurrentIndex(i)
                break
        for i in range(self.cmb_role.count()):
            if self.cmb_role.itemData(i) == gv.nguoi_dung.role:
                self.cmb_role.setCurrentIndex(i)
                break

    def _on_accept(self):
        errors = []
        if not self.inp_hoten.text().strip():
            errors.append("Họ tên không được để trống.")
        if not self.inp_email.text().strip():
            errors.append("Email không được để trống.")
        elif "@" not in self.inp_email.text():
            errors.append("Email không hợp lệ.")
        if not self.inp_magv.text().strip():
            errors.append("Mã GV không được để trống.")
        if errors:
            QMessageBox.warning(self, "Thiếu thông tin", "\n".join(errors))
            return
        self.accept()

    def get_data(self):
        data = {
            "ma_gv": self.inp_magv.text().strip(),
            "ho_ten": self.inp_hoten.text().strip(),
            "email": self.inp_email.text().strip(),
            "mon_day": self.inp_monday.text().strip(),
            "to_id": self.cmb_to.currentData(),
            "so_dien_thoai": self.inp_sdt.text().strip(),
            "active": self.chk_active.isChecked(),
            "role": self.cmb_role.currentData()
        }
        
        # Chỉ thêm mat_khau nếu có (khi thêm mới)
        if self.inp_matkhau:
            data["mat_khau"] = self.inp_matkhau.text().strip()
        
        return data