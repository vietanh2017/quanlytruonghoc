# modules/giao_vien_thi_dua/views/tabs/ca_nam_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QComboBox, QLabel,
    QPushButton, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from core.db.session import SessionLocal


class HorizontalBarChartCN(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumWidth(250)
        self.setMaximumWidth(320)
        self.setMinimumHeight(350)
        
    def set_data(self, data):
        self.data = data[:10]
        self.update()
        
    def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            if not self.data:
                painter.drawText(self.rect(), Qt.AlignCenter, "📊 Chưa có dữ liệu")
                return
            
            width = self.width() - 20
            height = self.height() - 60
            bar_height = max(12, (height - 20) // len(self.data))
            max_value = max([v for _, v in self.data]) if self.data else 100
            
            colors = [
                QColor("#FFD700"), QColor("#C0C0C0"), QColor("#CD7F32"),
                QColor("#1D9E75"), QColor("#2196F3"), QColor("#9C27B0"),
                QColor("#FF9800"), QColor("#F44336"), QColor("#607D8B"), QColor("#795548"),
            ]
            
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.setPen(QPen(QColor("#333")))
            painter.drawText(0, 20, width, 30, Qt.AlignCenter, "                              📊 TOP XẾP HẠNG")
            
            y_offset = 50
            for i, (label, value) in enumerate(self.data):
                bar_width = int((value / max_value) * (width - 100)) if max_value > 0 else 0
                y = y_offset + i * (bar_height + 3)
                
                # Thứ hạng
                painter.setPen(QPen(QColor("#FFD700") if i == 0 else QColor("#C0C0C0") if i == 1 else QColor("#CD7F32") if i == 2 else QColor("#999")))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                painter.drawText(5, y, 35, bar_height, Qt.AlignLeft | Qt.AlignVCenter, f"#{i+1}")
                
                # Tên
                painter.setPen(QPen(QColor("#333")))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(45, y, 70, bar_height, Qt.AlignLeft | Qt.AlignVCenter, label[:12])
                
                # Thanh bar
                color = colors[i] if i < len(colors) else colors[-1]
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.NoPen)
                rect = QRect(120, y + 2, bar_width, bar_height - 4)
                painter.drawRoundedRect(rect, 4, 4)
                
                # ===== SỐ HIỂN THỊ TRONG THANH =====
                painter.setPen(QPen(QColor("white")))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                
                # Chỉ hiển thị số nếu thanh đủ rộng (> 35px)
                if bar_width > 35:
                    painter.drawText(120, y + 2, bar_width - 5, bar_height - 4,
                                Qt.AlignRight | Qt.AlignVCenter, f"{value:.2f}")
                else:
                    # Nếu thanh quá ngắn, hiển thị số bên phải thanh
                    painter.setPen(QPen(QColor("#555")))
                    painter.drawText(120 + bar_width + 3, y + 2, 40, bar_height - 4,
                                Qt.AlignLeft | Qt.AlignVCenter, f"{value:.2f}")

class CaNamTab(QWidget):
    COLOR_TOP1 = QColor("#FFD700")
    COLOR_TOP2 = QColor("#C0C0C0")
    COLOR_TOP3 = QColor("#CD7F32")
    COLOR_LOW = QColor("#FFE5E5")
    COLOR_MEDIUM = QColor("#FFF3E0")
    COLOR_GOOD = QColor("#E8F5E9")

    def __init__(self, svc, nguoi_dung=None, parent=None):
        super().__init__(parent)
        self.svc = svc
        self.nguoi_dung = nguoi_dung
        self._user_to_id = None
        
        if nguoi_dung:
            try:
                from core.db.models.giao_vien import GiaoVien
                session = SessionLocal()
                gv = session.query(GiaoVien).filter(GiaoVien.nguoi_dung_id == nguoi_dung.id).first()
                if gv:
                    self._user_to_id = gv.to_id
                session.close()
            except:
                pass
        
        self._current_nam_hoc_id = None
        self._ds_gv = []
        
        self._build_ui()
        self._load_filters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 5, 10, 5)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        filter_layout.addWidget(QLabel("🏢 Tổ chuyên môn:"))
        self.cmb_to = QComboBox()
        self.cmb_to.setMinimumWidth(150)
        self.cmb_to.currentIndexChanged.connect(self._on_to_changed)
        filter_layout.addWidget(self.cmb_to)
        
        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc)

        self.btn_load = QPushButton("🔍 Hiển thị")
        self.btn_load.setFixedHeight(28)
        filter_layout.addWidget(self.btn_load)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:10px; padding:2px 4px;")
        self.status_label.setFixedHeight(22)
        layout.addWidget(self.status_label)

        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        self.table = QTableWidget()
        self._setup_table()
        left_layout.addWidget(self.table)
        
        right_widget = QFrame()
        right_widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(4)
        
        self.bar_chart = HorizontalBarChartCN()
        right_layout.addWidget(self.bar_chart)
        
        self.summary_label = QLabel("🏆 TỔNG QUAN: --")
        self.summary_label.setStyleSheet(
            "color:#555; font-size:11px; padding:3px; "
            "background:#F5F5F5; border-radius:5px; margin:5px;"
        )
        self.summary_label.setFixedHeight(32)
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setWordWrap(True)
        right_layout.addWidget(self.summary_label)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 380])
        
        layout.addWidget(splitter)

        note = QLabel(
            "💡 🥇 Vàng | 🥈 Bạc | 🥉 Đồng | 🟢 Xanh (>90) | 🟠 Cam (80-90) | 🔴 Đỏ (<80)"
        )
        note.setStyleSheet("color:#999; font-size:9px; padding:2px 0;")
        note.setFixedHeight(18)
        layout.addWidget(note)

        self.btn_load.clicked.connect(self._on_load)

    def _setup_table(self):
        headers = ["STT", "Mã GV", "Họ tên", "Điểm TB năm", "Xếp loại", "Xếp thứ"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 65)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 95)
        self.table.setColumnWidth(4, 200)
        self.table.setColumnWidth(5, 55)
        
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

    def _load_to_chuyen_mon(self):
        try:
            from core.db.models.to_chuyen_mon import ToChuyenMon
            ds_to = self.svc.session.query(ToChuyenMon).filter(ToChuyenMon.active == True).all()
            self.cmb_to.clear()
            self.cmb_to.addItem("-- Tất cả --", None)
            for to in ds_to:
                self.cmb_to.addItem(to.ten_to, to.id)
            
            if self._user_to_id:
                self.cmb_to.setCurrentIndex(self.cmb_to.findData(self._user_to_id))
                self.cmb_to.setEnabled(False)
        except Exception as e:
            print(f"Lỗi load tổ: {e}")

    def _load_filters(self):
        self._load_to_chuyen_mon()
        
        try:
            from core.db.models.nam_hoc import NamHoc
            nam_hocs = self.svc.session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all()
            for nh in nam_hocs:
                self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
            if self.cmb_nam_hoc.count() > 0:
                self.cmb_nam_hoc.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải năm học: {e}")

    def _on_to_changed(self):
        """Khi chọn tổ, reload dữ liệu"""
        # Chỉ load nếu đã có năm học
        if self.cmb_nam_hoc.currentData():
            self._on_load()

    def _on_load(self):
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        to_id = self.cmb_to.currentData()
        
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return
        
        result = self.svc.lay_ds_giao_vien_theo_to(to_id)
        if not result.ok:
            QMessageBox.critical(self, "Lỗi", result.error)
            return
        ds_gv = result.data or []
        
        if not ds_gv:
            QMessageBox.warning(self, "Thông báo", "Không có giáo viên nào trong tổ này!")
            self.table.setRowCount(0)
            return
        
        diem_list = []
        for gv in ds_gv:
            from core.db.models.hoc_ky import HocKy
            hks = self.svc.session.query(HocKy).filter(HocKy.nam_hoc_id == nam_hoc_id).order_by(HocKy.so_thu_tu).all()
            
            diem_hk_list = []
            for hk in hks:
                r = self.svc.tinh_diem_hoc_ky(gv.id, hk.id, nam_hoc_id)
                if r.ok:
                    diem_hk_list.append(r.data["diem"])
            
            if diem_hk_list:
                diem_tb = sum(diem_hk_list) / len(diem_hk_list)
                xep_loai = self.svc.xep_loai(diem_tb)
            else:
                diem_tb = 0
                xep_loai = "Chưa có dữ liệu"
            
            diem_list.append({
                'gv': gv,
                'diem': diem_tb,
                'xep_loai': xep_loai,
                'ten': gv.nguoi_dung.ho_ten if gv.nguoi_dung else f"GV{gv.id}"
            })
        
        diem_list.sort(key=lambda x: x['diem'], reverse=True)
        self._render_table(diem_list)
        self._update_chart(diem_list)
        
        ten_to = self.cmb_to.currentText()
        self.status_label.setText(f"🎯 Tổng kết cả năm - {self.cmb_nam_hoc.currentText()} - {ten_to}")

    def _render_table(self, diem_list):
        self.table.setRowCount(len(diem_list))
        
        for row, item in enumerate(diem_list):
            gv = item['gv']
            diem = item['diem']
            xep_loai = item['xep_loai']
            rank = row + 1
            
            item_stt = QTableWidgetItem(str(rank))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_stt)
            
            item_ma = QTableWidgetItem(gv.ma_giao_vien or "")
            item_ma.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item_ma)
            
            self.table.setItem(row, 2, QTableWidgetItem(item['ten']))
            
            item_diem = QTableWidgetItem(f"{diem:.1f}")
            item_diem.setTextAlignment(Qt.AlignCenter)
            if diem >= 90:
                item_diem.setBackground(self.COLOR_GOOD)
                item_diem.setForeground(QColor("#2E7D32"))
            elif diem >= 80:
                item_diem.setBackground(self.COLOR_MEDIUM)
                item_diem.setForeground(QColor("#E65100"))
            else:
                item_diem.setBackground(self.COLOR_LOW)
                item_diem.setForeground(QColor("#CC0000"))
            self.table.setItem(row, 3, item_diem)
            
            item_xl = QTableWidgetItem(xep_loai)
            item_xl.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item_xl)
            
            item_rank = QTableWidgetItem(str(rank))
            item_rank.setTextAlignment(Qt.AlignCenter)
            if rank == 1:
                item_rank.setBackground(self.COLOR_TOP1)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 2:
                item_rank.setBackground(self.COLOR_TOP2)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            elif rank == 3:
                item_rank.setBackground(self.COLOR_TOP3)
                item_rank.setFont(QFont("Arial", 10, QFont.Bold))
            self.table.setItem(row, 5, item_rank)

    def _update_chart(self, diem_list):
        # Lấy tên (phần cuối cùng sau khoảng trắng)
        chart_data = [(item['ten'].split()[-1] if ' ' in item['ten'] else item['ten'][:10], item['diem']) 
                    for item in diem_list[:10]]
        self.bar_chart.set_data(chart_data)
        
        if diem_list:
            top1 = diem_list[0]
            top2 = diem_list[1] if len(diem_list) > 1 else None
            top3 = diem_list[2] if len(diem_list) > 2 else None
            
            # Lấy tên cho phần tổng quan
            ten1 = top1['ten'].split()[-1] if ' ' in top1['ten'] else top1['ten']
            ten2 = top2['ten'].split()[-1] if top2 and ' ' in top2['ten'] else (top2['ten'] if top2 else "")
            ten3 = top3['ten'].split()[-1] if top3 and ' ' in top3['ten'] else (top3['ten'] if top3 else "")
            
            # Lấy tiêu đề phù hợp (tùy từng tab)
            if hasattr(self, '_current_thang'):
                tieu_de = f"🏆 Tháng {self._current_thang}: "
            elif hasattr(self, '_current_hoc_ky_id'):
                ten_hk = self.cmb_hoc_ky.currentText()
                tieu_de = f"🏆 {ten_hk}: "
            else:
                tieu_de = f"🏆 CẢ NĂM: "
            
            text = tieu_de
            text += f"🥇 {ten1} ({top1['diem']:.1f})"
            if top2:
                text += f" | 🥈 {ten2} ({top2['diem']:.1f})"
            if top3:
                text += f" | 🥉 {ten3} ({top3['diem']:.1f})"
            self.summary_label.setText(text)