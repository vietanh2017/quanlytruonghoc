# modules\timetable\service.py
# TODO: implement
from modules.timetable.repository import TimetableRepository
from shared.dto.result import ServiceResult

class TimetableService:
    def __init__(self, session):
        self.session = session
        self.repo = TimetableRepository(session)
    
    def lay_tkb_theo_lop(self, lop_hoc_id, nam_hoc_id, hoc_ky_id):
        try:
            ds = self.repo.get_by_lop(lop_hoc_id, nam_hoc_id, hoc_ky_id)
            return ServiceResult(ok=True, data=ds)
        except Exception as e:
            return ServiceResult(ok=False, error=str(e))
    
    def luu_tkb(self, lop_hoc_id, nam_hoc_id, hoc_ky_id, tkb_data):
        try:
            # Xóa dữ liệu cũ
            self.repo.delete_by_lop(lop_hoc_id, nam_hoc_id, hoc_ky_id)
            
            # Thêm dữ liệu mới
            for item in tkb_data:
                self.repo.create(
                    nam_hoc_id=nam_hoc_id,
                    hoc_ky_id=hoc_ky_id,
                    lop_hoc_id=lop_hoc_id,
                    mon_hoc_id=item['mon_hoc_id'],
                    giao_vien_id=item['giao_vien_id'],
                    thu=item['thu'],
                    tiet_bat_dau=item['tiet_bat_dau'],
                    so_tiet=item.get('so_tiet', 1),
                    phong_hoc=item.get('phong_hoc', '')
                )
            
            self.session.commit()
            return ServiceResult(ok=True, error="Lưu thời khóa biểu thành công")
        except Exception as e:
            self.session.rollback()
            return ServiceResult(ok=False, error=str(e))
    
    def lay_ds_lop(self):
        from core.db.models.lop_hoc import LopHoc
        return self.session.query(LopHoc).filter(LopHoc.active == True).all()
    
    def lay_ds_mon(self):
        from core.db.models.mon_hoc import MonHoc
        return self.session.query(MonHoc).filter(MonHoc.active == True).all()
    
    def lay_ds_giao_vien(self):
        from core.db.models.giao_vien import GiaoVien
        return self.session.query(GiaoVien).filter(GiaoVien.active == True).all()
    
    def lay_tiet_hoc_list(self):
        """Lấy danh sách tiết học từ cấu hình"""
        try:
            from core.db.models.tiet_hoc import TietHoc
            return self.session.query(TietHoc).filter(TietHoc.active == 1).order_by(TietHoc.so_thu_tu).all()
        except Exception as e:
            print(f"Lỗi lấy tiết học: {e}")
            # Trả về danh sách mặc định nếu chưa có dữ liệu
            return []
    def auto_generate_tkb_simple(self, lop_hoc_id, nam_hoc_id, hoc_ky_id):
        """Sinh TKB đơn giản dựa trên phân công"""
        try:
            from core.db.models.phan_cong import PhanCongGiangDay
            from core.db.models.mon_hoc_khoi import MonHocKhoi
            from core.db.models.tiet_hoc import TietHoc
            import random
            
            # Lấy phân công của lớp
            phan_cong_list = self.session.query(PhanCongGiangDay).filter(
                PhanCongGiangDay.lop_hoc_id == lop_hoc_id,
                PhanCongGiangDay.nam_hoc_id == nam_hoc_id,
                PhanCongGiangDay.hoc_ky_id == hoc_ky_id
            ).all()
            
            if not phan_cong_list:
                return ServiceResult(ok=False, error="Chưa có phân công giảng dạy cho lớp này")
            
            # Lấy số tiết mỗi ngày
            tiet_list = self.session.query(TietHoc).filter(TietHoc.active == 1).order_by(TietHoc.so_thu_tu).all()
            so_tiet_moi_ngay = len(tiet_list)
            
            # Ngày học (Thứ 2 -> Thứ 7, bỏ Chủ nhật)
            days = [2, 3, 4, 5, 6, 7]  # 6 ngày/tuần
            
            # Gom môn học theo số tiết
            mon_tiet_list = []
            for pc in phan_cong_list:
                khoi = pc.lop_hoc.khoi if pc.lop_hoc else 6
                so_tiet_mon = self.session.query(MonHocKhoi).filter(
                    MonHocKhoi.mon_hoc_id == pc.mon_hoc_id,
                    MonHocKhoi.khoi == khoi
                ).first()
                tiet_per_week = so_tiet_mon.so_tiet if so_tiet_mon else 2
                
                # Lấy tên môn và tên GV
                mon_name = pc.mon_hoc.ten_mon if pc.mon_hoc else "?"
                gv_name = pc.giao_vien.nguoi_dung.ho_ten if pc.giao_vien and pc.giao_vien.nguoi_dung else "?"
                
                mon_tiet_list.append({
                    'mon_hoc_id': pc.mon_hoc_id,
                    'giao_vien_id': pc.giao_vien_id,
                    'mon_name': mon_name,
                    'gv_name': gv_name,
                    'so_tiet': tiet_per_week
                })
            
            # Sắp xếp môn nhiều tiết lên trước
            mon_tiet_list.sort(key=lambda x: x['so_tiet'], reverse=True)
            
            # Tạo ma trận TKB: days x periods
            # Khởi tạo bảng trống
            tkb_matrix = {}
            for thu in days:
                for tiet in range(1, so_tiet_moi_ngay + 1):
                    tkb_matrix[(thu, tiet)] = None
            
            # Phân bố môn học vào các slot
            # Gom tất cả các slot cần phân bố
            all_slots = []
            for thu in days:
                for tiet in range(1, so_tiet_moi_ngay + 1):
                    all_slots.append((thu, tiet))
            
            # Xáo trộn để phân bố đều
            random.shuffle(all_slots)
            
            # Phân bố từng môn
            slot_idx = 0
            for mon in mon_tiet_list:
                for _ in range(mon['so_tiet']):
                    if slot_idx < len(all_slots):
                        thu, tiet = all_slots[slot_idx]
                        tkb_matrix[(thu, tiet)] = {
                            'mon_hoc_id': mon['mon_hoc_id'],
                            'giao_vien_id': mon['giao_vien_id'],
                            'mon_name': mon['mon_name'],
                            'gv_name': mon['gv_name'],
                            'thu': thu,
                            'tiet_bat_dau': tiet
                        }
                        slot_idx += 1
            
            # Chuyển ma trận thành list, bỏ qua các slot trống
            result = []
            for (thu, tiet), data in tkb_matrix.items():
                if data:
                    data['thu'] = thu
                    data['tiet_bat_dau'] = tiet
                    result.append(data)
            
            # Sắp xếp theo thứ tự ngày và tiết
            result.sort(key=lambda x: (x['thu'], x['tiet_bat_dau']))
            
            # In log để debug
            print(f"Đã sinh {len(result)} tiết học cho lớp")
            for item in result[:10]:  # In 10 item đầu
                print(f"  Thứ {item['thu']} - Tiết {item['tiet_bat_dau']}: {item['mon_name']} - {item['gv_name']}")
            
            return ServiceResult(ok=True, data=result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ServiceResult(ok=False, error=str(e))
    def auto_generate_tkb_genetic(self, lop_hoc_id, nam_hoc_id, hoc_ky_id, progress_callback=None):
        """Sinh TKB bằng giải thuật di truyền (tạm thời dùng simple)"""
        # Tạm thời gọi phương pháp simple
        if progress_callback:
            progress_callback.emit(50)
        
        result = self.auto_generate_tkb_simple(lop_hoc_id, nam_hoc_id, hoc_ky_id)
        
        if progress_callback:
            progress_callback.emit(100)
        
        return result