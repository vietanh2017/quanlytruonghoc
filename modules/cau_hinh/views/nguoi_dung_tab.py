# modules\cau_hinh\views\nguoi_dung_tab.py
# TODO: implement
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QAbstractItemView, QHeaderView, QLabel
)
from PySide6.QtCore import Qt
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.dialogs.nguoi_dung_dialog import NguoiDungDialog
from shared.enums import Role

ROLE_LABEL = {
    Role.ADMIN: "Admin",
    Role.TO_TRUONG: "Tổ trưởng",
    Role.TONG_PHU_TRACH: "Tổng phụ trách",
    Role.GIAO_VIEN: "Giáo viên",
}


class NguoiDungTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_them = QPushButton("+ Thêm tài khoản")
        self.btn_sua = QPushButton("✏ Sửa")
        self.btn_xoa = QPushButton("🗑 Xóa")
        self.btn_reset_mk = QPushButton("🔑 Đặt lại mật khẩu")
        self.btn_sua.setEnabled(False)
        self.btn_xoa.setEnabled(False)
        self.btn_reset_mk.setEnabled(False)
        
        self.btn_them.clicked.connect(self._them)
        self.btn_them.setObjectName("btn_primary")
        self.btn_sua.clicked.connect(self._sua)
        self.btn_sua.setObjectName("btn_warning")
        self.btn_xoa.clicked.connect(self._xoa)
        self.btn_xoa.setObjectName("btn_danger")
        self.btn_reset_mk.clicked.connect(self._reset_mat_khau)
        self.btn_reset_mk.setObjectName("btn_info")
        
        tb.addWidget(self.btn_them)
        tb.addWidget(self.btn_sua)
        tb.addWidget(self.btn_xoa)
        tb.addWidget(self.btn_reset_mk)
        tb.addStretch()
        
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: gray; font-size: 13px;")
        tb.addWidget(self.lbl_count)
        
        layout.addLayout(tb)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Họ tên", "Email", "Vai trò", "Trạng thái"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._sua)
        layout.addWidget(self.table)
    
    def _load(self):
        r = self.svc.lay_ds_nguoi_dung()
        if r.ok:
            self._render(r.data)
    
    def _render(self, data):
        self.table.setRowCount(0)
        for row, item in enumerate(data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.ho_ten))
            self.table.setItem(row, 2, QTableWidgetItem(item.email))
            self.table.setItem(row, 3, QTableWidgetItem(ROLE_LABEL.get(item.role, str(item.role))))
            
            status = "✓ Hoạt động" if item.active else "✗ Vô hiệu"
            self.table.setItem(row, 4, QTableWidgetItem(status))
            self.table.item(row, 0).setData(Qt.UserRole, item.id)
        
        self.lbl_count.setText(f"{len(data)} tài khoản")
    
    def _on_selection(self):
        has = bool(self.table.selectedItems())
        self.btn_sua.setEnabled(has)
        self.btn_xoa.setEnabled(has)
        self.btn_reset_mk.setEnabled(has)
    
    def _get_selected_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole)
        return None
    
    def _them(self):
        dlg = NguoiDungDialog(self)
        if dlg.exec() == NguoiDungDialog.Accepted:
            r = self.svc.them_nguoi_dung(**dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _sua(self):
        id = self._get_selected_id()
        if not id:
            return
        
        nd = self.svc.nguoi_dung_repo.get_by_id(id)
        dlg = NguoiDungDialog(self, nguoi_dung=nd)
        if dlg.exec() == NguoiDungDialog.Accepted:
            r = self.svc.sua_nguoi_dung(id, **dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _xoa(self):
        id = self._get_selected_id()
        if not id:
            return
        
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa tài khoản này?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.xoa_nguoi_dung(id)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _reset_mat_khau(self):
        id = self._get_selected_id()
        if not id:
            return
        
        reply = QMessageBox.question(self, "Xác nhận", 
                                     "Đặt lại mật khẩu về mặc định (eduschool@123)?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.reset_mat_khau(id)
            if r.ok:
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)