# ═══════════════════════════════════════════════════════════════
# THÊM VÀO modules/giao_vien/page.py
# ═══════════════════════════════════════════════════════════════
#
# 1. Trong toolbar (sau btn_reset_mk), thêm 2 nút:
#
#        self.btn_phan_cong = QPushButton("📋  Phân công")
#        self.btn_phan_cong.setEnabled(False)
#        self.btn_phan_cong.clicked.connect(self._on_phan_cong)
#
#        self.btn_import = QPushButton("📥  Nhập Excel")
#        self.btn_import.clicked.connect(self._on_import_excel)
#
#        for btn in [..., self.btn_phan_cong, self.btn_import]:
#            tb.addWidget(btn)
#
# 2. Trong _on_selection, thêm:
#        self.btn_phan_cong.setEnabled(has)
#
# 3. Thêm 2 hàm action sau _on_reset_mk:
# ═══════════════════════════════════════════════════════════════

    def _on_phan_cong(self):
        gv_id = self._sel_id()
        if not gv_id:
            return
        gv = self.svc.repo.get_by_id(gv_id)

        # Lấy dữ liệu cần thiết cho dialog
        ds_lop = self.svc.repo.get_all_lop() if hasattr(
            self.svc.repo, 'get_all_lop') else []
        ds_mon = self.svc.repo.get_all_mon_hoc() if hasattr(
            self.svc.repo, 'get_all_mon_hoc') else []
        ds_hk  = self.svc.repo.get_all_hoc_ky() if hasattr(
            self.svc.repo, 'get_all_hoc_ky') else []

        from modules.giao_vien.dialogs.phan_cong_dialog import PhanCongDialog
        dlg = PhanCongDialog(
            self, giao_vien=gv,
            ds_lop=ds_lop, ds_mon=ds_mon, ds_hoc_ky=ds_hk)

        if dlg.exec() == PhanCongDialog.Accepted:
            data = dlg.get_data()
            # Gọi service lưu phân công
            if hasattr(self.svc, 'luu_phan_cong'):
                r = self.svc.luu_phan_cong(gv_id, data)
                if r.ok:
                    QMessageBox.information(self, "Thành công",
                                            "Đã lưu phân công giảng dạy.")
                else:
                    QMessageBox.warning(self, "Lỗi", r.error)

    def _on_import_excel(self):
        ds_to = self.svc.lay_ds_to().data or []
        from modules.giao_vien.dialogs.import_excel_dialog import ImportExcelDialog
        dlg = ImportExcelDialog(self, ds_to=ds_to)

        if dlg.exec() == ImportExcelDialog.Accepted:
            valid_rows = dlg.get_valid_rows()
            if not valid_rows:
                return

            r = self.svc.import_tu_excel(valid_rows)
            if r.ok:
                self._load()
                data = r.data or {}
                msg  = r.error
                if data.get("loi"):
                    msg += "\n\nCác lỗi:\n" + "\n".join(data["loi"][:5])
                QMessageBox.information(self, "Kết quả nhập", msg)
            else:
                QMessageBox.warning(self, "Lỗi nhập", r.error)
