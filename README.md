# 🧸 Labubu 藏品管理系统

资深藏家 Labubu 藏品档案与置换记录管理平台，基于 Vue 3 + FastAPI + SQLite 构建。

## 快速启动

```bash
docker-compose up --build
```

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- OpenAPI 文档：http://localhost:8000/docs

## ER 图

```
┌──────────────────────────────┐       ┌──────────────────────────────┐
│           items              │       │         exchanges            │
├──────────────────────────────┤       ├──────────────────────────────┤
│ id          INTEGER PK       │◄──────│ item_id     INTEGER FK       │
│ series      VARCHAR(100)     │       │ id          INTEGER PK       │
│ style_id    VARCHAR(50)      │       │ exchange_date  VARCHAR(20)   │
│ name        VARCHAR(200)     │       │ counterparty   VARCHAR(100)  │
│ rarity      VARCHAR(20)      │       │ price_difference  FLOAT      │
│ acquisition_method VARCHAR(50)│      │ flow_status    VARCHAR(20)    │
│ purchase_price  FLOAT        │       │ notes       TEXT             │
│ status      VARCHAR(20)      │       │ created_at  DATETIME         │
│ batch_no    VARCHAR(50)      │       │ updated_at  DATETIME         │
│ image_path  VARCHAR(500)     │       │ deleted_at  DATETIME (NULL)  │
│ notes       TEXT             │       └──────────────────────────────┘
│ created_at  DATETIME         │
│ updated_at  DATETIME         │       ┌──────────────────────────────┐
│ deleted_at  DATETIME (NULL)  │       │      market_prices           │
└──────────────────────────────┘       ├──────────────────────────────┤
                                       │ id          INTEGER PK       │
关系:                                  │ style_id    VARCHAR(50)      │
  items 1 ──── N exchanges             │ platform    VARCHAR(50)      │
  market_prices 按 style_id 对照 items   │ deal_price  FLOAT            │
软删除: deleted_at 非空表示已删除        │ record_date VARCHAR(20)      │
                                       │ notes       TEXT             │
                                       │ deleted_at  DATETIME (NULL)  │
                                       └──────────────────────────────┘
```

## 接口清单

### 藏品档案 `/api/items`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/items` | 分页检索藏品（支持 series / rarity / keyword 筛选） |
| GET | `/api/items/series` | 获取所有系列列表 |
| GET | `/api/items/{id}` | 获取单个藏品详情 |
| POST | `/api/items` | 新增藏品（隐藏款必填 batch_no，格式: 两位字母+六位数字-两位数字） |
| PUT | `/api/items/{id}` | 更新藏品信息 |
| DELETE | `/api/items/{id}` | 软删除藏品（设置 deleted_at） |

### 置换记录 `/api/exchanges`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/exchanges` | 分页检索置换记录（支持 counterparty 筛选） |
| GET | `/api/exchanges/{id}` | 获取单条置换记录 |
| POST | `/api/exchanges` | 新增置换（仅「在库」藏品，自动置为置换中） |
| PUT | `/api/exchanges/{id}` | 更新置换记录（洽谈中可编辑） |
| POST | `/api/exchanges/{id}/confirm` | 成交确认（藏品→已出，记录锁定） |
| POST | `/api/exchanges/{id}/cancel` | 撤回置换（藏品→在库） |
| DELETE | `/api/exchanges/{id}` | 软删除置换记录 |

### 行情参考价 `/api/market-prices`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market-prices` | 分页检索（style_id / date_from / date_to） |
| GET | `/api/market-prices/trend/{style_id}` | 款式近 N 笔行情折线数据 |
| POST | `/api/market-prices` | 录入行情（同款式+平台+日期不可重复） |
| PUT | `/api/market-prices/{id}` | 更新行情 |
| DELETE | `/api/market-prices/{id}` | 软删除行情 |

### 资产看板 `/api/stats`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/dashboard` | 状态分布、系列统计、近六月置换趋势 |

### 回收站 `/api/recycle`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recycle` | 列出已软删除的藏品与置换 |
| POST | `/api/recycle/items/{id}/restore` | 恢复藏品 |
| POST | `/api/recycle/exchanges/{id}/restore` | 恢复置换 |
| DELETE | `/api/recycle/items/{id}` | 永久删除藏品 |
| DELETE | `/api/recycle/exchanges/{id}` | 永久删除置换 |

### 图片上传 `/api/uploads`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/uploads` | 上传图片（支持 jpg/jpeg/png/gif/webp），返回文件路径 |

## 业务规则

- **稀有度**: 常规 / 隐藏 / 限定
- **状态**: 在库 / 已出 / 置换中
- **置换流转**: 洽谈中 / 已成交 / 已撤回
- **行情平台**: 闲鱼 / 千岛 / 线下
- **获取方式**: 盲盒 / 直购 / 置换
- **隐藏款批次号**: 当 rarity=隐藏 时，batch_no 为必填，格式为 `两位字母+六位数字-两位数字`（如 `AB202601-01`）
- **软删除**: 删除操作仅设置 `deleted_at` 时间戳，回收站可恢复或永久删除
- **图片存储**: 上传至本地 `uploads/` 目录，通过 `/uploads/{filename}` 访问

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vue Router + Axios + ECharts + Vite |
| 后端 | FastAPI + SQLAlchemy + Pydantic v2 |
| 数据库 | SQLite |
| 部署 | Docker Compose + Nginx |

## 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```
