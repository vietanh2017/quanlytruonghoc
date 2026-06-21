# core/utils/logger.py

import os
import logging
from datetime import datetime
import traceback


class Logger:
    """Hệ thống ghi log cho ứng dụng"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """Khởi tạo logger"""
        # Tạo thư mục logs nếu chưa có
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Log file theo ngày
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"logs/app_{today}.log"
        
        # Cấu hình logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # In ra console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def info(self, message):
        """Ghi log INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Ghi log WARNING"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=True):
        """Ghi log ERROR"""
        if exc_info:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def debug(self, message):
        """Ghi log DEBUG"""
        self.logger.debug(message)
    
    def log_action(self, user, action, details=""):
        """Ghi log hành động của người dùng"""
        message = f"[{user}] {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_exception(self, e):
        """Ghi log exception"""
        self.error(f"Exception: {str(e)}\n{traceback.format_exc()}")


# Singleton instance
logger = Logger()