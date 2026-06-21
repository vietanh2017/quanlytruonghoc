from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QTextEdit, QMessageBox, QFrame, QAbstractSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from datetime import datetime

BTN_PRIMARY = """
    QPushButton {
        background:#1D9E75; color:white;
        border-radius:5px; padding:6px 14px;
        font-size:12px; font-weight:600; border:none;
    }
    QPushButton:hover { background:#0F6E56; }
    QPushButton:disabled { background:#A5D6C5; }
"""
BTN_STYLE = """
    QPushButton {
        background:#F5F5F5; border:1px solid #DDD;
        border-radius:5px; padding:6px 12px;
        font-size:12px; color:#333;
    }
    QPushButton:hover { background:#E8F5F0; border-color:#1D9E75; color:#1D9E75; }
"""


class ChamDiemTab(QWidget):
    def __init__(self, svc, nguoi_dung=None, parent=None):
        super().__init__(parent)
        self.svc = svc
        self.nguoi_dung = nguoi_dung
        self._user_to_id = None
        
        # Lấy to_id an toàn từ database
        if nguoi_dung:
            try:
                from core.db.models.giao_vien import GiaoVien
                from core.db.session import SessionLocal
                session = SessionLocal()
                gv = session.query(GiaoVien).filter(GiaoVien.nguoi_dung_id == nguoi_dung.id).first()
                if gv:
                    self._user_to_id = gv.to_id
                    print(f"DEBUG: Tổ trưởng có to_id={self._user_to_id}")
                session.close()
            except Exception as e:
                print(f"DEBUG: Lỗi lấy to_id: {e}")
        
        self._gv_id = None
        self._thang = 9
        self._nam_hoc_id = None
        self._hoc_ky_id = None
        self._tieu_chi_list = []
        self._diem_map = {}

        self._build_ui()
        self._load_filters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── Header + Filters ──────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(8)

        # Tổ chuyên môn
        lbl_to = QLabel("🏢 Tổ chuyên môn:")
        lbl_to.setStyleSheet("font-weight:500; font-size:12px;")
        self.cmb_to = QComboBox()
        self.cmb_to.setMinimumWidth(180)
        self.cmb_to.currentIndexChanged.connect(self._on_to_changed)
        hdr.addWidget(lbl_to)
        hdr.addWidget(self.cmb_to)

        # Giáo viên
        lbl_gv = QLabel("👨‍🏫 Giáo viên:")
        lbl_gv.setStyleSheet("font-weight:500; font-size:12px;")
        self.cmb_gv = QComboBox()
        self.cmb_gv.setMinimumWidth(200)
        self.cmb_gv.currentIndexChanged.connect(self._on_gv_changed)
        hdr.addWidget(lbl_gv)
        hdr.addWidget(self.cmb_gv)

        # Tháng - DÙNG COMBOBOX
        lbl_thang = QLabel("📅 Tháng:")
        lbl_thang.setStyleSheet("font-weight:500; font-size:12px;")
        self.cmb_thang = QComboBox()  # ← ĐỔI TÊN
        self.cmb_thang.setMinimumWidth(100)
        # Thêm tháng theo năm học
        for i in [9, 10, 11, 12, 1, 2, 3, 4, 5]:
            self.cmb_thang.addItem(f"Tháng {i}", i)
        self.cmb_thang.currentIndexChanged.connect(self._on_filter_changed)
        hdr.addWidget(lbl_thang)
        hdr.addWidget(self.cmb_thang)

        # Năm học
        lbl_nam = QLabel("📚 Năm học:")
        lbl_nam.setStyleSheet("font-weight:500; font-size:12px;")
        self.cmb_nam_hoc = QComboBox()
        self.cmb_nam_hoc.setMinimumWidth(120)
        self.cmb_nam_hoc.currentIndexChanged.connect(self._on_filter_changed)
        hdr.addWidget(lbl_nam)
        hdr.addWidget(self.cmb_nam_hoc)

        # Học kỳ
        lbl_hk = QLabel("📖 HK:")
        lbl_hk.setStyleSheet("font-weight:500; font-size:12px;")
        self.cmb_hoc_ky = QComboBox()
        self.cmb_hoc_ky.setMinimumWidth(100)
        self.cmb_hoc_ky.addItem("(Tất cả)", None)
        self.cmb_hoc_ky.currentIndexChanged.connect(self._on_filter_changed)
        hdr.addWidget(lbl_hk)
        hdr.addWidget(self.cmb_hoc_ky)

        # Nút tải lại
        btn_reload = QPushButton("🔄 Tải lại")
        btn_reload.setStyleSheet(BTN_STYLE)
        btn_reload.setFixedHeight(28)
        btn_reload.clicked.connect(self._load_diem)
        hdr.addWidget(btn_reload)
        
        hdr.addStretch()
        layout.addLayout(hdr)
        
        # ... phần còn lại giữ nguyên

        # ── Hiển thị điểm ─────────────────────────────────────
        diem_row = QHBoxLayout()
        diem_row.setSpacing(15)

        lbl_diem_label = QLabel("📊 ĐIỂM HIỆN TẠI:")
        lbl_diem_label.setStyleSheet("font-weight:600; font-size:12px; color:#333;")
        
        self.lbl_diem = QLabel("[100]")
        self.lbl_diem.setStyleSheet("""
            QLabel {
                background:#E8F5E9; color:#2E7D32;
                font-weight:700; font-size:16px;
                padding:6px 12px; border-radius:5px;
                min-width:60px; text-align:center;
            }
        """)

        lbl_xep = QLabel("→ Xếp loại:")
        lbl_xep.setStyleSheet("font-weight:600; font-size:12px; color:#333;")

        self.lbl_xep_loai = QLabel("[Chưa chấm]")
        self.lbl_xep_loai.setStyleSheet("""
            QLabel {
                background:#F5F5F5; color:#666;
                font-weight:600; font-size:12px;
                padding:6px 12px; border-radius:5px;
                min-width:150px;
            }
        """)

        diem_row.addWidget(lbl_diem_label)
        diem_row.addWidget(self.lbl_diem)
        diem_row.addWidget(lbl_xep)
        diem_row.addWidget(self.lbl_xep_loai)
        diem_row.addStretch()

        layout.addLayout(diem_row)

        # ── Bảng tiêu chí cộng ────────────────────────────────
        lbl_cong = QLabel("✅ TIÊU CHÍ CỘNG")
        lbl_cong.setStyleSheet("font-weight:600; font-size:13px; color:#2E7D32;")
        layout.addWidget(lbl_cong)

        self.tbl_cong = self._create_table()
        layout.addWidget(self.tbl_cong)

        # ── Bảng tiêu chí trừ ─────────────────────────────────
        lbl_tru = QLabel("❌ TIÊU CHÍ TRỪ")
        lbl_tru.setStyleSheet("font-weight:600; font-size:13px; color:#DC3545;")
        layout.addWidget(lbl_tru)

        self.tbl_tru = self._create_table()
        layout.addWidget(self.tbl_tru)

        # ── Ghi chú chung ─────────────────────────────────────
        lbl_ghi_chu = QLabel("📝 GHI CHÚ CHUNG")
        lbl_ghi_chu.setStyleSheet("font-weight:600; font-size:12px;")
        layout.addWidget(lbl_ghi_chu)

        self.txt_ghi_chu = QTextEdit()
        self.txt_ghi_chu.setPlaceholderText("Lưu ý đặc biệt về giáo viên này...")
        self.txt_ghi_chu.setFixedHeight(60)
        self.txt_ghi_chu.setStyleSheet("""
            QTextEdit {
                border:1px solid #DDD;
                border-radius:5px;
                padding:6px;
                font-size:11px;
            }
        """)
        layout.addWidget(self.txt_ghi_chu)

        # ── Nút hành động ─────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.btn_luu = QPushButton("💾 Lưu")
        self.btn_luu.setStyleSheet(BTN_PRIMARY)
        self.btn_luu.setFixedHeight(32)
        self.btn_luu.clicked.connect(self._save_all)

        self.btn_lam_moi = QPushButton("🔄 Làm mới")
        self.btn_lam_moi.setStyleSheet(BTN_STYLE)
        self.btn_lam_moi.setFixedHeight(32)
        self.btn_lam_moi.clicked.connect(self._load_diem)

        self.btn_copy_thang_truoc = QPushButton("📋 Copy tháng trước")
        self.btn_copy_thang_truoc.setStyleSheet(BTN_STYLE)
        self.btn_copy_thang_truoc.setFixedHeight(32)
        self.btn_copy_thang_truoc.clicked.connect(self._copy_thang_truoc)

        btn_row.addWidget(self.btn_luu)
        btn_row.addWidget(self.btn_lam_moi)
        btn_row.addWidget(self.btn_copy_thang_truoc)
        btn_row.addStretch()

        layout.addLayout(btn_row)

    def _create_table(self):
        """Tạo bảng tiêu chí"""
        tbl = QTableWidget()
        tbl.setColumnCount(4)
        tbl.setHorizontalHeaderLabels(["Tiêu chí", "Điểm tối đa", "Nhập điểm", "Ghi chú"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl.setColumnWidth(1, 90)
        tbl.setColumnWidth(2, 90)
        tbl.setColumnWidth(3, 120)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet("""
            QTableWidget {
                border:1px solid #DDD;
                gridline-color:#E8E8E8;
                font-size:11px;
            }
            QHeaderView::section {
                background:#F5F5F5; color:#333;
                font-weight:600; padding:5px;
                border:none;
            }
            QTableWidget::item {
                padding:4px;
            }
            QTableWidget::item:alternate { background:#F9F9F9; }
        """)
        return tbl

    # modules/giao_vien_thi_dua/views/tabs/cham_diem_tab.py
    def _on_to_changed(self):
        """Khi chọn tổ, load lại danh sách giáo viên"""
        to_id = self.cmb_to.currentData()
        print(f"DEBUG _on_to_changed: to_id = {to_id}")  # ← THÊM DÒNG NÀY
        self._load_gv_theo_to()
        self._on_gv_changed()

    def get_ds_thang_nam_hoc(self):
        """Lấy danh sách tháng trong năm học"""
        return [8, 9, 10, 11, 12, 1, 2, 3, 4, 5]
    
    def _load_to_chuyen_mon(self):
        try:
            from core.db.models.to_chuyen_mon import ToChuyenMon
            ds_to = self.svc.session.query(ToChuyenMon).filter(ToChuyenMon.active == True).all()
            self.cmb_to.clear()
            self.cmb_to.addItem("-- Tất cả --", None)  # ← Giá trị None
            for to in ds_to:
                self.cmb_to.addItem(to.ten_to, to.id)  # ← Giá trị là ID số
            print(f"DEBUG: Load tổ xong, có {len(ds_to)} tổ")
        except Exception as e:
            print(f"Lỗi load tổ: {e}")

    def _load_gv_theo_to(self):
        """Load giáo viên theo tổ được chọn"""
        to_id = self.cmb_to.currentData()
        print(f"DEBUG _load_gv_theo_to: to_id nhận được = {to_id}")
        
        # Nếu là tổ trưởng, chỉ hiển thị GV trong tổ của mình
        if self._user_to_id:
            to_id = self._user_to_id
            print(f"DEBUG: tổ trưởng, ép to_id = {to_id}")
            self.cmb_to.blockSignals(True)
            self.cmb_to.setCurrentIndex(self.cmb_to.findData(to_id))
            self.cmb_to.setEnabled(False)
            self.cmb_to.blockSignals(False)
        
        # Load danh sách giáo viên
        if to_id and to_id != "all":
            result = self.svc.lay_ds_giao_vien_theo_to(to_id)
            print(f"DEBUG: Lấy GV theo tổ {to_id}")
        else:
            result = self.svc.lay_ds_giao_vien()
            print(f"DEBUG: Lấy tất cả GV")
        
        if result.ok:
            self.cmb_gv.clear()
            for gv in result.data:
                ten = gv.nguoi_dung.ho_ten if gv.nguoi_dung else "?"
                self.cmb_gv.addItem(f"{gv.ma_giao_vien} - {ten}", gv.id)
            print(f"DEBUG: Đã load {len(result.data)} GV")
        else:
            print(f"DEBUG: Lỗi {result.error}")
    def _load_filters(self):
        """Load các dropdown"""
        # Load tổ chuyên môn
        self._load_to_chuyen_mon()
        
        # Load năm học
        r_nh = self.svc.lay_ds_nam_hoc()
        if r_nh.ok:
            for nh in r_nh.data:
                self.cmb_nam_hoc.addItem(nh.ten_nam_hoc, nh.id)
            if r_nh.data:
                self._nam_hoc_id = r_nh.data[0].id
                self.cmb_nam_hoc.setCurrentIndex(0)

        # Load học kỳ
        if self._nam_hoc_id:
            r_hk = self.svc.lay_ds_hoc_ky(self._nam_hoc_id)
            if r_hk.ok:
                self.cmb_hoc_ky.clear()
                self.cmb_hoc_ky.addItem("(Tất cả)", None)
                for hk in r_hk.data:
                    self.cmb_hoc_ky.addItem(hk.ten_hoc_ky, hk.id)
        
        # Load giáo viên theo tổ
        self._load_gv_theo_to()

    def _on_gv_changed(self):
        self._gv_id = self.cmb_gv.currentData()
        self._load_diem()

    def _on_filter_changed(self):
        """Khi thay đổi bộ lọc"""
        self._thang = self.cmb_thang.currentData()  # ← LẤY TỪ COMBOBOX
        self._nam_hoc_id = self.cmb_nam_hoc.currentData()
        self._hoc_ky_id = self.cmb_hoc_ky.currentData()
        self._load_diem()

    def _load_diem(self):
        """Load tiêu chí và điểm của GV"""
        if not self._gv_id or not self._nam_hoc_id:
            return

        # Load tiêu chí
        r_tc = self.svc.lay_ds_tieu_chi()
        if not r_tc.ok:
            QMessageBox.critical(self, "Lỗi", r_tc.error)
            return

        self._tieu_chi_list = r_tc.data or []

        # Load điểm
        r_diem = self.svc.lay_diem_thang(self._gv_id, self._thang, self._nam_hoc_id)
        self._diem_map = {}
        if r_diem.ok:
            for d in r_diem.data:
                self._diem_map[d.tieu_chi_id] = d

        # Hiển thị bảng
        self._render_tables()
        self._update_diem()

    def _render_tables(self):
        """Hiển thị bảng tiêu chí"""
        # Phân chia tiêu chí cộng/trừ
        tieu_chi_cong = [tc for tc in self._tieu_chi_list if tc.loai == "cong"]
        tieu_chi_tru = [tc for tc in self._tieu_chi_list if tc.loai == "tru"]

        self._render_table_data(self.tbl_cong, tieu_chi_cong)
        self._render_table_data(self.tbl_tru, tieu_chi_tru)

    def _render_table_data(self, tbl, tieu_chi_list):
        """Điền dữ liệu vào bảng"""
        tbl.setRowCount(0)

        for i, tc in enumerate(tieu_chi_list):
            tbl.insertRow(i)

            # Tiêu chí
            item_ten = QTableWidgetItem(tc.ten_tieu_chi)
            item_ten.setFlags(item_ten.flags() & ~Qt.ItemIsEditable)
            tbl.setItem(i, 0, item_ten)

            # Điểm tối đa
            item_max = QTableWidgetItem(str(tc.diem_toi_da))
            item_max.setTextAlignment(Qt.AlignCenter)
            item_max.setFlags(item_max.flags() & ~Qt.ItemIsEditable)
            tbl.setItem(i, 1, item_max)

            # Nhập điểm
            diem_val = ""
            if tc.id in self._diem_map:
                diem_val = str(self._diem_map[tc.id].diem)

            item_nhap = QTableWidgetItem(diem_val)
            item_nhap.setTextAlignment(Qt.AlignCenter)
            item_nhap.setData(Qt.UserRole, tc.id)  # Lưu tiêu chí ID
            tbl.setItem(i, 2, item_nhap)

            # Ghi chú
            ghi_chu_val = ""
            if tc.id in self._diem_map:
                ghi_chu_val = self._diem_map[tc.id].ghi_chu or ""

            item_ghi_chu = QTableWidgetItem(ghi_chu_val)
            tbl.setItem(i, 3, item_ghi_chu)

    def _update_diem(self):
        """Tính và cập nhật điểm hiện tại"""
        if not self._gv_id or not self._nam_hoc_id:
            return

        diem_total = 100.0

        # Tính từ bảng cộng
        for row in range(self.tbl_cong.rowCount()):
            item = self.tbl_cong.item(row, 2)
            text = item.text().strip()
            if text:
                try:
                    diem_total += float(text)
                except:
                    pass

        # Tính từ bảng trừ
        for row in range(self.tbl_tru.rowCount()):
            item = self.tbl_tru.item(row, 2)
            text = item.text().strip()
            if text:
                try:
                    diem_total -= float(text)
                except:
                    pass

        diem_total = max(0, diem_total)

        # Cập nhật label
        self.lbl_diem.setText(f"[{diem_total:.1f}]")
        xep_loai = self.svc.xep_loai(diem_total)
        self.lbl_xep_loai.setText(xep_loai)

        # Đổi màu theo xếp loại
        if diem_total >= 90:
            self.lbl_xep_loai.setStyleSheet("""
                QLabel {
                    background:#E8F5E9; color:#2E7D32;
                    font-weight:600; font-size:12px;
                    padding:6px 12px; border-radius:5px;
                }
            """)
        elif diem_total >= 80:
            self.lbl_xep_loai.setStyleSheet("""
                QLabel {
                    background:#E3F2FD; color:#1565C0;
                    font-weight:600; font-size:12px;
                    padding:6px 12px; border-radius:5px;
                }
            """)
        elif diem_total >= 70:
            self.lbl_xep_loai.setStyleSheet("""
                QLabel {
                    background:#FFF3E0; color:#E65100;
                    font-weight:600; font-size:12px;
                    padding:6px 12px; border-radius:5px;
                }
            """)
        else:
            self.lbl_xep_loai.setStyleSheet("""
                QLabel {
                    background:#FFEBEE; color:#C62828;
                    font-weight:600; font-size:12px;
                    padding:6px 12px; border-radius:5px;
                }
            """)

    def _save_all(self):
        """Lưu tất cả điểm"""
        if not self._gv_id or not self._nam_hoc_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn GV và năm học!")
            return

        so_luu = 0
        errors = []

        # Lưu từ bảng cộng
        for row in range(self.tbl_cong.rowCount()):
            tc_id = self.tbl_cong.item(row, 2).data(Qt.UserRole)
            diem_text = self.tbl_cong.item(row, 2).text().strip()
            ghi_chu = self.tbl_cong.item(row, 3).text().strip()

            if diem_text:
                try:
                    diem = float(diem_text)
                    r = self.svc.nhap_diem(
                        self._gv_id, tc_id, self._thang, self._nam_hoc_id,
                        diem, ghi_chu, None
                    )
                    if r.ok:
                        so_luu += 1
                    else:
                        errors.append(r.error)
                except ValueError:
                    errors.append(f"Hàng {row + 1}: Điểm không hợp lệ")

        # Lưu từ bảng trừ
        for row in range(self.tbl_tru.rowCount()):
            tc_id = self.tbl_tru.item(row, 2).data(Qt.UserRole)
            diem_text = self.tbl_tru.item(row, 2).text().strip()
            ghi_chu = self.tbl_tru.item(row, 3).text().strip()

            if diem_text:
                try:
                    diem = float(diem_text)
                    r = self.svc.nhap_diem(
                        self._gv_id, tc_id, self._thang, self._nam_hoc_id,
                        diem, ghi_chu, None
                    )
                    if r.ok:
                        so_luu += 1
                    else:
                        errors.append(r.error)
                except ValueError:
                    errors.append(f"Hàng {row + 1}: Điểm không hợp lệ")

        msg = f"✅ Đã lưu {so_luu} tiêu chí!"
        if errors:
            msg += f"\n⚠️ Lỗi: {'; '.join(errors[:3])}"

        QMessageBox.information(self, "Kết quả", msg)
        self._load_diem()

    def _copy_thang_truoc(self):
        """Copy điểm từ tháng trước"""
        thang_truoc = self._thang - 1 if self._thang > 1 else 12
        nam_truoc = self._nam_hoc_id if self._thang > 1 else self._nam_hoc_id

        r = self.svc.lay_diem_thang(self._gv_id, thang_truoc, nam_truoc)
        if not r.ok or not r.data:
            QMessageBox.warning(self, "Thông báo", "Tháng trước chưa có điểm!")
            return

        diem_map = {d.tieu_chi_id: d for d in r.data}

        # Copy vào bảng
        for row in range(self.tbl_cong.rowCount()):
            tc_id = self.tbl_cong.item(row, 2).data(Qt.UserRole)
            if tc_id in diem_map:
                self.tbl_cong.item(row, 2).setText(str(diem_map[tc_id].diem))

        for row in range(self.tbl_tru.rowCount()):
            tc_id = self.tbl_tru.item(row, 2).data(Qt.UserRole)
            if tc_id in diem_map:
                self.tbl_tru.item(row, 2).setText(str(diem_map[tc_id].diem))

        self._update_diem()
        QMessageBox.information(self, "Thành công", "✅ Đã copy điểm từ tháng trước!")
