# modules\cau_hinh\views\nam_hoc_tab.py
# TODO: implement
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QMessageBox, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, Signal
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.dialogs.nam_hoc_dialog import NamHocDialog

class NamHocTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_them = QPushButton("+ Thêm năm học")
        self.btn_sua = QPushButton("✏ Sửa")
        self.btn_xoa = QPushButton("🗑 Xóa")
        self.btn_sua.setEnabled(False)
        self.btn_xoa.setEnabled(False)
        
        self.btn_them.clicked.connect(self._them)
        self.btn_them.setObjectName("btn_primary")
        self.btn_sua.clicked.connect(self._sua)
        self.btn_sua.setObjectName("btn_warning")
        self.btn_xoa.clicked.connect(self._xoa)
        self.btn_xoa.setObjectName("btn_danger")
        
        tb.addWidget(self.btn_them)
        tb.addWidget(self.btn_sua)
        tb.addWidget(self.btn_xoa)
        tb.addStretch()
        layout.addLayout(tb)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Tên năm học", "Trạng thái"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_selection)
        layout.addWidget(self.table)
    
    def _load(self):
        r = self.svc.lay_ds_nam_hoc()
        if r.ok:
            self._render(r.data)
    
    def _render(self, data):
        self.table.setRowCount(0)
        for row, item in enumerate(data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.ten_nam_hoc))
            status = "✓ Hoạt động" if item.active else "✗ Không hoạt động"
            self.table.setItem(row, 2, QTableWidgetItem(status))
            self.table.item(row, 0).setData(Qt.UserRole, item.id)
    
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
        dlg = NamHocDialog(self)
        if dlg.exec() == NamHocDialog.Accepted:
            r = self.svc.them_nam_hoc(**dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _sua(self):
        id = self._get_selected_id()
        if not id:
            return
        
        # Lấy đối tượng năm học
        nam_hoc = self.svc.nam_hoc_repo.get_by_id(id)
        dlg = NamHocDialog(self, nam_hoc=nam_hoc)
        if dlg.exec() == NamHocDialog.Accepted:
            r = self.svc.sua_nam_hoc(id, **dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _xoa(self):
        id = self._get_selected_id()
        if not id:
            return
        
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.xoa_nam_hoc(id)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)