# modules/giao_vien_thi_dua/views/thi_dua_gv_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from modules.giao_vien_thi_dua.service.thi_dua_gv_service import ThiDuaGVService
from modules.giao_vien_thi_dua.views.tabs.quan_ly_tieu_chi_tab import QuanLyTieuChiTab
from modules.giao_vien_thi_dua.views.tabs.cham_diem_tab import ChamDiemTab
from modules.giao_vien_thi_dua.views.tabs.theo_thang_tab import TheoThangTab
from modules.giao_vien_thi_dua.views.tabs.hoc_ky_tab import HocKyTab
from modules.giao_vien_thi_dua.views.tabs.ca_nam_tab import CaNamTab


class ThiDuaGVWidget(QWidget):
    """Widget chính cho module Thi đua giáo viên"""
    
    def __init__(self, nguoi_dung=None, parent=None):
        super().__init__(parent)
        self.nguoi_dung = nguoi_dung
        self.svc = ThiDuaGVService()
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        # Tab 1: Quản lý tiêu chí
        self.quan_ly_tieu_chi_tab = QuanLyTieuChiTab(svc=self.svc)
        self.tab_widget.addTab(self.quan_ly_tieu_chi_tab, "⚙️ Quản lý tiêu chí")
        
        # Tab 2: Chấm điểm
        self.cham_diem_tab = ChamDiemTab(svc=self.svc, nguoi_dung=self.nguoi_dung)
        self.tab_widget.addTab(self.cham_diem_tab, "📝 Chấm điểm")
        
        # Tab 3: Theo tháng
        self.theo_thang_tab = TheoThangTab(svc=self.svc)
        self.tab_widget.addTab(self.theo_thang_tab, "📊 Theo tháng")
        
        # Tab 4: Học kỳ
        self.hoc_ky_tab = HocKyTab(svc=self.svc)
        self.tab_widget.addTab(self.hoc_ky_tab, "📚 Học kỳ")
        
        # Tab 5: Cả năm
        self.ca_nam_tab = CaNamTab(svc=self.svc)
        self.tab_widget.addTab(self.ca_nam_tab, "🎯 Cả năm")
        
        layout.addWidget(self.tab_widget)
    
    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)