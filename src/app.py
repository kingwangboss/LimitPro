try:
    from flask import Flask, render_template, jsonify
    from crawler import EastMoneySpider
    from analyzer import LimitPredictor
    from datetime import datetime
    import time
except ImportError as e:
    print(f"导入错误: {str(e)}")
    print("请检查依赖是否正确安装")
    exit(1)

app = Flask(__name__)
spider = EastMoneySpider()
predictor = LimitPredictor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    try:
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        
        # 获取股票数据
        stocks = spider.get_auction_data()
        if stocks:
            # 获取推荐股票
            predictions = predictor.predict(stocks)
            
            # 为所有股票计算得分
            all_stocks = predictor.calculate_scores(stocks)
            
            print(f"预测完成，共 {len(predictions)} 只推荐股票，总计 {len(all_stocks)} 只股票")
            
            return jsonify({
                'status': 'success',
                'time': current_time,
                'data': predictions,
                'allStocks': all_stocks,
                'total': len(predictions)
            })
        else:
            return jsonify({
                'status': 'error',
                'time': current_time,
                'message': '获取数据失败',
                'data': [],
                'allStocks': []
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': f'服务器错误: {str(e)}',
            'data': [],
            'allStocks': []
        })

if __name__ == '__main__':
    app.run(debug=True, port=5555) 