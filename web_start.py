from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pymongo
from flask_cors import CORS
from app.models.mongodb import MongoDBClient
from app.config.settings import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, STOCK_API_URL

app = Flask(__name__)
CORS(app)

def get_target_date():
    """根据当前时间确定要获取的数据日期"""
    now = datetime.now()
    current_time = now.time()
    cutoff_time = datetime.strptime("16:30", "%H:%M").time()
    
    # 如果当前时间在16:30之前，返回昨天的日期
    if current_time < cutoff_time:
        target_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        target_date = now.strftime("%Y-%m-%d")
    return target_date

@app.route('/')
def index():
    return render_template('index.html', stock_api_url=STOCK_API_URL)

@app.route('/api/stocks')
def get_stocks():
    try:
        mongo_client = MongoDBClient()
        target_date = get_target_date()
        data = mongo_client.get_data_by_date(target_date)
        
        if data:
            return jsonify({
                'status': 'success',
                'date': data['date'],
                'stocks': data['stocks']
            })
        return jsonify({
            'status': 'error',
            'message': f'No data found for date: {target_date}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 