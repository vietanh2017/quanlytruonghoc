from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class LopHocTable(QWidget):
    selection_changed = Signal(object)
    double_clicked = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_id = None
        
        self._build_ui()
        self._setup_table()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
    def _setup_table(self):
        headers = ["STT", "Mã lớp", "Tên lớp", "Khối", "Sĩ số", "GVCN", "Năm học", "Trạng thái"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        # Độ rộng cột
        self.table.setColumnWidth(0, 40)   # STT
        self.table.setColumnWidth(1, 55)   # Mã lớp
        self.table.setColumnWidth(2, 50)   # Tên lớp (cố định)
        self.table.setColumnWidth(3, 50)   # Khối
        self.table.setColumnWidth(4, 50)   # Sĩ số
        self.table.setColumnWidth(6, 85)   # Năm học
        self.table.setColumnWidth(7, 90)   # Trạng thái

        # Cột Tên lớp cố định, không co giãn
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)

        # Cột GVCN co giãn linh hoạt
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

        # Tắt stretch cho cột cuối
        self.table.horizontalHeader().setStretchLastSection(False)

        # Style
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

        # Kết nối signals
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._on_double_click)
        
    def load_data(self, data):
        """Load dữ liệu vào bảng"""
        self.table.setRowCount(0)
        
        for i, row in enumerate(data):
            self.table.insertRow(i)
            
            # STT
            self._set_item(i, 0, str(i + 1), Qt.AlignCenter)
            
            # Mã lớp
            self._set_item(i, 1, row.ma_lop, Qt.AlignCenter)
            
            # Tên lớp
            self._set_item(i, 2, row.ten_lop)
            
            # Khối
            self._set_item(i, 3, str(row.khoi), Qt.AlignCenter)
            
            # Sĩ số
            self._set_item(i, 4, str(row.si_so or 0), Qt.AlignCenter)
            
            # GVCN - Lấy từ relationship nếu có
            gvcn = "—"
            if hasattr(row, 'giao_vien_cn') and row.giao_vien_cn:
                if hasattr(row.giao_vien_cn, 'nguoi_dung'):
                    gvcn = row.giao_vien_cn.nguoi_dung.ho_ten
            self._set_item(i, 5, gvcn)
            
          # Năm học - hiển thị tên
            nam_hoc = row.nam_hoc_obj.ten_nam_hoc if row.nam_hoc_obj and row.nam_hoc_obj.ten_nam_hoc else ""
            self._set_item(i, 6, nam_hoc)
            
            # Trạng thái
            tt_item = QTableWidgetItem("✓ Hoạt động" if row.active else "✗ Vô hiệu")
            tt_item.setTextAlignment(Qt.AlignCenter)
            tt_item.setForeground(QColor("#0F6E56") if row.active else QColor("#993C1D"))
            self.table.setItem(i, 7, tt_item)
            
            # Lưu ID vào item STT
            self.table.item(i, 0).setData(Qt.UserRole, row.id)
            
    def _set_item(self, row, col, text, align=Qt.AlignLeft | Qt.AlignVCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        self.table.setItem(row, col, item)
        
    def _on_selection(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self._selected_id = self.table.item(row, 0).data(Qt.UserRole)
            # THÊM DÒNG NÀY - phát signal với ID
            self.selection_changed.emit(self._selected_id)
        else:
            self._selected_id = None
            self.selection_changed.emit(None)
            
    def _on_double_click(self):
        if self._selected_id:
            self.double_clicked.emit(self._selected_id)
            
    def get_selected_id(self):
        return self._selected_id
        
    def clear_selection(self):
        self.table.clearSelection()
        self._selected_id = None