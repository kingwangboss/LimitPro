from ..spiders.volume_spider import VolumeSpider
from ..models.mongodb import MongoDBClient
import pandas as pd
import logging
from datetime import datetime

class VolumeService:
    def __init__(self):
        self.spider = VolumeSpider()
        self.mongo_client = MongoDBClient()

    def run_daily_task(self):
        """执行每日成交量分析任务"""
        try:
            logging.info("开始执行成交量分析任务...")
            
            # 获取成交量分析数据
            volume_result = self.spider.get_volume_stocks()
            
            if volume_result is not None and len(volume_result) > 0:
                current_date = datetime.now().strftime("%Y-%m-%d")
                self.mongo_client.update_daily_data(volume_result, current_date, 'volume')
                logging.info(f"成交量分析数据已保存，日期：{current_date}")
            else:
                logging.info("没有找到符合成交量条件的股票")
            
        except Exception as e:
            logging.error(f"成交量分析任务执行失败: {str(e)}")
            raise 