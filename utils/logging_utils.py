# utils/logging_utils.py
"""
로깅 유틸리티
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoggingUtils:
    """로깅 관련 유틸리티"""
    
    @staticmethod
    def setup_logger(name: str, 
                    log_file: Optional[Path] = None, 
                    level: str = "INFO") -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 파일 핸들러
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_execution_time(func):
        """실행 시간 로깅 데코레이터"""
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger = logging.getLogger(func.__module__)
            logger.info(f"{func.__name__} 실행 시간: {execution_time:.2f}초")
            
            return result
        
        return wrapper
    
    @staticmethod
    def log_memory_usage():
        """메모리 사용량 로깅"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            logger = logging.getLogger(__name__)
            logger.info(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.1f}MB")
            
        except ImportError:
            pass