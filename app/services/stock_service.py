from ..spiders.eastmoney import EastMoneySpider
from ..models.mongodb import MongoDBClient
from ..config.settings import ANALYSIS_API_URL
import pandas as pd
import logging
from datetime import datetime
import requests

class StockService:
    def __init__(self):
        self.spider = EastMoneySpider()
        self.mongo_client = MongoDBClient()

    def screen_stocks(self):
        # [原screen_stocks方法的代码]
        pass

    def analyze_stocks(self, df):
        """调用分析接口获取推荐情况"""
        logging.info("\n开始调用分析接口...")
        analyze_results = []
        
        for _, row in df.iterrows():
            code = row['代码']
            name = row['名称']
            try:
                url = f'{ANALYSIS_API_URL}?stock={code}'
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
            
            # 第一步：获取股票列表并筛选
            logging.info("步骤1: 获取涨停且换手率20%以下的股票...")
            stock_list = self.spider.get_stock_list()
            
            if stock_list is None or len(stock_list) == 0:
                logging.info("没有找到符合初步条件的股票")
                return
            
            logging.info(f"找到 {len(stock_list)} 只符合初步条件的股票")
            
            # 第二步：筛选技术指标
            logging.info("\n步骤2: 筛选技术指标...")
            final_stocks = []
            total = len(stock_list)
            
            for idx, row in stock_list.iterrows():
                code = row['代码']
                name = row['名称']
                logging.info(f"\n处理: {idx+1}/{total} - {code} {name}")
                
                # 获取历史数据并进行技术指标筛选
                hist_data = self.spider.get_stock_history(code)
                if hist_data is None or len(hist_data) < 233:
                    logging.info(f"{code} 历史数据不足，跳过")
                    continue
                
                # 检查连续涨停
                latest_three_days = hist_data.tail(3)
                if all(latest_three_days['涨跌幅'] >= 9.9):
                    logging.info(f"{code} 连续三个涨停板，跳过")
                    continue
                
                # 计算均线
                hist_data['MA144'] = hist_data['收盘'].rolling(window=144).mean()
                hist_data['MA233'] = hist_data['收盘'].rolling(window=233).mean()
                
                latest_close = hist_data['收盘'].iloc[-1]
                latest_ma144 = hist_data['MA144'].iloc[-1]
                latest_ma233 = hist_data['MA233'].iloc[-1]
                
                if not (latest_close >= latest_ma144 or latest_close >= latest_ma233):
                    logging.info(f"{code} 不满足均线条件，跳过")
                    continue
                
                # 检查30日高点
                last_30_days = hist_data.tail(30)
                history_high = max(last_30_days['最高'].max(), last_30_days['收盘'].max())
                
                if latest_close >= history_high:
                    recent_ups = latest_three_days['涨跌幅'].tolist()
                    recent_ups_str = [f"{x:.1f}%" for x in recent_ups]
                    
                    final_stocks.append({
                        '代码': code,
                        '名称': name,
                        '收盘价': latest_close,
                        '换手率': row['换手率'],
                        '涨跌幅': row['涨跌幅'],
                        'MA144': latest_ma144,
                        'MA233': latest_ma233,
                        '30日高点': history_high,
                        '近三日涨幅': ' -> '.join(recent_ups_str)
                    })
                    logging.info(f"{code} 符合所有技术指标！")
                else:
                    logging.info(f"{code} 未突破30日高点")
            
            if not final_stocks:
                logging.info("没有股票符合技术指标条件")
                return
            
            # 第三步：调用分析接口
            logging.info("\n步骤3: 调用分析接口...")
            tech_df = pd.DataFrame(final_stocks)
            analyze_df = self.analyze_stocks(tech_df)
            
            if len(analyze_df) > 0:
                # 合并技术分析和API分析结果
                final_df = pd.merge(tech_df, analyze_df, on=['代码', '名称'], how='inner')
                
                # 筛选趋势为上升且可能性>=80%的股票
                final_df = final_df[
                    (final_df['当前趋势'] == '上升') & 
                    (final_df['出现可能性'].between(70, 75))
                ]
                
                if len(final_df) > 0:
                    logging.info(f"\n最终找到 {len(final_df)} 只符合所有条件的股票")
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    self.mongo_client.update_daily_data(final_df, current_date)
                    logging.info(f"数据已保存到数据库，日期：{current_date}")
                else:
                    logging.info("没有股票同时满足技术指标和趋势分析条件")
            else:
                logging.info("分析接口未返回有效数据")
            
        except Exception as e:
            logging.error(f"任务执行失败: {str(e)}")
            raise