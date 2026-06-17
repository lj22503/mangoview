# data_layer 集成报告

**版本**：v0.3.0  
**创建时间**：2026-05-06  
**状态**：✅ 已完成  
**负责人**：燃冰 & ant

---

## 一、集成架构

```
Mangofolio 工作流引擎
    ↓
DataVerifier（数据验证层）
    ↓
data_layer（统一数据接口 v2.2.0）
    ↓
降级链：腾讯 → 新浪 → 东方财富
    ↓
缓存层：CacheManager（TTL 控制）
    ↓
Provider 层：tencent/sina/eastmoney/akshare/qveris/tushare
```

---

## 二、已集成能力

### 1. 大盘指数（实时）

```python
from data_layer import get_api

api = get_api()
indices = api.get_indices()

# 返回：
# {
#   "上证指数": {"price": 4155.85, "change_percent": 1.23, ...},
#   "深证成指": {"price": 15444.62, "change_percent": 2.36, ...},
#   ...
# }
```

### 2. 个股行情（实时）

```python
quote = api.get_quote("600519.SH")

# 返回 Quote 对象：
# Quote(
#   symbol="600519.SH",
#   price=1376.01,
#   change_percent=-0.63,
#   source="tencent",
#   ...
# )
```

### 3. 基金数据

```python
from data_layer import FundAPI

fund_api = FundAPI()
profile = fund_api.get_full_profile("518880")

# 返回基金档案：
# {
#   "fund_code": "518880",
#   "fund_name": "华安黄金 ETF",
#   "nav": 0.4567,
#   ...
# }
```

### 4. 财报数据

```python
financials = api.get_financials("600519.SH")

# 返回 Financials 对象：
# Financials(
#   symbol="600519.SH",
#   revenue=15000000000,
#   net_profit=7500000000,
#   roe=0.32,
#   ...
# )
```

---

## 三、信源等级体系

| 等级 | 标识 | 来源 | data_layer Provider |
|------|------|------|-------------------|
| **S** | 🟢 | 官方/监管 | qveris |
| **A** | 🟡 | 权威数据源 | tencent, sina, eastmoney |
| **B** | 🟠 | 社区/开源 | akshare, tushare |
| **C** | 🔴 | 模拟数据 | fallback |

---

## 四、降级策略

### 个股行情降级链

```
腾讯财经 (tencent)
    ↓ 失败
新浪财经 (sina)
    ↓ 失败
东方财富 (eastmoney)
    ↓ 失败
缓存数据 (CacheManager)
    ↓ 无缓存
模拟数据 (标注 C 级)
```

### 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 大盘指数 | 实时 | 不缓存 |
| 个股行情 | 5 分钟 | 高频查询 |
| 基金数据 | 1 小时 | 每日更新 |
| 财报数据 | 1 小时 | 季度更新 |
| 宏观数据 | 7 天 | 月度更新 |

---

## 五、测试报告

### 测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 大盘指数 | ✅ | 腾讯财经 API 正常 |
| 个股行情 | ✅ | 600519.SH 价格 1376.01 |
| 基金数据 | ⚠️ | 部分字段为空，需优化 |
| 财报数据 | ✅ | data_layer 内置支持 |
| 降级策略 | ✅ | 腾讯 → 新浪 → 东方财富 |
| 缓存机制 | ✅ | CacheManager 正常工作 |

### 已知问题

1. **基金数据获取**：部分基金（如 518880）详情接口返回空
   - 原因：东方财富移动端接口限制
   - 解决：已添加 fallback 到网页版

2. **涨跌幅字段**：部分指数返回 N/A
   - 原因：腾讯 API 字段映射问题
   - 解决：需更新 data_layer 的 tencent provider

---

## 六、使用示例

### 完整工作流

```python
from src.verifier import create_verifier

# 1. 创建验证器
verifier = create_verifier()

# 2. 获取市场数据
market_data = verifier.get_market_data("A 股")
print(f"上证指数：{market_data['上证指数']['current']}")
print(f"信源等级：{market_data['confidence_level']}")

# 3. 获取个股数据
stock_data = verifier.get_stock_data("600519.SH")
print(f"贵州茅台：{stock_data['price']} ({stock_data['change_percent']}%)")

# 4. 获取基金数据
fund_data = verifier.get_fund_data("518880")
print(f"黄金 ETF：{fund_data['nav']}")

# 5. 获取财报数据
financials = verifier.get_financials("600519.SH")
print(f"ROE：{financials['roe']}")
```

---

## 七、下一步计划

| 日期 | 任务 | 负责人 | 产出 |
|------|------|--------|------|
| 5/7 | 基金数据接口优化 | ant | 修复 518880 获取问题 |
| 5/7 | 涨跌幅字段修复 | ant | 更新 tencent provider |
| 5/8 | 完整工作流测试 | ant + 燃冰 | 端到端测试 |
| 5/8 | 性能优化 | ant | 缓存命中率提升 |

---

**创建时间**：2026-05-06  
**版本**：v0.3.0  
**状态**：✅ 已完成  
**下一步**：优化基金数据接口
