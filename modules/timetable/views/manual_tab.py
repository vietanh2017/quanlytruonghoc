# modules/timetable/views/manual_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QMessageBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QComboBox as QTableComboBox
)
from PySide6.QtCore import Qt, Signal
from core.db.session import SessionLocal
from modules.timetable.service import TimetableService


class ManualTimetableTab(QWidget):
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = SessionLocal()
        self.svc = TimetableService(self.session)
        self._current_tkb_data = {}
        self._ds_mon = []
        self._ds_giao_vien = []
        self._tiet_list = []
        self._build_ui()
        self._load_filters()
    
    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Bộ lọc
        filter_group = QGroupBox("Chọn lớp và học kỳ")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Lớp học:"))
        self.cmb_lop = QComboBox()
        self.cmb_lop.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_lop)
        
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(130)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_nam_hoc_changed)
        filter_layout.addWidget(self.cmb_nam_hoc)
        
        filter_layout.addWidget(QLabel("Học kỳ:"))
        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.setMinimumWidth(100)
        filter_layout.addWidget(self.cmb_hoc_ky)
        
        self.btn_load = QPushButton("📅 Tải TKB")
        self.btn_save = QPushButton("💾 Lưu TKB")
        self.btn_clear = QPushButton("🗑 Xóa tất cả")
        self.btn_save.setEnabled(False)
        
        filter_layout.addWidget(self.btn_load)
        filter_layout.addWidget(self.btn_save)
        filter_layout.addWidget(self.btn_clear)
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Bảng TKB
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Tiết", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.itemDoubleClicked.connect(self._on_cell_double_click)
        layout.addWidget(self.table)
        
        # Kết nối sự kiện
        self.btn_load.clicked.connect(self._load)
        self.btn_save.clicked.connect(self._save)
        self.btn_clear.clicked.connect(self._clear_all)
    
    def _load_filters(self):
        # Load lớp
        ds_lop = self.svc.lay_ds_lop()
        for lop in ds_lop:
            self.cmb_lop.addItem(f"{lop.ma_lop} - {lop.ten_lop}", lop.id)
        
        # Load năm học
        from core.db.models.nam_hoc import NamHoc
        ds_nam_hoc = self.session.query(NamHoc).filter(NamHoc.active == True).all()
        for nh in ds_nam_hoc:
            self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
        
        # Load danh sách môn và GV
        self._ds_mon = self.svc.lay_ds_mon()
        self._ds_giao_vien = self.svc.lay_ds_giao_vien()
        self._tiet_list = self.svc.lay_tiet_hoc_list()
    
    def _on_nam_hoc_changed(self):
        self.cmb_hoc_ky.clear()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if nam_hoc_id:
            from core.db.models.hoc_ky import HocKy
            ds_hoc_ky = self.session.query(HocKy).filter(
                HocKy.nam_hoc_id == nam_hoc_id,
                HocKy.active == True
            ).all()
            for hk in ds_hoc_ky:
                self.cmb_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)
    
    def _load(self):
        lop_id = self.cmb_lop.currentData()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()
        
        if not lop_id or not nam_hoc_id or not hoc_ky_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đầy đủ thông tin")
            return
        
        r = self.svc.lay_tkb_theo_lop(lop_id, nam_hoc_id, hoc_ky_id)
        
        if r.ok:
            self._render_timetable(r.data)
            self.btn_save.setEnabled(True)
            QMessageBox.information(self, "Thành công", "Đã tải thời khóa biểu")
        else:
            self._render_empty()
            QMessageBox.warning(self, "Lỗi", r.error)
    
    def _render_timetable(self, tkb_data):
        """Hiển thị TKB lên bảng"""
        self.table.setRowCount(len(self._tiet_list))
        
        # Cột tiết
        for i, tiet in enumerate(self._tiet_list):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(f"Tiết {tiet.so_thu_tu}"))
            self.table.setRowHeight(i, 60)
        
        # Lưu dữ liệu để dễ truy xuất
        self._current_tkb_data = {}
        for pc in tkb_data:
            thu = pc.thu
            tiet = pc.tiet_bat_dau
            self._current_tkb_data[(thu, tiet)] = {
                'id': pc.id,
                'mon_hoc_id': pc.mon_hoc_id,
                'giao_vien_id': pc.giao_vien_id,
                'phong_hoc': pc.phong_hoc
            }
        
        # Đổ dữ liệu vào bảng
        for i, tiet in enumerate(self._tiet_list):
            for col, thu in enumerate([2, 3, 4, 5, 6, 7, 8], start=1):
                key = (thu, tiet.so_thu_tu)
                if key in self._current_tkb_data:
                    data = self._current_tkb_data[key]
                    mon = self._get_mon_by_id(data['mon_hoc_id'])
                    gv = self._get_gv_by_id(data['giao_vien_id'])
                    text = f"{mon.ten_mon if mon else '?'}\n{gv.nguoi_dung.ho_ten if gv else '?'}"
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, col, item)
                else:
                    self.table.setItem(i, col, QTableWidgetItem(""))
    
    def _render_empty(self):
        """Hiển thị bảng trống"""
        self.table.setRowCount(len(self._tiet_list))
        for i, tiet in enumerate(self._tiet_list):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(f"Tiết {tiet.so_thu_tu}"))
            for col in range(1, 8):
                self.table.setItem(i, col, QTableWidgetItem(""))
        self._current_tkb_data = {}
    
    def _get_mon_by_id(self, mon_id):
        for mon in self._ds_mon:
            if mon.id == mon_id:
                return mon
        return None
    
    def _get_gv_by_id(self, gv_id):
        for gv in self._ds_giao_vien:
            if gv.id == gv_id:
                return gv
        return None
    
    def _on_cell_double_click(self, item):
        """Xử lý double click để chỉnh sửa ô"""
        row = item.row()
        col = item.column()
        if col == 0:  # Cột tiết không cho sửa
            return
        
        thu = [2, 3, 4, 5, 6, 7, 8][col - 1]
        tiet = self._tiet_list[row].so_thu_tu
        key = (thu, tiet)
        
        # Tạo dialog nhập liệu
        self._show_edit_dialog(row, col, key)
    
    def _show_edit_dialog(self, row, col, key):
        """Hiển thị dialog chỉnh sửa"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Chỉnh sửa thời khóa biểu")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Combo môn học
        cmb_mon = QComboBox()
        cmb_mon.addItem("-- Chọn môn --", None)
        for mon in self._ds_mon:
            cmb_mon.addItem(f"{mon.ma_mon} - {mon.ten_mon}", mon.id)
        
        # Combo giáo viên
        cmb_gv = QComboBox()
        cmb_gv.addItem("-- Chọn giáo viên --", None)
        for gv in self._ds_giao_vien:
            cmb_gv.addItem(f"{gv.ma_giao_vien} - {gv.nguoi_dung.ho_ten}", gv.id)
        
        # Lấy dữ liệu cũ nếu có
        if key in self._current_tkb_data:
            data = self._current_tkb_data[key]
            idx = cmb_mon.findData(data['mon_hoc_id'])
            if idx >= 0:
                cmb_mon.setCurrentIndex(idx)
            idx = cmb_gv.findData(data['giao_vien_id'])
            if idx >= 0:
                cmb_gv.setCurrentIndex(idx)
        
        form.addRow("Môn học:", cmb_mon)
        form.addRow("Giáo viên:", cmb_gv)
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Lưu")
        btn_cancel = QPushButton("Hủy")
        btn_clear = QPushButton("Xóa")
        
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        def clear_cell():
            if key in self._current_tkb_data:
                del self._current_tkb_data[key]
            self.table.setItem(row, col, QTableWidgetItem(""))
            dialog.accept()
        
        btn_clear.clicked.connect(clear_cell)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.Accepted:
            mon_id = cmb_mon.currentData()
            gv_id = cmb_gv.currentData()
            
            if mon_id and gv_id:
                mon = self._get_mon_by_id(mon_id)
                gv = self._get_gv_by_id(gv_id)
                text = f"{mon.ten_mon}\n{gv.nguoi_dung.ho_ten}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
                
                self._current_tkb_data[key] = {
                    'mon_hoc_id': mon_id,
                    'giao_vien_id': gv_id,
                    'phong_hoc': ''
                }
            else:
                # Xóa nếu không chọn
                if key in self._current_tkb_data:
                    del self._current_tkb_data[key]
                self.table.setItem(row, col, QTableWidgetItem(""))
            
            self.btn_save.setEnabled(True)
    
    def _clear_all(self):
        """Xóa toàn bộ TKB"""
        reply = QMessageBox.question(self, "Xác nhận", "Xóa toàn bộ thời khóa biểu?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._current_tkb_data = {}
            for row in range(self.table.rowCount()):
                for col in range(1, 8):
                    self.table.setItem(row, col, QTableWidgetItem(""))
            self.btn_save.setEnabled(True)
    
    def _save(self):
        """Lưu TKB vào database"""
        lop_id = self.cmb_lop.currentData()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()
        
        if not lop_id or not nam_hoc_id or not hoc_ky_id:
            return
        
        # Chuyển đổi dữ liệu
        tkb_list = []
        for (thu, tiet), data in self._current_tkb_data.items():
            tkb_list.append({
                'thu': thu,
                'tiet_bat_dau': tiet,
                'mon_hoc_id': data['mon_hoc_id'],
                'giao_vien_id': data['giao_vien_id'],
                'phong_hoc': data.get('phong_hoc', '')
            })
        
        r = self.svc.luu_tkb(lop_id, nam_hoc_id, hoc_ky_id, tkb_list)
        
        if r.ok:
            QMessageBox.information(self, "Thành công", r.error)
            self.btn_save.setEnabled(False)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)