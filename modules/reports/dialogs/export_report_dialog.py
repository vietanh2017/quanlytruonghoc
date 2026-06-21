# modules/reports/dialogs/export_report_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QLabel, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt
import os


class ExportReportDialog(QDialog):
    """Dialog xuất báo cáo Word/PDF"""

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self.svc = svc
        self._export_path = ""
        self.setWindowTitle("📄 Xuất báo cáo")
        self.setMinimumWidth(550)
        self.setModal(True)
        self._build_ui()
        self._load_filters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(24, 20, 24, 20)

        # ===== Loại báo cáo =====
        group_loai = QGroupBox("📁 Loại báo cáo")
        loai_layout = QHBoxLayout(group_loai)
        self.radio_gv = QRadioButton("👨‍🏫 Giáo viên")
        self.radio_hs = QRadioButton("👨‍🎓 Học sinh")
        self.radio_gv.setChecked(True)
        loai_layout.addWidget(self.radio_gv)
        loai_layout.addWidget(self.radio_hs)
        loai_layout.addStretch()
        layout.addWidget(group_loai)

        # ===== Thời gian =====
        group_time = QGroupBox("📅 Thời gian")
        time_layout = QVBoxLayout(group_time)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Năm học:"))
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(150)
        row1.addWidget(self.cmb_nam_hoc)

        row1.addWidget(QLabel("Kỳ:"))
        self.cmb_ky = QComboBox()
        self.cmb_ky.addItem("Học kỳ I", 1)
        self.cmb_ky.addItem("Học kỳ II", 2)
        self.cmb_ky.addItem("Cả năm", 3)
        row1.addWidget(self.cmb_ky)

        row1.addWidget(QLabel("Tháng:"))
        self.cmb_thang = QComboBox()
        self.cmb_thang.addItem("-- Tất cả --", None)
        for i in [9, 10, 11, 12]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        self.cmb_thang.addItem("Tháng 1a (HK1)", "1a")
        self.cmb_thang.addItem("Tháng 1b (HK2)", "1b")
        for i in [2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        row1.addWidget(self.cmb_thang)
        time_layout.addLayout(row1)

        self.chk_all_thang = QCheckBox("📋 Xuất tất cả tháng (mỗi tháng 1 trang)")
        time_layout.addWidget(self.chk_all_thang)

        layout.addWidget(group_time)

        # ===== Định dạng xuất =====
        group_format = QGroupBox("📄 Định dạng xuất")
        format_layout = QHBoxLayout(group_format)
        self.chk_word = QCheckBox("📝 Word (.docx)")
        self.chk_pdf = QCheckBox("📄 PDF (.pdf)")
        self.chk_word.setChecked(True)
        self.chk_pdf.setChecked(True)
        format_layout.addWidget(self.chk_word)
        format_layout.addWidget(self.chk_pdf)
        format_layout.addStretch()
        layout.addWidget(group_format)

        # ===== Nội dung =====
        group_content = QGroupBox("📋 Nội dung")
        content_layout = QVBoxLayout(group_content)
        self.chk_chi_tiet = QCheckBox("📊 Bảng điểm chi tiết")
        self.chk_bieu_do = QCheckBox("📈 Biểu đồ xếp hạng")
        self.chk_thong_ke = QCheckBox("📋 Thống kê tổng hợp")
        self.chk_ky_ten = QCheckBox("✍️ Chữ ký")
        self.chk_chi_tiet.setChecked(True)
        self.chk_thong_ke.setChecked(True)
        self.chk_ky_ten.setChecked(True)
        content_layout.addWidget(self.chk_chi_tiet)
        content_layout.addWidget(self.chk_bieu_do)
        content_layout.addWidget(self.chk_thong_ke)
        content_layout.addWidget(self.chk_ky_ten)
        layout.addWidget(group_content)

        # ===== Đường dẫn lưu =====
        row_path = QHBoxLayout()
        self.lbl_path = QLabel("Chưa chọn thư mục lưu")
        self.lbl_path.setStyleSheet("color: #666; padding: 4px; border: 1px solid #DDD; border-radius: 4px;")
        self.lbl_path.setMinimumWidth(300)
        row_path.addWidget(self.lbl_path)

        self.btn_browse = QPushButton("📂 Chọn thư mục")
        self.btn_browse.clicked.connect(self._browse_folder)
        row_path.addWidget(self.btn_browse)
        layout.addLayout(row_path)

        # ===== Buttons =====
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_export = QPushButton("📤 Xuất")
        self.btn_export.setStyleSheet("background: #1D9E75; color: white; font-weight: bold;")
        self.btn_export.setFixedHeight(40)
        self.btn_export.setFixedWidth(120)
        self.btn_export.clicked.connect(self._export)

        self.btn_cancel = QPushButton("❌ Hủy")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(self.btn_export)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

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
            self.lbl_path.setText(folder)

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

        self.btn_export.setEnabled(False)
        self.btn_export.setText("Đang xuất...")

        try:
            from modules.reports.service.export_report_service import ExportReportService
            export_svc = ExportReportService()

            # Xuất Word
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
                    QMessageBox.critical(self, "Lỗi", f"Xuất Word thất bại: {result.error}")

            # Xuất PDF
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
                    QMessageBox.critical(self, "Lỗi", f"Xuất PDF thất bại: {result.error}")

            self.btn_export.setEnabled(True)
            self.btn_export.setText("📤 Xuất")

            QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo thành công!\nThư mục: {self._export_path}")
            self.accept()

        except Exception as e:
            self.btn_export.setEnabled(True)
            self.btn_export.setText("📤 Xuất")
            QMessageBox.critical(self, "Lỗi", str(e))