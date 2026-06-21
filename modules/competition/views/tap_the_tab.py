# modules/competition/views/tap_the_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox, QLabel,
    QPushButton, QTabWidget, QFrame, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush

from modules.competition.service.diem_tap_the_service import DiemTapTheService


class HorizontalBarChart(QWidget):
    """Biểu đồ thanh ngang - hiển thị bên phải bảng"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # List of (label, value, color)
        self.setMinimumWidth(280)
        self.setMaximumWidth(350)
        self.setMinimumHeight(400)
        
    def set_data(self, data):
        """data: list of (label, value, color)"""
        self.data = data[:15]
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            painter.drawText(self.rect(), Qt.AlignCenter, "📊 Chưa có dữ liệu\nNhấn 'Hiển thị' để xem")
            return
        
        width = self.width() - 20
        height = self.height() - 80
        bar_height = max(22, (height - 20) // len(self.data))
        max_value = max([v for _, v, _ in self.data]) if self.data else 100
        
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.setPen(QPen(QColor("#333")))
        painter.drawText(QRect(0, 0, width, 30), Qt.AlignCenter, "📊 TOP XẾP HẠNG")
        
        y_offset = 35
        for i, (label, value, color) in enumerate(self.data):
            bar_width = int((value / max_value) * (width - 120)) if max_value > 0 else 0
            y = y_offset + i * (bar_height + 4)
            
            painter.setPen(QPen(QColor("#FFD700") if i == 0 else QColor("#C0C0C0") if i == 1 else QColor("#CD7F32") if i == 2 else QColor("#999")))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(QRect(5, y, 35, bar_height), Qt.AlignLeft | Qt.AlignVCenter, f"#{i+1}")
            
            painter.setPen(QPen(QColor("#333")))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(QRect(45, y, 55, bar_height), Qt.AlignLeft | Qt.AlignVCenter, label[:10])
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRect(105, y, bar_width, bar_height - 2))
            
            painter.setPen(QPen(QColor("#555")))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(QRect(110 + bar_width, y, 50, bar_height - 2), 
                           Qt.AlignLeft | Qt.AlignVCenter, f"{value:.3f}")


class TapTheTab(QWidget):
    """Tab quản lý thi đua tập thể lớp - Tuần, Tháng, HK1, HK2"""

    COLOR_TOP1 = QColor("#FFD700")
    COLOR_TOP2 = QColor("#C0C0C0")
    COLOR_TOP3 = QColor("#CD7F32")
    COLOR_LOW = QColor("#FFE5E5")
    COLOR_MEDIUM = QColor("#FFF3E0")
    COLOR_GOOD = QColor("#E8F5E9")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc = DiemTapTheService()
        
        self._current_tuan = None
        self._current_nam_hoc_id = None
        self._ds_lop = []
        self._unsaved = False
        
        # Dictionary lưu trạng thái khóa theo tuần: {tuan: True/False}
        self._locked_weeks = {}
        
        self._build_ui()
        self._load_nam_hoc()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        self.tab_widget = QTabWidget()
        
        # Tab 1: Theo tuần
        self.week_tab = QWidget()
        self._setup_week_tab()
        self.tab_widget.addTab(self.week_tab, "📅 Theo tuần")
        
        # Tab 2: Theo tháng
        self.month_tab = QWidget()
        self._setup_month_tab()
        self.tab_widget.addTab(self.month_tab, "📊 Theo tháng")
        
        # Tab 3: Học kỳ 1
        self.hk1_tab = QWidget()
        self._setup_hk_tab(hoc_ky=1)
        self.tab_widget.addTab(self.hk1_tab, "📚 Học kỳ 1")
        
        # Tab 4: Học kỳ 2
        self.hk2_tab = QWidget()
        self._setup_hk_tab(hoc_ky=2)
        self.tab_widget.addTab(self.hk2_tab, "📚 Học kỳ 2")
        
        # Tab 5: Cả năm
        self.year_tab = QWidget()
        self._setup_year_tab()
        self.tab_widget.addTab(self.year_tab, "🎯 Cả năm")
        
        # Tab 6: Đặc biệt
        self.special_tab = QWidget()
        self._setup_special_tab()
        self.tab_widget.addTab(self.special_tab, "⭐ Đặc biệt")
        
        # Tab 7: Cá nhân
        from modules.competition.views.ca_nhan_tab import CaNhanTab
        self.ca_nhan_tab = CaNhanTab()
        self.tab_widget.addTab(self.ca_nhan_tab, "👤 Cá nhân")
        
        layout.addWidget(self.tab_widget)

        # === CHỈ GIỮ MỘT CHÚ THÍCH DUY NHẤT ===
        note = QLabel(
            "💡 Màu sắc: 🥇 Vàng (Hạng 1) | 🥈 Bạc (Hạng 2) | 🥉 Đồng (Hạng 3) | "
            "🟢 Xanh (>180) | 🟠 Cam (100-150) | 🔴 Đỏ (<100)"
        )
        note.setStyleSheet("color:#999; font-size:10px; padding:4px;")
        layout.addWidget(note)
    # ==================== TAB THEO TUẦN ====================
    
    def _setup_week_tab(self):
        """Thiết lập tab theo tuần - bảng trái, biểu đồ phải"""
        layout = QVBoxLayout(self.week_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Thanh lọc
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc_week = QComboBox()
        self.cmb_nam_hoc_week.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc_week)

        filter_layout.addWidget(QLabel("Tuần:"))
        self.cmb_tuan = QComboBox()
        self.cmb_tuan.setMinimumWidth(100)
        for i in range(1, 36):
            self.cmb_tuan.addItem(f"Tuần {i}", i)
        filter_layout.addWidget(self.cmb_tuan)

        self.btn_load_week = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(self.btn_load_week)
        filter_layout.addStretch()

        self.btn_save_week = QPushButton("💾 Lưu tất cả")
        self.btn_save_week.setStyleSheet("background:#1D9E75; color:white; font-weight:bold;")
        self.btn_refresh_week = QPushButton("🔄 Làm mới")
        
        # === HAI NÚT KHÓA/MỞ KHÓA ===
        self.btn_lock_week = QPushButton("🔒 Khóa tuần")
        self.btn_lock_week.setStyleSheet("background:#FF9800; color:white; font-weight:bold;")
        
        self.btn_unlock_week = QPushButton("🔓 Mở khóa")
        self.btn_unlock_week.setStyleSheet("background:#F44336; color:white; font-weight:bold;")
        self.btn_unlock_week.hide()  # Ẩn ban đầu
        # ===========================
        
        filter_layout.addWidget(self.btn_save_week)
        filter_layout.addWidget(self.btn_refresh_week)
        filter_layout.addWidget(self.btn_lock_week)
        filter_layout.addWidget(self.btn_unlock_week)  # ← QUAN TRỌNG: Thêm dòng này
        layout.addLayout(filter_layout)

        # Status
        self.status_label_week = QLabel("✅ Sẵn sàng")
        self.status_label_week.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        layout.addWidget(self.status_label_week)

        # === Splitter: Bảng trái - Biểu đồ phải ===
        splitter = QSplitter(Qt.Horizontal)
        
        # Bảng bên trái
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_week = QTableWidget()
        self._setup_week_table()
        left_layout.addWidget(self.table_week)
        
        # Biểu đồ bên phải
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 0px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        self.bar_chart = HorizontalBarChart()
        right_layout.addWidget(self.bar_chart)
        
        # Tổng quan xếp hạng
        self.summary_label = QLabel("📈 TỔNG QUAN: --")
        self.summary_label.setStyleSheet(
            "color:#555; font-size:11px; padding:8px; "
            "background:#F5F5F5; border-radius:5px; margin:8px;"
        )
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setWordWrap(True)
        right_layout.addWidget(self.summary_label)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)

        # Kết nối signals
        self.btn_load_week.clicked.connect(self._on_load_week)
        self.btn_save_week.clicked.connect(self._on_save_week)
        self.btn_refresh_week.clicked.connect(self._on_refresh_week)
        self.btn_lock_week.clicked.connect(self._on_lock_week)
        self.btn_unlock_week.clicked.connect(self._on_unlock_week)  # ← QUAN TRỌNG: Kết nối
        self.cmb_tuan.currentIndexChanged.connect(self._on_tuan_changed)
        self.table_week.itemChanged.connect(self._on_week_item_changed)
        
        # Gán sự kiện phím cho bảng
        self.table_week.keyPressEvent = self._on_table_key_press

    def _on_lock_week(self):
        """Khóa tuần hiện tại"""
        if not self._current_tuan:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tải dữ liệu trước!")
            return
        
        if self._locked_weeks.get(self._current_tuan, False):
            QMessageBox.information(self, "Thông báo", f"Tuần {self._current_tuan} đã được khóa!")
            return
        
        reply = QMessageBox.question(
            self,
            "Xác nhận khóa tuần",
            f"Khóa Tuần {self._current_tuan}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Lưu trạng thái khóa
        self._locked_weeks[self._current_tuan] = True
        
        # Reload lại bảng với trạng thái khóa
        self._on_load_week()
        
        QMessageBox.information(self, "Thành công", f"Đã khóa Tuần {self._current_tuan}!")

    def _on_unlock_week(self):
        """Mở khóa tuần hiện tại"""
        if not self._current_tuan:
            return
        
        if not self._locked_weeks.get(self._current_tuan, False):
            QMessageBox.information(self, "Thông báo", f"Tuần {self._current_tuan} chưa được khóa!")
            return
        
        reply = QMessageBox.question(
            self,
            "Xác nhận mở khóa",
            f"Mở khóa Tuần {self._current_tuan}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Xóa trạng thái khóa
        self._locked_weeks[self._current_tuan] = False
        
        # Reload lại bảng
        self._on_load_week()
        
        QMessageBox.information(self, "Thành công", f"Đã mở khóa Tuần {self._current_tuan}!")

    def _setup_week_table(self):
        """Cấu hình bảng tuần - 7 cột"""
        headers = ["STT", "Lớp", "Điểm học tập", "Điểm Đội", "Tổng điểm", "Trung bình", "Xếp thứ"]
        self.table_week.setColumnCount(len(headers))
        self.table_week.setHorizontalHeaderLabels(headers)
        
        self.table_week.setColumnWidth(0, 50)
        self.table_week.setColumnWidth(1, 80)
        self.table_week.setColumnWidth(2, 110)
        self.table_week.setColumnWidth(3, 110)
        self.table_week.setColumnWidth(4, 110)
        self.table_week.setColumnWidth(5, 110)
        self.table_week.setColumnWidth(6, 70)
        
        # CHỈ CHO PHÉP EDIT CỘT 2 (Điểm học tập), KHÔNG EDIT CỘT 3 (Điểm Đội)
        self.table_week.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.EditKeyPressed
        )
        self.table_week.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table_week.setAlternatingRowColors(True)
        self.table_week.verticalHeader().setVisible(False)
        
        header = self.table_week.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        
        # Khóa các cột không cho edit (STT, Lớp, Điểm Đội, Tổng điểm, Trung bình, Xếp thứ)
        for row in range(self.table_week.rowCount()):
            for col in [0, 1, 3, 4, 5, 6]:  # Thêm cột 3 (Điểm Đội) vào danh sách khóa
                item = self.table_week.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def _on_table_key_press(self, event):
        """Xử lý phím nhấn trên bảng - Enter xuống dòng"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current = self.table_week.currentItem()
            if current:
                row = current.row()
                col = current.column()
                # Chỉ xử lý cột 2 và 3 (Điểm học tập và Điểm Đội)
                if col in [2, 3] and not self._locked_weeks.get(self._current_tuan, False):
                    next_row = row + 1
                    if next_row < self.table_week.rowCount():
                        next_item = self.table_week.item(next_row, col)
                        if next_item and (next_item.flags() & Qt.ItemIsEditable):
                            self.table_week.setCurrentCell(next_row, col)
                            self.table_week.edit(self.table_week.currentIndex())
                    return
        # Gọi xử lý mặc định
        QWidget.keyPressEvent(self.table_week, event)

    def _on_load_week(self):
        """Load dữ liệu tuần"""
        nam_hoc_id = self.cmb_nam_hoc_week.currentData()
        tuan = self.cmb_tuan.currentData()

        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return

        self._current_nam_hoc_id = nam_hoc_id
        self._current_tuan = tuan

        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        self._ds_lop = result.data or []

        if not self._ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return

        # Lấy điểm học tập từ bảng diem_tap_the_lop
        diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
        diem_dict = diem_result.data if diem_result.ok else {}

        # Lấy điểm Đội từ bảng diem_doi_ngay (tự động tính)
        diem_doi_dict = self.svc.get_diem_doi_tuan_all_lop(nam_hoc_id, tuan)

        # Gộp dữ liệu: điểm học tập từ bảng cũ, điểm Đội từ bảng mới
        for lop in self._ds_lop:
            if lop.id not in diem_dict:
                diem_dict[lop.id] = {}
            # Giữ nguyên điểm học tập (nếu có)
            diem_dict[lop.id]['diem_hoc_tap'] = diem_dict.get(lop.id, {}).get('diem_hoc_tap', 0)
            # Lấy điểm Đội từ bảng diem_doi_ngay (mặc định 0 nếu chưa có)
            diem_dict[lop.id]['diem_doi'] = diem_doi_dict.get(lop.id, 0)

        # Lưu lại để dùng cho render
        self._current_diem_dict = diem_dict

        # Lấy trạng thái khóa
        is_locked = self._locked_weeks.get(tuan, False)

        # Hiển thị nút phù hợp
        if is_locked:
            self.btn_lock_week.hide()
            self.btn_unlock_week.show()
        else:
            self.btn_lock_week.show()
            self.btn_unlock_week.hide()

        self._render_week_table(diem_dict, is_locked)
        self._unsaved = False
        self.status_label_week.setText(f"📅 Tuần {tuan} | {'🔒 Đã khóa' if is_locked else '🔓 Chưa khóa'}")

    def _render_week_table(self, diem_dict, is_locked=False):
        """Hiển thị bảng tuần và cập nhật biểu đồ"""
        self.table_week.itemChanged.disconnect(self._on_week_item_changed)
        self.table_week.setRowCount(len(self._ds_lop))

        tong_diem_list = []
        chart_data = []

        for row, lop in enumerate(self._ds_lop):
            diem_hoc_tap = diem_dict.get(lop.id, {}).get('diem_hoc_tap', 0)
            diem_doi = diem_dict.get(lop.id, {}).get('diem_doi', 10)
            tong = diem_hoc_tap + diem_doi
            diem_trung_binh = (diem_hoc_tap * 2 + diem_doi) / 3
            
            tong_diem_list.append({'row': row, 'tong': tong})
            chart_data.append((lop.ten_lop, diem_trung_binh))

            # STT - không edit
            item = QTableWidgetItem(str(row + 1))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table_week.setItem(row, 0, item)

            # Lớp - không edit
            item = QTableWidgetItem(lop.ten_lop)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_week.setItem(row, 1, item)

            # Điểm học tập
            item = QTableWidgetItem(f"{diem_hoc_tap:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            if is_locked:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(QColor("#FFE0B3"))
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
            self.table_week.setItem(row, 2, item)

            # Điểm Đội - KHÔNG BAO GIỜ CHO EDIT (chỉ đọc)
            item = QTableWidgetItem(f"{diem_doi:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Bỏ Qt.ItemIsEditable
            if is_locked:
                item.setBackground(QColor("#FFE0B3"))
            self.table_week.setItem(row, 3, item)

            # Tổng điểm - không edit
            item = QTableWidgetItem(f"{tong:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._color_total(item, tong)
            self.table_week.setItem(row, 4, item)
            
            # Trung bình - không edit
            item = QTableWidgetItem(f"{diem_trung_binh:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._color_total(item, diem_trung_binh)
            self.table_week.setItem(row, 5, item)
            
            # Xếp thứ - không edit
            item = QTableWidgetItem("---")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table_week.setItem(row, 6, item)

        self._update_week_ranking(tong_diem_list)
        self._update_chart(chart_data)
        self.table_week.itemChanged.connect(self._on_week_item_changed)

    def _update_chart(self, chart_data):
        sorted_data = sorted(chart_data, key=lambda x: x[1], reverse=True)
        
        colors = [
            QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
            QColor("#1D9E75"), QColor("#FFA500"),
        ]
        
        chart_with_colors = []
        for i, (label, value) in enumerate(sorted_data):
            if i < 3:
                color = colors[i]
            elif i < 10:
                color = colors[3]
            else:
                color = colors[4]
            chart_with_colors.append((label, value, color))
        
        self.bar_chart.set_data(chart_with_colors)
        
        if sorted_data:
            top1 = sorted_data[0]
            top2 = sorted_data[1] if len(sorted_data) > 1 else ("---", 0)
            top3 = sorted_data[2] if len(sorted_data) > 2 else ("---", 0)
            self.summary_label.setText(
                f"🏆 TỔNG QUAN TUẦN {self._current_tuan}:  "
                f"🥇 {top1[0]} ({top1[1]:.3f})  |  "
                f"🥈 {top2[0]} ({top2[1]:.3f})  |  "
                f"🥉 {top3[0]} ({top3[1]:.3f})"
            )

    def _update_week_ranking(self, tong_diem_list):
        sorted_list = sorted(tong_diem_list, key=lambda x: x['tong'], reverse=True)
        rank = 1
        for i, item in enumerate(sorted_list):
            if i > 0 and item['tong'] < sorted_list[i-1]['tong']:
                rank = i + 1
            
            item_rank = QTableWidgetItem(str(rank))
            item_rank.setTextAlignment(Qt.AlignCenter)
            item_rank.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            if rank == 1:
                item_rank.setBackground(self.COLOR_TOP1)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 2:
                item_rank.setBackground(self.COLOR_TOP2)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 3:
                item_rank.setBackground(self.COLOR_TOP3)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            
            self.table_week.setItem(item['row'], 6, item_rank)

    def _on_week_item_changed(self, item):
        """Khi sửa ô trong bảng tuần"""
        # Kiểm tra tuần hiện tại có bị khóa không
        if self._locked_weeks.get(self._current_tuan, False):
            return
        
        row = item.row()
        col = item.column()
        if col not in [2, 3]:
            return
        
        self._unsaved = True
        self.status_label_week.setText(f"⚠️ Có thay đổi chưa lưu ở Tuần {self._current_tuan}")
        self._update_week_total(row)

    def _update_week_total(self, row):
        """Cập nhật tổng điểm, trung bình, xếp thứ và biểu đồ"""
        try:
            item_hoc_tap = self.table_week.item(row, 2)
            item_doi = self.table_week.item(row, 3)
            
            if not item_hoc_tap or not item_doi:
                return
            
            diem_hoc_tap = float(item_hoc_tap.text() or 0)
            diem_doi = float(item_doi.text() or 0)
            tong = diem_hoc_tap + diem_doi
            diem_trung_binh = (diem_hoc_tap * 2 + diem_doi) / 3
            
            # Tổng điểm
            item = QTableWidgetItem(f"{tong:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._color_total(item, tong)
            self.table_week.setItem(row, 4, item)
            
            # Trung bình
            item = QTableWidgetItem(f"{diem_trung_binh:.3f}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._color_total(item, diem_trung_binh)
            self.table_week.setItem(row, 5, item)
            
            # Cập nhật lại xếp thứ
            tong_list = []
            chart_data = []
            for r in range(self.table_week.rowCount()):
                if r < len(self._ds_lop):
                    t_item = self.table_week.item(r, 4)
                    tb_item = self.table_week.item(r, 5)
                    if t_item and tb_item:
                        t = float(t_item.text() or 0)
                        tb = float(tb_item.text() or 0)
                        tong_list.append({'row': r, 'tong': t})
                        chart_data.append((self._ds_lop[r].ten_lop, tb))
            self._update_week_ranking(tong_list)
            self._update_chart(chart_data)
            
        except ValueError:
            pass

    def _collect_week_data(self):
        data = []
        for row in range(self.table_week.rowCount()):
            if row >= len(self._ds_lop):
                continue
            lop = self._ds_lop[row]
            try:
                diem_hoc_tap = float(self.table_week.item(row, 2).text() or 0)
                diem_doi = float(self.table_week.item(row, 3).text() or 0)
            except ValueError:
                diem_hoc_tap = 0
                diem_doi = 0
            data.append({
                'lop_hoc_id': lop.id,
                'diem_hoc_tap': round(diem_hoc_tap, 3),
                'diem_doi': round(diem_doi, 3),
                'ghi_chu': ''
            })
        return data

    def _on_save_week(self):
        if self._locked_weeks.get(self._current_tuan, False):
            QMessageBox.warning(self, "Không thể lưu", f"Tuần {self._current_tuan} đã bị khóa!")
            return
        if not self._current_nam_hoc_id or not self._current_tuan:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tải dữ liệu trước khi lưu!")
            return
        
        data = self._collect_week_data()
        result = self.svc.save_diem_tuan(
            self._current_nam_hoc_id, self._current_tuan, data, "Tổng phụ trách"
        )
        if result.ok:
            self._unsaved = False
            self.status_label_week.setText(f"✅ Đã lưu Tuần {self._current_tuan}!")
            QMessageBox.information(self, "Thành công", f"Đã lưu {len(data)} lớp!")
        else:
            QMessageBox.critical(self, "Lỗi", result.error)

    def _on_refresh_week(self):
        if self._unsaved:
            reply = QMessageBox.question(self, "Xác nhận", "Bỏ qua thay đổi chưa lưu?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        # Reset chỉ điểm học tập, giữ nguyên điểm Đội
        self.table_week.itemChanged.disconnect(self._on_week_item_changed)

        for row in range(self.table_week.rowCount()):
            # Chỉ reset Điểm học tập (cột 2) → 0.000
            item_hoc_tap = self.table_week.item(row, 2)
            if item_hoc_tap:
                item_hoc_tap.setText("0.000")
            
            # KHÔNG reset Điểm Đội (cột 3) - giữ nguyên giá trị từ database
            
            # Cập nhật lại tổng và trung bình
            self._update_week_total(row)

        self.table_week.itemChanged.connect(self._on_week_item_changed)
        self._unsaved = True
        self.status_label_week.setText(f"⚠️ Đã reset điểm học tập Tuần {self._current_tuan} — nhớ Lưu!")

    def _on_tuan_changed(self):
        if self._unsaved and self._current_tuan is not None:
            reply = QMessageBox.question(self, "Lưu thay đổi?", "Lưu trước khi chuyển tuần?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self._on_save_week()
            elif reply == QMessageBox.Cancel:
                self.cmb_tuan.setCurrentIndex(self.cmb_tuan.findData(self._current_tuan))
                return
        self._on_load_week()

    def _color_total(self, item, value):
        if value < 100:
            item.setBackground(self.COLOR_LOW)
            item.setForeground(QColor("#CC0000"))
        elif value < 150:
            item.setBackground(self.COLOR_MEDIUM)
            item.setForeground(QColor("#E65100"))
        elif value >= 180:
            item.setBackground(self.COLOR_GOOD)
            item.setForeground(QColor("#2E7D32"))
        else:
            item.setBackground(QColor(255, 255, 255))
            item.setForeground(QColor(0, 0, 0))

    # ==================== TAB THEO THÁNG ====================

    def _setup_month_tab(self):
        layout = QVBoxLayout(self.month_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc_month = QComboBox()
        self.cmb_nam_hoc_month.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc_month)

        filter_layout.addWidget(QLabel("Tháng:"))
        self.cmb_thang = QComboBox()
        self.cmb_thang.setMinimumWidth(100)
        for i in [9, 10, 11, 12]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        self.cmb_thang.addItem("Tháng 1a (HK1)", "1a")
        self.cmb_thang.addItem("Tháng 1b (HK2)", "1b")
        for i in [2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        filter_layout.addWidget(self.cmb_thang)

        self.btn_load_month = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(self.btn_load_month)
        filter_layout.addStretch()

        self.btn_export_month = QPushButton("📊 Xuất Excel")
        filter_layout.addWidget(self.btn_export_month)
        layout.addLayout(filter_layout)

        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_month = QTableWidget()
        self._setup_month_table()
        left_layout.addWidget(self.table_month)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 0px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        self.bar_chart_month = HorizontalBarChart()
        right_layout.addWidget(self.bar_chart_month)
        
        self.summary_label_month = QLabel("📈 TỔNG QUAN THÁNG: --")
        self.summary_label_month.setStyleSheet(
            "color:#555; font-size:11px; padding:8px; "
            "background:#F5F5F5; border-radius:5px; margin:8px;"
        )
        self.summary_label_month.setAlignment(Qt.AlignCenter)
        self.summary_label_month.setWordWrap(True)
        right_layout.addWidget(self.summary_label_month)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 460])
        
        layout.addWidget(splitter)

        self.btn_load_month.clicked.connect(self._on_load_month)

    def _setup_month_table(self):
        headers = ["STT", "Lớp", "Điểm TB học tập", "Điểm TB Đội", "TB tháng", "Xếp thứ"]
        self.table_month.setColumnCount(len(headers))
        self.table_month.setHorizontalHeaderLabels(headers)
        
        self.table_month.setColumnWidth(0, 50)
        self.table_month.setColumnWidth(1, 80)
        self.table_month.setColumnWidth(2, 130)
        self.table_month.setColumnWidth(3, 130)
        self.table_month.setColumnWidth(4, 130)
        self.table_month.setColumnWidth(5, 80)
        
        self.table_month.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_month.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_month.setAlternatingRowColors(True)
        self.table_month.verticalHeader().setVisible(False)
        header = self.table_month.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

    def _on_load_month(self):
        nam_hoc_id = self.cmb_nam_hoc_month.currentData()
        thang = self.cmb_thang.currentData()
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_lop = result.data or []
        
        if not ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return
        
        # Lấy tuần theo tháng (có thể là "1a" hoặc "1b")
        weeks = self._get_weeks_in_month(thang)
        
        month_data = []
        for lop in ds_lop:
            diem_hoc_tap_list = []
            diem_doi_list = []
            
            for tuan in weeks:
                diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
                if diem_result.ok:
                    diem_dict = diem_result.data
                    if lop.id in diem_dict:
                        diem_hoc_tap_list.append(diem_dict[lop.id].get('diem_hoc_tap', 0))
                        diem_doi_list.append(diem_dict[lop.id].get('diem_doi', 0))
            
            if diem_hoc_tap_list:
                tb_hoc_tap = sum(diem_hoc_tap_list) / len(diem_hoc_tap_list)
                tb_doi = sum(diem_doi_list) / len(diem_doi_list)
                tb_tong = (tb_hoc_tap * 2 + tb_doi) / 3
            else:
                tb_hoc_tap = 0
                tb_doi = 0
                tb_tong = 0
            
            month_data.append({
                'lop': lop,
                'tb_hoc_tap': tb_hoc_tap,
                'tb_doi': tb_doi,
                'tb_tong': tb_tong
            })
        
        self._render_month_table(month_data)

    def _render_month_table(self, month_data):
        self.table_month.setRowCount(len(month_data))
        
        sorted_data = sorted(month_data, key=lambda x: x['tb_tong'], reverse=True)
        
        rank_map = {}
        rank = 1
        for i, item in enumerate(sorted_data):
            if i > 0 and item['tb_tong'] < sorted_data[i-1]['tb_tong']:
                rank = i + 1
            rank_map[item['lop'].id] = rank
        
        chart_data = [(item['lop'].ten_lop, item['tb_tong']) for item in month_data]
        self._update_month_chart(chart_data)
        
        for row, item in enumerate(month_data):
            lop = item['lop']
            
            cell = QTableWidgetItem(str(row + 1))
            cell.setTextAlignment(Qt.AlignCenter)
            self.table_month.setItem(row, 0, cell)
            
            cell = QTableWidgetItem(lop.ten_lop)
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_month.setItem(row, 1, cell)
            
            cell = QTableWidgetItem(f"{item['tb_hoc_tap']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_month.setItem(row, 2, cell)
            
            cell = QTableWidgetItem(f"{item['tb_doi']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_month.setItem(row, 3, cell)
            
            cell = QTableWidgetItem(f"{item['tb_tong']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._color_total(cell, item['tb_tong'])
            self.table_month.setItem(row, 4, cell)
            
            rank = rank_map.get(lop.id, 0)
            cell = QTableWidgetItem(str(rank) if rank > 0 else "---")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if rank == 1:
                cell.setBackground(self.COLOR_TOP1)
                cell.setFont(QFont("Arial", 11, QFont.Bold))
            elif rank == 2:
                cell.setBackground(self.COLOR_TOP2)
                cell.setFont(QFont("Arial", 11, QFont.Bold))
            elif rank == 3:
                cell.setBackground(self.COLOR_TOP3)
                cell.setFont(QFont("Arial", 11, QFont.Bold))
            self.table_month.setItem(row, 5, cell)

    def _get_weeks_in_month(self, thang: int) -> list:
        weeks_map = {
            9: [1, 2, 3, 4],
            10: [5, 6, 7, 8],
            11: [9, 10, 11, 12],
            12: [13, 14, 15, 16],
            "1a": [17, 18],  # HK1
            "1b": [19, 20],  # HK2
            2: [21, 22, 23, 24],
            3: [25, 26, 27, 28],
            4: [29, 30, 31, 32],
            5: [33, 34, 35]
        }
        return weeks_map.get(thang, [])

    def _update_month_chart(self, chart_data):
        sorted_data = sorted(chart_data, key=lambda x: x[1], reverse=True)
        top_data = sorted_data[:10]
        
        colors = [
            QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
            QColor("#1D9E75"), QColor("#FFA500"),
        ]
        
        chart_with_colors = []
        for i, (label, value) in enumerate(top_data):
            if i < 3:
                color = colors[i]
            elif i < 6:
                color = colors[3]
            else:
                color = colors[4]
            chart_with_colors.append((label, value, color))
        
        self.bar_chart_month.set_data(chart_with_colors)
        
        if top_data:
            thang = self.cmb_thang.currentData()
            top1 = top_data[0]
            top2 = top_data[1] if len(top_data) > 1 else ("---", 0)
            top3 = top_data[2] if len(top_data) > 2 else ("---", 0)
            self.summary_label_month.setText(
                f"🏆 TOP 10 - THÁNG {thang}:  "
                f"🥇 {top1[0]} ({top1[1]:.3f})  |  "
                f"🥈 {top2[0]} ({top2[1]:.3f})  |  "
                f"🥉 {top3[0]} ({top3[1]:.3f})"
            )

    # ==================== TAB HỌC KỲ ====================

    def _setup_hk_tab(self, hoc_ky: int):
        """Thiết lập tab học kỳ - tính TBC trực tiếp từ các tuần"""
        if hoc_ky == 1:
            tab_widget = self.hk1_tab
            weeks = list(range(1, 19))  # Tuần 1-18
            ten_hk = "HK1"
        else:
            tab_widget = self.hk2_tab
            weeks = list(range(19, 36))  # Tuần 19-35
            ten_hk = "HK2"
        
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Năm học:"))
        cmb_nam_hoc = QComboBox()
        cmb_nam_hoc.setMinimumWidth(150)
        filter_layout.addWidget(cmb_nam_hoc)

        btn_load = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(btn_load)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        table = QTableWidget()
        self._setup_hk_table(table)
        left_layout.addWidget(table)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        bar_chart = HorizontalBarChart()
        right_layout.addWidget(bar_chart)
        
        summary_label = QLabel(f"📈 TỔNG QUAN {ten_hk}: --")
        summary_label.setStyleSheet(
            "color:#555; font-size:11px; padding:8px; "
            "background:#F5F5F5; border-radius:5px; margin:8px;"
        )
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setWordWrap(True)
        right_layout.addWidget(summary_label)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 420])
        
        layout.addWidget(splitter)

        # Lưu references
        if hoc_ky == 1:
            self.cmb_nam_hoc_hk1 = cmb_nam_hoc
            self.btn_load_hk1 = btn_load
            self.table_hk1 = table
            self.bar_chart_hk1 = bar_chart
            self.summary_label_hk1 = summary_label
            self.btn_load_hk1.clicked.connect(lambda: self._on_load_hk(1))
        else:
            self.cmb_nam_hoc_hk2 = cmb_nam_hoc
            self.btn_load_hk2 = btn_load
            self.table_hk2 = table
            self.bar_chart_hk2 = bar_chart
            self.summary_label_hk2 = summary_label
            self.btn_load_hk2.clicked.connect(lambda: self._on_load_hk(2))

    def _setup_hk_table(self, table):
        headers = ["STT", "Lớp", "Điểm TB HK học tập", "Điểm TB HK Đội", "TB Học kỳ", "Xếp thứ"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 140)
        table.setColumnWidth(3, 130)
        table.setColumnWidth(4, 140)
        table.setColumnWidth(5, 80)
        
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

    def _on_load_hk(self, hoc_ky: int):
        """Load tổng kết học kỳ - tính TBC trực tiếp từ các tuần"""
        if hoc_ky == 1:
            nam_hoc_id = self.cmb_nam_hoc_hk1.currentData()
            table = self.table_hk1
            bar_chart = self.bar_chart_hk1
            summary_label = self.summary_label_hk1
            weeks = list(range(1, 19))  # Tuần 1-18
            ten_hk = "HK1"
        else:
            nam_hoc_id = self.cmb_nam_hoc_hk2.currentData()
            table = self.table_hk2
            bar_chart = self.bar_chart_hk2
            summary_label = self.summary_label_hk2
            weeks = list(range(19, 36))  # Tuần 19-35
            ten_hk = "HK2"
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_lop = result.data or []
        
        if not ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return
        
        hk_data = []
        for lop in ds_lop:
            diem_hoc_tap_list = []
            diem_doi_list = []
            
            for tuan in weeks:
                diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
                if diem_result.ok:
                    diem_dict = diem_result.data
                    if lop.id in diem_dict:
                        diem_hoc_tap_list.append(diem_dict[lop.id].get('diem_hoc_tap', 0))
                        diem_doi_list.append(diem_dict[lop.id].get('diem_doi', 0))
            
            if diem_hoc_tap_list:
                tb_hoc_tap = sum(diem_hoc_tap_list) / len(diem_hoc_tap_list)
                tb_doi = sum(diem_doi_list) / len(diem_doi_list)
                tb_tong = (tb_hoc_tap * 2 + tb_doi) / 3
            else:
                tb_hoc_tap = 0
                tb_doi = 0
                tb_tong = 0
            
            hk_data.append({
                'lop': lop,
                'tb_hoc_tap': tb_hoc_tap,
                'tb_doi': tb_doi,
                'tb_tong': tb_tong
            })
        
        self._render_hk_table(table, hk_data, bar_chart, summary_label, ten_hk)

    def _render_hk_table(self, table, hk_data, bar_chart, summary_label, ten_hk):
        table.setRowCount(len(hk_data))
        
        sorted_data = sorted(hk_data, key=lambda x: x['tb_tong'], reverse=True)
        
        rank_map = {}
        rank = 1
        for i, item in enumerate(sorted_data):
            if i > 0 and item['tb_tong'] < sorted_data[i-1]['tb_tong']:
                rank = i + 1
            rank_map[item['lop'].id] = rank
        
        chart_data = [(item['lop'].ten_lop, item['tb_tong']) for item in hk_data]
        self._update_hk_chart(chart_data, bar_chart, summary_label, ten_hk)
        
        for row, item in enumerate(hk_data):
            lop = item['lop']
            
            cell = QTableWidgetItem(str(row + 1))
            cell.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, cell)
            
            cell = QTableWidgetItem(lop.ten_lop)
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            table.setItem(row, 1, cell)
            
            cell = QTableWidgetItem(f"{item['tb_hoc_tap']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            table.setItem(row, 2, cell)
            
            cell = QTableWidgetItem(f"{item['tb_doi']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            table.setItem(row, 3, cell)
            
            cell = QTableWidgetItem(f"{item['tb_tong']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._color_total(cell, item['tb_tong'])
            table.setItem(row, 4, cell)
            
            rank = rank_map.get(lop.id, 0)
            cell = QTableWidgetItem(str(rank) if rank > 0 else "---")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if rank == 1:
                cell.setBackground(self.COLOR_TOP1)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 2:
                cell.setBackground(self.COLOR_TOP2)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 3:
                cell.setBackground(self.COLOR_TOP3)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            table.setItem(row, 5, cell)

    def _update_hk_chart(self, chart_data, bar_chart, summary_label, ten_hk):
        sorted_data = sorted(chart_data, key=lambda x: x[1], reverse=True)
        top_data = sorted_data[:10]
        
        colors = [
            QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
            QColor("#1D9E75"), QColor("#FFA500"),
        ]
        
        chart_with_colors = []
        for i, (label, value) in enumerate(top_data):
            if i < 3:
                color = colors[i]
            elif i < 6:
                color = colors[3]
            else:
                color = colors[4]
            chart_with_colors.append((label, value, color))
        
        bar_chart.set_data(chart_with_colors)
        
        if top_data:
            top1 = top_data[0]
            top2 = top_data[1] if len(top_data) > 1 else ("---", 0)
            top3 = top_data[2] if len(top_data) > 2 else ("---", 0)
            summary_label.setText(
                f"🏆 TOP 10 - {ten_hk}:  "
                f"🥇 {top1[0]} ({top1[1]:.3f})  |  "
                f"🥈 {top2[0]} ({top2[1]:.3f})  |  "
                f"🥉 {top3[0]} ({top3[1]:.3f})"
            )
    # ==================== TAB TBC NĂM HỌC ====================

    def _setup_year_tab(self):
        """Thiết lập tab Cả năm - tính TBC từ HK1 và HK2"""
        layout = QVBoxLayout(self.year_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Thanh lọc
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc_year = QComboBox()
        self.cmb_nam_hoc_year.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc_year)

        self.btn_load_year = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(self.btn_load_year)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Splitter: Bảng trái - Biểu đồ phải
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_year = QTableWidget()
        self._setup_year_table()
        left_layout.addWidget(self.table_year)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        self.bar_chart_year = HorizontalBarChart()
        right_layout.addWidget(self.bar_chart_year)
        
        self.summary_label_year = QLabel("📈 TỔNG QUAN CẢ NĂM: --")
        self.summary_label_year.setStyleSheet(
            "color:#555; font-size:11px; padding:8px; "
            "background:#F5F5F5; border-radius:5px; margin:8px;"
        )
        self.summary_label_year.setAlignment(Qt.AlignCenter)
        self.summary_label_year.setWordWrap(True)
        right_layout.addWidget(self.summary_label_year)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 460])
        
        layout.addWidget(splitter)

        # Kết nối
        self.btn_load_year.clicked.connect(self._on_load_year)

    def _setup_year_table(self):
        """Cấu hình bảng cả năm - 6 cột"""
        headers = ["STT", "Lớp", "Điểm TB HK1", "Điểm TB HK2", "Điểm TB cả năm", "Xếp thứ"]
        self.table_year.setColumnCount(len(headers))
        self.table_year.setHorizontalHeaderLabels(headers)
        
        self.table_year.setColumnWidth(0, 50)
        self.table_year.setColumnWidth(1, 80)
        self.table_year.setColumnWidth(2, 130)
        self.table_year.setColumnWidth(3, 130)
        self.table_year.setColumnWidth(4, 130)
        self.table_year.setColumnWidth(5, 80)
        
        self.table_year.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_year.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_year.setAlternatingRowColors(True)
        self.table_year.verticalHeader().setVisible(False)
        header = self.table_year.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
    
    def _on_load_year(self):
        """Load tổng kết cả năm - tính TBC từ HK1 và HK2"""
        nam_hoc_id = self.cmb_nam_hoc_year.currentData()
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        # Lấy danh sách lớp
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_lop = result.data or []
        
        if not ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return
        
        # Tính điểm HK1 (tuần 1-18) và HK2 (tuần 19-35)
        year_data = []
        
        for lop in ds_lop:
            # Tính HK1
            diem_hk1_list = []
            for tuan in range(1, 19):
                diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
                if diem_result.ok:
                    diem_dict = diem_result.data
                    if lop.id in diem_dict:
                        diem_hoc_tap = diem_dict[lop.id].get('diem_hoc_tap', 0)
                        diem_doi = diem_dict[lop.id].get('diem_doi', 0)
                        diem_tb_tuan = (diem_hoc_tap * 2 + diem_doi) / 3
                        diem_hk1_list.append(diem_tb_tuan)
            
            if diem_hk1_list:
                tb_hk1 = sum(diem_hk1_list) / len(diem_hk1_list)
            else:
                tb_hk1 = 0
            
            # Tính HK2
            diem_hk2_list = []
            for tuan in range(19, 36):
                diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
                if diem_result.ok:
                    diem_dict = diem_result.data
                    if lop.id in diem_dict:
                        diem_hoc_tap = diem_dict[lop.id].get('diem_hoc_tap', 0)
                        diem_doi = diem_dict[lop.id].get('diem_doi', 0)
                        diem_tb_tuan = (diem_hoc_tap * 2 + diem_doi) / 3
                        diem_hk2_list.append(diem_tb_tuan)
            
            if diem_hk2_list:
                tb_hk2 = sum(diem_hk2_list) / len(diem_hk2_list)
            else:
                tb_hk2 = 0
            
            # Cả năm = (HK1 + HK2) / 2
            tb_nam = (tb_hk1 + tb_hk2) / 2
            
            year_data.append({
                'lop': lop,
                'tb_hk1': tb_hk1,
                'tb_hk2': tb_hk2,
                'tb_nam': tb_nam
            })
        
        self._render_year_table(year_data)
    
    def _render_year_table(self, year_data):
        """Hiển thị bảng cả năm"""
        self.table_year.setRowCount(len(year_data))
        
        # Sắp xếp theo tổng điểm cả năm
        sorted_data = sorted(year_data, key=lambda x: x['tb_nam'], reverse=True)
        
        # Tạo map thứ hạng
        rank_map = {}
        rank = 1
        for i, item in enumerate(sorted_data):
            if i > 0 and item['tb_nam'] < sorted_data[i-1]['tb_nam']:
                rank = i + 1
            rank_map[item['lop'].id] = rank
        
        # Chuẩn bị dữ liệu biểu đồ
        chart_data = [(item['lop'].ten_lop, item['tb_nam']) for item in year_data]
        self._update_year_chart(chart_data)
        
        for row, item in enumerate(year_data):
            lop = item['lop']
            
            # STT
            cell = QTableWidgetItem(str(row + 1))
            cell.setTextAlignment(Qt.AlignCenter)
            self.table_year.setItem(row, 0, cell)
            
            # Lớp
            cell = QTableWidgetItem(lop.ten_lop)
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_year.setItem(row, 1, cell)
            
            # Điểm TB HK1
            cell = QTableWidgetItem(f"{item['tb_hk1']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_year.setItem(row, 2, cell)
            
            # Điểm TB HK2
            cell = QTableWidgetItem(f"{item['tb_hk2']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_year.setItem(row, 3, cell)
            
            # Điểm TB cả năm
            cell = QTableWidgetItem(f"{item['tb_nam']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._color_total(cell, item['tb_nam'])
            self.table_year.setItem(row, 4, cell)
            
            # Xếp thứ
            rank = rank_map.get(lop.id, 0)
            cell = QTableWidgetItem(str(rank) if rank > 0 else "---")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if rank == 1:
                cell.setBackground(self.COLOR_TOP1)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 2:
                cell.setBackground(self.COLOR_TOP2)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 3:
                cell.setBackground(self.COLOR_TOP3)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            self.table_year.setItem(row, 5, cell)

    def _update_year_chart(self, chart_data):
        """Cập nhật biểu đồ cả năm"""
        sorted_data = sorted(chart_data, key=lambda x: x[1], reverse=True)
        top_data = sorted_data[:10]
        
        colors = [
            QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
            QColor("#1D9E75"), QColor("#FFA500"),
        ]
        
        chart_with_colors = []
        for i, (label, value) in enumerate(top_data):
            if i < 3:
                color = colors[i]
            elif i < 6:
                color = colors[3]
            else:
                color = colors[4]
            chart_with_colors.append((label, value, color))
        
        self.bar_chart_year.set_data(chart_with_colors)
        
        if top_data:
            top1 = top_data[0]
            top2 = top_data[1] if len(top_data) > 1 else ("---", 0)
            top3 = top_data[2] if len(top_data) > 2 else ("---", 0)
            self.summary_label_year.setText(
                f"🏆 TOP 10 - CẢ NĂM:  "
                f"🥇 {top1[0]} ({top1[1]:.3f})  |  "
                f"🥈 {top2[0]} ({top2[1]:.3f})  |  "
                f"🥉 {top3[0]} ({top3[1]:.3f})"
            )
    # ==================== TAB ĐẶC BIỆT ====================

    def _setup_special_table(self):
        """Cấu hình bảng đặc biệt - 6 cột"""
        headers = ["STT", "Lớp", "TB học tập", "TB Đội", "TB đợt", "Xếp thứ"]
        self.table_special.setColumnCount(len(headers))
        self.table_special.setHorizontalHeaderLabels(headers)
        
        self.table_special.setColumnWidth(0, 50)
        self.table_special.setColumnWidth(1, 80)
        self.table_special.setColumnWidth(2, 120)
        self.table_special.setColumnWidth(3, 100)
        self.table_special.setColumnWidth(4, 100)
        self.table_special.setColumnWidth(5, 70)
        
        self.table_special.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_special.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_special.setAlternatingRowColors(True)
        self.table_special.verticalHeader().setVisible(False)
        header = self.table_special.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

    def _setup_special_tab(self):
        """Thiết lập tab Đặc biệt - chọn các tuần tùy ý"""
        layout = QVBoxLayout(self.special_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Thanh lọc
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc_special = QComboBox()
        self.cmb_nam_hoc_special.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc_special)

        filter_layout.addWidget(QLabel("Chọn tuần:"))
        self.list_tuan_special = QComboBox()
        self.list_tuan_special.setMinimumWidth(200)
        self.list_tuan_special.setEditable(False)
        filter_layout.addWidget(self.list_tuan_special)
        
        self.btn_add_tuan = QPushButton("➕ Thêm tuần")
        filter_layout.addWidget(self.btn_add_tuan)
        
        self.btn_clear_tuan = QPushButton("🗑 Xóa hết")
        filter_layout.addWidget(self.btn_clear_tuan)
        
        filter_layout.addStretch()
        
        self.btn_load_special = QPushButton("🔍 Hiển thị")
        filter_layout.addWidget(self.btn_load_special)
        layout.addLayout(filter_layout)
        
        # Danh sách tuần đã chọn
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("Tuần đã chọn:"))
        self.lbl_selected_weeks = QLabel("(Chưa chọn tuần nào)")
        self.lbl_selected_weeks.setStyleSheet("color:#1D9E75; font-weight:bold;")
        selected_layout.addWidget(self.lbl_selected_weeks)
        selected_layout.addStretch()
        layout.addLayout(selected_layout)

        # Splitter: Bảng trái - Biểu đồ phải
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_special = QTableWidget()
        self._setup_special_table()  # Gọi method cấu hình bảng
        left_layout.addWidget(self.table_special)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        
        self.bar_chart_special = HorizontalBarChart()
        right_layout.addWidget(self.bar_chart_special)
        
        self.summary_label_special = QLabel("📈 TỔNG QUAN ĐỢT: --")
        self.summary_label_special.setStyleSheet(
            "color:#555; font-size:11px; padding:8px; "
            "background:#F5F5F5; border-radius:5px; margin:8px;"
        )
        self.summary_label_special.setAlignment(Qt.AlignCenter)
        self.summary_label_special.setWordWrap(True)
        right_layout.addWidget(self.summary_label_special)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([530, 550])
        
        layout.addWidget(splitter)

        # Lưu dữ liệu
        self._selected_weeks = []
        self._update_selected_weeks_display()
        
        # Kết nối signals
        self.btn_add_tuan.clicked.connect(self._on_add_tuan)
        self.btn_clear_tuan.clicked.connect(self._on_clear_tuan)
        self.btn_load_special.clicked.connect(self._on_load_special)
        
        # Load tuần vào combobox khi chọn năm học
        self.cmb_nam_hoc_special.currentIndexChanged.connect(self._load_weeks_to_combobox)
    
    def _load_weeks_to_combobox(self):
        """Load danh sách tuần vào combobox khi chọn năm học"""
        nam_hoc_id = self.cmb_nam_hoc_special.currentData()
        if not nam_hoc_id:
            return
        
        self.list_tuan_special.clear()
        for i in range(1, 36):
            self.list_tuan_special.addItem(f"Tuần {i}", i)
    
    def _update_selected_weeks_display(self):
        """Cập nhật hiển thị danh sách tuần đã chọn"""
        if not self._selected_weeks:
            self.lbl_selected_weeks.setText("(Chưa chọn tuần nào)")
        else:
            weeks_str = ", ".join([f"Tuần {w}" for w in sorted(self._selected_weeks)])
            self.lbl_selected_weeks.setText(weeks_str)

    def _on_add_tuan(self):
        """Thêm tuần được chọn vào danh sách"""
        tuan = self.list_tuan_special.currentData()
        if tuan and tuan not in self._selected_weeks:
            self._selected_weeks.append(tuan)
            self._selected_weeks.sort()
            self._update_selected_weeks_display()

    def _on_clear_tuan(self):
        """Xóa tất cả tuần đã chọn"""
        self._selected_weeks.clear()
        self._update_selected_weeks_display()
        # Xóa nội dung bảng
        self.table_special.setRowCount(0)
        self.summary_label_special.setText("📈 TỔNG QUAN ĐỢT: --")

    def _on_load_special(self):
        """Load dữ liệu cho đợt đặc biệt"""
        nam_hoc_id = self.cmb_nam_hoc_special.currentData()
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        if not self._selected_weeks:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 1 tuần!")
            return
        
        result = self.svc.get_ds_lop_theo_nam_hoc(nam_hoc_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_lop = result.data or []
        
        if not ds_lop:
            QMessageBox.warning(self, "Thông báo", "Không có lớp nào!")
            return
        
        special_data = []
        for lop in ds_lop:
            diem_hoc_tap_list = []
            diem_doi_list = []
            
            for tuan in self._selected_weeks:
                diem_result = self.svc.get_diem_tuan(nam_hoc_id, tuan)
                if diem_result.ok:
                    diem_dict = diem_result.data
                    if lop.id in diem_dict:
                        diem_hoc_tap_list.append(diem_dict[lop.id].get('diem_hoc_tap', 0))
                        diem_doi_list.append(diem_dict[lop.id].get('diem_doi', 0))
            
            if diem_hoc_tap_list:
                tb_hoc_tap = sum(diem_hoc_tap_list) / len(diem_hoc_tap_list)
                tb_doi = sum(diem_doi_list) / len(diem_doi_list)
                tb_dot = (tb_hoc_tap * 2 + tb_doi) / 3
            else:
                tb_hoc_tap = 0
                tb_doi = 0
                tb_dot = 0
            
            special_data.append({
                'lop': lop,
                'tb_hoc_tap': tb_hoc_tap,
                'tb_doi': tb_doi,
                'tb_dot': tb_dot
            })
        
        self._render_special_table(special_data)

    def _render_special_table(self, special_data):
        """Hiển thị bảng đặc biệt"""
        self.table_special.setRowCount(len(special_data))
        
        sorted_data = sorted(special_data, key=lambda x: x['tb_dot'], reverse=True)
        
        rank_map = {}
        rank = 1
        for i, item in enumerate(sorted_data):
            if i > 0 and item['tb_dot'] < sorted_data[i-1]['tb_dot']:
                rank = i + 1
            rank_map[item['lop'].id] = rank
        
        chart_data = [(item['lop'].ten_lop, item['tb_dot']) for item in special_data]
        self._update_special_chart(chart_data)
        
        for row, item in enumerate(special_data):
            lop = item['lop']
            
            # STT
            cell = QTableWidgetItem(str(row + 1))
            cell.setTextAlignment(Qt.AlignCenter)
            self.table_special.setItem(row, 0, cell)
            
            # Lớp
            cell = QTableWidgetItem(lop.ten_lop)
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_special.setItem(row, 1, cell)
            
            # TB học tập
            cell = QTableWidgetItem(f"{item['tb_hoc_tap']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_special.setItem(row, 2, cell)
            
            # TB Đội
            cell = QTableWidgetItem(f"{item['tb_doi']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_special.setItem(row, 3, cell)
            
            # TB đợt
            cell = QTableWidgetItem(f"{item['tb_dot']:.3f}")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self._color_total(cell, item['tb_dot'])
            self.table_special.setItem(row, 4, cell)
            
            # Xếp thứ
            rank = rank_map.get(lop.id, 0)
            cell = QTableWidgetItem(str(rank) if rank > 0 else "---")
            cell.setTextAlignment(Qt.AlignCenter)
            cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if rank == 1:
                cell.setBackground(self.COLOR_TOP1)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 2:
                cell.setBackground(self.COLOR_TOP2)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 3:
                cell.setBackground(self.COLOR_TOP3)
                cell.setFont(QFont("Arial", 10, QFont.Bold))
            self.table_special.setItem(row, 5, cell)

    def _update_special_chart(self, chart_data):
        """Cập nhật biểu đồ đặc biệt"""
        sorted_data = sorted(chart_data, key=lambda x: x[1], reverse=True)
        top_data = sorted_data[:10]
        
        colors = [
            QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
            QColor("#1D9E75"), QColor("#FFA500"),
        ]
        
        chart_with_colors = []
        for i, (label, value) in enumerate(top_data):
            if i < 3:
                color = colors[i]
            elif i < 6:
                color = colors[3]
            else:
                color = colors[4]
            chart_with_colors.append((label, value, color))
        
        self.bar_chart_special.set_data(chart_with_colors)
        
        if top_data:
            weeks_str = ", ".join([f"Tuần{w}" for w in sorted(self._selected_weeks)])
            top1 = top_data[0]
            top2 = top_data[1] if len(top_data) > 1 else ("---", 0)
            top3 = top_data[2] if len(top_data) > 2 else ("---", 0)
            self.summary_label_special.setText(
                f"🏆 ĐỢT ({weeks_str}):  "
                f"🥇 {top1[0]} ({top1[1]:.3f})  |  "
                f"🥈 {top2[0]} ({top2[1]:.3f})  |  "
                f"🥉 {top3[0]} ({top3[1]:.3f})"
            )
    # ==================== LOAD NĂM HỌC ====================

    def _load_nam_hoc(self):
        try:
            from core.db.models.nam_hoc import NamHoc
            from core.db.session import SessionLocal

            session = SessionLocal()
            nam_hocs = session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all()
            for nh in nam_hocs:
                self.cmb_nam_hoc_week.addItem(nh.ten_nam_hoc, nh.id)
                self.cmb_nam_hoc_month.addItem(nh.ten_nam_hoc, nh.id)
                if hasattr(self, 'cmb_nam_hoc_hk1'):
                    self.cmb_nam_hoc_hk1.addItem(nh.ten_nam_hoc, nh.id)
                    self.cmb_nam_hoc_hk2.addItem(nh.ten_nam_hoc, nh.id)
                if hasattr(self, 'cmb_nam_hoc_year'):
                    self.cmb_nam_hoc_year.addItem(nh.ten_nam_hoc, nh.id)
                if hasattr(self, 'cmb_nam_hoc_special'):
                    self.cmb_nam_hoc_special.addItem(nh.ten_nam_hoc, nh.id)
            session.close()
            
            if self.cmb_nam_hoc_week.count() > 0:
                self.cmb_nam_hoc_week.setCurrentIndex(0)
                self.cmb_nam_hoc_month.setCurrentIndex(0)
                if hasattr(self, 'cmb_nam_hoc_hk1'):
                    self.cmb_nam_hoc_hk1.setCurrentIndex(0)
                    self.cmb_nam_hoc_hk2.setCurrentIndex(0)
                if hasattr(self, 'cmb_nam_hoc_year'):
                    self.cmb_nam_hoc_year.setCurrentIndex(0)
                if hasattr(self, 'cmb_nam_hoc_special'):
                    self.cmb_nam_hoc_special.setCurrentIndex(0)
                    self._load_weeks_to_combobox()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải năm học: {e}")

    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)