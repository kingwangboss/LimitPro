try:
    from flask import Flask, render_template, jsonify
    from crawler import EastMoneySpider
    from analyzer import LimitPredictor
    from datetime import datetime
    import time
    import os
except ImportError as e:
    print(f"导入错误: {str(e)}")
    print("请检查依赖是否正确安装")
    exit(1)

app = Flask(__name__)
spider = EastMoneySpider()
predictor = LimitPredictor()

# 添加调试信息
print(f"当前工作目录: {os.getcwd()}")
print(f"templates目录: {os.path.exists('templates')}")
print(f"index.html: {os.path.exists('templates/index.html')}")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"渲染模板错误: {str(e)}")
        return str(e), 500

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
    app.run(debug=True, port=5555, host='0.0.0.0') 