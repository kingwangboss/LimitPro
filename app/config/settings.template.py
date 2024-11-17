# MongoDB配置
MONGODB_URI = "mongodb://username:password@host:port/"
MONGODB_DB = "stock_analysis"
MONGODB_COLLECTION = "daily_analysis"

# API配置
ANALYSIS_API_URL = "http://118.31.54.202:5000/api/v1/analyze" 

# 数据库私有的不公布，API接口公布使用
# 本文件是配置模板文件，settings.template.py
# 使用的时候需要改成settings.py