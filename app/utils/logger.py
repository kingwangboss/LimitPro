import logging
import os
from pathlib import Path
from datetime import datetime
import sys

def setup_logger():
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    
    # 创建logs目录
    logs_dir = root_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 移除所有现有的处理器
    for handler in root_logger.handlers[:]:
        # 确保关闭文件
        handler.close()
        root_logger.removeHandler(handler)
    
    # 设置日志文件路径（包含当天日期）
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f'stock_screener_{current_date}.log'
    
    # 配置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')  # 使用追加模式
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logger initialized. Log file: {log_file}") 