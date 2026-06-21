# modules/cau_hinh/views/mon_hoc_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox,
    QAbstractItemView, QHeaderView, QLabel, QSpinBox, QDialog,
    QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt
from modules.cau_hinh.service import CauHinhService
from modules.cau_hinh.dialogs.mon_hoc_dialog import MonHocDialog


class SoTietDialog(QDialog):
    """Dialog nhập số tiết cho từng khối"""
    def __init__(self, parent=None, mon_hoc=None, khoi=None, so_tiet_hien_tai=0):
        super().__init__(parent)
        self.mon_hoc = mon_hoc
        self.khoi = khoi
        self.setWindowTitle(f"Nhập số tiết - {mon_hoc.ten_mon} - Khối {khoi}")
        self.setMinimumWidth(300)
        self._build_ui(so_tiet_hien_tai)
    
    def _build_ui(self, so_tiet_hien_tai):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.spin_tiet = QSpinBox()
        self.spin_tiet.setRange(0, 35)
        self.spin_tiet.setValue(so_tiet_hien_tai)
        self.spin_tiet.setSuffix(" tiết/tuần")
        form.addRow("Số tiết:", self.spin_tiet)
        
        layout.addLayout(form)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_so_tiet(self):
        return self.spin_tiet.value()


class MonHocTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_them = QPushButton("+ Thêm môn học")
        self.btn_sua = QPushButton("✏ Sửa thông tin")
        self.btn_xoa = QPushButton("🗑 Xóa môn")
        self.btn_so_tiet = QPushButton("📊 Số tiết theo khối")
        
        self.btn_sua.setEnabled(False)
        self.btn_xoa.setEnabled(False)
        self.btn_so_tiet.setEnabled(False)
        
        self.btn_them.clicked.connect(self._them)
        self.btn_sua.clicked.connect(self._sua)
        self.btn_xoa.clicked.connect(self._xoa)
        self.btn_so_tiet.clicked.connect(self._nhap_so_tiet)
        
        tb.addWidget(self.btn_them)
        tb.addWidget(self.btn_sua)
        tb.addWidget(self.btn_xoa)
        tb.addWidget(self.btn_so_tiet)
        tb.addStretch()
        
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: gray; font-size: 13px;")
        tb.addWidget(self.lbl_count)
        
        layout.addLayout(tb)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Mã môn", "Tên môn", "Tổ CM", "Số tiết theo khối", "Trạng thái"])
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tree.itemSelectionChanged.connect(self._on_selection)
        self.tree.itemDoubleClicked.connect(self._sua)
        layout.addWidget(self.tree)
    
    def _load(self):
        r = self.svc.lay_ds_mon_hoc()
        if r.ok:
            self._render_tree(r.data)
    
    def _render_tree(self, data):
        self.tree.clear()
        
        for mon in data:
            # Lấy số tiết theo khối
            so_tiet_str = self._format_so_tiet(mon)
            
            item = QTreeWidgetItem([
                mon.ma_mon,
                mon.ten_mon,
                mon.to_chuyen_mon.ten_to if mon.to_chuyen_mon else "—",
                so_tiet_str,
                "✓" if mon.active else "✗"
            ])
            item.setData(0, Qt.UserRole, mon.id)
            self.tree.addTopLevelItem(item)
        
        self.lbl_count.setText(f"{len(data)} môn học")
    
    def _format_so_tiet(self, mon):
        """Định dạng hiển thị số tiết"""
        so_tiet_list = self.svc.lay_so_tiet_theo_khoi(mon.id)
        if not so_tiet_list:
            return "Chưa cấu hình"
        
        parts = [f"Khối {k}: {t} tiết" for k, t in so_tiet_list.items()]
        return ", ".join(parts)
    
    def _on_selection(self):
        has = bool(self.tree.selectedItems())
        self.btn_sua.setEnabled(has)
        self.btn_xoa.setEnabled(has)
        self.btn_so_tiet.setEnabled(has)
    
    def _get_selected_id(self):
        item = self.tree.currentItem()
        if item:
            return item.data(0, Qt.UserRole)
        return None
    
    def _them(self):
        r = self.svc.lay_ds_to_chuyen_mon()
        ds_to = r.data if r.ok else []
        
        dlg = MonHocDialog(self, ds_to=ds_to)
        if dlg.exec() == MonHocDialog.Accepted:
            r = self.svc.them_mon_hoc(**dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _sua(self):
        mon_id = self._get_selected_id()
        if not mon_id:
            return
        
        mon = self.svc.mon_hoc_repo.get_by_id(mon_id)
        r = self.svc.lay_ds_to_chuyen_mon()
        ds_to = r.data if r.ok else []
        
        dlg = MonHocDialog(self, mon_hoc=mon, ds_to=ds_to)
        if dlg.exec() == MonHocDialog.Accepted:
            r = self.svc.sua_mon_hoc(mon_id, **dlg.get_data())
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _xoa(self):
        mon_id = self._get_selected_id()
        if not mon_id:
            return
        
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa môn học này?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.xoa_mon_hoc(mon_id)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    
    def _nhap_so_tiet(self):
        """Nhập số tiết cho từng khối của môn học"""
        mon_id = self._get_selected_id()
        if not mon_id:
            return
        
        mon = self.svc.mon_hoc_repo.get_by_id(mon_id)
        
        # Lấy số tiết hiện tại
        so_tiet_hien_tai = self.svc.lay_so_tiet_theo_khoi(mon_id)
        
        # Tạo dialog cho từng khối 6,7,8,9
        for khoi in [6, 7, 8, 9]:
            so_tiet = so_tiet_hien_tai.get(khoi, 0)
            dlg = SoTietDialog(self, mon, khoi, so_tiet)
            if dlg.exec() == SoTietDialog.Accepted:
                so_tiet_moi = dlg.get_so_tiet()
                r = self.svc.cap_nhat_so_tiet(mon_id, khoi, so_tiet_moi)
                if not r.ok:
                    QMessageBox.warning(self, "Lỗi", r.error)
        
        self._load()
        QMessageBox.information(self, "Thành công", "Đã cập nhật số tiết theo khối")