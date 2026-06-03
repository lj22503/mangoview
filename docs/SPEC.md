# MangoView 技术规格说明书

> **版本**: v2.0.0  
> **日期**: 2026-06-03  
> **状态**: 草案（独立项目）  
> **负责人**: 燃冰 + ant  
> **项目路径**: `/home/admin/.openclaw/workspace/projects/mangoview`  

---

## 一、产品概述

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| **产品名** | MangoView |
| **域名** | view.mangofolio.com |
| **Slogan** | 自上而下，看清每一笔投资 |
| **品牌线** | Mangofolio 系列（投资工具矩阵） |
| **定位** | 基于经典框架的 SaaS 投资辅助工具 |
| **目标用户** | 个人投资者（3-5 年经验，有体系化需求） |

### 1.2 核心逻辑

**自上而下（Top-Down）**：宏观周期定位 → 行业周期定位 → 寻找机会

- **数据层**：提供客观数据（宏观/行业/事件），不做主观判断
- **工具层**：将经典投资框架（格雷厄姆/巴菲特/达利欧等）外化为可复用的工具
- **配置层**：基于用户画像 + 数据层 + 工具集，通过"黑盒引擎"输出个性化配置方案

### 1.3 产品边界

| 是 | 不是 |
|----|------|
| 数据 + 工具 + 框架的 SaaS 平台 | 直接提供买卖建议的投顾平台 |
| 帮助用户建立自己的投资体系 | 单纯的数据堆砌 |
| 提供分析方法和决策辅助 | 保证收益的投资产品 |

---

## 二、技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                     │
│  Next.js + Tailwind CSS + Recharts/ECharts              │
├─────────────────────────────────────────────────────────┤
│                    API 网关 (Gateway)                    │
│  Next.js API Routes                                     │
│  - 认证鉴权  - 限流  - 日志  - 缓存                      │
├─────────────────────────────────────────────────────────┤
│                  业务逻辑层 (Service)                    │
│  Python (FastAPI)                                       │
│  - 数据处理  - 工具计算  - 配置推演  - 报告生成          │
├─────────────────────────────────────────────────────────┤
│                  数据层 (Data Layer)                     │
│  - 外部 API 自动采集（东方财富/新浪财经/国家统计局）     │
│  - Redis 缓存（行情 1 天/宏观 7 天）                    │
│  - SQLite/PostgreSQL（用户配置/机会追踪）                │
├─────────────────────────────────────────────────────────┤
│                  基础设施 (Infra)                        │
│  - 阿里云服务器                                         │
│  - Cloudflare Tunnel (域名解析)                         │
│  - GitHub (代码托管)                                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选型

| 层级 | 技术 | 理由 |
|------|------|------|
| **前端** | Next.js 14 + React 18 | SSR/SSG 支持，SEO 友好 |
| **样式** | Tailwind CSS + shadcn/ui | 快速开发，组件丰富 |
| **图表** | Recharts / ECharts | 金融图表支持好 |
| **API** | Next.js API Routes | 与前端同构，部署简单 |
| **后端** | Python (FastAPI) | 数据处理/ML 生态好 |
| **数据库** | SQLite/PostgreSQL | 结构化数据（用户配置/机会追踪） |
| **数据源** | 东方财富/新浪财经/国家统计局 API | 自动采集宏观/行业/行情数据 |
| **缓存** | Redis | 高性能，支持过期策略（行情 1 天/宏观 7 天） |
| **部署** | 阿里云 + PM2 | 已有服务器，成本低 |

### 2.3 项目结构

```
mangoview/
├── docs/                      # 文档
│   ├── SPEC.md               # 技术规格
│   ├── DESIGN.md             # 设计规范
│   └── DATA_TEST_REPORT.md   # 数据测试报告
├── frontend/                  # 前端项目（Next.js 14）
│   ├── src/
│   │   ├── app/              # App Router
│   │   │   ├── page.tsx      # 首页
│   │   │   ├── market/       # 市场看版
│   │   │   ├── tools/        # 工具集
│   │   │   ├── portfolio/    # 配置中心
│   │   │   └── reports/      # 扫描报告
│   │   ├── components/       # 公共组件
│   │   └── lib/              # 工具函数
│   └── package.json
├── backend/                   # 后端项目（FastAPI）
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── api/              # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── models/           # 数据模型
│   │   └── utils/            # 工具函数
│   └── scripts/              # 数据采集脚本
├── data/                      # 数据（SQLite）
└── README.md
```

---

## 三、功能模块详述

### 3.1 📊 市场看版（Market Dashboard）

**URL**: `/market`

**功能**: 提供宏观数据、行业四象限、边际变化，帮助用户"看清市场位置"。

#### 3.1.1 顶部定调

- **内容**: 宏观数据快照（9 维度表格）
- **字段**: GDP/CPI/PMI/社融/PPI/工业利润/固定资产投资/新开工面积/M2
- **展示**: 当前值 | 上期值 | 方向 | 历史分位 | 数据日期 | 来源
- **更新**: 月度（15-20 日）

#### 3.1.2 Tab 1: 周期定位

- **内容**: 四周期嵌套数据表（基钦/朱格拉/库兹涅茨/康波）
- **展示**: 最新数据 + 历史对照 + 当前状态
- **原则**: 只展示数据，不做主观判断（不显示"向上/向下"）

#### 3.1.3 Tab 2: 行业大图

- **四象限矩阵**: 估值分位（X 轴）vs 净利润增速（Y 轴），气泡大小=权重，颜色=周期阶段
- **数据表格**: 行业 | 周期阶段 | 渗透率 | CR3 | PE 分位 | 净利润增速
- **行业秩**: 降秩拆解（核心生成器 + 行业性质 + 跟踪要点）

#### 3.1.4 Tab 3: 机会扫描

- **边际变化**: 闸门/管道/背离事件追踪（三把尺子评分）
- **综合看板**: 跨模块联动（周期底部 + 估值低位 + 边际改善）

**转化钩子**: 🔒 历史市场印证 + 深入洞察 → [加入星球解锁]

---

### 3.2 🛠️ 工具集（Tools）

**URL**: `/tools`

**功能**: 独立分析工具，帮助用户"掌握分析方法"。

#### 3.2.1 工具分类

| 分类 | 工具 | 状态 |
|------|------|------|
| 宏观周期 | 周期定位器 (cycle-locator) | ✅ 免费 |
| 行业分析 | 行业分析仪 (industry-analyst) | ✅ 免费 |
| 行业分析 | 行业专家 (industry-specialist) | 🔒 锁定 |
| 微观选股 | 价值评估器 (value-analyzer) | ✅ 免费 |
| 微观选股 | 护城河评估 (moat-evaluator) | ✅ 免费 |
| 资产配置 | 资产配置器 (asset-allocator) | ✅ 免费 |
| 行为纪律 | 决策清单 (decision-checklist) | ✅ 免费 |
| 行为纪律 | 偏差检测 (bias-detector) | 🔒 锁定 |
| 高级工具 | 降秩引擎 (rank-derangement) | 🔒 锁定 |
| 高级工具 | 事件研判器 (event-analyzer) | 🔒 锁定 |
| 高级工具 | 回测工具 (backtester) | 🔒 锁定 |

#### 3.2.2 工具卡片示例（周期定位器）

```
┌─────────────────────────────────────────┐
│  📐 周期定位器                           │
│  框架：基钦/朱格拉/库兹涅茨/康波 四周期嵌套│
│  ─────────────────────────────────────  │
│  📥 输入：PMI / PPI / 固定资产投资 / 新开工│
│  📤 输出：当前周期定位 + 历史对照 + 配置建议│
│  [立即使用]                              │
└─────────────────────────────────────────┘
```

**转化钩子**: 🔒 高级工具（降秩/回测） → [加入星球解锁]

---

### 3.3 💰 配置中心（Portfolio）

**URL**: `/portfolio`

**功能**: 个性化推演，帮助用户"获得专属方案"。

#### 3.3.1 用户画像输入

```
┌─────────────────────────────────────────┐
│  风险偏好：[保守] [平衡] [积极]          │
│  投资期限：[1-3 年] [3-5 年] [5 年以上]  │
│  可投资金：[100 万]                      │
│  熟悉行业：[消费] [科技] [医药] [金融]   │
│  [输入参数，启动引擎]                    │
└─────────────────────────────────────────┘
```

#### 3.3.2 引擎推演（黑盒）

**展示逻辑**: 展示"推演过程"（怎么算的），锁定"具体结果"（算出什么）。

| Tab | 名称 | 工具 | 内容 |
|-----|------|------|------|
| Tab 1 | 战略配置 | asset-allocator + cycle-locator | 大类资产配置比例 |
| Tab 2 | 战术配置 | value-analyzer + moat-evaluator | 行业/标的选择 |
| Tab 3 | 机会追踪 | second-level-thinker + future-forecaster | 机会评分与触发 |
| Tab 4 | 纪律检查 | decision-checklist + bias-detector | 资金隔离与违规预警 |

**转化钩子**: 🌟 加入知识星球，解锁您的个性化配置方案。

---

### 3.4 📰 扫描报告（Reports）

**URL**: `/reports`

**功能**: 定期扫描服务，帮助用户"省时省力"。

| 频率 | 时间 | 内容 |
|------|------|------|
| 每日 | 交易日 09:00/15:30 | 大盘情绪 + 资金流向 + 关键信号 |
| 每周 | 周一 10:00 | 行业轮动 + 政策跟踪 + 配置建议 |
| 每月 | 月末 | 组合表现 + 持仓检查 + 调仓建议 |

**展示**: 摘要免费可见，完整版深度解读锁定。

**转化钩子**: 🔒 完整报告 + 实时推送 + 历史归档 → [加入星球解锁]

---

### 3.5 📖 说明（About）

**URL**: `/about`

**功能**: 框架说明、数据源、合规声明。

**内容**:
- 投资框架说明（自上而下方法论）
- 数据源说明（东方财富/新浪财经/国家统计局）
- 工具使用指南
- 合规声明
- 知识星球介绍

---

## 四、API 设计

### 4.1 数据层 API

#### 4.1.1 获取宏观数据

```http
GET /api/v1/market/macro
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "indicators": [
      {
        "name": "PMI",
        "current": 50.8,
        "previous": 50.2,
        "direction": "up",
        "percentile": 65.2,
        "date": "2026-05-31",
        "source": "国家统计局"
      }
    ],
    "updated_at": "2026-06-01T10:00:00Z"
  }
}
```

#### 4.1.2 获取行业数据

```http
GET /api/v1/market/industries
```

**查询参数**:
- `quadrant`: 象限筛选（low_val_high_growth / low_val_low_growth / high_val_high_growth / high_val_low_growth）
- `cycle_stage`: 周期阶段筛选

**响应**:
```json
{
  "code": 0,
  "data": {
    "industries": [
      {
        "code": "CI001",
        "name": "消费",
        "cycle_stage": "复苏早期",
        "penetration": 0.75,
        "cr3": 0.42,
        "pe_percentile": 28.5,
        "net_profit_growth": 12.3,
        "weight": 0.15
      }
    ],
    "updated_at": "2026-06-01T10:00:00Z"
  }
}
```

#### 4.1.3 获取机会扫描

```http
GET /api/v1/market/opportunities
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "opportunities": [
      {
        "id": "OPP001",
        "name": "消费复苏",
        "score": 22,
        "trigger_level": "二级",
        "conditions": "周期底部 + 估值低位 + 边际改善",
        "suggested_position": 0.15,
        "status": "active"
      }
    ],
    "updated_at": "2026-06-01T10:00:00Z"
  }
}
```

### 4.2 工具 API

#### 4.2.1 周期定位

```http
POST /api/v1/tools/cycle-locator
```

**请求体**:
```json
{
  "indicators": {
    "pmi": 50.8,
    "ppi": -2.1,
    "fixed_asset_investment": 4.0,
    "new_start_area": -10.5
  }
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "cycle_position": {
      "kitchin": "复苏早期",
      "juglar": "衰退后期",
      "kuznets": "萧条期",
      "kondratieff": "萧条期"
    },
    "historical_comparison": [
      {"period": "2012-2013", "similarity": 0.78},
      {"period": "2015-2016", "similarity": 0.65}
    ],
    "allocation_suggestion": {
      "equity": "适度",
      "bond": "优先",
      "gold": "适度",
      "cash": "回避"
    }
  }
}
```

### 4.3 配置中心 API

#### 4.3.1 生成配置方案

```http
POST /api/v1/portfolio/generate
```

**请求体**:
```json
{
  "risk_profile": "balanced",
  "time_horizon": "3-5 年",
  "investable_amount": 1000000,
  "familiar_industries": ["消费", "科技"]
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "strategy": {
      "logic": "当前宏观处于复苏早期，结合您的平衡型偏好...",
      "allocation": {
        "equity": { "locked": true },
        "bond": { "locked": true },
        "gold": { "locked": true }
      }
    },
    "tactics": {
      "logic": "基于估值分位<30% + 股息率>4%，结合您熟悉的消费/科技...",
      "targets": { "locked": true }
    },
    "requires_subscription": true
  }
}
```

### 4.4 报告 API

#### 4.4.1 获取报告列表

```http
GET /api/v1/reports?type=daily|weekly|monthly&page=1&limit=10
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "reports": [
      {
        "id": "RPT001",
        "type": "daily",
        "date": "2026-06-03",
        "title": "2026-06-03 早盘扫描",
        "summary": "大盘情绪中性偏多，北向资金净流入...",
        "is_locked": false
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 10
  }
}
```

---

## 五、数据结构设计

### 5.1 数据源架构

```
外部 API（东方财富/新浪财经/国家统计局）
  ↓
data layer（自动采集 + 清洗 + 缓存）
  ↓
本地数据库（SQLite/PostgreSQL）
  ↓
后端 API（直接读取）
  ↓
前端展示
```

### 5.2 数据库表设计

| 表名称 | 对应步骤 | 主键 | 更新方式 |
|--------|---------|------|---------|
| macro_indicators | 第一步 | id | 自动采集（月度） |
| industry_info | 第二步 | industry_code | 自动采集（年度） |
| industry_financials | 第二步 | (industry_code, year, quarter) | 自动采集（季度） |
| industry_valuation | 第二步 | (industry_code, date) | 自动采集（月度） |
| strategic_allocation | 第三步 | asset_class | 手动配置（年度） |
| tactical_holdings | 第三步 | industry_code | 自动采集（季度） |
| opportunities | 第四步 | id | 自动采集（每周） |
| discipline_checks | 第五步 | check_date | 自动采集（每周） |
| user_profiles | 独立 | user_id | 用户输入（动态） |

### 5.3 核心字段设计

#### macro_indicators（经济周期指标表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| indicator_name | TEXT | 基钦/朱格拉/库兹涅茨/康波 |
| indicator_code | TEXT | PMI/PPI/固定资产投资/新开工面积 |
| current_value | REAL | 最新数据 |
| previous_value | REAL | 上期数据 |
| direction | TEXT | up/down/flat |
| historical_percentile | REAL | 0-100 |
| data_date | DATE | 数据所属日期 |
| source | TEXT | 国家统计局/央行等 |
| updated_at | TIMESTAMP | 更新时间 |

#### industry_valuation（行业估值 - 股息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| industry_code | TEXT | 主键 |
| stat_date | DATE | 主键 |
| pe_ttm | REAL | 市盈率 |
| pe_percentile | REAL | 历史分位 |
| pb_lf | REAL | 市净率 |
| pb_percentile | REAL | 历史分位 |
| dividend_yield | REAL | 年化股息率 |
| dividend_percentile | REAL | 历史分位 |
| quadrant | TEXT | 估值 - 股息象限 |
| updated_at | TIMESTAMP | 更新时间 |

#### opportunities（机会追踪表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 机会描述 |
| score | INTEGER | 0-25 |
| trigger_level | TEXT | none/level1/level2/level3 |
| conditions | TEXT | 触发逻辑 |
| suggested_position | REAL | 0-1 |
| tools_used | TEXT | 使用的工具 |
| status | TEXT | active/expired/watching |
| updated_at | TIMESTAMP | 更新时间 |

### 5.4 数据更新日历

| 频率 | 日期 | 更新内容 | 负责表 | 数据源 |
|------|------|---------|--------|--------|
| 每月 | 15-20 日 | PMI/PPI/CPI/工业利润 | macro_indicators | 国家统计局 API |
| 每月 | 月末 | 估值 - 股息数据 | industry_valuation | 东方财富 API |
| 每周 | 周一 | 纪律检查 | discipline_checks | 自动计算 |
| 每季度 | 4/8/10 月末 | 行业财务指标 | industry_financials | 东方财富 API |
| 年度 | 12 月 | 战略层再平衡 | strategic_allocation | 手动配置 |

---

## 六、合规设计

### 6.1 合规底线

1. **页面声明**: 顶部固定显示
   > 本平台仅提供投资框架与数据参考，不构成任何投资建议。市场有风险，投资需谨慎。请独立判断并自行承担风险。

2. **去观点化**: 所有分析标注"基于框架逻辑推演"，不出现"强烈建议买入/卖出"等主观表述。

3. **黑盒化**: 配置中心的具体结果（比例/标的）对免费用户锁定，避免直接输出投资建议。

### 6.2 数据合规

1. **数据来源标注**: 所有数据标注来源和时间。
2. **缓存策略**: 宏观数据缓存 7 天，行情数据缓存 1 天，避免重复调用。
3. **用户数据**: 不存储用户敏感信息（身份证号/银行卡号等）。

---

## 七、变现设计

### 7.1 免费用户

- 查看市场数据（宏观/行业/机会）
- 使用基础工具（周期定位/行业分析/价值评估/资产配置/决策清单）
- 查看报告摘要

### 7.2 星球用户（付费）

- 解锁全部高级工具（降秩/回测/事件研判/偏差检测）
- 解锁个性化配置方案（比例/标的/分批计划）
- 解锁完整报告 + 实时推送
- AI 分析额度（100 次/月）

### 7.3 转化路径

```
免费用户 → 使用工具/查看数据 → 看到锁定内容 → 微信扫码加入星球 → 获取专属账号 → 解锁全部功能
```

---

## 八、开发计划

### 8.1 Phase 1: 基础设施（3 天）

| 任务 | 交付物 | 负责人 |
|------|--------|--------|
| 开发 data layer | 自动采集脚本（akshare/tushare） | ant |
| 搭建本地数据库 | SQLite 9 张表结构 + 历史数据导入 | ant |
| 项目初始化 | 前端/后端项目结构 | ant |

### 8.2 Phase 2: 核心功能（5 天）

| 任务 | 交付物 | 负责人 |
|------|--------|--------|
| 市场看版 | 页面 + 数据展示 | 开发团队 |
| 工具集 | 基础工具实现 | 开发团队 |
| 配置中心 | 用户画像 + 推演引擎 | 开发团队 |

### 8.3 Phase 3: 测试 + 部署（4 天）

| 任务 | 交付物 | 负责人 |
|------|--------|--------|
| 测试 | 测试报告 + 修复 | 燃冰 + ant |
| 文档 | 使用指南 + 合规声明 | ant |
| 部署 | 生产环境（Cloudflare Tunnel） | ant |

**总时间线**：2 周（12 个工作日）  
**MVP 上线目标**：2026-06-17

---

## 九、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 合规风险 | 被认定为投顾平台 | 严格去观点化，黑盒化配置结果 |
| 数据风险 | 数据延迟/错误 | 多源校验，缓存策略，及时更新 |
| 技术风险 | 服务器宕机 | PM2 自动重启，Cloudflare Tunnel 备份 |
| 用户风险 | 用户流失 | 持续迭代，增加价值，社群运营 |

---

## 十、附录

### 10.1 参考文档

- [产品方案](./INVESTMENT_DASHBOARD_PLAN_V1.md)
- [投资框架教程](https://github.com/lj22503/investment-framework-skill)
- [东方财富 API 文档](https://push2his.eastmoney.com/api/qt/stock/kline/get)
- [新浪财经 API 文档](http://hq.sinajs.cn/list)

### 10.2 术语表

| 术语 | 说明 |
|------|------|
| 自上而下 | Top-Down，从宏观到微观的投资方法论 |
| 四周期嵌套 | 基钦/朱格拉/库兹涅茨/康波 |
| 降秩 | 从宏观周期推导行业配置的方法 |
| 黑盒 | 展示逻辑，锁定结果 |
| 知识星球 | 付费社群，变现渠道 |

---

*本文档由 ant 基于与燃冰的讨论整理生成。*  
*最后更新：2026-06-03 08:05*
