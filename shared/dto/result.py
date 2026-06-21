# D:\QUANLYTRUONGHOC\shared\dto\result.py
"""
ServiceResult: kết quả trả về từ tầng Service.
Dùng thống nhất toàn app thay vì raise exception.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceResult:
    ok: bool
    data: Any = None
    error: str = ""

    def __bool__(self):
        return self.ok
