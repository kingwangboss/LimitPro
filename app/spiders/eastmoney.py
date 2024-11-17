import requests
import pandas as pd
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import logging

class EastMoneySpider:
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
            allowed_methods=frozenset(['GET', 'POST']),
            raise_on_status=True,
            raise_on_redirect=True
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _make_request_with_retry(self, url, params=None, max_retries=3):
        """带有重试机制的请求函数"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, json.JSONDecodeError) as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    logging.error(f"All retry attempts failed for URL: {url}")
                    raise
                time.sleep(2 ** attempt)  # 指数退避
                continue

    def get_stock_history(self, stock_code, retry_count=3):
        """获取个股历史数据，带有重试机制"""
        url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
        params = {
            'secid': f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}',
            'ut': '7eea3edcaed734bea9cbfc24409ed989',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '101',
            'fqt': '1',
            'beg': '0',
            'end': '20500000',
            'lmt': '233'
        }

        for attempt in range(retry_count):
            try:
                data = self._make_request_with_retry(url, params)
                if not data.get('data') or not data['data'].get('klines'):
                    raise ValueError(f"Invalid data format for stock {stock_code}")

                klines = [line.split(',') for line in data['data']['klines']]
                df = pd.DataFrame(klines, columns=['日期', '开盘', '收盘', '最高', '最低', 
                                                 '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'])
                
                # 转换数据类型
                numeric_columns = ['开盘', '收盘', '最高', '最低', '涨跌幅', '换手率']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df

            except Exception as e:
                logging.warning(f"获取股票 {stock_code} 历史数据失败 (尝试 {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logging.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"获取股票 {stock_code} 历史数据最终失败")
                    return None

    def get_stock_list(self, retry_count=3):
        """获取股票列表，带有重试机制"""
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
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
            'fields': 'f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18',
        }
        
        try:
            # 获取上证数据
            logging.info("获取上证主板数据...")
            data_sh = self._make_request_with_retry(url, params)
            
            # 获取深证数据
            params['fs'] = 'm:0+t:6,m:0+t:13'  # 深证主板
            logging.info("获取深证主板数据...")
            data_sz = self._make_request_with_retry(url, params)
            
            # 合并数据
            stock_list = []
            if data_sh.get('data') and data_sh['data'].get('diff'):
                stock_list.extend(data_sh['data']['diff'])
            if data_sz.get('data') and data_sz['data'].get('diff'):
                stock_list.extend(data_sz['data']['diff'])
            
            if not stock_list:
                logging.error("未获取到股票列表数据")
                return None
                
            df = pd.DataFrame(stock_list)
            
            # 重命名列
            columns_map = {
                'f12': '代码',
                'f14': '名称',
                'f2': '最新价',
                'f3': '涨跌幅',
                'f8': '换手率',
            }
            
            # 选择并重命名列
            df = df[columns_map.keys()].rename(columns=columns_map)
            
            # 数据处理
            df['代码'] = df['代码'].astype(str).str.zfill(6)
            df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
            df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
            df['换手率'] = pd.to_numeric(df['换手率'], errors='coerce')
            
            # 筛选条件
            df = df[(df['涨跌幅'] >= 9.9) & (df['换手率'] <= 20)]
            
            logging.info(f"获取到 {len(df)} 只符合条件的股票")
            return df
            
        except Exception as e:
            logging.error(f"获取股票列表失败: {str(e)}")
            return None