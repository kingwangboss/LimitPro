import requests
import pandas as pd
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import logging

class VolumeSpider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # 配置重试策略
        self.session = requests.Session()
        retries = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(['GET', 'POST'])  # 允许重试的请求方法
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _make_request_with_retry(self, url, params=None, max_retries=3):
        """统一的请求处理函数"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:  # 最后一次重试
                    raise
                time.sleep(2 ** attempt)  # 指数退避
                continue

    def get_stock_history(self, stock_code):
        """获取个股历史数据"""
        url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
        params = {
            'secid': f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}',
            'ut': '7eea3edcaed734bea9cbfc24409ed989',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '101',  # 日线
            'fqt': '1',    # 前复权
            'end': '20500000',
            'beg': '-5',   # 只获取最近5天数据
            'lmt': '5'     # 限制返回5条数据
        }
        
        try:
            data = self._make_request_with_retry(url, params)
            if not data.get('data') or not data['data'].get('klines'):
                logging.error(f"获取股票 {stock_code} 的历史数据失败")
                return None
            
            klines = [line.split(',') for line in data['data']['klines']]
            df = pd.DataFrame(klines, columns=['日期', '开盘', '收盘', '最高', '最低', 
                                             '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'])
            
            # 转换数据类型
            df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
            
            # 打印成交量数据，用于调试
            logging.info(f"最近5天成交量: {df['成交量'].tolist()}")
            
            return df
            
        except Exception as e:
            logging.error(f"获取股票 {stock_code} 历史数据失败: {str(e)}")
            return None

    def get_volume_stocks(self):
        """获取符合成交量规则的股票列表"""
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        
        try:
            logging.info("开始获取股票列表...")
            all_stocks = []
            
            # 获取上证主板数据
            sh_params = {
                'pn': 1,
                'pz': 5000,
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'wbp2u': '|0|0|0|web',
                'fid': 'f3',
                'fs': 'm:1+t:2,m:1+t:23',  # 上证主板
                'fields': 'f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f22,f23',
            }
            
            logging.info("获取上证主板数据...")
            sh_data = self._make_request_with_retry(url, sh_params)
            if sh_data.get('data') and sh_data['data'].get('diff'):
                all_stocks.extend(sh_data['data']['diff'])
                logging.info(f"获取到 {len(sh_data['data']['diff'])} 只上证股票")
            
            # 获取深证主板数据
            sz_params = sh_params.copy()
            sz_params['fs'] = 'm:0+t:6,m:0+t:13'  # 深证主板
            
            logging.info("获取深证主板数据...")
            sz_data = self._make_request_with_retry(url, sz_params)
            if sz_data.get('data') and sz_data['data'].get('diff'):
                all_stocks.extend(sz_data['data']['diff'])
                logging.info(f"获取到 {len(sz_data['data']['diff'])} 只深证股票")
            
            if all_stocks:
                df = pd.DataFrame(all_stocks)
                logging.info(f"总共获取到 {len(df)} 只股票的原始数据")
                
                # 重命名列
                columns_map = {
                    'f12': 'code',
                    'f14': 'name',
                    'f2': 'price',
                    'f3': 'percent',
                    'f8': 'turnover',
                    'f10': 'volume_ratio',
                    'f20': 'total_value',
                    'f21': 'market_value',
                    'f5': 'volume',
                    'f6': 'amount',
                }
                
                df = df[columns_map.keys()].rename(columns=columns_map)
                
                # 数据类型转换
                df['code'] = df['code'].astype(str).str.zfill(6)
                numeric_columns = ['price', 'percent', 'turnover', 'volume_ratio', 'total_value', 'market_value', 'volume', 'amount']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 过滤科创板
                df = df[~df['code'].str.startswith('688')]
                
                # 流通市值单位转换（从元转换为亿元）
                df['market_value'] = df['market_value'] / 100000000
                
                # 打印一些样本数据
                logging.info("\n流通市值样本数据:")
                sample_stocks = df.sample(min(5, len(df)))
                for _, row in sample_stocks.iterrows():
                    logging.info(f"{row['code']} {row['name']} 流通市值: {row['market_value']:.2f}亿")
                
                # 打印每个条件筛选后的数量
                logging.info(f"涨跌幅(3-5%): {len(df[df['percent'].between(3, 5)])} 只")
                logging.info(f"换手率(5-10%): {len(df[df['turnover'].between(5, 10)])} 只")
                logging.info(f"量比>1: {len(df[df['volume_ratio'] > 1])} 只")
                logging.info(f"流通市值(30-100亿): {len(df[df['market_value'].between(30, 100)])} 只")
                
                # 应用筛选条件
                df = df[
                    (df['percent'].between(3, 5)) &  # 涨幅3%-5%
                    (df['turnover'].between(5, 10)) &  # 换手率5%-10%
                    (df['volume_ratio'] > 1) &  # 量比大于1
                    (df['market_value'].between(30, 100))  # 流通市值30-100亿
                ]
                
                logging.info(f"初步筛选后剩余 {len(df)} 只股票")
                
                # 打印初步筛选后的股票列表
                if not df.empty:
                    logging.info("\n初步筛选结果:")
                    for _, row in df.iterrows():
                        logging.info(f"{row['code']} {row['name']} "
                                   f"涨跌幅:{row['percent']:.2f}% "
                                   f"换手率:{row['turnover']:.2f}% "
                                   f"量比:{row['volume_ratio']:.2f} "
                                   f"流通市值:{row['market_value']:.2f}亿")
                
                # 获取历史数据检查成交量趋势
                filtered_stocks = []
                for _, row in df.iterrows():
                    code = row['code']
                    name = row['name']
                    logging.info(f"\n检查 {code} {name} 的成交量趋势...")
                    hist_data = self.get_stock_history(code)
                    
                    if hist_data is not None and len(hist_data) >= 5:
                        # 检查成交量趋势
                        volumes = hist_data['成交量'].tolist()
                        volumes.reverse()  # 反转列表，使其按时间顺序排列
                        logging.info(f"成交量序列（从前到后）: {volumes}")
                        
                        # 计算最近两天的成交量变化
                        today_volume = volumes[0]
                        yesterday_volume = volumes[1]
                        
                        # 计算前3天的平均成交量
                        avg_volume = sum(volumes[2:]) / 3
                        
                        # 判断条件：
                        # 1. 今天的成交量大于昨天
                        # 2. 今天的成交量是前3天平均值的1.8倍以上
                        if (today_volume > yesterday_volume and 
                            today_volume > avg_volume * 1.8):
                            logging.info(f"成交量符合条件：")
                            logging.info(f"今日成交量: {today_volume:.0f}")
                            logging.info(f"昨日成交量: {yesterday_volume:.0f}")
                            logging.info(f"前3天平均: {avg_volume:.0f}")
                            logging.info(f"今日/平均: {(today_volume/avg_volume):.2f}倍")
                            
                            # 添加成交量倍数到结果中
                            stock_data = row.to_dict()
                            stock_data['volume_times'] = today_volume / avg_volume
                            filtered_stocks.append(stock_data)
                        else:
                            if today_volume <= yesterday_volume:
                                logging.info("今日成交量未超过昨日")
                            if today_volume <= avg_volume * 1.8:
                                logging.info(f"今日成交量未达到前3天平均的1.8倍 (当前: {(today_volume/avg_volume):.2f}倍)")
                    else:
                        logging.info("获取历史数据失败或数据不足")
                
                logging.info(f"\n最终找到 {len(filtered_stocks)} 只符合所有条件的股票")
                return filtered_stocks
                
            return None
        except Exception as e:
            logging.error(f"获取股票列表失败: {str(e)}")
            return None 