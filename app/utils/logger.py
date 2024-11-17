import logging
import os
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_logs(log_dir, days_to_keep=30):
    """清理指定天数之前的日志文件"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        for log_file in log_dir.glob('*.log*'):
            # 获取文件修改时间
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                log_file.unlink()  # 删除文件
                logging.info(f"Deleted old log file: {log_file}")
    except Exception as e:
        logging.error(f"Error cleaning up logs: {str(e)}")

def setup_logger():
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    
    # 创建logs目录
    logs_dir = root_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # 设置日志文件路径（按日期命名）
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f'stock_screener_{current_date}.log'
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # 清理30天前的日志文件
    cleanup_old_logs(logs_dir)
    
    logging.info(f"Logger initialized. Log file: {log_file}") 