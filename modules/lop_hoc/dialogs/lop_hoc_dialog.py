from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt


class LopHocDialog(QDialog):
    def __init__(self, parent=None, lop=None, ds_gv=None, ds_nam_hoc=None):
        super().__init__(parent)

        self.lop = lop
        self.ds_gv = ds_gv or []
        self.ds_nam_hoc = ds_nam_hoc or []

        self.setWindowTitle("Sửa lớp học" if lop else "Thêm lớp học")
        self.setMinimumWidth(420)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Mã lớp
        lbl_ma = QLabel("Mã lớp *")
        self.inp_ma = QLineEdit()
        
        # Tên lớp
        lbl_ten = QLabel("Tên lớp *")
        self.inp_ten = QLineEdit()
        
        # Khối
        lbl_khoi = QLabel("Khối")
        self.cmb_khoi = QComboBox()
        for k in [6, 7, 8, 9]:
            self.cmb_khoi.addItem(str(k), k)
        
        # Sĩ số - THÊM MỚI
        lbl_si_so = QLabel("Sĩ số")
        self.inp_si_so = QLineEdit()
        self.inp_si_so.setPlaceholderText("0")
        
        # GVCN
        lbl_gv = QLabel("GVCN")
        self.cmb_gv = QComboBox()
        self.cmb_gv.addItem("-- Chọn giáo viên --", None)
        for gv in self.ds_gv:
            ten = gv.nguoi_dung.ho_ten
            self.cmb_gv.addItem(f"{gv.ma_giao_vien} - {ten}", gv.id)
        
        # Năm học
        lbl_nh = QLabel("Năm học")
        self.cmb_nh = QComboBox()
        self.cmb_nh.addItem("-- Chọn năm học --", None)
        for nh in self.ds_nam_hoc:
            self.cmb_nh.addItem(nh.ten_nam_hoc, nh.id)
        
        # Trạng thái
        self.chk_active = QCheckBox("Hoạt động")
        self.chk_active.setChecked(True)
        
        # Buttons
        row_btn = QHBoxLayout()
        row_btn.addStretch()
        btn_ok = QPushButton("Lưu")
        btn_cancel = QPushButton("Huỷ")
        btn_ok.clicked.connect(self._on_accept)
        btn_cancel.clicked.connect(self.reject)
        row_btn.addWidget(btn_ok)
        row_btn.addWidget(btn_cancel)
        
        # Add widgets
        for w in [lbl_ma, self.inp_ma, lbl_ten, self.inp_ten, 
                  lbl_khoi, self.cmb_khoi, lbl_si_so, self.inp_si_so,
                  lbl_gv, self.cmb_gv, lbl_nh, self.cmb_nh, 
                  self.chk_active]:
            layout.addWidget(w)
        layout.addLayout(row_btn)

    def _load_data(self):
        if not self.lop:
            return
        
        self.inp_ma.setText(self.lop.ma_lop)
        self.inp_ten.setText(self.lop.ten_lop)
        self.inp_si_so.setText(str(self.lop.si_so or 0))
        
        idx = self.cmb_khoi.findData(self.lop.khoi)
        if idx >= 0:
            self.cmb_khoi.setCurrentIndex(idx)
        
        idx = self.cmb_gv.findData(self.lop.giao_vien_cn_id)
        if idx >= 0:
            self.cmb_gv.setCurrentIndex(idx)
        
        idx = self.cmb_nh.findData(self.lop.nam_hoc_id)
        if idx >= 0:
            self.cmb_nh.setCurrentIndex(idx)
        
        self.chk_active.setChecked(self.lop.active)

    def _on_accept(self):
        if not self.inp_ma.text().strip():
            QMessageBox.warning(self, "Lỗi", "Chưa nhập mã lớp.")
            return
        if not self.inp_ten.text().strip():
            QMessageBox.warning(self, "Lỗi", "Chưa nhập tên lớp.")
            return
        
        self.accept()

    def get_data(self):
        si_so_str = self.inp_si_so.text().strip()
        si_so = int(si_so_str) if si_so_str.isdigit() else 0
        
        return {
            "ma_lop": self.inp_ma.text().strip(),
            "ten_lop": self.inp_ten.text().strip(),
            "khoi": self.cmb_khoi.currentData(),
            "si_so": si_so,
            "giao_vien_cn_id": self.cmb_gv.currentData(),
            "nam_hoc_id": self.cmb_nh.currentData(),
            "active": self.chk_active.isChecked(),
        }