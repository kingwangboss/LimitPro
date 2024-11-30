from app.spiders.volume_spider import VolumeSpider
import logging
from app.utils.logger import setup_logger

def test_volume_spider():
    # 设置日志
    setup_logger()
    
    # 初始化爬虫
    spider = VolumeSpider()
    logging.info("开始测试成交量爬虫...")
    
    try:
        # 获取符合条件的股票
        stocks = spider.get_volume_stocks()
        
        if stocks and len(stocks) > 0:
            logging.info(f"\n找到 {len(stocks)} 只符合条件的股票:")
            for stock in stocks:
                logging.info(f"\n代码: {stock['code']}")
                logging.info(f"名称: {stock['name']}")
                logging.info(f"最新价: {stock['price']:.2f}")
                logging.info(f"涨跌幅: {stock['percent']:.2f}%")
                logging.info(f"换手率: {stock['turnover']:.2f}%")
                logging.info(f"量比: {stock['volume_ratio']:.2f}")
                logging.info(f"流通市值: {stock['market_value']:.2f}亿")
                logging.info(f"成交量: {stock['volume']}")
                logging.info("-" * 50)
        else:
            logging.info("没有找到符合条件的股票")
            
    except Exception as e:
        logging.error(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_volume_spider() 