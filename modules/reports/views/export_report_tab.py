# modules/reports/views/export_report_tab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QLabel, QFrame, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QTextEdit, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
import os

from modules.reports.service.export_report_service import ExportReportService


class ExportReportTab(QWidget):
    """Tab xuất báo cáo Word/PDF"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc = None
        self._export_path = ""
        self._preview_data = None
        self._build_ui()
        self._load_filters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ===== Hàng 1: Bộ lọc =====
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.group_loai = QButtonGroup()
        self.radio_gv = QRadioButton("👨‍🏫 Giáo viên")
        self.radio_hs = QRadioButton("👨‍🎓 Học sinh")
        self.radio_gv.setChecked(True)
        self.group_loai.addButton(self.radio_gv)
        self.group_loai.addButton(self.radio_hs)
        filter_layout.addWidget(self.radio_gv)
        filter_layout.addWidget(self.radio_hs)

        filter_layout.addWidget(QLabel("|"))

        filter_layout.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(150)
        filter_layout.addWidget(self.cmb_nam_hoc)

        filter_layout.addWidget(QLabel("Kỳ:"))
        self.cmb_ky = QComboBox()
        self.cmb_ky.addItem("Học kỳ I", 1)
        self.cmb_ky.addItem("Học kỳ II", 2)
        self.cmb_ky.addItem("Cả năm", 3)
        filter_layout.addWidget(self.cmb_ky)

        filter_layout.addWidget(QLabel("Tháng:"))
        self.cmb_thang = QComboBox()
        self.cmb_thang.setMinimumWidth(100)
        self.cmb_thang.addItem("-- Tất cả --", None)
        for i in [9, 10, 11, 12]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        self.cmb_thang.addItem("Tháng 1a (HK1)", "1a")
        self.cmb_thang.addItem("Tháng 1b (HK2)", "1b")
        for i in [2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        filter_layout.addWidget(self.cmb_thang)

        self.btn_preview = QPushButton("👁️ Xem trước")
        self.btn_preview.setFixedHeight(30)
        self.btn_preview.setStyleSheet("background: #2196F3; color: white; font-weight: bold;")
        self.btn_preview.clicked.connect(self._preview)
        filter_layout.addWidget(self.btn_preview)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # ===== Hàng 2: Nội dung và định dạng =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        group_content = QGroupBox("📋 Nội dung xuất")
        group_content.setStyleSheet("""
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
        content_layout_v = QVBoxLayout(group_content)
        
        self.chk_thong_ke = QCheckBox("📊 Thống kê tổng hợp")
        self.chk_chi_tiet = QCheckBox("📋 Bảng điểm chi tiết")
        self.chk_bieu_do = QCheckBox("📈 Biểu đồ xếp hạng")
        self.chk_ky_ten = QCheckBox("✍️ Chữ ký")
        
        self.chk_thong_ke.setChecked(True)
        self.chk_chi_tiet.setChecked(True)
        self.chk_bieu_do.setChecked(True)
        self.chk_ky_ten.setChecked(True)
        
        content_layout_v.addWidget(self.chk_thong_ke)
        content_layout_v.addWidget(self.chk_chi_tiet)
        content_layout_v.addWidget(self.chk_bieu_do)
        content_layout_v.addWidget(self.chk_ky_ten)
        content_layout_v.addStretch()

        group_format = QGroupBox("📄 Định dạng")
        group_format.setStyleSheet("""
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
        format_layout_v = QVBoxLayout(group_format)
        
        self.chk_word = QCheckBox("📝 Word (.docx)")
        self.chk_pdf = QCheckBox("📄 PDF (.pdf)")
        self.chk_word.setChecked(True)
        self.chk_pdf.setChecked(True)
        
        format_layout_v.addWidget(self.chk_word)
        format_layout_v.addWidget(self.chk_pdf)
        format_layout_v.addStretch()

        content_layout.addWidget(group_content)
        content_layout.addWidget(group_format)
        layout.addLayout(content_layout)

        # ===== Hàng 3: Preview =====
        group_preview = QGroupBox("👁️ Xem trước báo cáo")
        group_preview.setStyleSheet("""
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
        preview_layout = QVBoxLayout(group_preview)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("📄 Chọn thông tin và nhấn 'Xem trước' để hiển thị báo cáo")
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                font-family: 'Times New Roman';
                font-size: 12px;
                padding: 10px;
                background: #FAFAFA;
            }
        """)
        self.preview_text.setMinimumHeight(300)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(group_preview)

        # ===== Hàng 4: Nút hành động =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.lbl_path = QLabel("📁 Chưa chọn thư mục lưu")
        self.lbl_path.setStyleSheet("color: #666; padding: 6px; border: 1px solid #DDD; border-radius: 4px;")
        self.lbl_path.setMinimumWidth(250)
        btn_layout.addWidget(self.lbl_path)

        self.btn_browse = QPushButton("📂 Chọn thư mục")
        self.btn_browse.setFixedHeight(32)
        self.btn_browse.clicked.connect(self._browse_folder)
        btn_layout.addWidget(self.btn_browse)

        btn_layout.addStretch()

        self.btn_export = QPushButton("📤 Xuất báo cáo")
        self.btn_export.setStyleSheet("background: #1D9E75; color: white; font-weight: bold;")
        self.btn_export.setFixedHeight(36)
        self.btn_export.setFixedWidth(150)
        self.btn_export.clicked.connect(self._export)
        btn_layout.addWidget(self.btn_export)

        layout.addLayout(btn_layout)

        self.status_label = QLabel("✅ Sẵn sàng")
        self.status_label.setStyleSheet("color:#666; font-size:11px; padding:4px;")
        layout.addWidget(self.status_label)

    def _load_filters(self):
        try:
            from core.db.models.nam_hoc import NamHoc
            from core.db.session import SessionLocal
            session = SessionLocal()
            nam_hocs = session.query(NamHoc).order_by(NamHoc.ten_nam_hoc.desc()).all()
            for nh in nam_hocs:
                self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
            session.close()
            if self.cmb_nam_hoc.count() > 0:
                self.cmb_nam_hoc.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải năm học: {e}")

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu")
        if folder:
            self._export_path = folder
            self.lbl_path.setText(f"📁 {folder}")

    def _get_preview_data(self):
        """Lấy dữ liệu cho preview"""
        nam_hoc_id = self.cmb_nam_hoc.currentData()
        ky = self.cmb_ky.currentData()
        thang = self.cmb_thang.currentData()
        loai = "giao_vien" if self.radio_gv.isChecked() else "hoc_sinh"

        if not nam_hoc_id:
            return None

        if not self.svc:
            from modules.reports.service.bao_cao_service import BaoCaoService
            self.svc = BaoCaoService()

        data = {}
        
        # Thống kê
        if self.chk_thong_ke.isChecked():
            result = self.svc.thong_ke_tong_quan(nam_hoc_id)
            if result.ok:
                data['thong_ke'] = result.data

        # Bảng xếp hạng - LẤY TOÀN BỘ
        if self.chk_chi_tiet.isChecked():
            if loai == "giao_vien":
                result = self.svc.xep_hang_giao_vien(nam_hoc_id, ky, thang)
            else:
                result = self.svc.xep_hang_lop(nam_hoc_id, ky, thang)
            if result.ok:
                data['bang_xep_hang'] = result.data  # Lấy toàn bộ, không giới hạn 15

        return data

    def _preview(self):
        """Xem trước báo cáo"""
        if not self.cmb_nam_hoc.currentData():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return

        self.preview_text.clear()
        self.status_label.setText("⏳ Đang tạo xem trước...")
        
        data = self._get_preview_data()
        if not data:
            self.preview_text.setPlainText("Không có dữ liệu để hiển thị!")
            self.status_label.setText("❌ Không có dữ liệu")
            return

        # Tạo preview
        html = self._build_preview_html(data)
        self.preview_text.setHtml(html)
        self.status_label.setText("✅ Đã tạo xem trước")

    def _build_preview_html(self, data):
        """Tạo HTML preview"""
        loai = "GIÁO VIÊN" if self.radio_gv.isChecked() else "HỌC SINH"
        ky_text = "CẢ NĂM" if self.cmb_ky.currentData() == 3 else ("HỌC KỲ I" if self.cmb_ky.currentData() == 1 else "HỌC KỲ II")
        nam_hoc = self.cmb_nam_hoc.currentText()

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Times New Roman', serif; padding: 20px; }}
                h1 {{ text-align: center; font-size: 18pt; }}
                h2 {{ font-size: 14pt; margin-top: 15px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th {{ background-color: #1D9E75; color: white; padding: 6px; font-size: 11pt; }}
                td {{ padding: 4px 6px; border: 1px solid #ccc; font-size: 10pt; text-align: center; }}
                .header {{ text-align: center; }}
                .stats {{ margin: 10px 0; font-size: 11pt; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>TRƯỜNG THCS PHONG BẮC</h1>
                <h2>BÁO CÁO TỔNG KẾT THI ĐUA {loai}</h2>
                <p><b>Năm học {nam_hoc} - {ky_text}</b></p>
                <hr>
            </div>
        """

        # Thống kê
        if 'bang_xep_hang' in data:
            bang = data['bang_xep_hang']
            if bang:
                html += f"""
                <h2>II. BẢNG XẾP HẠNG</h2>
                <table>
                    <tr>
                        <th>STT</th>
                        <th>{'Mã GV' if self.radio_gv.isChecked() else 'Mã lớp'}</th>
                        <th>{'Họ tên' if self.radio_gv.isChecked() else 'Tên lớp'}</th>
                        <th>Điểm</th>
                        <th>{'Xếp loại' if self.radio_gv.isChecked() else 'Xếp thứ'}</th>
                    </tr>
                """
                # HIỂN THỊ TẤT CẢ (không giới hạn)
                for item in bang:
                    ten = item.get('ten', '')
                    if self.radio_gv.isChecked() and len(ten) > 30:
                        ten = ten[:27] + "..."
                    html += f"""
                    <tr>
                        <td>{item.get('thu_hang', 0)}</td>
                        <td>{item.get('ma', '')}</td>
                        <td style="text-align:left; padding-left:10px;">{ten}</td>
                        <td>{item.get('diem', 0):.3f}</td>
                        <td>{item.get('xep_loai', '') if self.radio_gv.isChecked() else item.get('thu_hang', 0)}</td>
                    </tr>
                    """
                html += "</table>"
                
                # Thêm dòng tổng số
                html += f"<p style='margin-top:5px; font-size:10pt; color:#666;'>Tổng số: {len(bang)} {('giáo viên' if self.radio_gv.isChecked() else 'lớp')}</p>"

        # Chữ ký
        if self.chk_ky_ten.isChecked():
            from datetime import datetime
            html += f"""
            <div style="margin-top: 40px; text-align: right;">
                <p>Ngày {datetime.now().day} tháng {datetime.now().month} năm {datetime.now().year}</p>
                <p style="margin-top: 40px;"><b>HIỆU TRƯỞNG</b></p>
            </div>
            """

        html += """
        </body>
        </html>
        """
        return html

    def _export(self):
        if not self._export_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thư mục lưu!")
            return

        if not self.chk_word.isChecked() and not self.chk_pdf.isChecked():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 1 định dạng!")
            return

        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return

        loai = "giao_vien" if self.radio_gv.isChecked() else "hoc_sinh"
        ky = self.cmb_ky.currentData()
        thang = self.cmb_thang.currentData()

        if not self.svc:
            from modules.reports.service.bao_cao_service import BaoCaoService
            self.svc = BaoCaoService()

        self.btn_export.setEnabled(False)
        self.btn_export.setText("Đang xuất...")
        self.status_label.setText("⏳ Đang xuất báo cáo...")

        try:
            from modules.reports.service.export_report_service import ExportReportService
            export_svc = ExportReportService()

            success = True
            errors = []

            if self.chk_word.isChecked():
                word_path = os.path.join(self._export_path, f"bao_cao_{loai}.docx")
                result = export_svc.export_word(
                    loai=loai,
                    nam_hoc_id=nam_hoc_id,
                    ky=ky,
                    thang=thang,
                    export_path=word_path,
                    options={
                        'chi_tiet': self.chk_chi_tiet.isChecked(),
                        'bieu_do': self.chk_bieu_do.isChecked(),
                        'thong_ke': self.chk_thong_ke.isChecked(),
                        'ky_ten': self.chk_ky_ten.isChecked(),
                    }
                )
                if not result.ok:
                    success = False
                    errors.append(f"Word: {result.error}")

            if self.chk_pdf.isChecked():
                pdf_path = os.path.join(self._export_path, f"bao_cao_{loai}.pdf")
                result = export_svc.export_pdf(
                    loai=loai,
                    nam_hoc_id=nam_hoc_id,
                    ky=ky,
                    thang=thang,
                    export_path=pdf_path,
                    options={
                        'chi_tiet': self.chk_chi_tiet.isChecked(),
                        'bieu_do': self.chk_bieu_do.isChecked(),
                        'thong_ke': self.chk_thong_ke.isChecked(),
                        'ky_ten': self.chk_ky_ten.isChecked(),
                    }
                )
                if not result.ok:
                    success = False
                    errors.append(f"PDF: {result.error}")

            self.btn_export.setEnabled(True)
            self.btn_export.setText("📤 Xuất báo cáo")

            if success:
                self.status_label.setText(f"✅ Xuất thành công! Thư mục: {self._export_path}")
                QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo thành công!\nThư mục: {self._export_path}")
            else:
                self.status_label.setText("❌ Xuất thất bại!")
                QMessageBox.critical(self, "Lỗi", "\n".join(errors))

        except Exception as e:
            self.btn_export.setEnabled(True)
            self.btn_export.setText("📤 Xuất báo cáo")
            self.status_label.setText("❌ Xuất thất bại!")
            QMessageBox.critical(self, "Lỗi", str(e))

    def closeEvent(self, event):
        if self.svc:
            self.svc.close()
        super().closeEvent(event)