# modules/system/views/log_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QComboBox, QDateEdit,
    QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import os
from datetime import datetime


class LogTab(QWidget):
    """Tab nhật ký hệ thống"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_logs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # === Bộ lọc ===
        filter_group = QGroupBox("🔍 Lọc nhật ký")
        filter_group.setStyleSheet("""
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
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Từ ngày:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("Đến ngày:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(QLabel("Mức độ:"))
        self.cmb_level = QComboBox()
        self.cmb_level.addItem("Tất cả", "all")
        self.cmb_level.addItem("ℹ️ Thông tin", "INFO")
        self.cmb_level.addItem("⚠️ Cảnh báo", "WARNING")
        self.cmb_level.addItem("❌ Lỗi", "ERROR")
        filter_layout.addWidget(self.cmb_level)

        self.btn_filter = QPushButton("🔍 Lọc")
        self.btn_filter.clicked.connect(self._load_logs)
        filter_layout.addWidget(self.btn_filter)

        self.btn_export = QPushButton("📤 Xuất log")
        self.btn_export.clicked.connect(self._export_logs)
        filter_layout.addWidget(self.btn_export)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # === Bảng nhật ký ===
        self.table_log = QTableWidget()
        headers = ["STT", "Thời gian", "Mức độ", "Nội dung"]
        self.table_log.setColumnCount(len(headers))
        self.table_log.setHorizontalHeaderLabels(headers)
        self.table_log.setColumnWidth(0, 40)
        self.table_log.setColumnWidth(1, 150)
        self.table_log.setColumnWidth(2, 100)
        self.table_log.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_log.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_log.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_log.setAlternatingRowColors(True)
        self.table_log.verticalHeader().setVisible(False)
        self.table_log.doubleClicked.connect(self._show_log_detail)
        layout.addWidget(self.table_log)

        # === Chi tiết log ===
        detail_group = QGroupBox("📄 Chi tiết")
        detail_group.setStyleSheet("""
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
        detail_layout = QVBoxLayout(detail_group)
        self.txt_detail = QTextEdit()
        self.txt_detail.setReadOnly(True)
        self.txt_detail.setMaximumHeight(100)
        self.txt_detail.setPlaceholderText("Chọn một dòng log để xem chi tiết...")
        detail_layout.addWidget(self.txt_detail)
        layout.addWidget(detail_group)

        # Status
        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        layout.addWidget(self.status_label)

    def _load_logs(self):
        """Load nhật ký từ file"""
        self.table_log.setRowCount(0)
        self.txt_detail.clear()

        log_dir = "logs"
        if not os.path.exists(log_dir):
            self.status_label.setText("📁 Chưa có thư mục logs")
            return

        # Lấy ngày
        from_date = self.date_from.date().toPython()
        to_date = self.date_to.date().toPython()
        level = self.cmb_level.currentData()

        logs = []
        for file in os.listdir(log_dir):
            if file.endswith(".log"):
                file_path = os.path.join(log_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            # Parse log
                            parts = line.split(' - ', 3)
                            if len(parts) >= 4:
                                timestamp_str = parts[0]
                                level_str = parts[1]
                                module = parts[2]
                                content = parts[3]

                                try:
                                    log_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                except:
                                    continue

                                # Lọc theo ngày
                                if log_date.date() < from_date or log_date.date() > to_date:
                                    continue

                                # Lọc theo level
                                if level != "all" and level_str != level:
                                    continue

                                logs.append({
                                    'timestamp': log_date,
                                    'level': level_str,
                                    'module': module,
                                    'content': content
                                })
                except:
                    continue

        # Sắp xếp theo thời gian giảm dần
        logs.sort(key=lambda x: x['timestamp'], reverse=True)

        # Hiển thị
        self.table_log.setRowCount(len(logs))
        for row, log in enumerate(logs):
            # STT
            item_stt = QTableWidgetItem(str(row + 1))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table_log.setItem(row, 0, item_stt)

            # Thời gian
            item_time = QTableWidgetItem(log['timestamp'].strftime("%d/%m/%Y %H:%M:%S"))
            item_time.setTextAlignment(Qt.AlignCenter)
            self.table_log.setItem(row, 1, item_time)

            # Mức độ
            item_level = QTableWidgetItem(log['level'])
            item_level.setTextAlignment(Qt.AlignCenter)
            if log['level'] == "ERROR":
                item_level.setBackground(QColor("#FFE5E5"))
                item_level.setForeground(QColor("#CC0000"))
            elif log['level'] == "WARNING":
                item_level.setBackground(QColor("#FFF3E0"))
                item_level.setForeground(QColor("#E65100"))
            elif log['level'] == "INFO":
                item_level.setBackground(QColor("#E8F5E9"))
                item_level.setForeground(QColor("#2E7D32"))
            self.table_log.setItem(row, 2, item_level)

            # Nội dung
            display_content = log['content'][:100] + "..." if len(log['content']) > 100 else log['content']
            self.table_log.setItem(row, 3, QTableWidgetItem(display_content))

            # Lưu dữ liệu đầy đủ vào row
            self.table_log.item(row, 3).setData(Qt.UserRole, log['content'])

        self.status_label.setText(f"📋 Hiển thị {len(logs)} dòng log")

    def _show_log_detail(self):
        """Hiển thị chi tiết log khi double-click"""
        row = self.table_log.currentRow()
        if row >= 0:
            item = self.table_log.item(row, 3)
            if item:
                detail = item.data(Qt.UserRole) or item.text()
                self.txt_detail.setText(detail)

    def _export_logs(self):
        """Xuất log ra file text"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất nhật ký",
            f"logs_{datetime.now().strftime('%Y%m%d')}.txt",
            "Text Files (*.txt)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("NHẬT KÝ HỆ THỐNG\n")
                f.write(f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                for row in range(self.table_log.rowCount()):
                    time = self.table_log.item(row, 1).text()
                    level = self.table_log.item(row, 2).text()
                    content = self.table_log.item(row, 3).data(Qt.UserRole) or self.table_log.item(row, 3).text()
                    f.write(f"[{time}] {level}: {content}\n")

            QMessageBox.information(self, "Thành công", f"Đã xuất log ra file:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))