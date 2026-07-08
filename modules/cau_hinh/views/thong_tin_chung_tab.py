# modules/cau_hinh/views/thong_tin_chung_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QComboBox, QDateEdit, QPushButton, QMessageBox,
    QGroupBox, QScrollArea, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPixmap
from modules.cau_hinh.service import CauHinhService
import requests
from io import BytesIO


class ThongTinChungTab(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.service = CauHinhService(session)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ═══ Tiêu đề ═══
        title = QLabel("🏫 THÔNG TIN CHUNG")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1D9E75;
            padding: 10px 0;
            border-bottom: 2px solid #E9ECEF;
        """)
        layout.addWidget(title)
        
        # ═══ Scroll Area ═══
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # ═══ Group 1: Thông tin trường ═══
        group1 = QGroupBox("Thông tin trường")
        group1.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form1 = QFormLayout()
        form1.setSpacing(12)
        form1.setLabelAlignment(Qt.AlignRight)
        
        self.txt_ten_truong = QLineEdit()
        self.txt_ten_truong.setPlaceholderText("Nhập tên trường")
        form1.addRow("Tên trường:", self.txt_ten_truong)
        
        self.txt_ten_truong_ta = QLineEdit()
        self.txt_ten_truong_ta.setPlaceholderText("Nhập tên trường tiếng Anh")
        form1.addRow("Tên trường (TA):", self.txt_ten_truong_ta)
        
        self.txt_dia_chi = QLineEdit()
        self.txt_dia_chi.setPlaceholderText("Nhập địa chỉ")
        form1.addRow("Địa chỉ:", self.txt_dia_chi)
        
        self.txt_dien_thoai = QLineEdit()
        self.txt_dien_thoai.setPlaceholderText("Nhập số điện thoại")
        form1.addRow("Điện thoại:", self.txt_dien_thoai)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Nhập email")
        form1.addRow("Email:", self.txt_email)
        
        self.txt_website = QLineEdit()
        self.txt_website.setPlaceholderText("Nhập website")
        form1.addRow("Website:", self.txt_website)
        
        self.txt_ma_so_truong = QLineEdit()
        self.txt_ma_so_truong.setPlaceholderText("Nhập mã số trường")
        form1.addRow("Mã số trường:", self.txt_ma_so_truong)
        
        group1.setLayout(form1)
        scroll_layout.addWidget(group1)
        
        # ═══ Group 2: Năm học - Học kỳ ═══
        group2 = QGroupBox("Năm học - Học kỳ")
        group2.setStyleSheet(group1.styleSheet())
        form2 = QFormLayout()
        form2.setSpacing(12)
        form2.setLabelAlignment(Qt.AlignRight)
        
        self.cbo_nam_hoc = QComboBox()
        self.cbo_nam_hoc.addItem("-- Chọn năm học --", None)
        form2.addRow("Năm học:", self.cbo_nam_hoc)
        
        self.cbo_hoc_ky = QComboBox()
        self.cbo_hoc_ky.addItem("-- Chọn học kỳ --", None)
        form2.addRow("Học kỳ:", self.cbo_hoc_ky)
        
        self.date_ngay_bat_dau = QDateEdit()
        self.date_ngay_bat_dau.setCalendarPopup(True)
        self.date_ngay_bat_dau.setDisplayFormat("dd/MM/yyyy")
        self.date_ngay_bat_dau.setDate(QDate.currentDate())
        form2.addRow("Ngày bắt đầu:", self.date_ngay_bat_dau)
        
        self.date_ngay_ket_thuc = QDateEdit()
        self.date_ngay_ket_thuc.setCalendarPopup(True)
        self.date_ngay_ket_thuc.setDisplayFormat("dd/MM/yyyy")
        self.date_ngay_ket_thuc.setDate(QDate.currentDate())
        form2.addRow("Ngày kết thúc:", self.date_ngay_ket_thuc)
        
        group2.setLayout(form2)
        scroll_layout.addWidget(group2)
        
        # ═══ Group 3: Lãnh đạo ═══
        group3 = QGroupBox("Lãnh đạo")
        group3.setStyleSheet(group1.styleSheet())
        form3 = QFormLayout()
        form3.setSpacing(12)
        form3.setLabelAlignment(Qt.AlignRight)
        
        self.txt_hieu_truong = QLineEdit()
        self.txt_hieu_truong.setPlaceholderText("Nhập tên hiệu trưởng")
        form3.addRow("Hiệu trưởng:", self.txt_hieu_truong)
        
        self.txt_hieu_pho = QLineEdit()
        self.txt_hieu_pho.setPlaceholderText("Nhập tên hiệu phó")
        form3.addRow("Hiệu phó:", self.txt_hieu_pho)
        
        self.txt_to_truong_cm = QLineEdit()
        self.txt_to_truong_cm.setPlaceholderText("Nhập tên tổ trưởng chuyên môn")
        form3.addRow("Tổ trưởng CM:", self.txt_to_truong_cm)
        
        self.txt_nguoi_lap = QLineEdit()
        self.txt_nguoi_lap.setPlaceholderText("Nhập tên người lập")
        form3.addRow("Người lập:", self.txt_nguoi_lap)
        
        group3.setLayout(form3)
        scroll_layout.addWidget(group3)
        
        # ═══ Button lưu ═══
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Lưu thông tin")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: #1D9E75;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #168B65;
            }
            QPushButton:pressed {
                background: #117A58;
            }
        """)
        self.btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(self.btn_save)
        
        scroll_layout.addLayout(btn_layout)
        scroll_layout.addStretch()
        
        # ═══ Hoàn thiện Scroll ═══
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def load_data(self):
        """Load dữ liệu thông tin trường"""
        try:
            # Load danh sách năm học, học kỳ
            self._load_nam_hoc()
            self._load_hoc_ky()
            
            # Load thông tin trường
            result = self.service.lay_thong_tin_truong()
            if result.ok and result.data:
                data = result.data
                self.txt_ten_truong.setText(data.get('ten_truong', ''))
                self.txt_ten_truong_ta.setText(data.get('ten_truong_tieng_anh', ''))
                self.txt_dia_chi.setText(data.get('dia_chi', ''))
                self.txt_dien_thoai.setText(data.get('dien_thoai', ''))
                self.txt_email.setText(data.get('email', ''))
                self.txt_website.setText(data.get('website', ''))
                self.txt_ma_so_truong.setText(data.get('ma_so_truong', ''))
                
                # Năm học
                if data.get('nam_hoc_id'):
                    index = self.cbo_nam_hoc.findData(data['nam_hoc_id'])
                    if index >= 0:
                        self.cbo_nam_hoc.setCurrentIndex(index)
                
                # Học kỳ
                if data.get('hoc_ky_id'):
                    index = self.cbo_hoc_ky.findData(data['hoc_ky_id'])
                    if index >= 0:
                        self.cbo_hoc_ky.setCurrentIndex(index)
                
                # Ngày tháng
                if data.get('ngay_bat_dau'):
                    self.date_ngay_bat_dau.setDate(QDate.fromString(data['ngay_bat_dau'], "yyyy-MM-dd"))
                if data.get('ngay_ket_thuc'):
                    self.date_ngay_ket_thuc.setDate(QDate.fromString(data['ngay_ket_thuc'], "yyyy-MM-dd"))
                
                self.txt_hieu_truong.setText(data.get('hieu_truong', ''))
                self.txt_hieu_pho.setText(data.get('hieu_pho', ''))
                self.txt_to_truong_cm.setText(data.get('to_truong_cm', ''))
                self.txt_nguoi_lap.setText(data.get('nguoi_lap', ''))
                
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")

    def _load_nam_hoc(self):
        """Load danh sách năm học"""
        try:
            from core.db.models.nam_hoc import NamHoc
            nam_hoc_list = self.session.query(NamHoc).filter(NamHoc.active == True).all()
            self.cbo_nam_hoc.clear()
            self.cbo_nam_hoc.addItem("-- Chọn năm học --", None)
            for nh in nam_hoc_list:
                self.cbo_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
        except Exception as e:
            print(f"Lỗi load năm học: {e}")

    def _load_hoc_ky(self):
        """Load danh sách học kỳ"""
        try:
            from core.db.models.hoc_ky import HocKy
            hoc_ky_list = self.session.query(HocKy).filter(HocKy.active == True).all()
            self.cbo_hoc_ky.clear()
            self.cbo_hoc_ky.addItem("-- Chọn học kỳ --", None)
            for hk in hoc_ky_list:
                self.cbo_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)
        except Exception as e:
            print(f"Lỗi load học kỳ: {e}")

    def save_data(self):
        """Lưu thông tin trường"""
        try:
            data = {
                'ten_truong': self.txt_ten_truong.text().strip(),
                'ten_truong_tieng_anh': self.txt_ten_truong_ta.text().strip(),
                'dia_chi': self.txt_dia_chi.text().strip(),
                'dien_thoai': self.txt_dien_thoai.text().strip(),
                'email': self.txt_email.text().strip(),
                'website': self.txt_website.text().strip(),
                'ma_so_truong': self.txt_ma_so_truong.text().strip(),
                'nam_hoc_id': self.cbo_nam_hoc.currentData(),
                'hoc_ky_id': self.cbo_hoc_ky.currentData(),
                'ngay_bat_dau': self.date_ngay_bat_dau.date().toString("yyyy-MM-dd"),
                'ngay_ket_thuc': self.date_ngay_ket_thuc.date().toString("yyyy-MM-dd"),
                'hieu_truong': self.txt_hieu_truong.text().strip(),
                'hieu_pho': self.txt_hieu_pho.text().strip(),
                'to_truong_cm': self.txt_to_truong_cm.text().strip(),
                'nguoi_lap': self.txt_nguoi_lap.text().strip(),
            }
            
            # Kiểm tra tên trường không được trống
            if not data['ten_truong']:
                QMessageBox.warning(self, "Lỗi", "Tên trường không được để trống!")
                return
            
            result = self.service.luu_thong_tin_truong(data)
            if result.ok:
                QMessageBox.information(self, "Thành công", "Đã lưu thông tin thành công!")
                self.load_data()  # Reload lại dữ liệu
            else:
                QMessageBox.warning(self, "Lỗi", f"Lưu thất bại: {result.error}")
                
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")