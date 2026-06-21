from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QCheckBox, QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

class LichHocTuanDialog(QDialog):
    def __init__(self, parent=None, nam_hoc_id=None, hoc_ky_id=None, lich_hien_tai=None):
        super().__init__(parent)
        self.nam_hoc_id = nam_hoc_id
        self.hoc_ky_id = hoc_ky_id
        self.setWindowTitle("Cấu hình lịch học trong tuần")
        self.setMinimumWidth(400)
        self._build_ui(lich_hien_tai)
    
    def _build_ui(self, lich_hien_tai):
        layout = QVBoxLayout(self)
        
        # Chuyển đổi dữ liệu hiện tại thành dict
        lich_dict = {}
        for item in lich_hien_tai or []:
            lich_dict[item.thu] = (item.co_sang, item.co_chieu)
        
        # Tạo form cho từng thứ
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        thu_nums = [2, 3, 4, 5, 6, 7, 8]
        
        self.checkboxes = {}
        
        for day, thu in zip(days, thu_nums):
            group = QGroupBox(day)
            group_layout = QHBoxLayout(group)
            
            co_sang, co_chieu = lich_dict.get(thu, (True, False))
            
            cb_sang = QCheckBox("Học sáng")
            cb_sang.setChecked(co_sang)
            cb_chieu = QCheckBox("Học chiều")
            cb_chieu.setChecked(co_chieu)
            
            group_layout.addWidget(cb_sang)
            group_layout.addWidget(cb_chieu)
            group_layout.addStretch()
            
            layout.addWidget(group)
            self.checkboxes[thu] = (cb_sang, cb_chieu)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_ok = QPushButton("Lưu")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
    
    def get_data(self):
        """Trả về danh sách các bản ghi để lưu"""
        result = []
        for thu, (cb_sang, cb_chieu) in self.checkboxes.items():
            result.append({
                'nam_hoc_id': self.nam_hoc_id,
                'hoc_ky_id': self.hoc_ky_id,
                'thu': thu,
                'co_sang': cb_sang.isChecked(),
                'co_chieu': cb_chieu.isChecked()
            })
        return result
    
    def get_lich_dict(self):
        """Trả về dict {thu: (co_sang, co_chieu)}"""
        result = {}
        for thu, (cb_sang, cb_chieu) in self.checkboxes.items():
            result[thu] = (cb_sang.isChecked(), cb_chieu.isChecked())
        return result