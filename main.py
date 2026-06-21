# D:\QUANLYTRUONGHOC\main.py

"""
Điểm khởi động EduSchool Suite.
Chạy: python main.py  hoặc  py -3.11 main.py
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QFile

# ===== THÊM PHẦN TẠO THƯ MỤC =====
REQUIRED_DIRS = ["logs", "backups", "uploads", "temp", "restore_temp"]
for dir_name in REQUIRED_DIRS:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"📁 Đã tạo thư mục: {dir_name}")

# ===== THÊM LOGGER =====
from core.utils.logger import logger

# Ghi log khởi động
logger.info("=" * 50)
logger.info("🚀 EduSchool Suite khởi động")
logger.info(f"📅 Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
logger.info(f"💻 Máy tính: {os.name}")
logger.info("=" * 50)


def load_stylesheet():
    """Tải file CSS cho giao diện"""
    file = QFile("core/styles/app.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        stylesheet = file.readAll().data().decode()
        file.close()
        return stylesheet
    return ""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EduSchool Suite")
    app.setOrganizationName("EduSchool")
    app.setFont(QFont("Segoe UI", 10))
    
    # Áp dụng style sheet
    app.setStyleSheet(load_stylesheet())

    # Khởi tạo DB (tạo bảng nếu chưa có)
    from core.db.session import init_db
    init_db()
    logger.info("✅ Kết nối database thành công")

    # Mở màn hình đăng nhập
    from ui.login_page import LoginPage
    login = LoginPage()
    login.show()
    logger.info("👤 Hiển thị màn hình đăng nhập")

    # Ghi log khi thoát
    def on_exit():
        logger.info("🛑 EduSchool Suite đóng")
        logger.info("=" * 50)
    
    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()