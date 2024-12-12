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
    
    # 设置日志文件路径
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f'stock_screener_{current_date}.log'
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    logging.root.setLevel(logging.INFO)
    logging.root.handlers = []  # 清除现有的处理器
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
    
    logging.info(f"Logger initialized. Log file: {log_file}") 