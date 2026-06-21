# modules/giao_vien_thi_dua/views/tabs/quan_ly_tieu_chi_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QPushButton, QLabel,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox,
    QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class QuanLyTieuChiTab(QWidget):
    """Tab quản lý tiêu chí thi đua giáo viên"""
    
    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self.svc = svc
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        
        self.btn_them = QPushButton("➕ Thêm tiêu chí")
        self.btn_them.setFixedHeight(30)
        self.btn_them.clicked.connect(self._them)
        
        self.btn_sua = QPushButton("✏️ Sửa")
        self.btn_sua.setFixedHeight(30)
        self.btn_sua.clicked.connect(self._sua)
        
        self.btn_xoa = QPushButton("🗑️ Xóa")
        self.btn_xoa.setFixedHeight(30)
        self.btn_xoa.clicked.connect(self._xoa)
        
        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setFixedHeight(30)
        self.btn_refresh.clicked.connect(self._load_data)
        
        toolbar.addWidget(self.btn_them)
        toolbar.addWidget(self.btn_sua)
        toolbar.addWidget(self.btn_xoa)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Bảng tiêu chí
        self.table = QTableWidget()
        headers = ["ID", "Mã", "Tên tiêu chí", "Điểm tối đa", "Loại", "Mô tả"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 65)
        self.table.setColumnWidth(2, 280)
        self.table.setColumnWidth(3, 95)
        self.table.setColumnWidth(4, 85)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #DDD;
                gridline-color: #E8E8E8;
                font-size: 12px;
            }
            QHeaderView::section {
                background: #1D9E75; color: white;
                font-weight: 600; font-size: 12px;
                padding: 6px; border: none;
            }
            QTableWidget::item:alternate { background: #F9F9F9; }
            QTableWidget::item:selected { background: #D0EDE4; color: #000; }
        """)
        layout.addWidget(self.table)

    def _load_data(self):
        """Load danh sách tiêu chí"""
        result = self.svc.lay_ds_tieu_chi()
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        
        ds = result.data or []
        self.table.setRowCount(len(ds))
        
        for row, tc in enumerate(ds):
            # ID
            item = QTableWidgetItem(str(tc.id))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)
            
            # Mã
            item = QTableWidgetItem(tc.ma_tieu_chi or "")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item)
            
            # Tên tiêu chí
            self.table.setItem(row, 2, QTableWidgetItem(tc.ten_tieu_chi or ""))
            
            # Điểm tối đa
            item = QTableWidgetItem(f"{tc.diem_toi_da:.1f}")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item)
            
            # Loại
            loai_text = "✅ Cộng" if tc.loai == "cong" else "❌ Trừ"
            item = QTableWidgetItem(loai_text)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item)
            
            # Mô tả
            self.table.setItem(row, 5, QTableWidgetItem(tc.mo_ta or ""))
        
        # Cập nhật status
        vp = sum(1 for tc in ds if tc.loai == "tru")
        tt = sum(1 for tc in ds if tc.loai == "cong")
        #self.parent().status_label.setText(f"📋 Tổng số: {len(ds)} tiêu chí  |  ✅ Cộng: {tt}  |  ❌ Trừ: {vp}")

    def _them(self):
        """Thêm tiêu chí mới"""
        dlg = TieuChiDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        
        # Sinh mã tự động
        ma = self._gen_ma(data['loai'])
        result = self.svc.them_tieu_chi(ma, data['ten'], data['diem'], data['loai'], data['mo_ta'])
        
        if result.ok:
            QMessageBox.information(self, "Thành công", f"Đã thêm tiêu chí: {data['ten']}")
            self._load_data()
            # Refresh tab chấm điểm
            self._refresh_cham_diem_tab()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _sua(self):
        """Sửa tiêu chí"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn tiêu chí!")
            return
        
        tc_id = int(self.table.item(row, 0).text())
        ma = self.table.item(row, 1).text()
        ten = self.table.item(row, 2).text()
        diem = float(self.table.item(row, 3).text())
        loai = "cong" if "Cộng" in self.table.item(row, 4).text() else "tru"
        mo_ta = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
        
        dlg = TieuChiDialog(self, ten=ten, diem=diem, loai=loai, mo_ta=mo_ta)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        
        result = self.svc.sua_tieu_chi(tc_id, 
                                       ten_tieu_chi=data['ten'], 
                                       diem_toi_da=data['diem'], 
                                       loai=data['loai'], 
                                       mo_ta=data['mo_ta'])
        
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã cập nhật tiêu chí!")
            self._load_data()
            self._refresh_cham_diem_tab()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _xoa(self):
        """Xóa tiêu chí"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn tiêu chí!")
            return
        
        ten = self.table.item(row, 2).text()
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                     f"Bạn có chắc muốn xóa tiêu chí:\n{ten}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        tc_id = int(self.table.item(row, 0).text())
        result = self.svc.xoa_tieu_chi(tc_id)
        
        if result.ok:
            QMessageBox.information(self, "Thành công", "Đã xóa tiêu chí!")
            self._load_data()
            self._refresh_cham_diem_tab()
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _gen_ma(self, loai):
        """Sinh mã tự động TCxx"""
        prefix = "TC"
        result = self.svc.lay_ds_tieu_chi()
        ds = result.data or []
        numbers = []
        for tc in ds:
            if tc.ma_tieu_chi and tc.ma_tieu_chi.startswith(prefix):
                try:
                    num = int(tc.ma_tieu_chi[2:])
                    numbers.append(num)
                except:
                    pass
        num = 1
        while num in numbers:
            num += 1
        return f"{prefix}{num:02d}"

    def _refresh_cham_diem_tab(self):
        """Làm mới tab chấm điểm"""
        parent = self.parent()
        if parent and hasattr(parent, 'tab_widget'):
            for i in range(parent.tab_widget.count()):
                tab = parent.tab_widget.widget(i)
                if hasattr(tab, '_load_diem'):
                    tab._load_diem()
                    break


class TieuChiDialog(QDialog):
    """Dialog thêm/sửa tiêu chí"""
    
    def __init__(self, parent=None, ten="", diem=0, loai="cong", mo_ta=""):
        super().__init__(parent)
        self.setWindowTitle("Thêm tiêu chí mới" if not ten else "Sửa tiêu chí")
        self.setMinimumWidth(450)
        self._build_ui(ten, diem, loai, mo_ta)

    def _build_ui(self, ten, diem, loai, mo_ta):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        form = QFormLayout()
        form.setSpacing(10)
        
        # Tên tiêu chí
        self.txt_ten = QLineEdit()
        self.txt_ten.setText(ten)
        self.txt_ten.setPlaceholderText("Ví dụ: Soạn bài đầy đủ, đúng phân phối")
        form.addRow("📌 Tên tiêu chí:", self.txt_ten)
        
        # Loại
        self.cmb_loai = QComboBox()
        self.cmb_loai.addItem("✅ Tiêu chí cộng", "cong")
        self.cmb_loai.addItem("❌ Tiêu chí trừ", "tru")
        idx = 0 if loai == "cong" else 1
        self.cmb_loai.setCurrentIndex(idx)
        self.cmb_loai.currentIndexChanged.connect(self._on_loai_changed)
        form.addRow("🏷️ Loại tiêu chí:", self.cmb_loai)
        
        # Điểm tối đa
        self.spin_diem = QDoubleSpinBox()
        self.spin_diem.setRange(0, 100)
        self.spin_diem.setValue(diem if diem > 0 else 10)
        self.spin_diem.setSuffix(" điểm")
        form.addRow("⭐ Điểm tối đa:", self.spin_diem)
        
        # Mô tả
        self.txt_mo_ta = QTextEdit()
        self.txt_mo_ta.setPlainText(mo_ta)
        self.txt_mo_ta.setMaximumHeight(80)
        self.txt_mo_ta.setPlaceholderText("Mô tả chi tiết về tiêu chí (không bắt buộc)...")
        form.addRow("📝 Mô tả:", self.txt_mo_ta)
        
        layout.addLayout(form)
        
        # Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self._on_loai_changed()

    def _on_loai_changed(self):
        """Gợi ý điểm theo loại"""
        loai = self.cmb_loai.currentData()
        if loai == "cong" and self.spin_diem.value() < 0:
            self.spin_diem.setValue(10)
        elif loai == "tru" and self.spin_diem.value() > 0:
            self.spin_diem.setValue(5)

    def get_data(self):
        return {
            'ten': self.txt_ten.text().strip(),
            'loai': self.cmb_loai.currentData(),
            'diem': self.spin_diem.value(),
            'mo_ta': self.txt_mo_ta.toPlainText()
        }