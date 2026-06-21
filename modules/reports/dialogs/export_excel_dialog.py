# modules/reports/dialogs/export_excel_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QLabel, QFrame
)
from PySide6.QtCore import Qt


class ExportExcelDialog(QDialog):
    """Dialog xuất báo cáo Excel"""

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self.svc = svc
        self._export_path = ""
        self.setWindowTitle("📤 Xuất báo cáo Excel")
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
        self.radio_gv.toggled.connect(self._on_loai_changed)
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
        for i in [9, 10, 11, 12, 1, 2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        row1.addWidget(self.cmb_thang)
        time_layout.addLayout(row1)

        self.chk_all_thang = QCheckBox("📋 Xuất tất cả tháng (mỗi tháng 1 sheet)")
        time_layout.addWidget(self.chk_all_thang)

        layout.addWidget(group_time)

        # ===== Nội dung xuất =====
        group_content = QGroupBox("📋 Nội dung xuất")
        content_layout = QVBoxLayout(group_content)
        self.chk_chi_tiet = QCheckBox("📊 Bảng điểm chi tiết")
        self.chk_bieu_do = QCheckBox("📈 Biểu đồ xếp hạng")
        self.chk_thong_ke = QCheckBox("📋 Thống kê tổng hợp")
        self.chk_chi_tiet.setChecked(True)
        self.chk_bieu_do.setChecked(True)
        self.chk_thong_ke.setChecked(True)
        content_layout.addWidget(self.chk_chi_tiet)
        content_layout.addWidget(self.chk_bieu_do)
        content_layout.addWidget(self.chk_thong_ke)
        layout.addWidget(group_content)

        # ===== Định dạng =====
        row_format = QHBoxLayout()
        row_format.addWidget(QLabel("💾 Định dạng:"))
        self.cmb_format = QComboBox()
        self.cmb_format.addItem("Excel (.xlsx)", "xlsx")
        self.cmb_format.addItem("Excel 97-2003 (.xls)", "xls")
        row_format.addWidget(self.cmb_format)
        row_format.addStretch()
        layout.addLayout(row_format)

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

        self.btn_export = QPushButton("📊 Xuất")
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
        """Load danh sách năm học"""
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

    def _on_loai_changed(self):
        """Khi đổi loại báo cáo"""
        is_hs = self.radio_hs.isChecked()
        # Có thể thay đổi giao diện tùy theo loại
        pass

    def _browse_folder(self):
        """Chọn thư mục lưu file"""
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu")
        if folder:
            self._export_path = folder
            self.lbl_path.setText(folder)

    def _export(self):
        """Thực hiện xuất Excel"""
        if not self._export_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thư mục lưu!")
            return

        nam_hoc_id = self.cmb_nam_hoc.currentData()
        if not nam_hoc_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn năm học!")
            return

        # Lấy thông tin
        ky = self.cmb_ky.currentData()
        thang = self.cmb_thang.currentData()
        chon_thang = self.chk_all_thang.isChecked()
        loai = "giao_vien" if self.radio_gv.isChecked() else "hoc_sinh"

        # Tạo tên file
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ten_loai = "giao_vien" if loai == "giao_vien" else "hoc_sinh"
        file_name = f"bao_cao_{ten_loai}_{now}.xlsx"
        full_path = f"{self._export_path}/{file_name}"

        # Gọi service xuất
        try:
            self.btn_export.setEnabled(False)
            self.btn_export.setText("Đang xuất...")

            from modules.reports.service.export_excel_service import ExportExcelService
            export_svc = ExportExcelService()
            
            result = export_svc.export_report(
                loai=loai,
                nam_hoc_id=nam_hoc_id,
                ky=ky,
                thang=thang,
                chon_thang=chon_thang,
                export_path=full_path,
                options={
                    'chi_tiet': self.chk_chi_tiet.isChecked(),
                    'bieu_do': self.chk_bieu_do.isChecked(),
                    'thong_ke': self.chk_thong_ke.isChecked(),
                }
            )

            self.btn_export.setEnabled(True)
            self.btn_export.setText("📊 Xuất")

            if result.ok:
                QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo thành công!\n{full_path}")
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", result.error)
        except Exception as e:
            self.btn_export.setEnabled(True)
            self.btn_export.setText("📊 Xuất")
            QMessageBox.critical(self, "Lỗi", str(e))

    def get_data(self):
        """Lấy dữ liệu từ dialog"""
        return {
            'loai': 'giao_vien' if self.radio_gv.isChecked() else 'hoc_sinh',
            'nam_hoc_id': self.cmb_nam_hoc.currentData(),
            'ky': self.cmb_ky.currentData(),
            'thang': self.cmb_thang.currentData(),
            'chon_thang': self.chk_all_thang.isChecked(),
            'export_path': self._export_path,
            'options': {
                'chi_tiet': self.chk_chi_tiet.isChecked(),
                'bieu_do': self.chk_bieu_do.isChecked(),
                'thong_ke': self.chk_thong_ke.isChecked(),
            }
        }