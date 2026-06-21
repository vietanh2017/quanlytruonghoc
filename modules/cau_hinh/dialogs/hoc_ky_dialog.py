from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QCheckBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

class HocKyDialog(QDialog):
    def __init__(self, parent=None, hoc_ky=None, ds_nam_hoc=None):
        super().__init__(parent)
        self.hoc_ky = hoc_ky
        self.ds_nam_hoc = ds_nam_hoc or []
        self.setWindowTitle("Sửa học kỳ" if hoc_ky else "Thêm học kỳ")
        self.setMinimumWidth(350)
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Năm học
        self.cmb_nam_hoc = QComboBox()
        for nh in self.ds_nam_hoc:
            self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
        form.addRow("Năm học:", self.cmb_nam_hoc)
        
        # Chọn học kỳ (I hoặc II)
        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.addItem("Học kỳ I", 1)
        self.cmb_hoc_ky.addItem("Học kỳ II", 2)
        form.addRow("Học kỳ:", self.cmb_hoc_ky)
        
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
        if self.hoc_ky:
            # Chọn năm học
            idx = self.cmb_nam_hoc.findData(self.hoc_ky.nam_hoc_id)
            if idx >= 0:
                self.cmb_nam_hoc.setCurrentIndex(idx)
            
            # Chọn học kỳ (1 hoặc 2)
            idx = self.cmb_hoc_ky.findData(self.hoc_ky.so_thu_tu)
            if idx >= 0:
                self.cmb_hoc_ky.setCurrentIndex(idx)
            
            self.chk_active.setChecked(self.hoc_ky.active)
    
    def _on_accept(self):
        if not self.cmb_nam_hoc.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn năm học")
            return
        self.accept()
    
    def get_data(self):
        so_thu_tu = self.cmb_hoc_ky.currentData()
        ten_hoc_ky = "Học kỳ I" if so_thu_tu == 1 else "Học kỳ II"
        
        return {
            "ten_hoc_ky": ten_hoc_ky,
            "nam_hoc_id": self.cmb_nam_hoc.currentData(),
            "so_thu_tu": so_thu_tu,
            "active": self.chk_active.isChecked()
        }