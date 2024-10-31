from crawler import EastMoneySpider
from analyzer import LimitPredictor
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    spider = EastMoneySpider()
    predictor = LimitPredictor()
    
    while True:
        try:
            # 获取竞价数据
            auction_data = spider.get_auction_data()
            
            if auction_data:
                # 分析预测
                prediction = predictor.predict(auction_data)
                
                # 输出结果
                if prediction['is_potential_limit']:
                    logger.info(f"发现潜在涨停股票！概率: {prediction['probability']}")
                    logger.info(f"影响因素: {prediction['factors']}")
            
            # 等待下一次获取数据
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"运行出错: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main() 