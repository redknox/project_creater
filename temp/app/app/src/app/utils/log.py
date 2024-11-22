"""
日志模块，提供统一的日志记录功能。

特性：
1. 同时输出到文件和终端
2. 文件日志级别为INFO
3. 终端日志级别为DEBUG
4. 终端输出包含详细的模块位置信息
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name, log_dir='logs'):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件存储目录
    
    Returns:
        logger: 配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 示例用法
if __name__ == '__main__':
    logger = setup_logger('test_logger')
    logger.debug('这是一条调试信息')
    logger.info('这是一条信息')
    logger.warning('这是一条警告')
    logger.error('这是一条错误信息')
