from app.utils.logger import setup_logger
from app.services.stock_service import StockService
import schedule
import time
import logging

def run_task_with_retry():
    """执行任务，失败时重试一次"""
    service = StockService()
    try:
        print("开始执行数据获取任务...")
        service.run_daily_task()
        print("数据获取任务执行成功")
        return True
    except Exception as e:
        print(f"第一次执行失败: {str(e)}")
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

def main():
    # 设置日志
    setup_logger()
    
    # 启动时先执行一次任务
    print("程序启动，执行首次数据获取...")
    run_task_with_retry()
    
    # 设置每天下午4点执行的定时任务
    print("设置每天下午4点的定时任务...")
    schedule.every().day.at("16:00").do(run_task_with_retry)
    
    # 运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 