import requests
import json
from datetime import datetime

class EastMoneySpider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Referer': 'http://quote.eastmoney.com/center/gridlist.html'
        }
        self.timeout = 5
        
    def get_auction_data(self):
        """获取竞价数据"""
        url = "http://83.push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 2000,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'wbp2u': '|0|0|0|web',
            'fid': 'f3',
            'fs': 'm:1+t:2',  # 上证主板
            'fields': 'f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f22,f23,f100,f26',
            '_': str(int(datetime.now().timestamp() * 1000))
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            result = response.json()
            
            if result['rc'] == 0 and 'data' in result and 'diff' in result['data']:
                stocks = self._parse_stock_data(result['data']['diff'])
                print(f"获取数据成功，共 {len(stocks)} 只股票")
                return stocks
            return None
            
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            return None
    
    def _parse_stock_data(self, data_list):
        """解析股票数据"""
        stocks = []
        filtered_count = 0
        for item in data_list:
            try:
                # 过滤退市、ST和科创板股票
                name = str(item['f14'])
                code = str(item['f12'])
                if (any(x in name for x in ['退市', 'ST', '*ST', 'PT', 'S']) or 
                    code.startswith('688') or
                    '-' in str(item.get('f2', ''))):  # 过滤掉含有'-'的数据
                    filtered_count += 1
                    continue
                
                # 转换数值，处理特殊值
                def safe_float(value, default=0.0):
                    try:
                        if isinstance(value, (int, float)):
                            return float(value)
                        if isinstance(value, str):
                            value = value.replace('-', '0')
                            return float(value) if value else default
                        return default
                    except:
                        return default
                
                # 确保上市天数大于10天
                listing_days = safe_float(item.get('f26', 0))
                if listing_days < 10:
                    filtered_count += 1
                    continue
                    
                stock = {
                    'code': code,
                    'name': name,
                    'price': safe_float(item['f2']),
                    'change_percent': safe_float(item['f3']),
                    'change_amount': safe_float(item['f4']),
                    'volume': safe_float(item['f5']),
                    'amount': safe_float(item['f6']),
                    'amplitude': safe_float(item['f7']),
                    'turnover_rate': safe_float(item['f8']),
                    'pe_ratio': safe_float(item.get('f9', 0)),
                    'volume_ratio': safe_float(item.get('f22', 0)),
                    'high': safe_float(item['f15']),
                    'low': safe_float(item['f16']),
                    'open': safe_float(item['f17']),
                    'prev_close': safe_float(item['f18']),
                    'speed': safe_float(item.get('f23', 0)),
                    'listing_days': listing_days
                }
                
                # 过滤掉异常数据
                if (stock['price'] <= 0 or 
                    stock['prev_close'] <= 0 or 
                    stock['volume'] <= 0):
                    filtered_count += 1
                    continue
                    
                stocks.append(stock)
            except Exception as e:
                print(f"解析股票 {name}({code}) 数据失败: {str(e)}")
                continue
        
        print(f"过滤掉 {filtered_count} 只股票（退市、ST、科创板、新股、异常数据）")
        return stocks

if __name__ == "__main__":
    # 简单测试
    spider = EastMoneySpider()
    data = spider.get_auction_data()
    if data:
        print("\n前5只股票信息：")
        for stock in data[:5]:
            print(f"\n{stock['name']} ({stock['code']})")
            print(f"价格: {stock['price']:.2f}")
            print(f"涨跌幅: {stock['change_percent']:.2f}%")
            print(f"涨速: {stock['speed']:.2f}")
            print(f"量比: {stock['volume_ratio']:.2f}")
            print(f"换手率: {stock['turnover_rate']:.2f}%")