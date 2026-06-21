# D:\QUANLYTRUONGHOC\ui\login_page.py

import traceback
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QPainter, QLinearGradient, QBrush, QPen, QPixmap, QPainterPath
from core.db.session import SessionLocal
from core.auth.auth_service import AuthService


# ── Widget vẽ banner bên trái (sóng + trường) ──────────────────────────────
class BannerWidget(QWidget):
    """Vẽ panel bên trái: gradient xanh navy + hình minh họa trường học."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(480)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # --- Gradient nền xanh navy ---
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#0D3B6E"))   # xanh đậm trên
        grad.setColorAt(0.6, QColor("#1565C0"))   # xanh vừa
        grad.setColorAt(1.0, QColor("#1976D2"))   # xanh nhạt dưới
        p.fillRect(self.rect(), QBrush(grad))

        # --- Vòng tròn trang trí mờ ---
        p.setOpacity(0.08)
        p.setBrush(QColor("white"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(w - 180, -80, 320, 320)
        p.drawEllipse(-60, h - 220, 280, 280)
        p.setOpacity(0.05)
        p.drawEllipse(w // 2 - 150, h // 2 - 150, 300, 300)
        p.setOpacity(1.0)

        # --- Sóng trắng ở đáy ---
        p.setOpacity(0.15)
        p.setBrush(QColor("white"))
        wave = QPainterPath()
        wave.moveTo(0, h - 80)
        wave.cubicTo(w * 0.25, h - 140, w * 0.55, h - 20, w, h - 90)
        wave.lineTo(w, h)
        wave.lineTo(0, h)
        wave.closeSubpath()
        p.drawPath(wave)

        wave2 = QPainterPath()
        wave2.moveTo(0, h - 50)
        wave2.cubicTo(w * 0.3, h - 100, w * 0.65, h - 10, w, h - 60)
        wave2.lineTo(w, h)
        wave2.lineTo(0, h)
        wave2.closeSubpath()
        p.setOpacity(0.1)
        p.drawPath(wave2)
        p.setOpacity(1.0)

        # --- Hình minh họa: toà nhà trường ---
        self._draw_school(p, w, h)

    def _draw_school(self, p: QPainter, w: int, h: int):
        """Vẽ hình minh họa toà trường đơn giản."""
        cx = w // 2
        base_y = h - 110   # đáy toà nhà

        p.setOpacity(0.55)
        p.setPen(Qt.NoPen)

        # --- Toà nhà chính ---
        bw, bh = 200, 120
        bx = cx - bw // 2
        by = base_y - bh
        p.setBrush(QColor("#BBDEFB"))
        p.drawRect(bx, by, bw, bh)

        # Cổng
        p.setBrush(QColor("#1A237E"))
        p.drawRect(cx - 20, base_y - 50, 40, 50)

        # Cửa sổ (4 cái)
        p.setBrush(QColor("#E3F2FD"))
        for i in range(4):
            wx_ = bx + 18 + i * 44
            p.drawRect(wx_, by + 20, 28, 30)

        # Mái tam giác
        roof = QPainterPath()
        roof.moveTo(bx - 20, by)
        roof.lineTo(cx, by - 50)
        roof.lineTo(bx + bw + 20, by)
        roof.closeSubpath()
        p.setBrush(QColor("#1E3A5F"))
        p.drawPath(roof)

        # Cột tam giác nhỏ trên mái
        p.setBrush(QColor("#E3F2FD"))
        tri = QPainterPath()
        tri.moveTo(cx - 20, by)
        tri.lineTo(cx, by - 28)
        tri.lineTo(cx + 20, by)
        tri.closeSubpath()
        p.drawPath(tri)

        # Cột trụ (2 bên cổng)
        p.setBrush(QColor("#90CAF9"))
        p.drawRect(cx - 30, base_y - 50, 10, 50)
        p.drawRect(cx + 20, base_y - 50, 10, 50)

        # --- Tòa nhà phụ trái ---
        sw, sh = 100, 75
        sx = bx - sw - 15
        sy = base_y - sh
        p.setBrush(QColor("#90CAF9"))
        p.drawRect(sx, sy, sw, sh)
        # Mái phụ trái
        rs = QPainterPath()
        rs.moveTo(sx - 8, sy)
        rs.lineTo(sx + sw // 2, sy - 28)
        rs.lineTo(sx + sw + 8, sy)
        rs.closeSubpath()
        p.setBrush(QColor("#1E3A5F"))
        p.drawPath(rs)
        # Cửa sổ trái
        p.setBrush(QColor("#E3F2FD"))
        p.drawRect(sx + 12, sy + 16, 22, 22)
        p.drawRect(sx + sw - 34, sy + 16, 22, 22)

        # --- Tòa nhà phụ phải ---
        sx2 = bx + bw + 15
        p.setBrush(QColor("#90CAF9"))
        p.drawRect(sx2, sy, sw, sh)
        rs2 = QPainterPath()
        rs2.moveTo(sx2 - 8, sy)
        rs2.lineTo(sx2 + sw // 2, sy - 28)
        rs2.lineTo(sx2 + sw + 8, sy)
        rs2.closeSubpath()
        p.setBrush(QColor("#1E3A5F"))
        p.drawPath(rs2)
        p.setBrush(QColor("#E3F2FD"))
        p.drawRect(sx2 + 12, sy + 16, 22, 22)
        p.drawRect(sx2 + sw - 34, sy + 16, 22, 22)

        # --- Đường dẫn / sân trường ---
        p.setBrush(QColor("#E3F2FD"))
        path_pts = QPainterPath()
        path_pts.moveTo(cx - 20, base_y)
        path_pts.lineTo(cx - 30, base_y + 40)
        path_pts.lineTo(cx + 30, base_y + 40)
        path_pts.lineTo(cx + 20, base_y)
        path_pts.closeSubpath()
        p.drawPath(path_pts)

        # --- Cây (3 cây) ---
        for tx, ty_ in [(bx - 55, base_y - 20), (bx + bw + 55, base_y - 20), (cx - 110, base_y - 15)]:
            p.setBrush(QColor("#1B5E20"))
            p.drawEllipse(tx - 16, ty_ - 32, 32, 32)
            p.setBrush(QColor("#4CAF50"))
            p.drawEllipse(tx - 12, ty_ - 36, 24, 28)
            p.setBrush(QColor("#5D4037"))
            p.drawRect(tx - 4, ty_, 8, 20)

        # --- Cờ trên nóc ---
        p.setBrush(QColor("#E3F2FD"))
        p.drawRect(cx - 2, by - 88, 3, 38)
        p.setBrush(QColor("#F44336"))
        flag = QPainterPath()
        flag.moveTo(cx + 1, by - 88)
        flag.lineTo(cx + 22, by - 80)
        flag.lineTo(cx + 1, by - 72)
        flag.closeSubpath()
        p.drawPath(flag)

        # --- Chim bay (3 chim nhỏ) ---
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("white"), 1.5))
        for bx_, by_ in [(cx - 60, by - 110), (cx - 40, by - 130), (cx - 20, by - 118)]:
            bird = QPainterPath()
            bird.moveTo(bx_, by_)
            bird.cubicTo(bx_ + 6, by_ - 6, bx_ + 12, by_ - 6, bx_ + 18, by_)
            p.drawPath(bird)

        p.setOpacity(1.0)
        p.setPen(Qt.NoPen)


# ── Trang đăng nhập chính ───────────────────────────────────────────────────
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self._session = SessionLocal()
        self.auth_svc = AuthService(session=self._session)
        self.setWindowTitle("EduSchool Suite — Đăng nhập")
        self.setFixedSize(990, 610)
        self.setWindowFlag(Qt.Window)
        self.setStyleSheet("background: #E8EDF5;")
        self._build_ui()

        self.inp_email.setText("admin@eduschool.vn")
        self.inp_mk.setText("admin123")

    # ── Xây dựng UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Outer layout
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignCenter)

        # Card trắng trung tâm
        card = QFrame()
        card.setFixedSize(980, 590)
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background: white;
                border-radius: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 55))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── BANNER BÊN TRÁI ──────────────────────────────────────────────
        banner = BannerWidget()
        banner.setObjectName("banner")

        # Nội dung trên banner
        banner_inner = QVBoxLayout(banner)
        banner_inner.setContentsMargins(40, 44, 40, 36)
        banner_inner.setSpacing(0)

        # Logo + tên sở
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        # Quốc huy (emoji thay thế)
        logo_lbl = QLabel("🏛️")
        logo_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        logo_lbl.setFixedSize(56, 56)
        top_row.addWidget(logo_lbl)

        dept_col = QVBoxLayout()
        dept_col.setSpacing(2)
        dept1 = QLabel("       UBND XÃ KỲ XUÂN")
        dept1.setStyleSheet("color: rgba(255,255,255,0.80); font-size: 13px; font-weight: 600; background: transparent; letter-spacing: 0.5px;")
        dept2 = QLabel("TRƯỜNG THCS PHONG BẮC")
        dept2.setStyleSheet("color: white; font-size: 13px; font-weight: 800; background: transparent; letter-spacing: 0.5px;")
        # Đường gạch xanh nhạt
        line_lbl = QLabel()
        line_lbl.setFixedHeight(2)
        line_lbl.setStyleSheet("background: #64B5F6; border-radius: 1px; margin-top: 4px;")
        dept_col.addWidget(dept1)
        dept_col.addWidget(dept2)
        dept_col.addWidget(line_lbl)
        top_row.addLayout(dept_col)
        top_row.addStretch()
        banner_inner.addLayout(top_row)

        banner_inner.addStretch()

        # Tiêu đề lớn
        title1 = QLabel("HỆ THỐNG")
        title1.setStyleSheet("""
            color: white; font-size: 32px; font-weight: 900;
            background: transparent; letter-spacing: 1px;
        """)
        banner_inner.addWidget(title1)

        title2 = QLabel("QUẢN LÝ NHÀ TRƯỜNG")
        title2.setStyleSheet("""
            color: white; font-size: 32px; font-weight: 900;
            background: transparent; letter-spacing: 1px;
        """)
        banner_inner.addWidget(title2)

        # Gạch dưới title
        title_line = QLabel()
        title_line.setFixedHeight(3)
        title_line.setFixedWidth(80)
        title_line.setStyleSheet("background: #64B5F6; border-radius: 2px; margin-top: 8px; margin-bottom: 14px;")
        banner_inner.addWidget(title_line)

        slogan = QLabel("Kết nối – Quản lý – Hiệu quả – Minh bạch")
        slogan.setStyleSheet("color: rgba(255,255,255,0.80); font-size: 13px; background: transparent;")
        banner_inner.addWidget(slogan)

        banner_inner.addStretch(3)   # đẩy nội dung lên, nhường chỗ cho hình

        card_layout.addWidget(banner)

        # ── FORM BÊN PHẢI ────────────────────────────────────────────────
        right = QFrame()
        right.setObjectName("right")
        right.setAttribute(Qt.WA_StyledBackground, True)
        right.setStyleSheet("""
            QFrame#right {
                background: white;
                border-top-right-radius: 24px;
                border-bottom-right-radius: 24px;
            }
            QFrame#right QLabel {
                background: transparent;
            }
            QFrame#right QCheckBox {
                background: transparent;
            }
        """)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(52, 48, 52, 36)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignTop)

        # Tiêu đề form (giống ảnh: nền xanh đậm, chữ trắng)
        form_header = QFrame()
        form_header.setStyleSheet("""
            QFrame {
                background: #1565C0;
                border-radius: 12px;
                padding: 2px;
            }
        """)
        form_header.setFixedHeight(52)
        fh_layout = QHBoxLayout(form_header)
        fh_layout.setContentsMargins(16, 0, 16, 0)
        fh_layout.setSpacing(10)

        icon_h = QLabel("👤")
        icon_h.setStyleSheet("font-size: 20px; background: transparent;")
        fh_layout.addWidget(icon_h)

        lbl_title = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        lbl_title.setStyleSheet("color: white; font-size: 15px; font-weight: 800; background: transparent; letter-spacing: 1px;")
        fh_layout.addWidget(lbl_title)
        fh_layout.addStretch()

        right_layout.addWidget(form_header)
        right_layout.addSpacing(28)

        # Tài khoản
        lbl_email = QLabel("Tài khoản (Email)")
        lbl_email.setStyleSheet("font-size: 13px; font-weight: 700; color: #222; margin-bottom: 6px; background: transparent;")
        right_layout.addWidget(lbl_email)
        right_layout.addSpacing(6)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("admin@eduschool.vn")
        self.inp_email.setFixedHeight(46)
        self.inp_email.setStyleSheet(self._field_style())
        right_layout.addWidget(self.inp_email)
        right_layout.addSpacing(18)

        # Mật khẩu
        lbl_mk = QLabel("Mật khẩu")
        lbl_mk.setStyleSheet("font-size: 13px; font-weight: 700; color: #222; margin-bottom: 6px; background: transparent;")
        right_layout.addWidget(lbl_mk)
        right_layout.addSpacing(6)

        self.inp_mk = QLineEdit()
        self.inp_mk.setPlaceholderText("••••••••••")
        self.inp_mk.setEchoMode(QLineEdit.Password)
        self.inp_mk.setFixedHeight(46)
        self.inp_mk.setStyleSheet(self._field_style())
        self.inp_mk.returnPressed.connect(self._on_login)
        right_layout.addWidget(self.inp_mk)
        right_layout.addSpacing(12)

        # Ghi nhớ + Quên mật khẩu
        opts_row = QHBoxLayout()
        self.chk_remember = QCheckBox("Ghi nhớ đăng nhập")
        self.chk_remember.setStyleSheet("""
            QCheckBox { color: #666; font-size: 12px; spacing: 6px; background: transparent; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 2px solid #CCC; background: white; }
            QCheckBox::indicator:checked { background: #1565C0; border-color: #1565C0; }
        """)
        opts_row.addWidget(self.chk_remember)
        opts_row.addStretch()
        btn_forgot = QPushButton("Quên mật khẩu?")
        btn_forgot.setStyleSheet("""
            QPushButton { background: transparent; color: #1565C0; font-size: 12px; font-weight: 600; border: none; padding: 0; }
            QPushButton:hover { color: #0D47A1; text-decoration: underline; }
        """)
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.clicked.connect(lambda: QMessageBox.information(self, "Quên mật khẩu", "Vui lòng liên hệ quản trị viên!"))
        opts_row.addWidget(btn_forgot)
        right_layout.addLayout(opts_row)
        right_layout.addSpacing(6)

        # Lỗi
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #D32F2F; font-size: 11px; margin-top: 4px; background: transparent;")
        self.lbl_error.setVisible(False)
        self.lbl_error.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.lbl_error)
        right_layout.addSpacing(10)

        # Nút đăng nhập
        self.btn_login = QPushButton("Đăng nhập  →")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }
            QPushButton:hover { background: #0D47A1; }
            QPushButton:pressed { background: #0A2F6B; }
            QPushButton:disabled { background: #90CAF9; }
        """)
        self.btn_login.clicked.connect(self._on_login)
        right_layout.addWidget(self.btn_login)
        right_layout.addSpacing(16)

        # Divider "hoặc"
        div_row = QHBoxLayout()
        line_l = QFrame(); line_l.setFrameShape(QFrame.HLine); line_l.setStyleSheet("color: #DDD; background: transparent;")
        or_lbl = QLabel("hoặc"); or_lbl.setStyleSheet("color: #AAA; font-size: 12px; padding: 0 10px; background: transparent;")
        or_lbl.setAlignment(Qt.AlignCenter)
        line_r = QFrame(); line_r.setFrameShape(QFrame.HLine); line_r.setStyleSheet("color: #DDD; background: transparent;")
        div_row.addWidget(line_l)
        div_row.addWidget(or_lbl)
        div_row.addWidget(line_r)
        right_layout.addLayout(div_row)
        right_layout.addSpacing(12)

        # Nút SSO
        btn_sso = QPushButton("🛡  Đăng nhập với SSO (SSO)")
        btn_sso.setFixedHeight(46)
        btn_sso.setCursor(Qt.PointingHandCursor)
        btn_sso.setStyleSheet("""
            QPushButton {
                background: white;
                color: #555;
                border: 2px solid #DDD;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { border-color: #1565C0; color: #1565C0; background: #F0F5FF; }
        """)
        btn_sso.clicked.connect(lambda: QMessageBox.information(self, "SSO", "Tính năng đang phát triển!"))
        right_layout.addWidget(btn_sso)

        right_layout.addStretch()

        # Version + footer
        ver_lbl = QLabel("ⓘ  Phiên bản 1.0.0")
        ver_lbl.setStyleSheet("color: #BBB; font-size: 11px; background: transparent;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(ver_lbl)

        card_layout.addWidget(right)

    # ── Style chung cho input ───────────────────────────────────────────────
    @staticmethod
    def _field_style() -> str:
        return """
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                background: #F8F9FA;
                color: #222;
            }
            QLineEdit:focus {
                border-color: #1565C0;
                background: white;
            }
        """

    # ── Logic ───────────────────────────────────────────────────────────────
    def _set_error(self, msg: str):
        self.lbl_error.setText(msg)
        self.lbl_error.setVisible(bool(msg))

    def _on_login(self):
        email = self.inp_email.text().strip()
        mk = self.inp_mk.text()

        if not email:
            self._set_error("Vui lòng nhập email.")
            self.inp_email.setFocus()
            return
        if not mk:
            self._set_error("Vui lòng nhập mật khẩu.")
            self.inp_mk.setFocus()
            return

        self._set_error("")
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Đang đăng nhập...")

        try:
            result = self.auth_svc.login(email=email, mat_khau=mk)
        except Exception as e:
            self.btn_login.setEnabled(True)
            self.btn_login.setText("Đăng nhập  →")
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))
            return

        self.btn_login.setEnabled(True)
        self.btn_login.setText("Đăng nhập  →")

        if result.success:
            if self.chk_remember.isChecked():
                print("User:", result.user)        # ← thêm dòng này
                print("Role:", result.user.role)   # ← và dòng này
                pass  # TODO: lưu thông tin đăng nhập
            self._session.close()
            self._open_main(result.user, result.to_id)
            # QMessageBox.information(self, "Thành công", "Đăng nhập thành công! ✅")
        else:
            self._set_error(result.error)
            self.inp_mk.clear()
            self.inp_mk.setFocus()

    def _open_main(self, nguoi_dung, to_id=None):
        from ui.main_window import MainWindow
        self.main_win = MainWindow(nguoi_dung=nguoi_dung, to_id=to_id)
        self.main_win.showMaximized()
        self.close()


# ── Chạy thử độc lập ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = LoginPage()
    win.show()
    sys.exit(app.exec())