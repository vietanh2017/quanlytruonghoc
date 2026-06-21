from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QAbstractItemView, QHeaderView, QLabel
)
from PySide6.QtCore import Qt
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.dialogs.tiet_hoc_dialog import TietHocDialog

class TietHocTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        tb = QHBoxLayout()
        self.btn_them = QPushButton("+ Thêm tiết")
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
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Thứ tự", "Tên tiết", "Bắt đầu", "Kết thúc"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._sua)
        layout.addWidget(self.table)
    
    def _load(self):
        r = self.svc.lay_ds_tiet_hoc()
        if r.ok:
            self._render(r.data)
    
    def _render(self, data):
        self.table.setRowCount(0)
        for row, item in enumerate(data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.so_thu_tu)))
            self.table.setItem(row, 2, QTableWidgetItem(item.ten_tiet))
            self.table.setItem(row, 3, QTableWidgetItem(item.thoi_gian_bat_dau or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item.thoi_gian_ket_thuc or ""))
            self.table.item(row, 0).setData(Qt.UserRole, item.id)
        self.lbl_count.setText(f"{len(data)} tiết học")
    
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
        dlg = TietHocDialog(self)
        if dlg.exec() == TietHocDialog.Accepted:
            r = self.svc.them_tiet_hoc(**dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _sua(self):
        id = self._get_selected_id()
        if not id:
            return
        item = self.svc.tiet_hoc_repo.get_by_id(id)
        dlg = TietHocDialog(self, tiet_hoc=item)
        if dlg.exec() == TietHocDialog.Accepted:
            r = self.svc.sua_tiet_hoc(id, **dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _xoa(self):
        id = self._get_selected_id()
        if not id:
            return
        reply = QMessageBox.question(self, "Xác nhận", "Xóa tiết học này?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.xoa_tiet_hoc(id)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)