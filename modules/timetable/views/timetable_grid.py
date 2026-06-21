from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QLabel, QMessageBox, QHeaderView,
    QAbstractItemView, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class TimetableGrid(QWidget):
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}  # {(thu, tiet): mon_hoc_id, giao_vien_id}
        self._ds_mon = []
        self._ds_giao_vien = []
        self._tiet_list = []
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_clear = QPushButton("🗑 Xóa tất cả")
        self.btn_clear.clicked.connect(self._clear_all)
        tb.addStretch()
        tb.addWidget(self.btn_clear)
        layout.addLayout(tb)
        
        # Bảng TKB
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Thứ 2 -> Chủ nhật
        headers = ["Tiết", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table)
    
    def set_data(self, ds_mon, ds_giao_vien, tiet_list, tkb_data=None):
        """Khởi tạo dữ liệu cho grid"""
        self._ds_mon = ds_mon
        self._ds_giao_vien = ds_giao_vien
        self._tiet_list = tiet_list
        
        # Khởi tạo data structure
        self._data = {}
        if tkb_data:
            for item in tkb_data:
                key = (item.thu, item.tiet_bat_dau)
                self._data[key] = {
                    'mon_hoc_id': item.mon_hoc_id,
                    'giao_vien_id': item.giao_vien_id,
                    'phong_hoc': item.phong_hoc
                }
        
        self._render_grid()
    
    def _render_grid(self):
        """Vẽ bảng TKB"""
        self.table.setRowCount(len(self._tiet_list) + 1)  # +1 cho header cột Tiết
        
        # Cột đầu tiên: số tiết
        for i, tiet in enumerate(self._tiet_list, 1):
            item = QTableWidgetItem(f"Tiết {tiet.so_thu_tu}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QColor("#F5F5F5"))
            self.table.setVerticalHeaderItem(i-1, item)
        
        # Các ô còn lại
        for thu in range(2, 9):  # 2: Thứ 2, 8: Chủ nhật
            for tiet_idx, tiet in enumerate(self._tiet_list):
                key = (thu, tiet.so_thu_tu)
                self._create_cell_widget(tiet_idx, thu - 1, key)
    
    def _create_cell_widget(self, row, col, key):
        """Tạo widget cho mỗi ô"""
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Combo chọn môn
        cmb_mon = QComboBox()
        cmb_mon.addItem("-- Chọn môn --", None)
        for mon in self._ds_mon:
            cmb_mon.addItem(f"{mon.ma_mon} - {mon.ten_mon}", mon.id)
        
        # Combo chọn giáo viên
        cmb_gv = QComboBox()
        cmb_gv.addItem("-- Chọn GV --", None)
        for gv in self._ds_giao_vien:
            cmb_gv.addItem(f"{gv.ma_giao_vien} - {gv.nguoi_dung.ho_ten}", gv.id)
        
        # Phòng học
        txt_phong = QLineEdit()
        txt_phong.setPlaceholderText("Phòng")
        txt_phong.setFixedWidth(60)
        
        # Lấy dữ liệu cũ nếu có
        if key in self._data:
            data = self._data[key]
            if data['mon_hoc_id']:
                idx = cmb_mon.findData(data['mon_hoc_id'])
                if idx >= 0:
                    cmb_mon.setCurrentIndex(idx)
            if data['giao_vien_id']:
                idx = cmb_gv.findData(data['giao_vien_id'])
                if idx >= 0:
                    cmb_gv.setCurrentIndex(idx)
            txt_phong.setText(data.get('phong_hoc', ''))
        
        # Lưu dữ liệu khi thay đổi
        def save_data():
            mon_id = cmb_mon.currentData()
            gv_id = cmb_gv.currentData()
            
            if mon_id and gv_id:
                self._data[key] = {
                    'mon_hoc_id': mon_id,
                    'giao_vien_id': gv_id,
                    'phong_hoc': txt_phong.text()
                }
            elif key in self._data:
                del self._data[key]
            self.data_changed.emit()
        
        cmb_mon.currentIndexChanged.connect(save_data)
        cmb_gv.currentIndexChanged.connect(save_data)
        txt_phong.textChanged.connect(save_data)
        
        layout.addWidget(cmb_mon)
        layout.addWidget(cmb_gv)
        layout.addWidget(txt_phong)
        
        self.table.setCellWidget(row, col, widget)
    
    def _clear_all(self):
        """Xóa tất cả dữ liệu"""
        reply = QMessageBox.question(self, "Xác nhận", "Xóa toàn bộ thời khóa biểu?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._data.clear()
            self._render_grid()
            self.data_changed.emit()
    
    def get_data(self):
        """Lấy dữ liệu TKB dạng list"""
        result = []
        for (thu, tiet), data in self._data.items():
            result.append({
                'thu': thu,
                'tiet_bat_dau': tiet,
                'mon_hoc_id': data['mon_hoc_id'],
                'giao_vien_id': data['giao_vien_id'],
                'phong_hoc': data.get('phong_hoc', '')
            })
        return result