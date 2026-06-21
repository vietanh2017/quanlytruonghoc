# modules/phan_cong/dialogs/phan_cong_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QLabel, QMessageBox,
    QFrame, QDialogButtonBox, QCheckBox, QListWidget,
    QListWidgetItem, QWidget, QScrollArea, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QInputDialog

class PhanCongDialog(QDialog):
    def __init__(self, parent=None,
                 ds_nam_hoc=None, ds_hoc_ky=None,
                 ds_giao_vien=None, ds_mon_hoc=None,
                 ds_lop_hoc=None,
                 phan_cong_hien_tai=None,
                 lay_phan_cong_theo_gv_func=None):
        super().__init__(parent)
        self.ds_nam_hoc = ds_nam_hoc or []
        self.ds_hoc_ky = ds_hoc_ky or []
        self.ds_giao_vien = ds_giao_vien or []
        self.ds_mon_hoc = ds_mon_hoc or []
        self.ds_lop_hoc = ds_lop_hoc or []
        self.pc_hien_tai = phan_cong_hien_tai or []
        self.lay_phan_cong_theo_gv_func = lay_phan_cong_theo_gv_func
        self._selected_data = {}  # {mon_id: set(lop_ids)}
        self._mon_name_cache = {}  # {mon_id: display_name}

        self.setWindowTitle("Phân công giảng dạy")
        self.setMinimumWidth(850)
        self.setMinimumHeight(650)
        self.setModal(True)
        self._build_ui()
        self._connect_signals()
        self._on_nam_hoc_changed()
        QTimer.singleShot(100, self._fill_hien_tai)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Phần trên
        top = QFormLayout()
        top.setSpacing(8)

        self.cmb_gv = QComboBox()
        self.cmb_gv.setMinimumWidth(280)
        for gv in self.ds_giao_vien:
            ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
            self.cmb_gv.addItem(f"{gv.ma_giao_vien} – {ten}", gv.id)
        top.addRow("Giáo viên:", self.cmb_gv)

        row_nhhk = QHBoxLayout()
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(130)
        for nh in self.ds_nam_hoc:
            self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)

        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.setMinimumWidth(130)
        self.cmb_hoc_ky.setEnabled(False)

        row_nhhk.addWidget(self.cmb_nam_hoc)
        row_nhhk.addWidget(QLabel("Học kỳ:"))
        row_nhhk.addWidget(self.cmb_hoc_ky)
        row_nhhk.addStretch()
        top.addRow("Năm học:", row_nhhk)

        self.chk_clear_old = QCheckBox("Xóa tất cả phân công cũ trước khi lưu")
        self.chk_clear_old.setChecked(False)
        top.addRow("", self.chk_clear_old)

        layout.addLayout(top)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#E4E8F0; max-height:1px;")
        layout.addWidget(sep)

        # Phần chính
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)

        # Bên trái: Danh sách môn học
        left_group = QGroupBox("Danh sách môn học")
        left_layout = QVBoxLayout(left_group)

        self.list_mon = QListWidget()
        self.list_mon.setMinimumWidth(200)
        self.list_mon.setMaximumWidth(250)
        self.list_mon.itemSelectionChanged.connect(self._on_mon_selected)
        left_layout.addWidget(self.list_mon)

        btn_them_mon = QPushButton("➕ Thêm môn")
        btn_them_mon.clicked.connect(self._them_mon)
        left_layout.addWidget(btn_them_mon)

        btn_xoa_mon = QPushButton("🗑 Xóa môn")
        btn_xoa_mon.clicked.connect(self._xoa_mon)
        left_layout.addWidget(btn_xoa_mon)

        main_layout.addWidget(left_group)

        # Bên phải: Checkbox lớp
        right_group = QGroupBox("Chọn lớp")
        right_layout = QVBoxLayout(right_group)

        self.lbl_mon_name = QLabel("Chọn môn học từ danh sách bên trái")
        self.lbl_mon_name.setStyleSheet("font-weight: bold; color: #1D9E75;")
        right_layout.addWidget(self.lbl_mon_name)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(400)

        self.lop_container = QWidget()
        self.lop_layout = QVBoxLayout(self.lop_container)
        self.lop_layout.setSpacing(10)
        self.lop_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll.setWidget(self.lop_container)

        right_layout.addWidget(self.scroll)
        main_layout.addWidget(right_group, stretch=1)

        layout.addLayout(main_layout)

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("💾 Lưu phân công")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _connect_signals(self):
        self.cmb_gv.currentIndexChanged.connect(self._load_phan_cong_hien_tai)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_nam_hoc_changed)
        self.cmb_hoc_ky.currentIndexChanged.connect(self._load_phan_cong_hien_tai)

    def _on_nam_hoc_changed(self):
        self.cmb_hoc_ky.clear()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if not nam_hoc_id:
            self.cmb_hoc_ky.setEnabled(False)
            return

        hoc_ky_list = [hk for hk in self.ds_hoc_ky if hk.nam_hoc_id == nam_hoc_id]
        if hoc_ky_list:
            for hk in hoc_ky_list:
                self.cmb_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)
            self.cmb_hoc_ky.setEnabled(True)
        else:
            self.cmb_hoc_ky.addItem("-- Không có học kỳ --", None)
            self.cmb_hoc_ky.setEnabled(False)

        self._load_phan_cong_hien_tai()

    def _clear_lop_layout(self):
        """Xóa toàn bộ layout bên phải an toàn"""
        # Xóa tất cả widget trong lop_container
        for i in reversed(range(self.lop_layout.count())):
            item = self.lop_layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                layout = item.layout()
                # Xóa các widget trong layout con
                for j in reversed(range(layout.count())):
                    sub_item = layout.itemAt(j)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                layout.deleteLater()
        
        # Xóa tất cả item trong layout
        while self.lop_layout.count():
            self.lop_layout.takeAt(0)

    def _load_phan_cong_hien_tai(self):
        gv_id = self.cmb_gv.currentData()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        hoc_ky_id = self.cmb_hoc_ky.currentData()

        if not gv_id or not nam_hoc_id or not hoc_ky_id:
            return

        if self.lay_phan_cong_theo_gv_func:
            ds = self.lay_phan_cong_theo_gv_func(gv_id, nam_hoc_id, hoc_ky_id)
            self._render_phan_cong(ds)
        else:
            # Nếu không có hàm, reset dữ liệu
            self._selected_data = {}
            self._mon_name_cache = {}
            self.list_mon.clear()
            self.lbl_mon_name.setText("Chưa có môn nào. Nhấn 'Thêm môn' để thêm.")
            self._clear_lop_layout()

    def _render_phan_cong(self, ds):
        """Hiển thị phân công hiện tại"""
        # Reset dữ liệu
        self._selected_data = {}
        self._mon_name_cache = {}

        # Gom dữ liệu từ phân công hiện tại
        for pc in ds:
            mon_id = pc.mon_hoc_id if hasattr(pc, 'mon_hoc_id') else pc.get('mon_hoc_id')
            lop_id = pc.lop_hoc_id if hasattr(pc, 'lop_hoc_id') else pc.get('lop_hoc_id')
            if mon_id not in self._selected_data:
                self._selected_data[mon_id] = set()
            self._selected_data[mon_id].add(lop_id)

        # Xóa list môn cũ
        self.list_mon.clear()

        # Thêm các môn đã có
        for mon_id, lop_set in self._selected_data.items():
            for mon in self.ds_mon_hoc:
                if mon.id == mon_id:
                    display = f"{mon.ma_mon} - {mon.ten_mon}"
                    self._mon_name_cache[mon_id] = display
                    item = QListWidgetItem(display)
                    item.setData(Qt.UserRole, mon_id)
                    self.list_mon.addItem(item)
                    break

        # Chọn môn đầu tiên nếu có
        if self.list_mon.count() > 0:
            self.list_mon.setCurrentRow(0)
        else:
            self.lbl_mon_name.setText("Chưa có môn nào. Nhấn 'Thêm môn' để thêm.")
            self._clear_lop_layout()

    def _them_mon(self):
        """Thêm môn mới vào danh sách"""
        # Lấy danh sách môn chưa có
        existing_mon_ids = set(self._selected_data.keys())
        available_mons = [m for m in self.ds_mon_hoc if m.id not in existing_mon_ids]
        
        if not available_mons:
            QMessageBox.information(self, "Thông báo", "Tất cả môn học đã có trong danh sách.")
            return
        
        mon_names = [f"{m.ma_mon} - {m.ten_mon}" for m in available_mons]
        mon_name, ok = QInputDialog.getItem(
            self, "Thêm môn", "Chọn môn học:", mon_names, 0, False)
        
        if ok and mon_name:
            for mon in available_mons:
                if f"{mon.ma_mon} - {mon.ten_mon}" == mon_name:
                    # Thêm vào dữ liệu
                    self._selected_data[mon.id] = set()
                    self._mon_name_cache[mon.id] = mon_name
                    
                    # Thêm vào list
                    item = QListWidgetItem(mon_name)
                    item.setData(Qt.UserRole, mon.id)
                    self.list_mon.addItem(item)
                    
                    # Chọn môn vừa thêm
                    self.list_mon.setCurrentItem(item)
                    break

    def _xoa_mon(self):
        """Xóa môn đang chọn"""
        current = self.list_mon.currentItem()
        if not current:
            return
        
        mon_id = current.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Xác nhận", 
                                      f"Xóa môn '{current.text()}' và toàn bộ phân công của môn này?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Xóa khỏi dữ liệu
            if mon_id in self._selected_data:
                del self._selected_data[mon_id]
            if mon_id in self._mon_name_cache:
                del self._mon_name_cache[mon_id]
            # Xóa khỏi list
            row = self.list_mon.row(current)
            self.list_mon.takeItem(row)
            # Chọn môn khác nếu còn
            if self.list_mon.count() > 0:
                self.list_mon.setCurrentRow(0)
            else:
                self.lbl_mon_name.setText("Chưa có môn nào. Nhấn 'Thêm môn' để thêm.")
                self._clear_lop_layout()

    def _on_mon_selected(self):
        """Khi chọn môn, hiển thị checkbox lớp"""
        current = self.list_mon.currentItem()
        if not current:
            return

        mon_id = current.data(Qt.UserRole)
        mon_name = self._mon_name_cache.get(mon_id, "?")
        
        self.lbl_mon_name.setText(f"Chọn lớp cho môn: {mon_name}")

        # Xóa layout cũ an toàn
        self._clear_lop_layout()

        selected_set = self._selected_data.get(mon_id, set())

        # Gom lớp theo khối
        lops_by_khoi = {}
        for lop in self.ds_lop_hoc:
            khoi = getattr(lop, 'khoi', 6)
            if khoi not in lops_by_khoi:
                lops_by_khoi[khoi] = []
            lops_by_khoi[khoi].append(lop)

        # Tạo container mới
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        for khoi in sorted(lops_by_khoi.keys()):
            # Label khối
            lbl = QLabel(f"Khối {khoi}:")
            lbl.setStyleSheet("font-weight: bold; color: #1D9E75; font-size: 13px;")
            container_layout.addWidget(lbl)

            # Layout cho checkbox
            grid = QGridLayout()
            grid.setSpacing(8)
            grid.setContentsMargins(10, 5, 10, 5)
            
            class_list = sorted(lops_by_khoi[khoi], key=lambda x: x.ten_lop)
            cols = 6
            for idx, lop in enumerate(class_list):
                row = idx // cols
                col = idx % cols
                cb = QCheckBox(lop.ten_lop)
                cb.setProperty("lop_id", lop.id)
                cb.setProperty("mon_id", mon_id)
                cb.setChecked(lop.id in selected_set)
                cb.setStyleSheet("min-width: 55px;")
                cb.stateChanged.connect(self._on_checkbox_changed)
                grid.addWidget(cb, row, col)
            
            container_layout.addLayout(grid)
        
        container_layout.addStretch()
        
        # Xóa widget cũ trong scroll và set widget mới
        old_widget = self.scroll.takeWidget()
        if old_widget:
            old_widget.deleteLater()
        self.scroll.setWidget(container)
    def _on_checkbox_changed(self, checked):
        """Xử lý khi checkbox thay đổi"""
        cb = self.sender()
        mon_id = cb.property("mon_id")
        lop_id = cb.property("lop_id")
        
        if mon_id is None or lop_id is None:
            return
            
        if mon_id not in self._selected_data:
            self._selected_data[mon_id] = set()
        if checked:
            self._selected_data[mon_id].add(lop_id)
        else:
            self._selected_data[mon_id].discard(lop_id)

    def _fill_hien_tai(self):
        self._load_phan_cong_hien_tai()

    def _get_phan_cong_list(self):
        """Lấy danh sách phân công"""
        result = []
        for mon_id, lop_set in self._selected_data.items():
            for lop_id in lop_set:
                result.append({
                    "mon_hoc_id": mon_id,
                    "lop_hoc_id": lop_id
                })
        return result

    def _on_accept(self):
        if not self.cmb_gv.currentData():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn giáo viên.")
            return
        if not self.cmb_hoc_ky.currentData():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn học kỳ.")
            return

        phan_cong_list = self._get_phan_cong_list()
        if not phan_cong_list:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng chọn ít nhất 1 môn và 1 lớp.")
            return

        self.accept()

    def get_data(self):
        return {
            "giao_vien_id": self.cmb_gv.currentData(),
            "nam_hoc_id": self.cmb_nam_hoc.currentData(),
            "hoc_ky_id": self.cmb_hoc_ky.currentData(),
            "phan_cong_list": self._get_phan_cong_list(),
            "clear_old": self.chk_clear_old.isChecked()
        }