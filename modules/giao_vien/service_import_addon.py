# ═══════════════════════════════════════════════════════
# THÊM VÀO CUỐI modules/giao_vien/service.py
# ═══════════════════════════════════════════════════════

    def import_tu_excel(self, rows: list[dict]) -> ServiceResult:
        """
        Nhập hàng loạt GV từ dữ liệu Excel đã parse.
        rows: list[dict] từ ImportExcelDialog.get_valid_rows()
        Bỏ qua dòng email đã tồn tại, không dừng toàn bộ.
        """
        them_duoc = 0
        bo_qua    = 0
        loi_list  = []

        for row in rows:
            try:
                if self.repo.get_nguoi_dung_by_email(row["email"].lower()):
                    bo_qua += 1
                    continue
                nd = self.repo.create_nguoi_dung(
                    ho_ten=row["ho_ten"].strip(),
                    email=row["email"].strip().lower(),
                    mat_khau_hash=__import__(
                        'core.auth.password',
                        fromlist=['hash_password']
                    ).hash_password("eduschool@123"),
                    role=__import__(
                        'shared.enums', fromlist=['Role']
                    ).Role.GIAO_VIEN,
                )
                self.repo.create(
                    nguoi_dung_id=nd.id,
                    ma_gv=row["ma_gv"].strip().upper(),
                    mon_day=row.get("mon_day", "").strip(),
                    to_id=row.get("to_id"),
                    so_dien_thoai=row.get("so_dt", "").strip(),
                )
                them_duoc += 1
            except Exception as e:
                loi_list.append(f"{row.get('ho_ten','?')}: {e}")

        if them_duoc > 0:
            self._commit()
        else:
            self._rollback()

        msg_parts = [f"Đã thêm: {them_duoc} giáo viên"]
        if bo_qua:
            msg_parts.append(f"bỏ qua: {bo_qua} (email trùng)")
        if loi_list:
            msg_parts.append(f"lỗi: {len(loi_list)}")

        return ServiceResult(
            ok=them_duoc > 0 or bo_qua > 0,
            data={"them": them_duoc, "bo_qua": bo_qua, "loi": loi_list},
            error=" | ".join(msg_parts)
        )
