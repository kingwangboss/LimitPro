import pandas as pd
import numpy as np
from datetime import datetime

class LimitPredictor:
    def __init__(self):
        self.top_n = 10  # 推荐股票数量
        
    def predict(self, stocks_data):
        """预测可能涨停的股票"""
        if not stocks_data:
            return []
            
        try:
            # 转换为DataFrame
            df = pd.DataFrame(stocks_data)
            
            # 确保数值类型
            numeric_columns = ['change_percent', 'amount', 'volume_ratio', 
                             'turnover_rate', 'speed']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 填充缺失值
            df = df.fillna(0)
            
            # 计算各项得分
            df['change_score'] = self._normalize(df['change_percent']) * 0.3
            df['amount_score'] = self._normalize(df['amount']) * 0.2
            df['volume_ratio_score'] = self._normalize(df['volume_ratio']) * 0.2
            df['turnover_score'] = self._normalize(df['turnover_rate']) * 0.15
            df['speed_score'] = self._normalize(df['speed']) * 0.15
            
            # 计算总分
            df['total_score'] = (df['change_score'] + 
                               df['amount_score'] + 
                               df['volume_ratio_score'] + 
                               df['turnover_score'] + 
                               df['speed_score'])
            
            # 计算涨停概率（根据总分计算，不再使用阈值过滤）
            df['probability'] = df['total_score'].apply(lambda x: min(x * 100, 99.99))
            
            # 直接获取前10只得分最高的股票
            top_stocks = df.nlargest(self.top_n, 'probability')
            
            # 构建结果
            results = []
            for _, stock in top_stocks.iterrows():
                result = {
                    'code': stock['code'],
                    'name': stock['name'],
                    'probability': round(stock['probability'], 2),
                    'factors': {
                        '竞价涨幅': f"{stock['change_percent']:.2f}%",
                        '竞价金额': f"{stock['amount']/10000:.2f}万",
                        '量比': f"{stock['volume_ratio']:.2f}",
                        '换手率': f"{stock['turnover_rate']:.2f}%",
                        '涨速': f"{stock['speed']:.2f}%",
                        '现价': f"{stock['price']:.2f}元",
                        '振幅': f"{stock['amplitude']:.2f}%",
                        '总得分': f"{stock['total_score']:.2f}"  # 添加总得分显示
                    }
                }
                results.append(result)
                
            print(f"分析完成，推荐 {len(results)} 只股票")
            return results
            
        except Exception as e:
            print(f"预测过程出错: {str(e)}")
            return []
    
    def _normalize(self, series):
        """归一化处理"""
        if len(series) == 0:
            return series
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series.apply(lambda x: 0.5)
        return (series - min_val) / (max_val - min_val)

    def calculate_scores(self, stocks_data):
        """为所有股票计算得分"""
        if not stocks_data:
            return []
            
        try:
            df = pd.DataFrame(stocks_data)
            
            # 确保数值类型
            numeric_columns = ['change_percent', 'amount', 'volume_ratio', 
                             'turnover_rate', 'speed']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.fillna(0)
            
            # 计算各项得分
            df['change_score'] = self._normalize(df['change_percent']) * 0.3
            df['amount_score'] = self._normalize(df['amount']) * 0.2
            df['volume_ratio_score'] = self._normalize(df['volume_ratio']) * 0.2
            df['turnover_score'] = self._normalize(df['turnover_rate']) * 0.15
            df['speed_score'] = self._normalize(df['speed']) * 0.15
            
            # 计算总分
            df['total_score'] = (df['change_score'] + 
                               df['amount_score'] + 
                               df['volume_ratio_score'] + 
                               df['turnover_score'] + 
                               df['speed_score'])
            
            # 转换为列表
            result = df.to_dict('records')
            return sorted(result, key=lambda x: x['total_score'], reverse=True)
            
        except Exception as e:
            print(f"计算所有股票得分时出错: {str(e)}")
            return []

if __name__ == "__main__":
    from crawler import EastMoneySpider
    
    spider = EastMoneySpider()
    predictor = LimitPredictor()
    
    stocks = spider.get_auction_data()
    if stocks:
        predictions = predictor.predict(stocks)
        print("\n预测结果：")
        for i, stock in enumerate(predictions, 1):
            print(f"\n{i}. {stock['name']}({stock['code']}) - 涨停概率: {stock['probability']}%")
            print("影响因素:")
            for factor, value in stock['factors'].items():
                print(f"  {factor}: {value}")