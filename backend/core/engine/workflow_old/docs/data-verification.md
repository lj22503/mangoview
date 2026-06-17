# 数据验证层设计文档

**版本**：v0.2.0  
**创建时间**：2026-05-06  
**状态**：✅ 已完成（基于 data_layer 架构）  
**负责人**：燃冰 & ant

---

## 一、设计目标

### 核心理念
**Every number is verifiable**（每个数据都可追溯）

### 设计原则
1. **复用 data_layer 架构**：统一数据接口，继承降级链
2. **信源等级标注**：每个数据标注信源等级（S/A/B/C）
3. **时效性检查**：自动检查数据是否过期
4. **缓存机制**：复用 data_layer 的缓存管理

---

## 二、信源等级体系

| 等级 | 标识 | 来源类型 | 使用方式 |
|------|------|---------|---------|
| **S** | 🟢 | 官方文档、监管机构、且慢 MCP | 直接引用 |
| **A** | 🟡 | 权威数据源（东方财富/同花顺/财联社） | 交叉验证后使用 |
| **B** | 🟠 | 技术社区、自媒体、AKShare | 多源印证或标注不确定性 |
| **C** | 🔴 | 模拟数据、单一来源爆料 | 仅作线索，标注「待核实」 |

---

## 三、数据源配置

### 已接入数据源（基于 data_layer）

| 数据源 | 信源等级 | 缓存时间 | 状态 |
|--------|---------|---------|------|
| **腾讯财经** | A | 实时 | ✅ 已接入 |
| **新浪财经** | A | 实时 | ✅ 已接入 |
| **东方财富** | A | 5 分钟 | ✅ 已接入 |
| **AKShare** | B | 30 分钟 | ✅ 已接入 |
| **且慢 MCP** | S | 1 小时 | ⏳ 待接入 |
| **Tushare** | B | 1 天 | ✅ 已接入 |
| **QVeris** | S | 7 天 | ✅ 已接入 |

### 数据源 API 配置（基于 data_layer）

```python
from src.verifier import create_verifier

verifier = create_verifier()

# 获取大盘指数
market_data = verifier.get_market_data("A 股")

# 获取个股行情
stock_data = verifier.get_stock_data("600519.SH")

# 获取基金数据
fund_data = verifier.get_fund_data("518880")

# 获取财报数据
financials = verifier.get_financials("600519.SH")
```

---

## 四、数据验证流程（基于 data_layer）

```
用户请求
    ↓
DataVerifier（数据验证层）
    ↓
DataAPI（统一数据接口）
    ↓
降级链：腾讯 → 新浪 → 东方财富
    ↓
CacheManager（缓存管理）
    ↓
1. 检测数据源
2. 获取信源等级
3. 检查时效性
4. 添加验证元数据
    ↓
返回验证后的数据
```

### 验证元数据

每个验证后的数据都包含以下元数据：

```json
{
  "verified": true,
  "verify_time": "2026-05-06T13:38:59.741143",
  "data_source": "东方财富",
  "confidence_level": "A",
  "is_fresh": true,
  "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
}
```

---

## 五、降级策略（基于 data_layer）

### API 失败时的降级路径

```
DataAPI 调用
    ↓ 失败
CacheManager（缓存数据）
    ↓ 无缓存
模拟数据（标注 C 级）
```

### 降级示例（data_layer 内置）

```python
# data_layer 内置降级链
providers = [
    ('tencent', self._get_quote_tencent),
    ('eastmoney', self._get_quote_eastmoney),
    ('sina', self._get_quote_sina),
]

for name, fn in providers:
    try:
        data = fn(symbol)
        self._cache.set(cache_key, data, ttl=300)
        return Quote.from_dict(data)
    except Exception as e:
        last_error = e
        continue
```

---

## 六、使用示例（基于 data_layer）

### 示例 1：获取市场数据

```python
from src.verifier import create_verifier

verifier = create_verifier()

# 获取 A 股市场数据
market_data = verifier.get_market_data("A 股")

print(f"上证指数：{market_data['上证指数']['current']}")
print(f"信源等级：{market_data['confidence_level']}")
print(f"时效性：{market_data['is_fresh']}")
```

### 示例 2：获取个股数据

```python
# 获取贵州茅台数据
stock_data = verifier.get_stock_data("600519.SH")

print(f"代码：{stock_data['symbol']}")
print(f"当前价：{stock_data['price']}")
print(f"涨跌幅：{stock_data['change_percent']}%")
print(f"信源等级：{stock_data['confidence_level']}")
```

### 示例 3：获取基金数据

```python
# 获取黄金 ETF 数据
fund_data = verifier.get_fund_data("518880")

print(f"代码：{fund_data['fund_code']}")
print(f"净值：{fund_data['nav']}")
print(f"信源等级：{fund_data['confidence_level']}")
```

### 示例 4：获取财报数据

```python
# 获取贵州茅台财报
financials = verifier.get_financials("600519.SH")

print(f"代码：{financials['symbol']}")
print(f"营收：{financials['revenue']}")
print(f"净利润：{financials['net_profit']}")
print(f"ROE：{financials['roe']}")
```

---

## 七、测试报告

### 测试环境
- 时间：2026-05-06 13:45
- 服务器：阿里云（iZuf6eegzkdecz06p2dapkZ）
- Python：3.8+
- data_layer：v2.2.0

### 测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| data_layer 集成 | ✅ 通过 | 成功复用统一数据接口 |
| 降级链测试 | ✅ 通过 | 腾讯 → 新浪 → 东方财富 |
| 信源等级标注 | ✅ 通过 | 所有数据正确标注等级 |
| 时效性检查 | ✅ 通过 | 正确判断数据新鲜度 |
| 缓存机制 | ✅ 通过 | 复用 data_layer 缓存 |

### 降级测试

| 场景 | 预期 | 实际 | 结果 |
|------|------|------|------|
| API 连接失败 | 返回缓存/模拟数据 | 返回缓存/模拟数据 | ✅ |
| 缓存命中 | 返回缓存数据 | 返回缓存数据 | ✅ |
| 信源等级 | 正确标注 S/A/B/C | 正确标注 S/A/B/C | ✅ |

---

## 八、下一步计划

| 日期 | 任务 | 负责人 | 产出 |
|------|------|--------|------|
| 5/7 | 完整工作流测试 | ant + 燃冰 | 测试报告 |
| 5/7 | 且慢 MCP 接入（基金数据） | ant | 扩展 data_layer |
| 5/8 | 性能优化 | ant | 缓存命中率提升 |
| 5/8 | 文档完善 | ant | API 文档 |

---

**创建时间**：2026-05-06  
**版本**：v0.1.0  
**状态**：🚧 开发中  
**下一步**：接入且慢 MCP API
