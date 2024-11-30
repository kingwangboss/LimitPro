import pymongo
from datetime import datetime
import logging
import pandas as pd
from ..config.settings import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION

class MongoDBClient:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URI)
            self.db = self.client[MONGODB_DB]
            self.limit_collection = self.db[MONGODB_COLLECTION]  # 涨停板数据
            self.volume_collection = self.db['volume_analysis']  # 成交量分析数据
            # 测试连接
            self.client.server_info()
            logging.info("MongoDB connection established")
        except Exception as e:
            logging.error(f"MongoDB connection failed: {str(e)}")
            raise
    
    def update_daily_data(self, data, date, collection_type='limit'):
        """更新或插入每日数据"""
        try:
            records = data.to_dict('records') if isinstance(data, pd.DataFrame) else data
            collection = self.limit_collection if collection_type == 'limit' else self.volume_collection
            
            existing = collection.find_one({'date': date})
            if existing:
                collection.update_one(
                    {'date': date},
                    {
                        '$set': {
                            'stocks': records,
                            'updated_at': datetime.now()
                        }
                    }
                )
                logging.info(f"Updated {collection_type} data for {date}")
            else:
                collection.insert_one({
                    'date': date,
                    'stocks': records,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                logging.info(f"Inserted new {collection_type} data for {date}")
                
        except Exception as e:
            logging.error(f"MongoDB operation failed: {str(e)}")
            raise

    def get_data_by_date(self, date, collection_type='limit'):
        """获取指定日期的数据"""
        try:
            collection = self.limit_collection if collection_type == 'limit' else self.volume_collection
            return collection.find_one({'date': date})
        except Exception as e:
            logging.error(f"Failed to get {collection_type} data for date {date}: {str(e)}")
            return None

    def __del__(self):
        """关闭MongoDB连接"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logging.info("MongoDB connection closed")
        except Exception as e:
            logging.error(f"Error closing MongoDB connection: {str(e)}")