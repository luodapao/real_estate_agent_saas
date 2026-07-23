"""
日志工具
提供统一的日志记录功能
"""

import logging
import os
from datetime import datetime
from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建日志目录
    log_dir = settings.LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_info(logger: logging.Logger, message: str):
    """记录INFO级别日志"""
    logger.info(message)


def log_error(logger: logging.Logger, message: str, exc_info=None):
    """记录ERROR级别日志"""
    logger.error(message, exc_info=exc_info)


def log_warning(logger: logging.Logger, message: str):
    """记录WARNING级别日志"""
    logger.warning(message)


def log_debug(logger: logging.Logger, message: str):
    """记录DEBUG级别日志"""
    logger.debug(message)