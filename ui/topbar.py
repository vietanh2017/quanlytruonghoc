from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
from PySide6.QtCore import Qt, Signal
from core.db.session import SessionLocal
from core.db.models.nam_hoc import NamHoc
from core.db.models.hoc_ky import HocKy


class Topbar(QWidget):
    logout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = SessionLocal()
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # Style cho combo box
        combo_style = """
            QComboBox {
                border: 1px solid #D8D8D8;
                border-radius: 5px;
                padding: 5px 8px;
                background: white;
                font-size: 12px;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #1D9E75;
            }
            QComboBox:focus {
                border-color: #1D9E75;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
        """
        
        # Style cho label
        label_style = "color: #555; font-size: 12px; font-weight: 500;"
        
        # Năm học
        lbl_nam_hoc = QLabel("📅 Năm học:")
        lbl_nam_hoc.setStyleSheet(label_style)
        layout.addWidget(lbl_nam_hoc)
        
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setStyleSheet(combo_style)
        self.cmb_nam_hoc.setFixedWidth(130)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_nam_hoc_changed)
        layout.addWidget(self.cmb_nam_hoc)
        
        # Học kỳ
        lbl_hoc_ky = QLabel("📖 Học kỳ:")
        lbl_hoc_ky.setStyleSheet(label_style)
        layout.addWidget(lbl_hoc_ky)
        
        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.setStyleSheet(combo_style)
        self.cmb_hoc_ky.setFixedWidth(110)
        layout.addWidget(self.cmb_hoc_ky)
        
        layout.addStretch()
        
        # Style cho nút
        button_style = """
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #F0F0F0;
            }
        """
        
        # Các nút chức năng
        #self.btn_backup = QPushButton("💾 Sao lưu")
        #self.btn_backup.setStyleSheet(button_style)
        
        #self.btn_import = QPushButton("📥 Nhập Excel")
        #self.btn_import.setStyleSheet(button_style)
        
        #self.btn_export = QPushButton("📊 Xuất báo cáo")
        #self.btn_export.setStyleSheet(button_style)
        
        #layout.addWidget(self.btn_backup)
        #layout.addWidget(self.btn_import)
        #layout.addWidget(self.btn_export)
        
        # Thông tin người dùng
        self.lbl_user = QLabel()
        self.lbl_user.setStyleSheet("""
            QLabel {
                color: #1D9E75;
                font-weight: bold;
                font-size: 12px;
                background: #E8F5E9;
                border-radius: 15px;
                padding: 5px 12px;
            }
        """)
        layout.addWidget(self.lbl_user)
        
        # Nút đăng xuất
        self.btn_logout = QPushButton("🚪 Đăng xuất")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                background: #FFEBEE;
                color: #DC3545;
            }
            QPushButton:hover {
                background: #FFCDD2;
            }
        """)
        self.btn_logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.btn_logout)
    
    def _load_data(self):
        # Load năm học
        nam_hoc_list = self.session.query(NamHoc).filter(NamHoc.active == True).all()
        for nh in nam_hoc_list:
            self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
        
        if self.cmb_nam_hoc.count() > 0:
            self.cmb_nam_hoc.setCurrentIndex(0)
    
    def _on_nam_hoc_changed(self):
        self.cmb_hoc_ky.clear()
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        
        if nam_hoc_id:
            hoc_ky_list = self.session.query(HocKy).filter(
                HocKy.nam_hoc_id == nam_hoc_id,
                HocKy.active == True
            ).all()
            for hk in hoc_ky_list:
                self.cmb_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)
    
    def set_user_name(self, ho_ten):
        # Lấy chữ cái đầu tiên để làm avatar
        avatar = ho_ten[0] if ho_ten else "U"
        self.lbl_user.setText(f"👤 {ho_ten}")
    
    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)