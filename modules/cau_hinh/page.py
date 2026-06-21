from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core.db.session import SessionLocal
from modules.cau_hinh.views.nam_hoc_tab import NamHocTab
from modules.cau_hinh.views.to_chuyen_mon_tab import ToChuyenMonTab
from modules.cau_hinh.views.mon_hoc_tab import MonHocTab
from modules.cau_hinh.views.nguoi_dung_tab import NguoiDungTab
from modules.cau_hinh.views.phan_quyen_tab import PhanQuyenTab
from modules.cau_hinh.views.hoc_ky_tab import HocKyTab
from modules.cau_hinh.views.tiet_hoc_tab import TietHocTab


class CauHinhPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = SessionLocal()
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Style cho tab - bo góc rõ ràng
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 0px;
            }
            QTabBar {
                background: #F8F9FA;
                border-bottom: 2px solid #E9ECEF;
            }
            QTabBar::tab {
                background: transparent;
                color: #6C757D;
                padding: 10px 24px;
                margin: 0 2px;
                border: none;
                font-size: 13px;
                font-weight: 500;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:hover {
                background: #E9ECEF;
                color: #1D9E75;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1D9E75;
                border-bottom: 3px solid #1D9E75;
                font-weight: 600;
            }
        """)
        
        # Thêm các tab với icon
        self.nam_hoc_tab = NamHocTab(self.session)
        self.tab_widget.addTab(self.nam_hoc_tab, "📅  Năm học")
        
        self.hoc_ky_tab = HocKyTab(self.session)
        self.tab_widget.addTab(self.hoc_ky_tab, "📖  Học kỳ")
        
        self.to_chuyen_mon_tab = ToChuyenMonTab(self.session)
        self.tab_widget.addTab(self.to_chuyen_mon_tab, "🏢  Tổ chuyên môn")
        
        self.mon_hoc_tab = MonHocTab(self.session)
        self.tab_widget.addTab(self.mon_hoc_tab, "📚  Môn học")

        self.tiet_hoc_tab = TietHocTab(self.session)
        self.tab_widget.addTab(self.tiet_hoc_tab, "⏰  Tiết học")
        
        self.nguoi_dung_tab = NguoiDungTab(self.session)
        self.tab_widget.addTab(self.nguoi_dung_tab, "👥  Tài khoản")
        
        self.phan_quyen_tab = PhanQuyenTab(self.session)
        self.tab_widget.addTab(self.phan_quyen_tab, "🔐  Phân quyền")
        
        # Màu sắc cho từng tab (tùy chọn)
        self.tab_widget.tabBar().setTabTextColor(0, QColor(29, 158, 117))   # Năm học
        self.tab_widget.tabBar().setTabTextColor(1, QColor(33, 150, 243))   # Học kỳ
        self.tab_widget.tabBar().setTabTextColor(2, QColor(255, 152, 0))    # Tổ CM
        self.tab_widget.tabBar().setTabTextColor(3, QColor(156, 39, 176))   # Môn học
        self.tab_widget.tabBar().setTabTextColor(4, QColor(0, 188, 212))    # Tài khoản
        self.tab_widget.tabBar().setTabTextColor(5, QColor(244, 67, 54))    # Phân quyền
        
        layout.addWidget(self.tab_widget)
    
    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)