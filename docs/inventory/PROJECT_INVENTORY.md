# Mangofolio 项目清单总览

> 最后更新：2026-06-10（自进化框架补充）

---

## 一、品牌架构

**Mangofolio** = 理财师 AI 工作台（B端）+ 投资者认知入口（C端）+ 超级系统站

```
Mangofolio 品牌
├── 个人版（C端）    ← investment-assistant + SaaS 可视化界面
├── 投顾版（B端）    ← mangofolio B端工作台
└── 超级系统站      ← 知识系统 + 通用能力系统 + 数据系统 + 分析引擎
```

**定位对标**：Vanguard（先锋领航）
- 个人版：个人投资者的"第二大脑"
- 投顾版：理财师/投顾的专业工作台
- 超级系统站：底层能力中枢，可被内外调用

---

## 二、系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│ 超级系统站 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  知识系统   │  │ 通用能力系统 │  │  数据系统   │  │  分析引擎   │ │
│  │             │  │             │  │             │  │             │ │
│  │ 大师思想库 │  │ risk-assess │  │ 宏观数据   │  │ 六步流程   │ │
│  │ 行业知识   │  │ sentiment   │  │ 市场数据   │  │ Skill包 │ │
│  │ 估值体系   │  │ bias-detect │  │ 基金数据   │  │ 七层架构   │ │
│  │ 周期模型   │  │ decision    │  │            │  │            │ │
│ └─────────────┘  └─────────────┘ └─────────────┘  └─────────────┘ │
│                                                                     │
│  API接口 ← 被调用 │
└─────────────────────────────────────────────────────────────────────┘
           ↑ 被调用              ↑ 被调用              ↑ 被调用
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │   个人版     │      │   投顾版     │      │   超级站 │
    │  (assistant) │      │ (mangofolio) │      │ (mangoview)  │
    │              │      │      B端     │      │    前端     │
    │ ┌────────┐ │ │  ┌────────┐ │      │  ┌────────┐ │
    │  │ 前端   │ │      │  │ 工作台 │ │      │  │ 数据 │ │
    │  │ 界面   │ │      │  │ 界面   │ │      │  │ 展示   │ │
    │└────────┘ │      │  └────────┘ │      │  └────────┘ │
    │ ┌────────┐ │      │  ┌────────┐ │      │  ┌────────┐ │
    │  │ 对话   │ │      │  │ CRM/   │ │      │  │ 引流 │ │
    │  │ 界面   │ │      │  │ 合规等 │ │      │  │ 介绍   │ │
    │  └────────┘ │      │  └────────┘ │      │  └────────┘ │
    │  ┌────────┐ │      │  ┌────────┐ │      │            │
    │  │记忆   │ │      │  │ 记忆   │ │      │            │
    │  │ 系统   │ │      │  │ 系统   │ │      │            │
    │  │(场景化)│ │      │  │(场景化)│ │      │            │
    │  └────────┘ │      │  └────────┘ │      │            │
    └──────────────┘      └──────────────┘      └──────────────┘
```

---

## 三、超级系统站详解

### 3.1 知识系统

**定位**：投资相关的结构化知识，可被各端查询调用

**组成**：
| 模块 | 内容 | 调用方式 |
|------|------|---------|
| 大师思想库 | 巴菲特/芒格/段永平/马克斯等的投资思想 | RAG检索 |
| 行业知识 | 估值体系、周期模型、分析框架 | 查询 |
| 案例库 | 历史事件、情景推演结果 | 检索 |

**文件位置**：`D:\claudework\workspace\mangoview\skills\investment-framework-skill\china-masters\`

---

### 3.2 通用能力系统

**定位**：跨场景通用的分析能力，所有端都可用

| 能力 | 功能 | 特点 |
|------|------|------|
| risk-assessor | 风险评估（市场/信用/流动性） | 通用 |
| sentiment-analyzer | 市场情绪分析（贪婪恐惧/拥挤度） | 通用 |
| bias-detector | 认知偏差检测（确认偏误/损失厌恶等） | 通用 |
| decision-checklist | 芒格多元思维决策检查 | 通用 |

**文件位置**：`D:\claudework\workspace\mangoview\skills\investment-framework-skill\`

---

### 3.3 数据系统

**定位**：外部业务数据的采集、清洗、存储

**数据源**：
| 数据类型 | 来源 | 状态 |
|----------|------|------|
| 宏观数据（PMI/CPI/GDP/M2/社融） | AKShare | ✅ 已接入 |
| 北向资金 | AKShare | ✅ 已接入 |
| 行业板块 | AKShare（受限） | ⚠️ Fallback |
| 指数/个股行情 | 东方财富（IP受限） | ❌ 待解决 |
| 基金数据 | 天天基金 | ✅ 已接入 |

**接口**：统一 API，各端通过 API 获取数据

---

### 3.4 分析引擎

**定位**：结构化投研流程的核心执行器，决策信号的源头

**三层分析框架**：
```
┌─────────────────────────────────────────────────────────────┐
│                      决策信号系统                           │
│                                                             │
│  天时（宏观）  ──┐                                          │
│                 ├──→  信号聚合  ──→  决策信号输出           │
│  地利（事件）  ──┤       ↑                                 │
│                 │       │ 提炼传递                         │
│  人和（公司/   ──┘       │                                 │
│        基金）            │                                 │
│                 ┌────────┴────────┐                       │
│                 │  各层内部：6步   │                       │
│                 │  数据契约+提炼传递│                       │
│                 └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**天时层（宏观）**：
| 子层 | 内容 | 输出信号 |
|------|------|---------|
| 经济周期 | 复苏/扩张/放缓/衰退定位 | 周期位置信号 |
| 行业周期 | 各行业在周期中的位置 | 行业机会信号 |
| 行业信号 | 动量/拥挤度/预期差 | 行业切换信号 |

**地利层（事件）**：
| 分析维度 | 内容 |
|----------|------|
| 叙事识别 | 市场在交易什么逻辑 |
| 传导路径 | 变量间如何传递 |
| 历史模式 | 相似事件的演绎路径 |
| 情景推演 | 乐观/基准/悲观情景 |

**人和层（实体）**：
| 实体类型 | 分析重点 | 输出信号 |
|----------|---------|---------|
| 公司 | 商业模式→财报→护城河→估值 | 公司信号 |
| 基金 | 业绩归因→经理能力→风险 | 基金信号 |

**六步研究流程 v2.0**（每层独立运行）：
```
Step 0（校验）→ Step 1（拆解）→ Step 2（传导）→ Step 3（历史）
→ Step 4（情景）→ Step 5（行动）→ Step 6（失效）
```

**数据契约设计**（为多Agent演进预留）：
- 每步输入/输出严格定义 JSON Schema
- 不是全量传递，是提炼传递：核心变量 + 置信度 + 关键假设 + 待验证项
- 接口标准化，Agent可独立替换/升级

**七层系统架构**：
```
数据输入层 → 事件触发层 → 研究流程层 → 情景库
→ 交易映射层 → 风险控制层 → 反馈系统
```

**付费分层模式**：
| 用户层级 | 可见内容 | 定价逻辑 |
|----------|---------|---------|
| 访客/免费 | 数据展示 + 简单结论 | 引流 |
| 基础付费 | 完整6步分析 + 信号 | 按需调用 |
| VIP | 实时监控 + 情景推送 + 多层联动 | 月/年订阅 |

**文件位置**：`D:\claudework\workspace\mangoview\SYSTEM_PROMPT.md`

---

## 三、分析引擎需求清单

### 需求总览

基于三层分析框架（天时/地利/人和）+ 六步研究流程 + 付费分层，设计以下需求：

---

### 需求 1：信号系统基础架构

**目标**：建立信号系统的核心数据模型和接口标准

#### 1.1 Signal 数据模型

```json
{
  "signal_id": "string",           // UUID，唯一标识
  "layer": "enum[TIANSHI|DILI|RENHE]",  // 信号层
  "sub_layer": "string|null",      // 子层，如 "ECONOMIC_CYCLE", "INDUSTRY", "EVENT"
  "entity_type": "string|null",    // 实体类型：stock/fund/event/macro
  "entity_id": "string|null",     // 实体标识：股票代码/基金代码等

  // 信号内容
  "signal_type": "string",        // 信号类型，如 "周期位置", "行业机会", "事件驱动"
  "direction": "enum[BULLISH|BEARISH|NEUTRAL]",  // 方向
  "intensity": "enum[STRONG|MEDIUM|WEAK]",       // 强度

  // 置信度与依据
  "confidence": "number[0-1]",     // 置信度 0-1
  "key_variables": [              // 关键变量（提炼传递用）
    {"name": "string", "value": "any", "importance": "enum[HIGH|MEDIUM|LOW]"}
  ],
  "key_assumptions": ["string"],   // 关键假设
  "pending_validations": ["string"],  // 待验证项

  // 失效条件
  "invalidation_conditions": [
    {"variable": "string", "threshold": "any", "direction": "string"}
  ],
  "monitoring_frequency": "enum[DAILY|WEEKLY|EVENT_DRIVEN]",

  // 元信息
  "source_data_timestamp": "datetime",  // 源数据时间戳
  "analysis_timestamp": "datetime",    // 分析时间戳
  "valid_until": "datetime|null",      // 有效期
  "step_completed": "number[0-6]",     // 分析到第几步

  // 付费分层
  "access_tier": "enum[FREE|BASIC|VIP]"  // 可访问层级
}
```

**JSON Schema 约束**：
- `confidence` 必须是 0-1 的数字，不能是 NaN/Inf
- `key_variables` 最多 5 个
- 所有字符串字段不能为 null，必要字段不能为空数组

#### 1.2 信号聚合层

**聚合算法**：
1. **同向信号叠加**：天时+地利+人和同向（都看多），强度叠加（STRONG×1.0 + MEDIUM×0.7 + WEAK×0.3）
2. **反向信号抵消**：方向冲突时，强度大的覆盖强度小的
3. **优先级规则**：
   - 人和层（公司/基金）> 地利层（事件）> 天时层（宏观）
   - 同层内，置信度高的覆盖置信度低的

**聚合输出**：
```json
{
  "aggregate_signal": {
    "direction": "BULLISH|BEARISH|NEUTRAL",
    "intensity": "STRONG|MEDIUM|WEAK",
    "confidence": "number[0-1]",
    "component_signals": ["signal_id_1", "signal_id_2"],
    "conflict_detected": "boolean",
    "conflict_resolution": "string|null"
  }
}
```

#### 1.3 信号 API

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/signal/{layer}` | GET | 获取某层信号列表 |
| `/api/v1/signal/{layer}/{entity_id}` | GET | 获取某实体信号 |
| `/api/v1/signal/aggregate` | GET | 获取聚合信号 |
| `/api/v1/signal/trigger` | POST | 触发事件分析（横向Scale筛选后的深度分析） |

**查询参数**：
- `tier`: 过滤可见层级（FLOAT 公共 / BASIC 付费 / VIP）
- `entity_type`: 过滤实体类型
- `since`: 时间范围
- `min_confidence`: 最低置信度

**验收标准**：
- 信号模型可序列化，无 NaN/Inf
- API 响应时间 < 500ms
- 各层信号可独立获取，也可聚合

#### 1.4 信号质量与评估周期（自进化补充）

**信号质量指标**：
| 指标 | 定义 | 计算方式 |
|------|------|---------|
| 信号准确率 | 信号发布后30天内市场走向是否符合预期 | 正确预测次数 / 总预测次数 |
| 信号延迟 | 从数据变点到信号生成的时间 | 分析时间戳 - 源数据时间戳 |
| 置信度校准度 | 预测置信度 vs 实际准确率的差距 | \|置信度 - 实际准确率\|，<0.15 为良好 |

**信号有效期**：
| 信号类型 | 有效期 | 重新评估触发 |
|----------|--------|-------------|
| 短期（事件驱动） | 24小时 | 下一个相关数据发布或事件触发 |
| 中期（行业轮动） | 7天 | 每周一例行重评 |
| 长期（经济周期） | 30天 | 月度宏观数据发布时 |

**准确判定标准**：
- 方向正确：信号预测方向与实际走向一致
- 偏差可接受：核心变量实际值偏离预测值 ≤ 15%
- **两个条件同时满足才算"准确"**

---

### 需求 2：天时层（宏观）分析模块

**目标**：宏观层的六步分析，输出经济周期+行业周期+行业信号

#### 2.1 横向 Scale 筛选（海量事件过滤）

**输入**：
- 宏观经济数据流（PMI/CPI/GDP/M2/社融/利率/汇率）
- 市场情绪数据（VIX/信用利差/拥挤度指标）
- 行业动量数据（各行业涨跌幅/资金流向）

**筛选规则**：
| 触发条件 | 阈值 |
|----------|------|
| 利率变动 | 单日 > 10bp |
| 美元指数突破 | 关键支撑/阻力位 |
| 油价单日涨跌 | > 3% |
| PMI 穿越荣枯线 | 50 上下穿越 |
| VIX 突破 | > 25 或 < 15 |
| 行业动量反差 | 强弱行业差距 > 15% |

**输出**：触发事件清单 + 优先级排序

#### 2.2 纵向六步分析（经济周期定位）

**Step 0 校验**：
- 输入：宏观数据（PMI/CPI/GDP/PPI/M2/社融）
- 处理：来源画像（官方/二手）、时效性、偏差检测
- 输出：`{source_credibility, data_freshness, bias_flag, final_rating}`

**Step 1 拆解**：
- 输入：宏观指标集合
- 处理：一级拆解（增长/通胀/货币/信用），二级变量提取
- 输出：核心变量清单（≤5个）+ 重要性排序

**Step 2 传导**：
- 输入：核心变量
- 处理：构建传导路径
  - 增长 → 通胀 → 货币政策 → 信用 → 股市
  - 反馈回路识别
- 输出：因果链 + 时效特征 + 阻滞点

**Step 3 历史**：
- 输入：当前变量结构
- 处理：检索历史相似时期（2-3个，如 2019年初、2022年底）
- 输出：相似案例 + 关键差异 + 可迁移模式

**Step 4 情景**：
- 输入：传导路径 + 历史模式
- 处理：生成基准/乐观/悲观情景
- 输出：情景概率分布 + 分叉点 + 一致性检查

**Step 5 行动**：
- 输入：情景推演结果
- 处理：映射到资产配置建议（股票/债券/商品/现金）
- 输出：基准行动 + 情景对应行动 + 不行动条件

**Step 6 失效**：
- 输入：情景假设
- 处理：定义逻辑失效条件 + 变量阈值 + 退出信号
- 输出：监控指标 + 频率 + 触发后行动

**经济周期判断规则**：
| 周期 | 判断条件 |
|------|---------|
| 复苏 | PMI↑ + CPI↓/平稳 + 货币宽松 + 信用扩张 |
| 扩张 | PMI高位 + CPI↑ + 货币边际收紧 + 信用持续扩张 |
| 放缓 | PMI↓ + CPI↑ + 货币收紧 + 信用收缩 |
| 衰退 | PMI↓↓ + CPI↓ + 信用收缩 + 失业率↑ |

**输出**：周期位置信号（复苏/扩张/放缓/衰退）+ 置信度 + 关键驱动

#### 2.3 纵向六步分析（行业周期定位）

**Step 0-6 同上**，但输入为：
- 各行业的历史表现数据
- 估值分位（PE/PB 历史分位）
- 宏观敏感度（行业 vs 经济周期相关性）

**行业周期判断规则**：
| 位置 | 判断条件 |
|------|---------|
| 机会区（领先） | 估值低位 + 宏观敏感度高 + 动量转正 |
| 中性 | 估值中位 + 宏观敏感度中等 |
| 风险区（滞后） | 估值高位 + 宏观敏感度高 + 动量负 |

**输出**：各行业机会信号 + 优先级排序

#### 2.4 行业信号扫描

**输入**：
- 动量指标：近1月/3月/6月涨幅排名
- 拥挤度：资金集中度、波动率异常
- 预期差：分析师评级变化、盈利预测调整

**信号类型**：
| 信号 | 条件 |
|------|------|
| 行业切换 | 原强势行业拥挤度升高 + 新行业出现动量 |
| 行业轮动 | 经济周期切换，行业机会区转移 |
| 行业拐点 | 预期差大幅逆转 |

**输出**：行业切换信号 + 置信度 + 失效条件

**数据依赖**：
- 宏观数据：已有（akshare）
- 行业数据：待解决（IP受限，fallback手动）

#### 2.5 天时层每步完成标准与回退机制（自进化补充）

| 步骤 | 通过条件 | 未通过处理 |
|------|---------|-----------|
| Step 0 校验 | source_credibility ≥ 0.5 | <0.3 直接拒绝；0.3-0.5 标记低可信、标注后继续 |
| Step 1 拆解 | core_variables ≤ 5 个 | >5 则合并降维，仍 >5 回退到 Step 0 重新校验 |
| Step 2 传导 | impact_pathways ≥ 2 条 | <2 条回退到 Step 1 重新拆解 |
| Step 3 历史 | similarity ≥ 0.3 | <0.3 标"无强相似案例"，以逻辑推导为主 |
| Step 4 情景 | 一致性检查通过 | 不通过回退到 Step 2 重分析传导路径 |
| Step 5 行动 | position_side 明确 | 无法明确则输出"观望"标记 |
| Step 6 失效 | exit_signals ≥ 1 条 | 0 条则标注"未定义退出条件，风险上升" |

---

### 需求 3：地利层（事件）分析模块

**目标**：事件的横向Scale筛选 + 纵向六步深度分析

#### 3.1 横向 Scale 筛选（海量事件过滤）

**输入**：
- 新闻流（政策、央行、地缘、行业、公司事件）
- 市场数据异动（涨跌幅、成交量异常）
- 宏观数据发布

**筛选规则**：
| 事件类型 | 筛选条件 |
|----------|---------|
| 政策事件 | 官方媒体确认 + 涉及重要行业 |
| 央行决议 | 利率变化 > 25bp、缩放表规模 > 500亿 |
| 地缘事件 | 涉及主要经济体 + 影响贸易/能源 |
| 行业事件 | 政策+财报+竞争格局变化 |
| 公司事件 | 重大并购/财报超预期/黑天鹅 |

**输出**：值得深度分析的事件清单 + 优先级

#### 3.2 纵向六步分析（事件深度解读）

**Step 0 校验**：
- 输入：事件描述 + 来源
- 处理：来源画像（官方/媒体/机构）、利益相关性、历史可信度
- 输出：`{source_credibility, bias_types[], final_rating}`

**Step 1 拆解**：
- 输入：事件描述
- 处理：一级拆解（受影响变量）+ 二级变量提取
- 输出：核心变量清单（≤5个）+ 重要性排序 + 分类（直接/间接/可观测/潜变量）

**Step 2 传导**：
- 输入：核心变量
- 处理：构建因果链 + 反馈回路 + 传导阻滞点 + 时效特征
- 输出：传导路径图 + 各路径强度 + 时间延迟

**Step 3 历史**：
- 输入：当前变量结构
- 处理：检索相似历史事件（2-3个）
- 输出：案例摘要 + 关键差异 + 可迁移模式 + 不可迁移模式

**Step 4 情景**：
- 输入：传导路径 + 历史模式
- 处理：生成乐观/基准/悲观情景 + 分叉点识别 + 一致性检查
- 输出：情景概率 + 触发条件 + 演化路径

**Step 5 行动**：
- 输入：情景推演
- 处理：映射到交易方向 + 仓位建议 + 时间窗口
- 输出：基准行动 + 情景行动 + 不行动条件 + 约束自检

**Step 6 失效**：
- 输入：情景假设
- 处理：定义失效条件 + 变量阈值 + 退出信号
- 输出：监控指标 + 频率 + 触发后行动

**叙事识别规则**：
- 同一时期市场通常在交易1-2个核心叙事
- 识别方式：近期涨幅最大的资产 + 资金流向 + 分析师共识
- 输出：当前核心叙事描述 + 置信度

**输出**：事件信号 + 叙事识别 + 传导路径 + 情景 + 行动建议

**验收标准**：
- 事件分析结果存入情景库
- 提炼传递：只输出核心变量+置信度+假设，不输出完整分析文本

#### 3.3 地利层每步完成标准与回退机制（自进化补充）

| 步骤 | 通过条件 | 未通过处理 |
|------|---------|-----------|
| Step 0 校验 | source_credibility ≥ 0.5 | <0.3 直接拒绝；0.3-0.5 标记后继续 |
| Step 1 拆解 | core_variables ≤ 5 个 | >5 合并降维，仍 >5 回退到 Step 0 |
| Step 2 传导 | impact_pathways ≥ 2 条 | <2 条回退到 Step 1 重新拆解 |
| Step 3 历史 | similar_cases ≥ 1 个且 similarity ≥ 0.3 | <0.3 以逻辑推导为主 |
| Step 4 情景 | 一致性检查通过（三个情景逻辑自洽） | 不通过回退到 Step 2 重分析因果链 |
| Step 5 行动 | position_side 明确 + 约束自检通过 | 约束不通过输出"条件不具备" |
| Step 6 失效 | exit_signals ≥ 1 条 | 0 条标"未定义退出条件，风险上升" |

---

### 需求 4：人和层（实体）分析模块

**目标**：上市公司和基金的六步分析

#### 4.1 公司分析（六步 + Skill）

**Step 0 校验**：
- 输入：公司财报/公告/研报
- 处理：来源可信度、完整性偏差检测
- 输出：`{source_credibility, bias_types[], final_rating}`

**Step 1 拆解**：
- 输入：公司基本信息 + 商业模式
- 处理：
  1. 商业模式分类（SaaS/制造/银行/平台/零售）
  2. 提取关键指标（按商业模式不同）
- 输出：
  ```json
  {
    "business_type": "SaaS|制造|银行|平台|零售",
    "key_metrics": ["指标1", "指标2"],
    "core_variables": [{"name": "string", "value": "any", "type": "直接|间接"}]
  }
  ```

**商业模式关键指标**：
| 类型 | 核心指标 |
|------|---------|
| SaaS | ARR增长率、净留存率(NRR)、客户获取成本(CAC)、毛利率 |
| 制造业 | 产能利用率、订单积压、库存周转、资本支出 |
| 银行 | 净息差(NIM)、存款成本、贷款增长率、不良贷款率(NPL) |
| 平台 | DAU/MAU、变现率(Take rate)、网络效应 |
| 零售 | 同店销售、库存周转、坪效 |

**Step 2 传导**：
- 输入：核心变量
- 处理：构建变量间传导路径
  - 收入增长 → 利润率变化 → 现金流 → 资产负债表
  - 管理层决策 → 竞争优势 → 长期价值
- 输出：因果链 + 反馈回路 + 阻滞点

**Step 3 历史**：
- 输入：公司历史财务数据 + 行业历史
- 处理：检索相似公司/历史时期
  - Skill调用：`financial-report-analyzer`（财报四层分析）
- 输出：历史表现 + 关键转折点 + 可迁移模式

**Step 4 情景**：
- 输入：传导路径 + 历史模式 + 行业周期
- 处理：生成基准/乐观/悲观情景
  - Skill调用：`moat-evaluator`（护城河评估）
  - Skill调用：`intrinsic-value-calculator`（内在价值计算 DCF/DDM）
- 输出：情景概率 + 估值区间 + 分叉点

**Step 5 行动**：
- 输入：情景 + 估值
- 处理：vs 当前股价计算预期差
  - Skill调用：`bias-detector`（认知偏差检测）
- 输出：信号（低估/合理/高估）+ 置信度 + 行动建议

**Step 6 失效**：
- 输入：情景假设
- 处理：定义失效条件 + 监控指标
- 输出：退出信号 + 监控频率

**Skill 串接规则**：
```
公司分析：
business-model-classifier → financial-report-analyzer → moat-evaluator 
→ intrinsic-value-calculator → bias-detector → decision-checklist
```

**输出**：公司信号（低估/合理/高估）+ 目标价区间 + 置信度 + 失效条件

#### 4.2 基金分析（六步 + Skill）

**Step 0 校验**：
- 输入：基金季报/年报 + 净值数据 + 持仓数据
- 处理：数据完整性、利益相关性检测
- 输出：`{source_credibility, bias_types[], final_rating}`

**Step 1 拆解**：
- 输入：基金净值序列 + 持仓信息
- 处理：
  1. 基金风格分类（成长/价值/平衡/行业/指数）
  2. 提取风险收益指标
- 输出：
  ```json
  {
    "fund_style": "成长|价值|平衡|行业|指数",
    "key_metrics": ["收益率", "波动率", "最大回撤", "夏普比率"],
    "core_variables": [{"name": "string", "value": "any"}]
  }
  ```

**Step 2 传导**：
- 输入：基金收益分解
- 处理：归因分析
  - 收益 = alpha + beta × 市场收益 + 行业暴露 × 行业收益 + 风格暴露 × 风格收益
  - 识别收益来源（选股/择时/行业/风格）
- 输出：收益分解 + 各因子贡献度 + 稳定性评估

**Step 3 历史**：
- 输入：基金历史表现 + 同类基金对比
- 处理：
  - Skill调用：`fund-analyzer-pro`（业绩归因/风险分析/经理能力）
  - 检索同类基金表现
- 输出：历史归因 + 能力持续性 + vs 同类排名

**Step 4 情景**：
- 输入：当前宏观环境 + 行业周期
- 处理：判断基金策略在当前环境的适应性
- 输出：情景分析（有利/中性/不利情景概率）

**Step 5 行动**：
- 输入：情景分析 + 基金信号
- 处理：
  - Skill调用：`bias-detector`
- 输出：基金信号（推荐/中性/回避）+ 理由 + 适用场景

**Step 6 失效**：
- 输入：情景假设
- 处理：定义经理能力失效条件、策略失效条件
- 输出：监控指标（净值回撤、换手率变化、持仓集中度）+ 退出信号

**Skill 串接规则**：
```
基金分析：
fund-style-classifier → fund-analyzer-pro → bias-detector → decision-checklist
```

**输出**：基金信号（推荐/中性/回避）+ 置信度 + 适用场景 + 失效条件

**验收标准**：
- 公司分析和基金分析模块独立
- 输出符合统一信号模型（需求1定义的数据结构）

#### 4.3 人和层每步完成标准与回退机制（自进化补充）

| 步骤 | 通过条件 | 未通过处理 |
|------|---------|-----------|
| Step 0 校验 | source_credibility ≥ 0.5 | <0.3 直接拒绝；0.3-0.5 标记后继续 |
| Step 1 拆解 | core_variables ≤ 5 个 + 商业模式分类置信度 ≥ 0.4 | >5 合并；分类置信度 <0.4 回退到 Step 0 |
| Step 2 传导 | 归因分解完整（公司：收入/利润/现金流；基金：alpha/beta/行业暴露） | 不完整回退到 Step 1 |
| Step 3 历史 | 相似案例 ≥ 1 个或归因数据完整 | 无数据则标注"缺乏历史参考" |
| Step 4 情景 | 估值区间完整（bull/base/bear 三个值） | 数据不足则仅输出基准情景 |
| Step 5 行动 | 信号方向明确 + 约束自检通过 | 约束不通过输出"条件不具备，等待" |
| Step 6 失效 | exit_signals ≥ 1 条 | 0 条标"未定义退出条件，风险上升" |

---

### 需求 5：Skill 层串接规则

**目标**：Skill 调用引擎 + 串接规则配置化

#### 5.1 Skill 调用引擎

**核心设计**：
- Skill 是独立的能力单元，有标准输入/输出
- 串接规则配置化，支持流程编排
- 支持条件分支（根据上一步结果决定下一步调用哪个Skill）

**配置结构**：
```yaml
skill_chains:
  company_analysis:
    step0: [data_validator]
    step1: [business-model-classifier]
    step2: [financial-report-analyzer]
    step3: [financial-report-analyzer, moat-evaluator]
    step4: [moat-evaluator, intrinsic-value-calculator]
    step5: [bias-detector]
    step6: [decision-checklist]
  
  fund_analysis:
    step0: [data_validator]
    step1: [fund-style-classifier]
    step2: [fund-analyzer-pro]
    step3: [fund-analyzer-pro]
    step4: [fund-analyzer-pro]
    step5: [bias-detector]
    step6: [decision-checklist]
```

**调用流程**：
1. 解析串接规则
2. 按顺序执行 Skill
3. 每步 Skill 输出作为下一步输入的一部分
4. 错误处理：某步失败可选择跳过或终止
5. 记录调用日志（输入/输出/耗时/错误）

#### 5.2 Skill 输入/输出 Schema（核心Skills）

**business-model-classifier**：
```json
// 输入
{"company_name": "string", "industry": "string", "description": "string"}

// 输出
{
  "classification": "SaaS|制造|银行|平台|零售",
  "confidence": "number[0-1]",
  "key_indicators": ["string"],
  "reasoning": "string"
}
```

**financial-report-analyzer**：
```json
// 输入
{"company_id": "string", "period": "string", "report_type": "annual|quarterly"}

// 输出
{
  "layer1_reading": {"revenue": "number", "margin": "number", "eps": "number", "cash_flow": "number"},
  "layer2_drivers": {"growth_driver": "string", "margin_driver": "string", "management_changes": "string"},
  "layer3_expectation_gap": {"vs_last_quarter": "number", "vs_consensus": "number", "vs_history": "number"},
  "layer4_action": {"outlook": "BULLISH|BEARISH|NEUTRAL", "key_factors": ["string"]},
  "confidence": "number[0-1]"
}
```

**moat-evaluator**：
```json
// 输入
{"company_id": "string", "business_type": "string"}

// 输出
{
  "moat_type": "无形资产管理|转换成本|网络效应|成本优势|政府许可",
  "moat_strength": "WIDE|NARROW|NONE",
  "factors": [{"type": "string", "impact": "positive|negative", "description": "string"}],
  "sustainability": "number[0-1]",
  "confidence": "number[0-1]"
}
```

**intrinsic-value-calculator**：
```json
// 输入
{"company_id": "string", "method": "DCF|DDM", "assumptions": {}

// 输出
{
  "method": "DCF|DDM",
  "intrinsic_value": "number",
  "current_price": "number",
  "upside_downside": "number[%]", 
  "scenario_analysis": {
    "bull_case": "number",
    "base_case": "number", 
    "bear_case": "number"
  },
  "key_assumptions": ["string"],
  "confidence": "number[0-1]"
}
```

**fund-analyzer-pro**：
```json
// 输入
{"fund_id": "string", "period": "string"}

// 输出
{
  "return_attribution": {
    "alpha": "number",
    "beta": "number", 
    "sector_contribution": "number",
    "style_contribution": "number"
  },
  "risk_metrics": {
    "volatility": "number",
    "max_drawdown": "number",
    "sharpe_ratio": "number"
  },
  "manager_ability": {
    "stock_selection": "number",
    "timing": "number", 
    "consistency": "number"
  },
  "confidence": "number[0-1]"
}
```

#### 5.3 Skill调用超时与降级策略（自进化补充）

**超时配置**：
| Skill 类型 | 默认超时 | 重试策略 |
|-----------|---------|---------|
| 数据校验类（data_validator） | 10s | 重试1次 |
| 分类识别类（business-model, fund-style） | 15s | 重试1次 |
| 分析推理类（moat, intrinsic-value, financial-report） | 30s | 重试1次 |
| 复杂计算类（fund-analyzer-pro） | 45s | 不重试，直接降级 |

**降级策略**：
| 失败场景 | 处理方式 |
|---------|---------|
| 超时 | 标记该步"超时"，使用默认值/缓存值继续 |
| 数据不足 | 跳过该步，标注"数据不足，推理受限" |
| 模型不可用 | 回退到上一步，等待恢复后重试 |
| 输出格式错误 | 重试 1 次，仍失败则标记"格式异常" |

**调用链保护**：
- 最大链式深度：6 步（与六步分析一致）
- 单次完整分析总超时上限：300s
- 失败累计 > 2 步时，终止整条链，输出"分析不完整"

---

### 需求 6：付费分层功能

**目标**：基于用户层级限制分析深度

#### 6.1 用户层级模型

| 层级 | 标识 | 定价 | 可见内容 |
|------|------|------|---------|
| 访客 | GUEST | 免费 | 数据展示 + 简单结论（无六步） |
| 免费用户 | FREE | 免费 | 数据展示 + 简单结论 |
| 付费用户 | BASIC | 按需/订阅 | 完整六步分析 + 信号 |
| VIP | VIP | 月/年订阅 | 完整分析 + 实时监控 + 多层联动 |

#### 6.2 API 访问控制

**实现方式**：同一接口，通过 `Authorization` header 判断层级，返回不同深度

**层级判断逻辑**：
```python
def get_access_tier(token):
    if not token: return "GUEST"
    # 解析 token，获取用户层级
    return user.tier  # GUEST | FREE | BASIC | VIP
```

**返回字段控制**：
```python
def filter_by_tier(signal, tier):
    if tier == "GUEST" or tier == "FREE":
        # 只返回基础信息
        return {
            "signal_type": signal.signal_type,
            "direction": signal.direction,
            "simple_conclusion": signal.summary_3sentences,  # 3句话总结
            "access_tier_required": "BASIC"
        }
    elif tier == "BASIC":
        # 返回完整六步 + 信号
        return signal  # 全部字段
    elif tier == "VIP":
        # 完整 + 实时监控配置
        return {
            **signal,
            "monitoring_config": signal.get_monitoring_config(),
            "related_signals": signal.get_related_signals()
        }
```

**付费墙展示**：
- 前端检测 `access_tier_required` 字段
- 若当前用户层级不足，显示付费引导

#### 6.3 层级升级触发点

| 触发位置 | 提示文案 |
|----------|---------|
| 查看六步分析 | "升级到付费版查看完整分析" |
| 查看信号详情 | "升级到VIP解锁实时监控" |
| 多层联动 | "VIP专属功能" |

**验收标准**：
- 同一信号接口，不同用户看到不同深度
- 不需要多个接口，层级在返回字段中体现

#### 6.4 "简单结论"标准与升级转化（自进化补充）

**"简单结论"定义**（访客/免费用户可见）：
- 字数 ≤ 3 句话（100 字以内）
- 内容范围：仅包含数据陈述（"PMI 当前值 50.8"），不含分析推导
- 禁止输出：信号方向、置信度、行动建议、归因分析
- 含引导文案："升级后可查看完整六步分析"

**升级转化触发指标**：
| 触发行为 | 转化动作 | 目标层级 |
|---------|---------|---------|
| 同一信号 7 天内查看 ≥ 3 次 | 弹出付费引导浮窗 | FREE → BASIC |
| 在付费墙页面停留 > 10s | 显示"今日特惠"卡片 | FREE → BASIC |
| 累计查看 5 个不同信号的摘要 | 推送周卡试用邀请 | FREE → BASIC |
| 连续使用 30 天（免费层） | 推送年付折扣 | BASIC → VIP |
| 触达监控信号上限（3 个免费信号） | 提示"升级获取无限信号监控" | BASIC → VIP |

**免费额度硬边界**：
- 每日信号摘要查看：10 次/天
- 月度深度分析调用：3 次/月
- 实时监控信号：最多 3 个
- 超过边界统一响应 402 Payment Required + 升级引导

---

### 需求 7：数据契约设计（多Agent演进预留）

**目标**：为将来拆分为多Agent管道预留接口标准

#### 7.1 六步分析 JSON Schema

**Step 0 校验**：
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "step": {"const": 0},
    "input": {
      "type": "object",
      "properties": {
        "data_source": "string",
        "source_type": "enum[一手|二手|官方|媒体|机构分析]",
        "利益相关性": "enum[直接利益|间接利益|无明显利益]",
        "历史可信度": "enum[高|中|低|未知]"
      }
    },
    "output": {
      "type": "object",
      "properties": {
        "source_credibility": "enum[高|中|低]",
        "bias_types": ["string"],
        "final_rating": "enum[直接使用|需验证后使用|仅作参考|不可用]",
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
      }
    }
  }
}
```

**Step 1 拆解**：
```json
{
  "step": 1,
  "input": {"raw_data": "any"},
  "output": {
    "core_variables": [
      {"name": "string", "value": "any", "importance": "enum[HIGH|MEDIUM|LOW]", "type": "enum[直接|间接|可观测|潜变量]"}
    ],
    "variable_importance": ["HIGH", "MEDIUM", "LOW"],
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "key_assumptions": ["string"],
    "pending_validations": ["string"]
  }
}
```

**Step 2 传导**：
```json
{
  "step": 2,
  "input": {"core_variables": []},
  "output": {
    "causal_chain": "string",
    "feedback_loops": [{"type": "enum[正反馈|负反馈]", "description": "string"}],
    "blockage_points": [{"location": "string", "reason": "string"}],
    "time_characteristics": [
      {"path": "string", "delay": "enum[即时|滞后|累积]", "timescale": "string"}
    ],
    "transmission_strength": "enum[强|弱|非线性]",
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

**Step 3 历史**：
```json
{
  "step": 3,
  "input": {"core_variables": [], "causal_chain": "string"},
  "output": {
    "similar_cases": [
      {"time": "string", "location": "string", "core_features": "string", "outcome": "string"}
    ],
    "similarity": {"variable_match": "number", "context_match": "number"},
    "key_differences": [{"difference": "string", "potential_impact": "string"}],
    "transferable_patterns": ["string"],
    "non_transferable_patterns": ["string"],
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

**Step 4 情景**：
```json
{
  "step": 4,
  "input": {"causal_chain": "string", "historical_cases": []},
  "output": {
    "base_case": {
      "probability": "enum[高|中|低]",
      "assumptions": ["string"],
      "path": "string",
      "impact": "string"
    },
    "bull_case": {"probability": "string", "trigger": "string", "path": "string", "impact": "string"},
    "bear_case": {"probability": "string", "trigger": "string", "path": "string", "impact": "string"},
    "key_bifurcation": {"variable": "string", "threshold": "any", "direction": "string"},
    "consistency_check": "boolean",
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

**Step 5 行动**：
```json
{
  "step": 5,
  "input": {"scenarios": {}},
  "output": {
    "base_action": {
      "direction": "enum[买入|卖出|持有|观望]",
      "object": "string",
      "logic": "string",
      "intensity": "enum[观察|轻仓|重仓|对冲]",
      "time_window": "string"
    },
    "bull_action": {"intensity": "string", "logic": "string"},
    "bear_action": {"intensity": "string", "logic": "string"},
    "no_action_condition": "string",
    "constraint_check": {"risk_capacity": "boolean", "fund_size": "boolean", "execution": "boolean"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

**Step 6 失效**：
```json
{
  "step": 6,
  "input": {"scenarios": {}, "assumptions": []},
  "output": {
    "logical_conditions": ["string"],
    "variable_thresholds": [{"variable": "string", "threshold": "any", "direction": "string", "effect": "string"}],
    "time_boundary": {"valid_period": "string", "reassess_after": "number"},
    "exit_signals": [
      {"signal": "string", "observable": "boolean", "trigger_action": "string"}
    ],
    "monitoring_frequency": "enum[每日|每周|事件驱动]",
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

#### 7.2 提炼传递规则

**核心原则**：只传递**判断结果**，不传递**分析过程**

| 传递内容 | 是否传递 | 说明 |
|----------|---------|------|
| 核心变量 + 取值 | ✅ | 用于下游推理 |
| 置信度 | ✅ | 下游判断是否采信 |
| 关键假设 | ✅ | 下游评估风险 |
| 待验证项 | ✅ | 下游决定是否补充 |
| 完整分析文本 | ❌ | 浪费 token，下游不需要 |
| 中间计算过程 | ❌ | 只需要最终判断 |

**传递格式**：
```json
{
  "refined_output": {
    "step": 1,
    "core_variables": [...],
    "confidence": 0.85,
    "key_assumptions": ["假设1", "假设2"],
    "pending_validations": ["待验证1"],
    "confidence_level": "高"  // 用于人类阅读
  }
}
```

#### 7.3 Agent 间数据传递（多Agent演进后）

```json
{
  "agent_contract": {
    "from_agent": "string",
    "to_agent": "string",
    "step": "number[0-6]",
    "refined_data": {
      "core_variables": [...],
      "confidence": "number",
      "key_assumptions": [...],
      "pending_validations": [...]
    },
    "pass_timestamp": "datetime",
    "schema_version": "string"
  }
}
```

**演进检查点**：
- 当某步成为瓶颈（耗时过长）时，考虑拆分为独立 Agent
- 当某步需要不同模型时（简单校验 vs 复杂推理），拆分
- 拆分后的 Agent 必须符合上述数据契约

#### 7.4 提炼传递量化标准与版本管理（自进化补充）

**提炼传递量化规则**：
| 传递项 | 最大数量 | 超出处理 |
|-------|---------|---------|
| core_variables | ≤ 5 个 | 按重要性排序截断 |
| key_assumptions | ≤ 3 条 | 保留最关键假设 |
| pending_validations | ≤ 3 项 | 保留最高优先级 |
| 传给下一步的 assumptions | ≤ 2 条 | 仅传递直接影响下一步的 |

**Schema 版本管理**：
- 格式：`v{大版本}.{小版本}.{补丁}`（SemVer）
- 大版本增长：字段增删或类型变更（不向下兼容）
- 小版本增长：新增可选字段（向下兼容）
- 补丁版本增长：描述/注释/示例更新
- 当前版本：`v1.0.0`
- Agent 间传递时必须携带 `schema_version` 字段
- 接收方校验版本兼容性，不兼容时回退到上一步

**版本兼容矩阵**：
| 接收方 \ 发送方 | v1.0.x | v1.1.x | v2.0.x |
|----------------|--------|--------|--------|
| v1.0.x | ✅ 兼容 | ⚠️ 忽略额外字段 | ❌ 不兼容 |
| v1.1.x | ✅ 兼容 | ✅ 兼容 | ❌ 不兼容 |
| v2.0.x | ❌ 不兼容 | ❌ 不兼容 | ✅ 兼容 |

---

## 四、三端产品详解

### 4.1 个人版（C端）

**定位**：个人投资者的"第二大脑"——解决"知行合一"问题

**核心能力**：
- 想法记录：用户说一句话 → AI解析 + 关联历史 + 生成卡片
- 投资知识 RAG：大师思想检索问答
- 记忆系统：用户画像、历史决策、行为模式
- 提醒触发：价格/时间/条件监控

**形态**：
- AI 对话界面（主要交互）
- SaaS 可视化界面（让用户知道有哪些服务）
- 记忆系统（跟着场景和 agent走）

**技术栈**：
- Harness 多 Agent 框架
- 知识库：GraphRAG
- 记忆层：Mem0/开源记忆库

**调用关系**：
```
个人版 → 调用超级系统站
       ├── 知识系统（RAG检索）
       ├── 数据系统（行情/宏观）
       ├── 分析引擎（六步流程）
       └── 通用能力（risk/sentiment/bias）
```

**文件位置**：`D:\claudework\workspace\investment-assistant\`

---

### 4.2 投顾版（B端）

**定位**：理财师/投顾的专业工作台

**组成模块**：
| 模块 | 功能 |
|------|------|
| b-compliance | 合规审查 |
| b-crm | 客户管理 |
| b-dashboard | 数据看板 |
| b-event | 事件解读 |
| b-fund | 基金诊断 |
| b-pipeline | Pipeline编排器 |
| b-template | 话术模板库 |
| b-trigger | 触发规则引擎 |

**形态**：
- 工作台界面（CRM/合规/话术等模块）
- 记忆系统（跟着场景和 agent走）

**调用关系**：
```
投顾版 → 调用超级系统站
       ├── 知识系统（话术模板/合规规则）
       ├── 数据系统（客户数据/市场数据）
       ├── 分析引擎（基金诊断/事件解读）
       └── 通用能力（risk/sentiment/bias）
```

**文件位置**：`D:\claudework\workspace\mangofolio\b-end\`

---

### 4.3 超级站（前端）

**定位**：超级系统站的展示界面 + SaaS 引流入口

**形态**：
- 数据展示（宏观数据、市场数据、基金数据）
- 引流介绍（超级系统站的能力说明）
- 服务入口（引导用户进入个人版或投顾版）

**调用关系**：
```
超级站前端 → 调用超级系统站
           ├── 数据展示（数据系统）
           └── 能力说明（知识系统）
```

**文件位置**：`D:\claudework\workspace\mangoview\frontend\`

---

## 五、记忆系统设计

**核心原则**：记忆跟着场景和 agent 走，各端独立

### 5.1 个人版记忆系统

**数据**：
- 用户画像（风险偏好、能力圈、投资原则）
- 历史决策（买了什么、为什么买、什么时候卖）
- 想法卡片（关于标的的想法）
- 行为模式（追高、止损过早等）

**特点**：用户私有，隐私优先

---

### 5.2 投顾版记忆系统

**数据**：
- 客户画像（风险偏好、持仓状况、交互历史）
- 理财师工作记录（分析历史、服务记录）
- 话术历史（使用过的话术模板）

**特点**：客户关系数据，需要保密

---

### 5.3 各端记忆独立

```
个人版记忆系统 ← 独立 → 投顾版记忆系统
     ↓ ↓
 用户A的数据客户B的数据
```

不同端之间的记忆**不互通**，各自隔离。

---

## 六、Skill 层设计

### 6.1 通用 Skill（超级系统站提供）

| Skill | 核心能力 | 适用场景 |
|-------|---------|---------|
| bias-detector | 认知偏差检测 | 任何决策前 |
| risk-assessor | 风险评估 | 任何投资决策 |
| sentiment-analyzer | 市场情绪分析 | 宏观 + 个股 |
| decision-checklist | 芒格多元思维决策检查 | 最终行动前 |

### 6.2 专用 Skill（按层分类）

**叙事层（地利）**：
| Skill | 核心能力 | 触发条件 |
|-------|---------|---------|
| fanli-analyzer | 反例分析 | 事件分析 |
| cycle-locator | 周期定位 | 宏观/行业 |

**天时层（宏观）**：
| Skill | 核心能力 | 触发条件 |
|-------|---------|---------|
| macro-data-parser | 宏观数据解析 | 宏观分析 |
| cycle-analyzer | 经济周期分析 | 宏观分析 |
| industry-cycle | 行业周期定位 | 行业分析 |
| sector-signal | 行业信号扫描 | 行业分析 |

**实体层（公司）**：
| Skill | 核心能力 | 触发条件 |
|-------|---------|---------|
| value-analyzer | 格雷厄姆价值分析 | 个股 |
| moat-evaluator | 护城河评估 | 个股 |
| intrinsic-value-calculator | 内在价值计算 | 个股 |
| financial-report-analyzer | 财报四层分析 | 财报 |
| business-model-classifier | 商业模式分类 | 个股 |

**实体层（基金）**：
| Skill | 核心能力 | 触发条件 |
|-------|---------|---------|
| fund-analyzer-pro | 基金诊断 | 基金 |
| fund-style-classifier | 基金风格分类 | 基金 |
| portfolio-optimizer | 组合优化 | 资产配置 |

**大师思想库**：
| Skill | 核心能力 | 触发条件 |
|-------|---------|---------|
| buffett-moat | 巴菲特护城河 | 价值投资 |
| monty-multiple | 芒格多元思维 | 复杂决策 |
| duan-longterm | 段永平"本分" | 长期投资 |
| mark-cycle | 马克斯周期 | 宏观 |

---

## 七、文件位置速查

| 产品/系统 | 路径 |
|----------|------|
| 个人版（C端）| `D:\claudework\workspace\investment-assistant\` |
| 投顾版（B端）| `D:\claudework\workspace\mangofolio\b-end\` |
| 超级系统站后端 | `D:\claudework\workspace\mangoview\backend\` |
| 超级系统站前端 | `D:\claudework\workspace\mangoview\frontend\` |
| framework-skill | `D:\claudework\workspace\mangoview\skills\investment-framework-skill\` |
| 系统设计文档 | `D:\claudework\workspace\mangoview\SYSTEM_PROMPT.md` |
| 项目总览 | `D:\claudework\workspace\mangofolio\PROJECT_INVENTORY.md` |

---

## 八、技术实现形态

### 8.1 API 分层设计（to Agent + to Human）

**同一套底层能力，两套接口协议，服务不同客户端**

```
┌─────────────────────────────────────────────────────────────┐
│                      超级系统站                              │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 知识系统│ │通用能力 │ │ 数据系统│ │分析引擎│          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
           │                              │
    ┌──────┴──────┐               ┌─────┴─────┐
    │  to Agent   │                │  to Human │
    │   (MCP)     │                │   (REST)  │
    └─────────────┘                └───────────┘
           │                              │
    ┌─────┴─────┐                 ┌──────┴──────┐
    │ assistant │                 │ mangoview │
    │ (AI Agent)│                 │   前端     │
    └───────────┘                 └────────────┘
```

**to Agent（MCP）**：
- 调用方：AI Agent（assistant 的 agent）
- 特点：工具调用、JSON 输入/输出、自动化调用链
-适用：AI 分析流程、多步骤工具调用

**to Human（REST）**：
- 调用方：人类用户（浏览器/App）
- 特点：人类友好格式、中文自然语言、支持分页过滤
- 适用：数据展示、用户操作、调试

---

### 8.2 隐私与安全架构

**密钥管理方案**：社交账号登录（微信扫码）

```
用户登录（微信扫码）
    ↓
获取 OAuth Token（微信授权）
    ↓
Token 关联用户账户和加密密钥
    ↓
密钥服务端不存储，只用户本地持有
    ↓
数据本地 AES-256 加密后上传云端
    ↓
其他设备登录时，通过微信扫码授权同步密钥
```

**数据加密策略**：

| 数据类型 | 存储方式 | 密钥管理 |
|----------|---------|---------|
| 用户私密数据 | 本地加密 + 云端密文 | 用户本地密钥 |
| 同步配置 | 云端加密存储 | 微信关联 |
| 公开数据 | 明文存储 | 无需密钥 |

**投顾客户数据归属**：
- 归投顾私有，服务端加密存储
- 服务商无法读取密文
- 投顾离职时，客户数据可交接或删除

---

### 8.3 同步与迁移架构

**多端同步策略**：

```
┌─────────────────────────────────────────────────────────────┐
│                     云端同步服务                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  用户数据仓库（加密存储）                            │   │
│  │  - 个人版：想法卡片、记忆、偏好                      │   │
│  │  - 投顾版：客户信息、工作流                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑                                  │
│                    加密同步                                 │
│                         ↑                                  │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
      ┌────┴────┐         ┌────┴────┐          ┌────┴────┐
      │ 手机端  │          │ 电脑端  │          │ 平板端  │
      │ 本地缓存│          │ 本地缓存│          │ 本地缓存│
      └─────────┘          └─────────┘└─────────┘
```

**同步类型**：
| 类型 | 说明 | 典型数据 |
|------|------|---------|
| 实时同步 | 任何变更立即同步 | 投顾的客户信息修改 |
| 增量同步 | 只同步变更部分 | 想法卡片（只同步新的） |
| 离线优先 | 先本地操作，网络恢复后同步 | 手机信号不好时 |

**终端迁移**：
```
新设备登录（微信扫码）
    ↓
从云端下载加密数据
    ↓
本地密钥解密
    ↓
重建数据
```

---

### 8.4 超级系统站 API 设计

**to Human（REST）**：
```
GET  /api/v1/knowledge/search?q={query}   # 知识检索
GET  /api/v1/data/macro?indicators=... # 宏观数据
GET  /api/v1/data/fund/{fund_code}        # 基金数据
POST /api/v1/analyze/event                # 事件分析
POST /api/v1/analyze/stock               # 个股分析
POST /api/v1/skill/{skill_name}           # 调用 Skill
```

**to Agent（MCP）**：
```
Tools:
- knowledge_search(query: string) →知识检索
- macro_data(indicators: string[]) → 宏观数据
- fund_data(fund_code: string) → 基金数据
- analyze_event(event: object) → 事件分析
- analyze_stock(company: string) → 个股分析
- call_skill(skill_name: string, args: object) → 调用 Skill
```

---

### 8.5 数据分层架构

```
用户数据
    │
    ├── 私密数据（本地加密，云端只存密文）
    │   ├── 个人版：投资想法、持仓记忆、决策记录
    │   └── 投顾版：客户信息、工作流、话术（归投顾私有）
    │
    ├── 同步数据（加密同步，多端一致）
    │   ├── 个人版：用户偏好、设置
    │   └── 投顾版：工作配置、设置
    │
    └── 公开数据（超级系统站，无需同步）
        ├── 宏观数据、市场数据
        ├── 分析结果（标准化的）
        └── Skills 配置
```

---

### 8.6 部署策略

| 阶段 | 部署形态 | 说明 |
|------|---------|------|
| MVP | 独立服务 + 云端存储 | 先跑通核心流程 |
| 正式版 | 独立服务 + 本地加密 + 云端密文 | 隐私优先 |
| 企业版 | 支持私有化部署 | 投顾机构需要 |

```
AKShare/东方财富 → 数据系统 → API → 各端
                            ↓
                      知识系统（RAG）
                            ↓
                      分析引擎（六步流程）
                            ↓
                      Skill包（framework-skill）
```

---

## 九、已确认决策

| 决策点 | 确认方案 |
|--------|---------|
| API 协议 | to Agent (MCP) + to Human (REST) 双轨并存 |
| 密钥管理 | 微信扫码社交登录 |
| 投顾数据归属 | 归投顾私有，服务端加密存储 |
| 终端迁移 | 自动从云端下载（微信登录后） |
| 同步冲突 | 最后写入胜出 |
| 投顾助手权限 | 需投顾授权才能访问客户数据 |

---

## 十、投顾助手（AI Agent）权限模型

```
投顾（人）→ 完全控制
    ↓授权
投顾的 AI Agent → 经授权可访问客户数据
    ↓
助手（如果有）→ 经投顾授权可有限访问
```

**典型授权场景**：
- "帮我分析客户A的持仓" → AI Agent 临时授权访问
- AI Agent 自动生成客户周报 → 批量授权读取
- 投顾可随时撤销授权

---

##十一、下一步

- [ ] 细化 MCP Server 接口设计
- [ ] 设计 Skills 同步机制
- [ ] 规划数据加密实现方案
- [ ] 制定各产品的开发优先级