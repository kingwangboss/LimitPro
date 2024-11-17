from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pymongo
from flask_cors import CORS
from app.models.mongodb import MongoDBClient
from app.config.settings import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION, STOCK_API_URL

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html', stock_api_url=STOCK_API_URL)

@app.route('/api/stocks')
def get_stocks():
    try:
        mongo_client = MongoDBClient()
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        data = mongo_client.get_data_by_date(yesterday)
        
        if data:
            return jsonify({
                'status': 'success',
                'date': data['date'],
                'stocks': data['stocks']
            })
        return jsonify({
            'status': 'error',
            'message': 'No data found for yesterday'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 