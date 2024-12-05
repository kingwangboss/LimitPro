from app.utils.logger import setup_logger
from app.services.volume_service import VolumeService
import schedule
import time
import logging
from datetime import datetime

def run_volume_task():
    """执行成交量分析任务"""
    service = VolumeService()
    try:
        print("开始执行成交量分析任务...")
        service.run_daily_task()
        print("成交量分析任务执行成功")
        return True
    except Exception as e:
        print(f"成交量分析任务执行失败: {str(e)}")
        print("等待30秒后重试...")
        time.sleep(30)
        try:
            print("开始重试...")
            service.run_daily_task()
            print("重试执行成功")
            return True
        except Exception as e:
            print(f"重试也失败了: {str(e)}")
            return False

def is_weekday():
    """判断是否为工作日（周一到周五）"""
    return datetime.now().weekday() < 5

def main():
    # 设置日志
    setup_logger()
    
    # 设置定时任务
    logging.info("设置定时任务...")
    # 成交量分析 - 工作日下午2:30
    schedule.every().day.at("14:30").do(lambda: run_volume_task() if is_weekday() else None)
    
    logging.info("定时任务已设置：")
    logging.info("- 成交量分析：工作日 14:30")
    
    # 运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 