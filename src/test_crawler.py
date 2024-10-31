import json
from crawler import EastMoneySpider
import time

def test_crawler():
    spider = EastMoneySpider()
    print("开始获取竞价数据...")
    
    # 获取3次数据，每次间隔3秒
    for i in range(3):
        data = spider.get_auction_data()
        if data:
            print(f"\n第 {i+1} 次获取数据成功，共 {len(data)} 只股票")
            print("\n前3只股票数据示例：")
            for stock in data[:3]:
                print("\n股票:", stock['name'], f"({stock['code']})")
                print(f"价格: {stock['price']}")
                print(f"涨跌幅: {stock['change_percent']}%")
                print(f"成交量: {stock['volume']}")
                print(f"成交额: {stock['amount']}")
                print(f"量比: {stock['volume_ratio']}")
        else:
            print(f"\n第 {i+1} 次获取数据失败")
        
        time.sleep(3)

if __name__ == "__main__":
    test_crawler() 