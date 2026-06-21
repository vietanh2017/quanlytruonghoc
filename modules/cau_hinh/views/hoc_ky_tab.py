# modules\cau_hinh\views\hoc_ky_tab.py
# TODO: implement
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QAbstractItemView, QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.dialogs.hoc_ky_dialog import HocKyDialog


class HocKyTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_them = QPushButton("+ Thêm học kỳ")
        self.btn_sua = QPushButton("✏ Sửa")
        self.btn_xoa = QPushButton("🗑 Xóa")
        self.btn_sua.setEnabled(False)
        self.btn_xoa.setEnabled(False)
        
        self.btn_them.clicked.connect(self._them)
        self.btn_sua.clicked.connect(self._sua)
        self.btn_xoa.clicked.connect(self._xoa)
        
        tb.addWidget(self.btn_them)
        tb.addWidget(self.btn_sua)
        tb.addWidget(self.btn_xoa)
        tb.addStretch()
        
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: gray; font-size: 13px;")
        tb.addWidget(self.lbl_count)
        
        layout.addLayout(tb)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tên học kỳ", "Năm học", "Thứ tự", "Trạng thái"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._sua)
        layout.addWidget(self.table)
    
    def _load(self):
        r = self.svc.lay_ds_hoc_ky()
        if r.ok:
            self._render(r.data)
    
    def _render(self, data):
        self.table.setRowCount(0)
        for row, item in enumerate(data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.ten_hoc_ky))
            
            ten_nam_hoc = item.nam_hoc.ten_nam_hoc if item.nam_hoc else ""
            self.table.setItem(row, 2, QTableWidgetItem(ten_nam_hoc))
            
            self.table.setItem(row, 3, QTableWidgetItem(str(item.so_thu_tu)))
            
            status = "✓ Hoạt động" if item.active else "✗ Vô hiệu"
            self.table.setItem(row, 4, QTableWidgetItem(status))
            self.table.item(row, 0).setData(Qt.UserRole, item.id)
        
        self.lbl_count.setText(f"{len(data)} học kỳ")
    
    def _on_selection(self):
        has = bool(self.table.selectedItems())
        self.btn_sua.setEnabled(has)
        self.btn_xoa.setEnabled(has)
    
    def _get_selected_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole)
        return None
    
    def _them(self):
        # Lấy danh sách năm học
        r = self.svc.lay_ds_nam_hoc()
        ds_nam_hoc = r.data if r.ok else []
        
        dlg = HocKyDialog(self, ds_nam_hoc=ds_nam_hoc)
        if dlg.exec() == HocKyDialog.Accepted:
            r = self.svc.them_hoc_ky(**dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _sua(self):
        id = self._get_selected_id()
        if not id:
            return
        
        hk = self.svc.hoc_ky_repo.get_by_id(id)
        r = self.svc.lay_ds_nam_hoc()
        ds_nam_hoc = r.data if r.ok else []
        
        dlg = HocKyDialog(self, hoc_ky=hk, ds_nam_hoc=ds_nam_hoc)
        if dlg.exec() == HocKyDialog.Accepted:
            r = self.svc.sua_hoc_ky(id, **dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _xoa(self):
        id = self._get_selected_id()
        if not id:
            return
        
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa học kỳ này?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.xoa_hoc_ky(id)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)