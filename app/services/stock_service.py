from ..spiders.eastmoney import EastMoneySpider
from ..models.mongodb import MongoDBClient
import pandas as pd
import logging
from datetime import datetime
import requests

class StockService:
    def __init__(self):
        self.spider = EastMoneySpider()
        self.mongo_client = MongoDBClient()

    def analyze_stocks(self, df):
        """调用分析接口获取推荐情况"""
        logging.info("\n开始调用分析接口...")
        analyze_results = []
        
        for _, row in df.iterrows():
            code = row['代码']
            name = row['名称']
            try:
                url = f'http://118.31.54.202:5000/api/v1/analyze?stock={code}'
                logging.info(f"\n分析股票 {code} {name}")
                logging.info(f"请求URL: {url}")
                
                response = requests.get(url)
                data = response.json()
                
                if data.get('code') == 200 and data.get('data', {}).get('prediction'):
                    prediction = data['data']['prediction']
                    
                    # 解析预测文本，提取关键信息
                    prediction_lines = prediction.split('\n')
                    trend = prediction_lines[0].replace('当前趋势：', '')
                    probability = prediction_lines[3].replace('出现可能性：', '').replace('%', '')
                    
                    result = {
                        '代码': code,
                        '名称': name,
                        '完整推荐': prediction,
                        '当前趋势': trend,
                        '出现可能性': float(probability),
                        '最新拐点日期': data['data']['turning_points'][-1]['date'],
                        '最新拐点价格': data['data']['turning_points'][-1]['price'],
                        '最新拐点类型': data['data']['turning_points'][-1]['type']
                    }
                    analyze_results.append(result)
                    logging.info(f"分析结果: {prediction}")
                    logging.info(f"最新拐点: {data['data']['turning_points'][-1]}")
                else:
                    logging.info(f"未获取到推荐情况或数据格式不正确")
                    
            except Exception as e:
                logging.error(f"分析股票 {code} 时出错: {str(e)}")
                continue
        
        return pd.DataFrame(analyze_results)

    def run_daily_task(self):
        """执行每日任务"""
        try:
            logging.info("开始执行每日数据获取任务...")
            
            # 获取筛选结果
            result = self.spider.get_stock_list()
            
            if result is not None and len(result) > 0:
                # 调用分析接口
                analyze_result = self.analyze_stocks(result)
                
                if len(analyze_result) > 0:
                    # 合并技术分析和API分析结果
                    final_df = pd.merge(result, analyze_result, on=['代码', '名称'], how='inner')
                    
                    # 筛选趋势为上升且可能性>=80%的股票
                    final_df = final_df[
                        (final_df['当前趋势'] == '上升') & 
                        (final_df['出现可能性'] >= 80)
                    ]
                    
                    if len(final_df) > 0:
                        logging.info(f"\n最终找到 {len(final_df)} 只符合所有条件的股票")
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        self.mongo_client.update_daily_data(final_df, current_date, 'limit')
                        logging.info(f"数据已保存到数据库，日期：{current_date}")
                    else:
                        logging.info("没有股票同时满足技术指标和趋势分析条件")
                else:
                    logging.info("分析接口未返回有效数据")
            else:
                logging.info("没有找到符合条件的股票")
            
        except Exception as e:
            logging.error(f"任务执行失败: {str(e)}")
            raise