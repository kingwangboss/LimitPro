# LimitPro 股票分析系统

一个基于东方财富网数据的股票分析系统，用于筛选和分析潜在的打板投资机会。


## 功能特点

- 自动获取股票数据
- 多维度条件筛选
- 技术分析和趋势预测
- Web界面实时展示
- 每日自动更新数据
- MongoDB数据存储
- 移动端适配支持
- Docker容器化部署

## 项目结构
```
LimitPro/
├── app/ # 后端应用
│ ├── config/ # 配置文件
│ │ ├── settings.py
│ │ └── settings.template.py
│ ├── models/ # 数据库模型
│ │ └── mongodb.py
│ ├── services/ # 业务逻辑
│ │ └── stock_service.py
│ ├── spiders/ # 爬虫模块
│ │ └── eastmoney.py
│ └── utils/ # 工具函数
│ └── logger.py
├── static/ # 静态资源
│ ├── css/ # 样式文件
│ │ └── common.css
│ └── js/ # JavaScript文件
│ └── common.js
├── templates/ # 模板文件
│ ├── index.html # 首页
│ └── history.html # 历史数据页
├── logs/ # 日志目录
├── crawler_start.py # 爬虫启动脚本
├── web_start.py # Web服务启动脚本
├── requirements.txt # 项目依赖
├── Dockerfile # Docker构建文件
└── docker-compose.yml # Docker编排文件
```


## 筛选条件

1. 基础筛选：
   - 当日收盘涨停
   - 换手率20%以下
   - 不包含创业板股票

2. 技术指标：
   - 均线在144日线或233日线之上
   - 当前价超过30个交易日内的前期高点
   - 排除连续三个涨停板

3. 趋势分析：
   - 当前趋势为上升
   - 出现可能性大于等于80%

## 交易策略

### 买入条件
- 开盘价-4%~6%买入
- 当日最低点不低于前30日最高点的最高价

### 卖出条件
- 买入后当天没涨停第二天不高开或平开
- 当天涨停第二天涨停封板还手率高于20%

## 部署方式

### 1. Docker部署（推荐）

#### 前置条件
- 安装 Docker
- 安装 Docker Compose

#### Docker操作命令

1. 构建并启动服务：
```bash
# 首次启动
docker compose up -d --build

# 后续启动
docker compose up -d
```

2. 查看服务状态：
```bash
# 查看所有服务状态
docker compose ps

# 查看web服务日志
docker compose logs -f web

# 查看爬虫服务日志
docker compose logs -f crawler
```

3. 停止服务：
```bash
# 停止所有服务
docker compose down

# 停止单个服务
docker compose stop web
docker compose stop crawler
```

4. 重启服务：
```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart web
docker compose restart crawler
```

5. 更新服务：
```bash
# 重新构建并更新
docker compose up -d --build --force-recreate
```

### 2. 直接部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行爬虫服务：
```bash
python crawler_start.py
```

3. 启动Web服务：
```bash
python web_start.py
```

## 访问服务

- Web界面：`http://localhost:5001`
- 数据更新：每天下午4点自动更新
- 日志位置：`logs/stock_screener_*.log`

## 注意事项

1. Docker部署：
   - 确保Docker和Docker Compose已正确安装
   - 检查端口5001是否被占用
   - 确保MongoDB服务可访问
   - 日志文件会保存在宿主机的logs目录

2. 直接部署：
   - 确保Python 3.11.0已安装
   - 检查依赖包是否完整安装
   - 确保MongoDB服务正常运行
   - 建议使用进程管理工具保持服务运行

3. 配置文件为settings.py
   - 代码只提供settings.template.py模板文件，需要修改名称为settings.py
   - API接口配置公开使用
   - 运行前端不影响，如需要部署爬虫需要自己部署mongodb，修改配置文件

## 技术支持

如有问题或建议，请提交Issue或Pull Request。
