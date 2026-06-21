from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QMenu
)
from PySide6.QtCore import Qt
from modules.lop_hoc.dialogs.hoc_sinh_dialog import HocSinhDialog


class HocSinhPanel(QWidget):
    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self.svc = svc
        self._lop_id = None
        self._lop_ten = ""
        self._ds = []

        # Buttons được set từ bên ngoài
        self.btn_them = None
        self.btn_sua = None
        self.btn_xoa = None
        self.btn_excel = None
        self.lbl_title = None
        self.lbl_count = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "STT", "Mã HS", "Họ và tên", "Ngày sinh", "Giới tính", "SĐT"
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 35)
        self.table.setColumnWidth(1, 65)
        self.table.setColumnWidth(3, 85)
        self.table.setColumnWidth(4, 65)
        self.table.setColumnWidth(5, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._on_sua)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #DDD;
                gridline-color: #E8E8E8;
                font-size: 12px;
            }
            QHeaderView::section {
                background: #1D9E75; color: white;
                font-weight: 600; font-size: 12px;
                padding: 5px; border: none;
            }
            QTableWidget::item:alternate { background: #F9F9F9; }
            QTableWidget::item:selected { background: #D0EDE4; color: #000; }
        """)
        layout.addWidget(self.table)

    def set_external_buttons(self, btn_them, btn_sua, btn_xoa, btn_excel, lbl_title, lbl_count):
        self.btn_them  = btn_them
        self.btn_sua   = btn_sua
        self.btn_xoa   = btn_xoa
        self.btn_excel = btn_excel
        self.lbl_title = lbl_title
        self.lbl_count = lbl_count

        self.btn_them.clicked.connect(self._on_them)
        self.btn_sua.clicked.connect(self._on_sua)
        self.btn_xoa.clicked.connect(self._show_delete_options) 
        self.btn_excel.clicked.connect(self._on_import_excel)

    def load_lop(self, lop_id, ten_lop):
        self._lop_id  = lop_id
        self._lop_ten = ten_lop
        self._load()

    def _load(self):
        if not self._lop_id:
            return
        r = self.svc.lay_ds_hoc_sinh(self._lop_id)
        if not r.ok:
            QMessageBox.critical(self, "Lỗi", r.error)
            return
        self._ds = r.data or []
        self._render()

    def _render(self):
        self.table.setRowCount(0)
        for i, hs in enumerate(self._ds):
            self.table.insertRow(i)
            stt = QTableWidgetItem(str(i + 1))
            stt.setTextAlignment(Qt.AlignCenter)
            stt.setData(Qt.UserRole, hs.id)
            self.table.setItem(i, 0, stt)
            self.table.setItem(i, 1, QTableWidgetItem(hs.ma_hoc_sinh or ""))
            self.table.setItem(i, 2, QTableWidgetItem(hs.ho_ten or ""))
            ns = hs.ngay_sinh.strftime("%d/%m/%Y") if hs.ngay_sinh else ""
            item_ns = QTableWidgetItem(ns)
            item_ns.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, item_ns)
            gt = QTableWidgetItem("Nam" if hs.gioi_tinh else "Nữ")
            gt.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, gt)
            self.table.setItem(i, 5, QTableWidgetItem(hs.so_dien_thoai or ""))

        if self.lbl_count:
            self.lbl_count.setText(f"{len(self._ds)} học sinh")
        self._update_buttons()

    def _on_selection(self):
        self._update_buttons()

    def _update_buttons(self):
        has = self.table.currentRow() >= 0 and len(self.table.selectedItems()) > 0
        if self.btn_sua:
            self.btn_sua.setEnabled(has)
        if self.btn_xoa:
            self.btn_xoa.setEnabled(len(self._ds) > 0)  # ← SỬA: xoá toàn bộ vẫn cần bật nút

    def _sel_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _on_them(self):
        if not self._lop_id:
            return
        dlg = HocSinhDialog(self)
        if dlg.exec() != HocSinhDialog.Accepted:
            return
        data = dlg.get_data()
        data["lop_hoc_id"] = self._lop_id
        r = self.svc.them_hoc_sinh(**data)
        if r.ok:
            self._load()
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)

    def _on_sua(self):
        hs_id = self._sel_id()
        if not hs_id:
            return
        hs = self.svc.hs_repo.get_by_id(hs_id)
        if not hs:
            return
        dlg = HocSinhDialog(self, hoc_sinh=hs)
        if dlg.exec() != HocSinhDialog.Accepted:
            return
        r = self.svc.sua_hoc_sinh(hs_id, **dlg.get_data())
        if r.ok:
            self._load()
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Lỗi", r.error)

    def _on_xoa(self):
        hs_id = self._sel_id()
        if not hs_id:
            return
        hs = self.svc.hs_repo.get_by_id(hs_id)
        ten = hs.ho_ten if hs else "học sinh này"
        reply = QMessageBox.question(self, "Xác nhận",
            f"Xóa học sinh {ten}?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        r = self.svc.xoa_hoc_sinh(hs_id)
        if r.ok:
            self._load()
        else:
            QMessageBox.warning(self, "Lỗi", r.error)
            
    def _show_delete_options(self):
        """Hiển thị menu lựa chọn xoá học sinh"""
        if not self._lop_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn lớp học trước!")
            return
        
        if len(self._ds) == 0:
            QMessageBox.information(self, "Thông báo", f"Lớp {self._lop_ten} hiện không có học sinh nào!")
            return
        
        # Tạo menu context
        menu = QMenu(self)
        
        # Tuỳ chọn 1: Xoá học sinh đang chọn
        menu.addAction("🗑️ Xoá học sinh đã chọn").triggered.connect(self._on_xoa)
        
        menu.addSeparator()
        
        # Tuỳ chọn 2: Xoá toàn bộ học sinh trong lớp
        menu.addAction(f"⚠️ Xoá TOÀN BỘ học sinh lớp {self._lop_ten}").triggered.connect(self._on_delete_all)
        
        # Hiển thị menu tại vị trí nút xoá
        menu.exec(self.btn_xoa.mapToGlobal(self.btn_xoa.rect().bottomLeft()))

    def _on_delete_all(self):
        """Xoá toàn bộ học sinh trong lớp"""
        total = len(self._ds)
        
        # Hộp thoại xác nhận
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("⚠️ Xác nhận xoá toàn bộ")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(f"Bạn sắp xoá TOÀN BỘ {total} học sinh của lớp {self._lop_ten}!")
        msg_box.setInformativeText("Hành động này KHÔNG THỂ khôi phục.\n\nBạn có chắc chắn muốn tiếp tục?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("✅ Có, xoá tất cả")
        msg_box.button(QMessageBox.No).setText("❌ Không, giữ lại")
        
        reply = msg_box.exec()
        
        if reply != QMessageBox.Yes:
            return
        
        # Xác nhận lần 2: nhập tên lớp
        from PySide6.QtWidgets import QInputDialog
        confirm_text, ok = QInputDialog.getText(
            self, 
            "Xác nhận lần cuối", 
            f"Nhập tên lớp '{self._lop_ten}' để xác nhận xoá toàn bộ học sinh:"
        )
        
        if not ok or confirm_text.strip() != self._lop_ten:
            QMessageBox.information(self, "Đã huỷ", "Thao tác xoá toàn bộ đã bị huỷ.")
            return
        
        # Thực hiện xoá
        try:
            r = self.svc.xoa_toan_bo_hoc_sinh(self._lop_id)
            if r.ok:
                QMessageBox.information(self, "Thành công", f"Đã xoá toàn bộ {total} học sinh của lớp {self._lop_ten}!")
                self._load()
            else:
                QMessageBox.critical(self, "Lỗi", r.error)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xoá: {str(e)}")
    def _on_import_excel(self):
        if not self._lop_id:
            return
        from modules.lop_hoc.dialogs.import_excel_dialog import ImportExcelDialog, MODE_REPLACE

        # Truyền số học sinh hiện có để dialog hiển thị cảnh báo chính xác
        dlg = ImportExcelDialog(
            self,
            ten_lop=self._lop_ten,
            existing_count=len(self._ds),
        )
        if dlg.exec() != ImportExcelDialog.Accepted:
            return

        rows = dlg.get_rows()
        mode = dlg.get_mode()
        if not rows:
            return

        so_them, so_cap_nhat, so_bo_qua, errors = self.svc.import_hoc_sinh_excel(
            self._lop_id, rows, mode
        )

        # Thông báo kết quả theo mode
        if mode == MODE_REPLACE:
            msg = f"✅ Đã xóa danh sách cũ và import {so_them} học sinh mới!"
        else:
            msg = f"✅ Thêm mới: {so_them}"
            if so_cap_nhat:
                msg += f"  |  🔄 Cập nhật: {so_cap_nhat}"

        if so_bo_qua:
            msg += f"\n⚠️ Bỏ qua {so_bo_qua} dòng lỗi."
        if errors:
            msg += "\n\nChi tiết lỗi:\n" + "\n".join(errors[:5])

        QMessageBox.information(self, "Kết quả import", msg)
        self._load()