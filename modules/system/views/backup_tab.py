# modules/system/views/backup_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
import os
import shutil
import sqlite3
from datetime import datetime
import zipfile


class BackupTab(QWidget):
    """Tab sao lưu và phục hồi dữ liệu"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backup_list = []
        self._build_ui()
        self._load_backup_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # === Hàng 1: Sao lưu mới ===
        backup_group = QGroupBox("💾 Sao lưu dữ liệu")
        backup_group.setStyleSheet("""
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
        backup_layout = QVBoxLayout(backup_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("📂 Thư mục lưu:"))

        self.lbl_backup_path = QLabel("D:/Backup/")
        self.lbl_backup_path.setStyleSheet("color: #666; padding: 4px; border: 1px solid #DDD; border-radius: 4px;")
        self.lbl_backup_path.setMinimumWidth(300)
        row1.addWidget(self.lbl_backup_path)

        self.btn_change_path = QPushButton("📂 Đổi")
        self.btn_change_path.clicked.connect(self._change_backup_path)
        row1.addWidget(self.btn_change_path)

        row1.addStretch()
        backup_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("📋 Nội dung sao lưu:"))

        self.chk_database = QCheckBox("🗄️ Cơ sở dữ liệu")
        self.chk_database.setChecked(True)
        self.chk_uploads = QCheckBox("📎 File uploads")
        self.chk_logs = QCheckBox("📝 Nhật ký hệ thống")

        row2.addWidget(self.chk_database)
        row2.addWidget(self.chk_uploads)
        row2.addWidget(self.chk_logs)
        row2.addStretch()
        backup_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.btn_backup = QPushButton("🔄 Tạo sao lưu mới")
        self.btn_backup.setStyleSheet("background: #1D9E75; color: white; font-weight: bold;")
        self.btn_backup.setFixedHeight(36)
        self.btn_backup.clicked.connect(self._create_backup)
        row3.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("♻️ Phục hồi")
        self.btn_restore.setStyleSheet("background: #FF9800; color: white; font-weight: bold;")
        self.btn_restore.setFixedHeight(36)
        self.btn_restore.clicked.connect(self._restore_backup)
        row3.addWidget(self.btn_restore)

        row3.addStretch()
        backup_layout.addLayout(row3)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        backup_layout.addWidget(self.progress)

        layout.addWidget(backup_group)

        # === Hàng 2: Danh sách sao lưu ===
        list_group = QGroupBox("📋 Danh sách sao lưu")
        list_group.setStyleSheet("""
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
        list_layout = QVBoxLayout(list_group)

        self.table_backup = QTableWidget()
        headers = ["STT", "Tên file", "Ngày tạo", "Dung lượng", "Trạng thái"]
        self.table_backup.setColumnCount(len(headers))
        self.table_backup.setHorizontalHeaderLabels(headers)
        self.table_backup.setColumnWidth(0, 40)
        self.table_backup.setColumnWidth(1, 200)
        self.table_backup.setColumnWidth(2, 150)
        self.table_backup.setColumnWidth(3, 100)
        self.table_backup.setColumnWidth(4, 100)
        self.table_backup.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_backup.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_backup.setAlternatingRowColors(True)
        self.table_backup.verticalHeader().setVisible(False)
        self.table_backup.doubleClicked.connect(self._on_backup_double_click)
        list_layout.addWidget(self.table_backup)

        # Nút xóa
        btn_delete = QPushButton("🗑️ Xóa sao lưu đã chọn")
        btn_delete.setFixedHeight(30)
        btn_delete.clicked.connect(self._delete_backup)
        list_layout.addWidget(btn_delete)

        layout.addWidget(list_group)

        # Status
        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        layout.addWidget(self.status_label)

    def _change_backup_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục sao lưu")
        if folder:
            self.lbl_backup_path.setText(folder)

    def _create_backup(self):
        """Tạo file sao lưu"""
        backup_dir = self.lbl_backup_path.text()
        if not os.path.exists(backup_dir):
            try:
                os.makedirs(backup_dir)
            except:
                QMessageBox.warning(self, "Lỗi", "Không thể tạo thư mục sao lưu!")
                return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"eduschool_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_name)

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_backup.setEnabled(False)
        self.status_label.setText("⏳ Đang tạo sao lưu...")

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Sao lưu database
                if self.chk_database.isChecked():
                    db_path = "eduschool.db"
                    if os.path.exists(db_path):
                        zipf.write(db_path, "database/eduschool.db")
                        self.progress.setValue(30)
                    else:
                        # Tạo file rỗng để báo hiệu
                        zipf.writestr("database/eduschool.db", "Database not found")
                        self.progress.setValue(30)

                # Sao lưu file uploads
                if self.chk_uploads.isChecked():
                    uploads_dir = "uploads"
                    if os.path.exists(uploads_dir):
                        for root, dirs, files in os.walk(uploads_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join("uploads", os.path.relpath(file_path, uploads_dir))
                                zipf.write(file_path, arcname)
                        self.progress.setValue(60)
                    else:
                        zipf.writestr("uploads/", "Uploads directory not found")
                        self.progress.setValue(60)

                # Sao lưu log
                if self.chk_logs.isChecked():
                    log_dir = "logs"
                    if os.path.exists(log_dir):
                        log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
                        for log_file in log_files:
                            file_path = os.path.join(log_dir, log_file)
                            zipf.write(file_path, f"logs/{log_file}")
                        self.progress.setValue(90)
                    else:
                        zipf.writestr("logs/", "Logs directory not found")
                        self.progress.setValue(90)

                # Thêm thông tin backup
                info = f"""
                ============================================
                THÔNG TIN SAO LƯU
                ============================================
                Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                Tên file: {backup_name}
                Database: {'Có' if self.chk_database.isChecked() else 'Không'}
                Uploads: {'Có' if self.chk_uploads.isChecked() else 'Không'}
                Logs: {'Có' if self.chk_logs.isChecked() else 'Không'}
                ============================================
                """
                zipf.writestr("backup_info.txt", info)

            self.progress.setValue(100)
            self.status_label.setText(f"✅ Đã tạo sao lưu: {backup_name}")
            
            # Ghi log
            from core.utils.logger import logger
            logger.log_action(
                user="Hệ thống",
                action="Tạo sao lưu",
                details=f"File: {backup_name}, Dung lượng: {self._format_size(os.path.getsize(backup_path))}"
            )
            
            QMessageBox.information(self, "Thành công", f"Đã tạo file sao lưu:\n{backup_path}")
            self._load_backup_list()

        except Exception as e:
            self.status_label.setText("❌ Tạo sao lưu thất bại!")
            QMessageBox.critical(self, "Lỗi", str(e))

        self.progress.setVisible(False)
        self.btn_backup.setEnabled(True)

    def _load_backup_list(self):
        """Load danh sách file sao lưu"""
        backup_dir = self.lbl_backup_path.text()
        self._backup_list = []

        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.startswith("eduschool_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(backup_dir, file)
                    stat = os.stat(file_path)
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    self._backup_list.append({
                        'name': file,
                        'path': file_path,
                        'date': mtime,
                        'size': size
                    })

        self._backup_list.sort(key=lambda x: x['date'], reverse=True)
        self._render_backup_list()

    def _render_backup_list(self):
        self.table_backup.setRowCount(len(self._backup_list))
        for row, item in enumerate(self._backup_list):
            # STT
            item_stt = QTableWidgetItem(str(row + 1))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table_backup.setItem(row, 0, item_stt)

            # Tên file
            self.table_backup.setItem(row, 1, QTableWidgetItem(item['name']))

            # Ngày tạo
            date_str = item['date'].strftime("%d/%m/%Y %H:%M:%S")
            item_date = QTableWidgetItem(date_str)
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table_backup.setItem(row, 2, item_date)

            # Dung lượng
            size_str = self._format_size(item['size'])
            item_size = QTableWidgetItem(size_str)
            item_size.setTextAlignment(Qt.AlignCenter)
            self.table_backup.setItem(row, 3, item_size)

            # Trạng thái
            item_status = QTableWidgetItem("✅ OK")
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table_backup.setItem(row, 4, item_status)

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _restore_backup(self):
        row = self.table_backup.currentRow()
        if row < 0 or row >= len(self._backup_list):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file sao lưu!")
            return

        item = self._backup_list[row]
        reply = QMessageBox.question(
            self,
            "Xác nhận phục hồi",
            f"Phục hồi dữ liệu từ file:\n{item['name']}\n\n"
            "Dữ liệu hiện tại sẽ bị ghi đè!\nBạn có chắc chắn?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.status_label.setText("⏳ Đang phục hồi dữ liệu...")

        try:
            with zipfile.ZipFile(item['path'], 'r') as zipf:
                zipf.extractall("restore_temp")

            # Kiểm tra database
            if os.path.exists("restore_temp/database/eduschool.db"):
                shutil.copy2("restore_temp/database/eduschool.db", "eduschool.db")

            # Phục hồi uploads
            if os.path.exists("restore_temp/uploads"):
                if os.path.exists("uploads"):
                    shutil.rmtree("uploads")
                shutil.copytree("restore_temp/uploads", "uploads")

            # Xóa thư mục tạm
            shutil.rmtree("restore_temp")

            self.status_label.setText("✅ Phục hồi thành công!")
            QMessageBox.information(self, "Thành công", "Đã phục hồi dữ liệu thành công!\nVui lòng khởi động lại ứng dụng.")

        except Exception as e:
            self.status_label.setText("❌ Phục hồi thất bại!")
            QMessageBox.critical(self, "Lỗi", str(e))

    def _delete_backup(self):
        row = self.table_backup.currentRow()
        if row < 0 or row >= len(self._backup_list):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file sao lưu!")
            return

        item = self._backup_list[row]
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Xóa file sao lưu:\n{item['name']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            os.remove(item['path'])
            self._load_backup_list()
            self.status_label.setText(f"✅ Đã xóa: {item['name']}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _on_backup_double_click(self):
        self._restore_backup()