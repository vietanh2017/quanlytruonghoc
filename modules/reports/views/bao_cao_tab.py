# modules/reports/views/bao_cao_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox, QLabel,
    QPushButton, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from modules.reports.service.bao_cao_service import BaoCaoService


class BaoCaoTab(QWidget):
    """Tab báo cáo tổng hợp"""
    
    COLOR_TOP1 = QColor("#FFD700")
    COLOR_TOP2 = QColor("#C0C0C0")
    COLOR_TOP3 = QColor("#CD7F32")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc = BaoCaoService()
        self._current_nam_hoc_id = None
        self._current_hoc_ky_id = None
        self._current_thang = None
        self.stat_values = {}  # Lưu tham chiếu các label giá trị
        self._build_ui()
        self._load_filters()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # === Bộ lọc ===
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(150)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.cmb_nam_hoc)
        
        filter_layout.addWidget(QLabel("Kỳ:"))
        self.cmb_ky = QComboBox()
        self.cmb_ky.setMinimumWidth(120)
        self.cmb_ky.addItem("Học kỳ I", 1)
        self.cmb_ky.addItem("Học kỳ II", 2)
        self.cmb_ky.addItem("Cả năm", 3)  # ← THÊM CẢ NĂM
        self.cmb_ky.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.cmb_ky)
        
        # Trong bao_cao_tab.py
        filter_layout.addWidget(QLabel("Tháng:"))
        self.cmb_thang = QComboBox()
        self.cmb_thang.setMinimumWidth(130)
        self.cmb_thang.addItem("-- Tất cả --", None)

        # Tháng theo năm học
        # Tháng theo năm học
        for i in [9, 10, 11, 12]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        # Tháng 1 chia làm 2 phần
        self.cmb_thang.addItem("Tháng 1a (HK1)", "1a")
        self.cmb_thang.addItem("Tháng 1b (HK2)", "1b")
        for i in [2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        self.cmb_thang.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.cmb_thang)
        #filter_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setFixedHeight(30)
        self.btn_refresh.clicked.connect(self._load_data)
        filter_layout.addWidget(self.btn_refresh)
        
        self.btn_export = QPushButton("📊 Xuất Excel")
        self.btn_export.setFixedHeight(30)
        self.btn_export.setStyleSheet("background:#1D9E75; color:white; font-weight:bold;")
        self.btn_export.clicked.connect(self._open_export_dialog)
        filter_layout.addWidget(self.btn_export)
        
        layout.addLayout(filter_layout)
        
        # ... phần còn lại giữ nguyên
        
        # === 4 Thẻ thống kê tổng quan ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.card_gv = self._create_stat_card("👨‍🏫", "Giáo viên", "giao_vien")
        self.card_hs = self._create_stat_card("👨‍🎓", "Học sinh", "hoc_sinh")
        self.card_lop = self._create_stat_card("🏫", "Lớp học", "lop_hoc")
        self.card_to = self._create_stat_card("⭐", "Tổ chuyên môn", "to_chuyen_mon")
        
        stats_layout.addWidget(self.card_gv)
        stats_layout.addWidget(self.card_hs)
        stats_layout.addWidget(self.card_lop)
        stats_layout.addWidget(self.card_to)
        layout.addLayout(stats_layout)
        
        # === Bảng xếp hạng giáo viên và lớp ===
        ranking_layout = QHBoxLayout()
        ranking_layout.setSpacing(15)
        
        # Bảng xếp hạng giáo viên
        gv_group = QGroupBox("🏆 TOP 10 GIÁO VIÊN XUẤT SẮC")
        gv_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        gv_layout = QVBoxLayout(gv_group)
        
        self.table_gv = QTableWidget()
        self._setup_gv_table()
        gv_layout.addWidget(self.table_gv)
        
        # Bảng xếp hạng lớp
        lop_group = QGroupBox("🏆 TOP 10 LỚP XUẤT SẮC")
        lop_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        lop_layout = QVBoxLayout(lop_group)
        
        self.table_lop = QTableWidget()
        self._setup_lop_table()
        lop_layout.addWidget(self.table_lop)
        
        ranking_layout.addWidget(gv_group, 2)
        ranking_layout.addWidget(lop_group, 1)
        layout.addLayout(ranking_layout)
        
        # Status
        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        layout.addWidget(self.status_label)
    
    def _create_stat_card(self, icon, title, key):
        """Tạo thẻ thống kê và lưu tham chiếu"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
        """)
        card.setFixedHeight(100)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_lbl)
        
        right_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #666; font-size: 12px;")
        value_lbl = QLabel("0")
        value_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #1D9E75;")
        value_lbl.setObjectName(f"stat_{key}")
        
        right_layout.addWidget(title_lbl)
        right_layout.addWidget(value_lbl)
        layout.addLayout(right_layout)
        
        # Lưu tham chiếu
        self.stat_values[key] = value_lbl
        
        return card
    
    def _setup_gv_table(self):
        headers = ["STT", "Mã GV", "Họ tên", "Điểm", "Xếp loại"]
        self.table_gv.setColumnCount(len(headers))
        self.table_gv.setHorizontalHeaderLabels(headers)
        self.table_gv.setColumnWidth(0, 45)
        self.table_gv.setColumnWidth(1, 80)
        self.table_gv.setColumnWidth(2, 150)
        self.table_gv.setColumnWidth(3, 80)
        self.table_gv.setColumnWidth(4, 220)
        self.table_gv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_gv.setAlternatingRowColors(True)
        self.table_gv.verticalHeader().setVisible(False)
        header = self.table_gv.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
    
    def _setup_lop_table(self):
        headers = ["STT", "Mã lớp", "Tên lớp", "Điểm TB", "Xếp thứ"]
        self.table_lop.setColumnCount(len(headers))
        self.table_lop.setHorizontalHeaderLabels(headers)
        self.table_lop.setColumnWidth(0, 45)
        self.table_lop.setColumnWidth(1, 70)
        self.table_lop.setColumnWidth(2, 120)
        self.table_lop.setColumnWidth(3, 80)
        self.table_lop.setColumnWidth(4, 70)
        self.table_lop.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_lop.setAlternatingRowColors(True)
        self.table_lop.verticalHeader().setVisible(False)
        header = self.table_lop.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
    
    def _load_filters(self):
        try:
            from core.db.models.nam_hoc import NamHoc
            nam_hocs = self.svc.session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all()
            for nh in nam_hocs:
                self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
            if self.cmb_nam_hoc.count() > 0:
                self.cmb_nam_hoc.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải năm học: {e}")
    
    def _on_filter_changed(self):
        self._load_data()
    
    def _load_data(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        ky_value = self.cmb_ky.currentData()
        thang = self.cmb_thang.currentData()
        
        if not nam_hoc_id:
            return
        
        self._current_nam_hoc_id = nam_hoc_id
        self._current_thang = thang
        
        # === KHÔNG CHUYỂN ĐỔI, TRUYỀN THẲNG ky_value ===
        # ky_value: 1=HK1, 2=HK2, 3=Cả năm
        
        # Xác định tên hiển thị
        if ky_value == 1:
            hien_thi_ky = "Học kỳ I"
        elif ky_value == 2:
            hien_thi_ky = "Học kỳ II"
        elif ky_value == 3:
            hien_thi_ky = "Cả năm"
        else:
            hien_thi_ky = "---"
        
        self._load_thong_ke(nam_hoc_id)
        
        # Load xếp hạng giáo viên - TRUYỀN THẲNG ky_value
        self._load_xep_hang_gv(nam_hoc_id, ky_value, thang)
        
        # Load xếp hạng lớp - TRUYỀN THẲNG ky_value
        self._load_xep_hang_lop(nam_hoc_id, ky_value, thang)
        
        # Cập nhật status
        thang_text = f"Tháng {thang}" if thang else "Tất cả tháng"
        self.status_label.setText(f"📊 {self.cmb_nam_hoc.currentText()} | {hien_thi_ky} | {thang_text}")
    
    def _load_thong_ke(self, nam_hoc_id):
        result = self.svc.thong_ke_tong_quan(nam_hoc_id)
        if result.ok:
            data = result.data
            self.stat_values.get("giao_vien", QLabel()).setText(str(data.get('so_giao_vien', 0)))
            self.stat_values.get("hoc_sinh", QLabel()).setText(str(data.get('so_hoc_sinh', 0)))
            self.stat_values.get("lop_hoc", QLabel()).setText(str(data.get('so_lop', 0)))
            self.stat_values.get("to_chuyen_mon", QLabel()).setText(str(data.get('so_to_chuyen_mon', 0)))
    
    def _load_xep_hang_gv(self, nam_hoc_id, hoc_ky_id, thang):
        result = self.svc.xep_hang_giao_vien(nam_hoc_id, hoc_ky_id, thang)
        if result.ok:
            self._render_gv_table(result.data)
    
    def _render_gv_table(self, data):
        self.table_gv.setRowCount(len(data))
        for row, item in enumerate(data):
            # STT
            item_stt = QTableWidgetItem(str(row + 1))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table_gv.setItem(row, 0, item_stt)
            
            # Mã GV
            item_ma = QTableWidgetItem(item['ma'])
            item_ma.setTextAlignment(Qt.AlignCenter)
            self.table_gv.setItem(row, 1, item_ma)
            
            # Họ tên
            item_ten = QTableWidgetItem(item['ten'])
            #item_ten.setTextAlignment(Qt.AlignCenter)
            self.table_gv.setItem(row, 2, item_ten)
            
            # Điểm
            item_diem = QTableWidgetItem(f"{item['diem']:.2f}")
            item_diem.setTextAlignment(Qt.AlignCenter)
            self.table_gv.setItem(row, 3, item_diem)
            
            # Xếp loại
            item_xl = QTableWidgetItem(item['xep_loai'])
            item_xl.setTextAlignment(Qt.AlignCenter)
            self.table_gv.setItem(row, 4, item_xl)
            
            # Tô màu top 3
            if row == 0:
                self.table_gv.item(row, 0).setBackground(self.COLOR_TOP1)
                self.table_gv.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
            elif row == 1:
                self.table_gv.item(row, 0).setBackground(self.COLOR_TOP2)
                self.table_gv.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
            elif row == 2:
                self.table_gv.item(row, 0).setBackground(self.COLOR_TOP3)
                self.table_gv.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
    
    def _load_xep_hang_lop(self, nam_hoc_id, hoc_ky_id, thang):
        result = self.svc.xep_hang_lop(nam_hoc_id, hoc_ky_id, thang)
        if result.ok:
            self._render_lop_table(result.data)
    
    def _render_lop_table(self, data):
        self.table_lop.setRowCount(len(data))
        for row, item in enumerate(data):
            # STT
            item_stt = QTableWidgetItem(str(row + 1))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table_lop.setItem(row, 0, item_stt)
            
            # Mã lớp
            item_ma = QTableWidgetItem(item['ma'])
            item_ma.setTextAlignment(Qt.AlignCenter)
            self.table_lop.setItem(row, 1, item_ma)
            
            # Tên lớp
            item_ten = QTableWidgetItem(item['ten'])
            item_ten.setTextAlignment(Qt.AlignCenter)
            self.table_lop.setItem(row, 2, item_ten)
            
            # Điểm TB
            item_diem = QTableWidgetItem(f"{item['diem']:.3f}")
            item_diem.setTextAlignment(Qt.AlignCenter)
            # Tô màu theo điểm
            if item['diem'] >= 9:
                item_diem.setBackground(QColor("#E8F5E9"))
                item_diem.setForeground(QColor("#2E7D32"))
            elif item['diem'] >= 7:
                item_diem.setBackground(QColor("#FFF3E0"))
                item_diem.setForeground(QColor("#E65100"))
            elif item['diem'] > 0:
                item_diem.setBackground(QColor("#FFE5E5"))
                item_diem.setForeground(QColor("#CC0000"))
            self.table_lop.setItem(row, 3, item_diem)
            
            # Xếp thứ
            item_rank = QTableWidgetItem(str(item['thu_hang']))
            item_rank.setTextAlignment(Qt.AlignCenter)
            self.table_lop.setItem(row, 4, item_rank)
            
            # Tô màu top 3
            if row == 0:
                self.table_lop.item(row, 0).setBackground(self.COLOR_TOP1)
                self.table_lop.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
            elif row == 1:
                self.table_lop.item(row, 0).setBackground(self.COLOR_TOP2)
                self.table_lop.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
            elif row == 2:
                self.table_lop.item(row, 0).setBackground(self.COLOR_TOP3)
                self.table_lop.item(row, 0).setFont(QFont("Arial", 9, QFont.Bold))
    
    def _open_export_dialog(self):
        """Mở dialog xuất Excel"""
        from modules.reports.dialogs.export_excel_dialog import ExportExcelDialog
        dlg = ExportExcelDialog(self.svc, self)
        dlg.exec()
    
    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)