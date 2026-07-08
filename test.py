# test_export.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.db.session import SessionLocal
from modules.tkb.export_service import TKBExportService

session = SessionLocal()

try:
    export_svc = TKBExportService(session)
    result = export_svc.export_tkb(nam_hoc_id=2, hoc_ky_id=1)
    
    # Lưu file ra đĩa để kiểm tra
    with open('test_output.xlsx', 'wb') as f:
        f.write(result.getvalue())
    
    print(f"✅ File created: test_output.xlsx ({len(result.getvalue())} bytes)")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()