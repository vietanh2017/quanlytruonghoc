from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDialogButtonBox,
    QDateEdit
)
from PySide6.QtCore import QDate


class HocSinhDialog(QDialog):
    def __init__(self, parent=None, hoc_sinh=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm học sinh" if not hoc_sinh else "Sửa học sinh")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.inp_ma = QLineEdit()
        self.inp_ma.setPlaceholderText("VD: HS001")

        self.inp_ten = QLineEdit()
        self.inp_ten.setPlaceholderText("Họ và tên đầy đủ")

        self.inp_ngay_sinh = QDateEdit()
        self.inp_ngay_sinh.setCalendarPopup(True)
        self.inp_ngay_sinh.setDisplayFormat("dd/MM/yyyy")
        self.inp_ngay_sinh.setDate(QDate(2010, 1, 1))

        self.cmb_gioi_tinh = QComboBox()
        self.cmb_gioi_tinh.addItem("Nam", True)
        self.cmb_gioi_tinh.addItem("Nữ", False)

        self.inp_sdt = QLineEdit()
        self.inp_sdt.setPlaceholderText("SĐT phụ huynh")

        form.addRow("Mã học sinh: *", self.inp_ma)
        form.addRow("Họ và tên: *", self.inp_ten)
        form.addRow("Ngày sinh:", self.inp_ngay_sinh)
        form.addRow("Giới tính:", self.cmb_gioi_tinh)
        form.addRow("Số điện thoại:", self.inp_sdt)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._validate)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        # Load dữ liệu nếu sửa
        if hoc_sinh:
            self.inp_ma.setText(hoc_sinh.ma_hoc_sinh or "")
            self.inp_ten.setText(hoc_sinh.ho_ten or "")
            if hoc_sinh.ngay_sinh:
                self.inp_ngay_sinh.setDate(QDate(
                    hoc_sinh.ngay_sinh.year,
                    hoc_sinh.ngay_sinh.month,
                    hoc_sinh.ngay_sinh.day
                ))
            idx = self.cmb_gioi_tinh.findData(hoc_sinh.gioi_tinh)
            if idx >= 0:
                self.cmb_gioi_tinh.setCurrentIndex(idx)
            self.inp_sdt.setText(hoc_sinh.so_dien_thoai or "")

    def _validate(self):
        if not self.inp_ma.text().strip():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã học sinh!")
            return
        if not self.inp_ten.text().strip():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên!")
            return
        self.accept()

    def get_data(self):
        from datetime import date
        d = self.inp_ngay_sinh.date()
        return {
            "ma_hoc_sinh": self.inp_ma.text().strip(),
            "ho_ten": self.inp_ten.text().strip(),
            "ngay_sinh": date(d.year(), d.month(), d.day()),
            "gioi_tinh": self.cmb_gioi_tinh.currentData(),
            "so_dien_thoai": self.inp_sdt.text().strip() or None,
        }