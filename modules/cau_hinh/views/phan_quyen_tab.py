# modules\cau_hinh\views\phan_quyen_tab.py
# TODO: implement
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QAbstractItemView, QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal
from modules.cau_hinh.service import CauHinhService
from shared.enums import Role

ROLE_LABEL = {
    Role.ADMIN: "Admin",
    Role.TO_TRUONG: "Tổ trưởng",
    Role.PHO_TO_TRUONG: "Phó tổ trưởng", 
    Role.TONG_PHU_TRACH: "Tổng phụ trách",
    Role.GIAO_VIEN: "Giáo viên",
}


class PhanQuyenTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.svc = CauHinhService(session)
        self._build_ui()
        self._load()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        tb = QHBoxLayout()
        
        self.cmb_vai_tro = QComboBox()
        self.cmb_vai_tro.setFixedWidth(150)
        self.cmb_vai_tro.addItem("-- Chọn vai trò --", None)
        for role, label in ROLE_LABEL.items():
            self.cmb_vai_tro.addItem(label, role)
        self.cmb_vai_tro.currentIndexChanged.connect(self._on_vai_tro_changed)
        
        self.btn_luu = QPushButton("💾 Lưu phân quyền")
        self.btn_luu.clicked.connect(self._luu_phan_quyen)
        self.btn_luu.setObjectName("btn_primary")
        
        tb.addWidget(QLabel("Vai trò:"))
        tb.addWidget(self.cmb_vai_tro)
        tb.addStretch()
        tb.addWidget(self.btn_luu)
        
        layout.addLayout(tb)
        
        # Tree hiển thị quyền
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Module", "Quyền", "Mô tả", "Đã chọn"])
        self.tree.setSelectionMode(QAbstractItemView.NoSelection)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.setColumnWidth(3, 80)
        layout.addWidget(self.tree)
    
    def _load(self):
        # Load danh sách quyền
        r = self.svc.lay_ds_quyen()
        if r.ok:
            self._all_quyen = r.data
            self._load_tree()
    
    def _load_tree(self):
        self.tree.clear()
        
        # Nhóm quyền theo module
        modules = {}
        for q in self._all_quyen:
            if q.module not in modules:
                modules[q.module] = []
            modules[q.module].append(q)
        
        for module, quyen_list in modules.items():
            module_item = QTreeWidgetItem([module, "", "", ""])
            module_item.setFlags(module_item.flags() & ~Qt.ItemIsSelectable)
            module_item.setExpanded(True)
            
            for quyen in quyen_list:
                # Kiểm tra xem vai trò hiện tại có quyền này không
                is_checked = self._check_vai_tro_co_quyen(quyen.id)
                
                item = QTreeWidgetItem([
                    "",
                    quyen.ten_quyen,
                    quyen.mo_ta or "",
                    "✓" if is_checked else ""
                ])
                item.setData(0, Qt.UserRole, quyen.id)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(3, Qt.Checked if is_checked else Qt.Unchecked)
                module_item.addChild(item)
            
            self.tree.addTopLevelItem(module_item)
    
    def _on_vai_tro_changed(self):
        """Khi chọn vai trò khác, reload tree với quyền tương ứng"""
        self._load_tree()
    
    def _check_vai_tro_co_quyen(self, quyen_id):
        """Kiểm tra vai trò hiện tại có quyền này không"""
        vai_tro = self.cmb_vai_tro.currentData()
        if not vai_tro:
            return False
        return self.svc.kiem_tra_vai_tro_co_quyen(vai_tro, quyen_id)
    
    def _luu_phan_quyen(self):
        """Lưu phân quyền cho vai trò"""
        vai_tro = self.cmb_vai_tro.currentData()
        if not vai_tro:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn vai trò")
            return
        
        # Lấy danh sách quyền đã chọn
        quyen_ids = []
        for i in range(self.tree.topLevelItemCount()):
            module_item = self.tree.topLevelItem(i)
            for j in range(module_item.childCount()):
                child = module_item.child(j)
                if child.checkState(3) == Qt.Checked:
                    quyen_id = child.data(0, Qt.UserRole)
                    if quyen_id:
                        quyen_ids.append(quyen_id)
        
        # Lưu
        r = self.svc.phan_quyen_cho_vai_tro(vai_tro, quyen_ids)
        if r.ok:
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)