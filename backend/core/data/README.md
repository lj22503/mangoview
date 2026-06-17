# 数据获取层（Data Layer）v2.0

> **原则：数据问题在这里一次性解决，所有项目共用，不跟项目走。**

## 架构

```
data-layer/
├── __init__.py        ← 统一导出
├── data_api.py        ← 统一入口（大盘/个股/财报/北向/宏观/新闻）
├── fund_api.py        ← 基金专用入口（估值/详情/业绩/持仓/配置）
├── models.py          ← 数据模型（Quote/Financials/FundProfile）
├── cache.py           ← 两层缓存（内存+文件）
├── config.py          ← 配置管理（config.yaml + .env）
├── exceptions.py      ← 统一异常
├── providers/         ← 数据源适配器
│   ├── tencent.py     ← 腾讯财经（大盘指数实时）
│   ├── sina.py        ← 新浪财经（个股/指数实时）
│   ├── eastmoney.py   ← 东方财富（个股行情+财报）
│   ├── fund_eastmoney.py ← 天天基金（基金全量数据）
│   ├── tushare_api.py ← Tushare（日线/涨跌停/北向资金）
│   ├── qveris.py      ← QVeris（北向/宏观/行业资金流向）
│   └── searxng.py     ← SearXNG（新闻/政策搜索）
├── cache/             ← 文件缓存目录
├── tests/             ← 测试
└── logs/              ← 调用日志
```

## 快速开始

```python
from data_layer import DataAPI, FundAPI

# === 股票/大盘 ===
api = DataAPI()
indices = api.get_indices()                          # 大盘指数
quote = api.get_quote('600519.SH')                   # 个股行情（Quote 对象）
fin = api.get_financials('600519.SH')                # 财报（Financials 对象）
north = api.get_northbound()                         # 北向资金
macro = api.get_macro('gdp')                         # 宏观数据
news = api.search_news('央行 利率')                   # 新闻搜索

# === 基金 ===
fund = FundAPI()
gz = fund.get_estimated_nav('005827')                # 盘中估值
detail = fund.get_detail('005827')                   # 基金详情
perf = fund.get_performance('005827')                # 阶段收益+排名
nav = fund.get_nav_history('005827', page_size=30)   # 历史净值
holdings = fund.get_holdings('005827')               # 重仓股
alloc = fund.get_asset_allocation('005827')          # 资产配置
results = fund.search('沪深300')                     # 搜索基金
profile = fund.get_full_profile('005827')            # 一键完整档案
```

## 数据源清单

| 数据源 | 覆盖数据 | 认证 | 状态 |
|--------|---------|------|------|
| 腾讯财经 | 大盘指数实时 | 无需 | ✅ |
| 新浪财经 | 个股/指数实时 | 无需 | ✅ |
| 东方财富 | 个股行情+财报 | 无需 | ✅ |
| 天天基金 | 基金估值/详情/业绩/持仓/配置 | 无需 | ✅ |
| Tushare | 日线/涨跌停/北向资金 | Token | ✅ |
| QVeris | 北向/宏观/行业资金流向 | API Key | ✅ |
| SearXNG | 新闻/政策搜索 | 无需（本地） | ✅ |

## 降级策略

```
个股行情：新浪 → 东方财富
财报数据：东方财富
北向资金：Tushare → QVeris
大盘指数：腾讯财经
基金数据：天天基金
```

## 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 大盘指数 | 不缓存 | 实时 |
| 个股行情 | 5 分钟 | |
| 财报 | 1 小时 | |
| 基金估值 | 1 分钟 | 盘中频繁变化 |
| 基金详情 | 1 小时 | |
| 基金业绩 | 30 分钟 | |
| 基金持仓/配置 | 1 天 | 季度更新 |
| 北向资金 | 1 天 | |
| 宏观数据 | 7 天 | |
| 新闻 | 不缓存 | |

## 环境变量（.env）

```
TUSHARE_TOKEN=xxx
QVERIS_API_KEY=xxx
```

## 版本历史

- **v2.0**（2026-03-25）：整合 data_fetcher，新增 sina/eastmoney/fund 数据源，统一缓存/配置/异常
- **v1.0**（2026-03-20）：初版，tencent/tushare/qveris/searxng
