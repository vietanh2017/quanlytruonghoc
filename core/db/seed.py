# core\db\seed.py
# TODO: implement
from core.db.session import SessionLocal
from core.db.models.nam_hoc import NamHoc

session = SessionLocal()
if not session.query(NamHoc).first():
    nam_hoc = NamHoc(ten_nam_hoc="2026-2027", active=True)
    session.add(nam_hoc)
    session.commit()
    print("✅ Đã thêm năm học 2026-2027")
session.close()