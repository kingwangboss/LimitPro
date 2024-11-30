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
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # 指定编码为utf-8
            logging.StreamHandler(sys.stdout)  # 使用stdout而不是stderr
        ]
    )
    
    logging.info(f"Logger initialized. Log file: {log_file}") 