from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import pymongo
from flask_cors import CORS
from app.models.mongodb import MongoDBClient
from app.config.settings import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, STOCK_API_URL
import os

# 设置模板和静态文件目录的绝对路径
template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

def get_target_date():
    """根据当前时间确定要获取的数据日期"""
    now = datetime.now()
    current_time = now.time()
    cutoff_time = datetime.strptime("16:30", "%H:%M").time()
    
    if current_time < cutoff_time:
        target_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        target_date = now.strftime("%Y-%m-%d")
    
    return target_date

@app.route('/')
def index():
    return render_template('volume.html')

@app.route('/volume')
def volume():
    return render_template('volume.html')

@app.route('/volume/history')
def volume_history():
    return render_template('volume_history.html')

@app.route('/api/volume')
def get_volume_stocks():
    try:
        mongo_client = MongoDBClient()
        current_date = datetime.now().strftime("%Y-%m-%d")
        data = mongo_client.get_data_by_date(current_date, 'volume')
        
        if data:
            return jsonify({
                'status': 'success',
                'date': data['date'],
                'stocks': data['stocks']
            })
        return jsonify({
            'status': 'error',
            'message': f'No volume data found for date: {current_date}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/volume/history')
def get_volume_history():
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({
                'status': 'error',
                'message': 'Date parameter is required (format: YYYY-MM-DD)'
            })
        
        mongo_client = MongoDBClient()
        data = mongo_client.get_data_by_date(date, 'volume')
        
        if data:
            return jsonify({
                'status': 'success',
                'date': data['date'],
                'stocks': data['stocks']
            })
        return jsonify({
            'status': 'error',
            'message': f'No volume data found for date: {date}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/api/logs')
def get_logs():
    try:
        current_date = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join('logs', f'stock_screener_{current_date}.log')
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            return jsonify({
                'status': 'success',
                'logs': log_content
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'No log file found for date: {current_date}'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 