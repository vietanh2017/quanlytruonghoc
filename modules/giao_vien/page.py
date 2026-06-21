# modules\giao_vien\page.py
# TODO: implement
# modules/giao_vien/page.py
"""
GiaoVienPage: màn hình quản lý giáo viên.
Dùng GiaoVienService từ modules/giao_vien/service.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QHeaderView, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from modules.giao_vien.service import GiaoVienService
from modules.giao_vien.dialogs.giao_vien_dialog import GiaoVienDialog
from modules.giao_vien.dialogs.import_excel_dialog import ImportExcelDialog
from shared.enums import Role

ROLE_LABEL = {
    Role.ADMIN:          "Admin",
    Role.TO_TRUONG:      "Tổ trưởng",
    Role.TONG_PHU_TRACH: "T. phụ trách",
    Role.GIAO_VIEN:      "Giáo viên",
    Role.NHAN_VIEN:      "Nhân viên",
}

COL_STT, COL_MAGV, COL_HOTEN, COL_MONDAY, COL_TO, COL_ROLE, COL_SDT, COL_TT = range(8)
HEADERS = ["STT", "Mã GV", "Họ và tên", "Môn dạy", "Tổ CM",
           "Vai trò", "SĐT", "Trạng thái"]


class GiaoVienPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc = GiaoVienService()
        self._all_gv = []
        self._build_ui()
        self._load()

    def closeEvent(self, event):
        self.svc.close()
        super().closeEvent(event)

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        lbl = QLabel("Danh sách giáo viên")
        lbl.setStyleSheet("font-size: 17px; font-weight: 600;")
        hdr.addWidget(lbl)
        hdr.addStretch()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔍  Tìm theo tên, mã, môn...")
        self.inp_search.setFixedWidth(240)
        self.inp_search.textChanged.connect(self._filter)
        hdr.addWidget(self.inp_search)
        layout.addLayout(hdr)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)

        self.btn_them = QPushButton("＋  Thêm giáo viên")
        self.btn_them.setStyleSheet(
            "QPushButton{background:#1D9E75;color:white;border-radius:6px;"
            "padding:6px 14px;font-weight:600;}"
            "QPushButton:hover{background:#0F6E56;}")
        self.btn_them.clicked.connect(self._on_them)
        self.btn_them.setObjectName("btn_primary")

        self.btn_import = QPushButton("📥  Nhập Excel")
        self.btn_import.setStyleSheet("""
            QPushButton{
                background:#2563EB;
                color:white;
                border-radius:6px;
                padding:6px 14px;
                font-weight:600;
            }
            QPushButton:hover{
                background:#1D4ED8;
            }
        """)
        self.btn_import.clicked.connect(self._on_import_excel)
        self.btn_import.setObjectName("btn_success")

        self.btn_sua = QPushButton("✏  Sửa")
        self.btn_sua.setEnabled(False)
        self.btn_sua.clicked.connect(self._on_sua)
        self.btn_sua.setObjectName("btn_warning")

        self.btn_xoa = QPushButton("🗑  Xóa")
        self.btn_xoa.setEnabled(False)
        self.btn_xoa.setStyleSheet(
            "QPushButton{background:#C0392B;color:white;border-radius:6px;"
            "padding:6px 12px;font-weight:600;}"
            "QPushButton:hover{background:#922B21;}"
            "QPushButton:disabled{background:#E8B4B0;color:#fff;}")
        self.btn_xoa.clicked.connect(self._on_xoa)
        self.btn_xoa.setObjectName("btn_danger")

        self.btn_doi_tt = QPushButton("⏸  Vô hiệu / Kích hoạt")
        self.btn_doi_tt.setEnabled(False)
        self.btn_doi_tt.clicked.connect(self._on_doi_tt)
        self.btn_doi_tt.setObjectName("btn_default")

        self.btn_reset_mk = QPushButton("🔑  Đặt lại mật khẩu")
        self.btn_reset_mk.setEnabled(False)
        self.btn_reset_mk.clicked.connect(self._on_reset_mk)
        self.btn_reset_mk.setObjectName("btn_info")

        for btn in [
        self.btn_them,
        self.btn_import,
        self.btn_sua,
        self.btn_xoa,
        self.btn_doi_tt,
        self.btn_reset_mk
        ]:
            tb.addWidget(btn)
        tb.addStretch()
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color:gray;font-size:13px;")
        tb.addWidget(self.lbl_count)
        layout.addLayout(tb)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            COL_HOTEN, QHeaderView.Stretch)
        self.table.setColumnWidth(COL_STT,  44)
        self.table.setColumnWidth(COL_MAGV, 72)
        self.table.setColumnWidth(COL_MONDAY,   130)  # Môn dạy
        self.table.setColumnWidth(COL_ROLE, 100)
        self.table.setColumnWidth(COL_TT,   130)
        self.table.setColumnWidth(COL_TO,   140)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._on_sua)
        layout.addWidget(self.table)

    # ── Data ──────────────────────────────────────────────────
    def _load(self):
        r = self.svc.lay_ds()
        if r.ok:
            self._all_gv = r.data
            self._render(self._all_gv)
        else:
            QMessageBox.critical(self, "Lỗi", r.error)

    def _render(self, gv_list):
        self.table.setRowCount(0)
        for i, gv in enumerate(gv_list):
            self.table.insertRow(i)
            nd = gv.nguoi_dung

            def cell(txt, align=Qt.AlignLeft | Qt.AlignVCenter):
                it = QTableWidgetItem(str(txt))
                it.setTextAlignment(align)
                return it

            self.table.setItem(i, COL_STT,    cell(i+1, Qt.AlignCenter))
            self.table.setItem(i, COL_MAGV,   cell(gv.ma_giao_vien, Qt.AlignCenter))
            self.table.setItem(i, COL_HOTEN,  cell(nd.ho_ten))
            self.table.setItem(i, COL_MONDAY, cell(gv.mon_day or ""))
            self.table.setItem(i, COL_TO,     cell(
                gv.to_chuyen_mon.ten_to if gv.to_chuyen_mon else "—"))
            self.table.setItem(i, COL_ROLE,   cell(
                ROLE_LABEL.get(nd.role, str(nd.role)), Qt.AlignCenter))
            self.table.setItem(i, COL_SDT,    cell(gv.so_dien_thoai or ""))

            tt = QTableWidgetItem("✓ Hoạt động" if gv.active else "✗ Vô hiệu")
            tt.setTextAlignment(Qt.AlignCenter)
            tt.setForeground(QColor("#0F6E56") if gv.active else QColor("#993C1D"))
            self.table.setItem(i, COL_TT, tt)
            self.table.item(i, COL_STT).setData(Qt.UserRole, gv.id)

        self.lbl_count.setText(f"{len(gv_list)} giáo viên")

    def _filter(self, text: str):
        kw = text.lower().strip()
        filtered = [
            gv for gv in self._all_gv
            if kw in gv.nguoi_dung.ho_ten.lower()
            or kw in gv.ma_giao_vien.lower()
            or kw in (gv.mon_day or "").lower()
        ]
        self._render(filtered)

    # ── Selection ─────────────────────────────────────────────
    def _on_selection(self):
        has = bool(self.table.selectedItems())
        for btn in [self.btn_sua, self.btn_xoa,
                    self.btn_doi_tt, self.btn_reset_mk]:
            btn.setEnabled(has)

    def _sel_id(self) -> int | None:
        if not self.table.selectedItems():
            return None
        return self.table.item(self.table.currentRow(),
                               COL_STT).data(Qt.UserRole)

    def _sel_ten(self) -> str:
        row = self.table.currentRow()
        if row < 0:
            return ""
        it = self.table.item(row, COL_HOTEN)
        return it.text() if it else ""

    # ── Actions ───────────────────────────────────────────────
    def _on_them(self):
        ds_to = self.svc.lay_ds_to().data or []
        dlg = GiaoVienDialog(self, ds_to=ds_to)
        if dlg.exec() == GiaoVienDialog.Accepted:
            d = dlg.get_data()
            r = self.svc.them(**d)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)
    def _on_import_excel(self):
        """
        Nhập danh sách giáo viên từ Excel.
        """
        # Lấy danh sách tổ chuyên môn
        r = self.svc.lay_ds_to()

        dlg = ImportExcelDialog(
            self,
            ds_to=r.data if r.ok else []
        )

        if dlg.exec() != ImportExcelDialog.Accepted:
            return

        rows = dlg.get_valid_rows()

        if not rows:
            return

        ok_count = 0
        fail_count = 0
        errors = []

        for row in rows:
            try:
                result = self.svc.them_giao_vien(
                    ma_giao_vien=row["ma_gv"],
                    ho_ten=row["ho_ten"],
                    email=row["email"],
                    mon_day=row["mon_day"],
                    to_id=row["to_id"],
                    so_dien_thoai=row["so_dt"],
                )

                if result.ok:
                    ok_count += 1
                else:
                    fail_count += 1
                    errors.append(
                        f"{row['ma_gv']}: {result.error}"
                    )

            except Exception as e:
                fail_count += 1
                errors.append(
                    f"{row['ma_gv']}: {str(e)}"
                )

        self._load()

        # Thông báo kết quả
        msg = (
            f"Đã nhập thành công {ok_count} giáo viên."
        )

        if fail_count:
            msg += (
                f"\n\n{fail_count} dòng lỗi:"
                f"\n- " + "\n- ".join(errors[:10])
            )

        QMessageBox.information(
            self,
            "Kết quả nhập Excel",
            msg
        )

    def _on_sua(self):
        gv_id = self._sel_id()
        if not gv_id:
            return
        gv    = self.svc.repo.get_by_id(gv_id)
        ds_to = self.svc.lay_ds_to().data or []
        dlg   = GiaoVienDialog(self, gv=gv, ds_to=ds_to)
        if dlg.exec() == GiaoVienDialog.Accepted:
            d = dlg.get_data()
            r = self.svc.sua(gv_id=gv_id, **d)
            if r.ok:
                self._load()
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)

    def _on_xoa(self):
        gv_id = self._sel_id()
        ten   = self._sel_ten()
        if not gv_id:
            return
        reply = QMessageBox.warning(
            self, "Xác nhận xóa",
            f"Xóa giáo viên:\n\n  {ten}\n\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        r = self.svc.xoa(gv_id)
        if r.ok:
            self._load()
            QMessageBox.information(self, "Thành công", r.error)
        else:
            QMessageBox.warning(self, "Không thể xóa", r.error)

    def _on_doi_tt(self):
        gv_id = self._sel_id()
        if not gv_id:
            return
        r = self.svc.doi_trang_thai(gv_id)
        if r.ok:
            self._load()
        else:
            QMessageBox.warning(self, "Lỗi", r.error)

    def _on_reset_mk(self):
        gv_id = self._sel_id()
        if not gv_id:
            return
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Đặt lại mật khẩu về mặc định (eduschool@123)?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            r = self.svc.dat_lai_mat_khau(gv_id)
            if r.ok:
                QMessageBox.information(self, "Thành công", r.error)
            else:
                QMessageBox.warning(self, "Lỗi", r.error)