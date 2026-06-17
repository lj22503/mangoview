# 投资技能系统对比分析报告

**分析日期**: 2026-06-04
**分析对象**: ranbing skill (D:\ranbing) vs investment-framework-skill (C:\tmp)

---

## 1. 当前状态总结

### 系统A — ranbing skill（160个技能）

**核心定位**: 专业行业研究与投资分析技能库，来源为专业投资书籍通过 pdf2skills 流水线转换生成。

**顶层架构**: `industry-research-workflow` 路由器，分5阶段推进：数据收集→行业分析→公司分析→估值→报告输出。

**技能特点**:
- 高度细粒度、垂直化的行业技能（5G、水泥、煤炭、银行、电子、白酒等）
- 每个技能对应书籍中的特定章节或知识点
- 数据层依赖 `data_utils.py`（AKShare + Tushare实时数据）
- 技能命名采用"行业-功能"结构（如 `cement-industry-demand-and-competition-analysis`）

**优势**: 覆盖大量细分行业，研究深度强，数据驱动
**劣势**: 缺乏框架层整合，技能之间协调性弱，重研究轻决策

### 系统B — investment-framework-skill（~30个技能）

**核心定位**: 基于经典投资书籍的手工构建决策框架系统，侧重投资决策流程。

**顶层架构**: `investment-framework-skill` (v4.1.0) 单一主技能，路由到子技能。

**技能特点**:
- 框架级技能（价值分析、护城河评估、内在价值计算、决策清单）
- 大师系列（中国李录、邱国鹭、段永平、吴军、林森池）
- 数据层多API集成（QVeris、东方财富、新浪财经、港交所等）
- 技能命名采用"功能-角色"结构（如 `moat-evaluator`、`value-analyzer`）

**优势**: 决策流程清晰，框架完整，大师智慧集成
**劣势**: 行业覆盖浅，缺乏细分行业深度，数据层与A系统存在潜在重叠

---

## 2. 重叠分析

### 2.1 功能重叠（按领域分组）

| 领域 | 系统A技能 | 系统B技能 | 重叠程度 | 说明 |
|------|---------|---------|---------|------|
| **行业研究** | `industry-research-framework`, `industry-analysis-framework`, `industry-business-model-analysis`, `industry-key-indicators-analysis` | `industry-analyst`, `industry-specialist` | 高 | A覆盖广而深，B覆盖框架层面 |
| **估值** | `stock-valuation-methods`, `market-approach-valuation`, `maotai-moat-and-valuation-analysis` | `intrinsic-value-calculator`, `valuation-analyzer` | 高 | A有具体行业估值案例，B有通用估值框架 |
| **护城河/竞争优势** | `maotai-moat-and-valuation-analysis`（茅台案例） | `moat-evaluator` | 中 | B有系统化护城河评估方法，A仅茅台案例 |
| **财务分析** | `financial-ratio-and-dupont-analysis` | `quality-analyzer` | 中 | A偏财务比率，B偏财务质量与造假识别 |
| **宏观周期** | `macroeconomic-cycle-analysis`, `merrill-lynch-investment-clock-asset-allocation` | `cycle-locator` | 中 | A有美林时钟具体应用，B有周期定位框架 |
| **数据收集** | `industry-research-data-collection` | `data-driven-investor` | 低 | A偏行业数据收集方法论，B偏量化因子 |
| **资产配置** | 无直接对应 | `asset-allocator`, `portfolio-designer`, `global-allocator` | 无 | A无资产配置相关技能 |
| **决策检查** | 无直接对应 | `decision-checklist`, `bias-detector` | 无 | A无认知偏差检测 |

### 2.2 重叠技能详细对照

| 重叠类型 | 系统A示例 | 系统B示例 | 评价 |
|---------|---------|---------|-----|
| 估值方法论 | `stock-valuation-methods` — DCF/PE/PB/PS | `intrinsic-value-calculator` — 4种估值方法+安全边际 | B更框架化，A有具体行业案例 |
| 行业分析框架 | `industry-analysis-framework` — 九要素/波特五力 | `industry-analyst` — 竞争格局/产业链 | A更体系化，B更精简 |
| 公司竞争力 | `company-bargaining-power-assessment`, `pricing-power-analysis` | `moat-evaluator` | B更系统，A偏细分指标 |
| 财务比率 | `financial-ratio-and-dupont-analysis` | `quality-analyzer` | A偏比率计算，B偏质量与风险 |
| 周期分析 | `macroeconomic-cycle-analysis`, `merrill-lynch-investment-clock-asset-allocation` | `cycle-locator` — 美林时钟 | A有具体应用场景，B有框架 |

**结论**: 两系统在高层次功能上存在明显重叠，但实现深度不同。A系统偏向垂直行业深度，B系统偏向横向决策框架。

---

## 3. 冲突分析

### 3.1 功能定位冲突

| 冲突点 | 系统A | 系统B | 冲突说明 |
|-------|------|------|---------|
| **输出格式** | 行业研究报告格式（自由文本） | 严格JSON格式（结构化） | 两者输出规范不统一 |
| **触发机制** | 行业+场景触发（如"分析水泥行业"） | 意图识别触发（如"分析这只股票"） | 用户交互方式不同 |
| **分析角度** | 自上而下（行业→公司→估值） | 自下而上结合（个股→行业→宏观反哺） | 分析路径差异 |
| **数据依赖** | AKShare + Tushare（实时） | 多API集成（QVeris、东方财富等） | 数据源可能有差异 |

### 3.2 潜在逻辑冲突

| 场景 | 系统A处理方式 | 系统B处理方式 | 是否冲突 |
|-----|------------|------------|--------|
| 茅台估值 | 基于护城河的DCF溢价模型（高成长假设） | 格雷厄姆标准+巴菲特护城河+安全边际 | 不冲突，但侧重点不同 |
| 周期定位 | 美林时钟资产配置 | 第二层思维+周期定位 | 不冲突，可互补 |
| 认知偏差 | 无 | 25种偏差识别+干预策略 | A缺失该维度 |
| 行业分析 | 细分行业完整框架 | 通用行业分析框架 | A更优，B可调用A |

### 3.3 冲突结论

两系统**不存在根本性冲突**，更多是**功能互补**。主要张力在于：
1. 输出格式不统一（文本报告 vs JSON结构化）
2. 触发机制不同（场景触发 vs 意图触发）
3. 数据层潜在重复但无直接矛盾

---

## 4. 差距分析（Gaps）

### 4.1 系统A独有内容（系统B缺失）

| 差距领域 | 说明 |
|--------|------|
| **细分行业覆盖** | 160个技能覆盖80+细分行业（5G/水泥/煤炭/银行/白酒/家电/光伏/半导体等），B完全没有这些行业的垂直分析能力 |
| **数据收集方法论** | `industry-research-data-collection` 专项技能，A有完整方法论，B无对应技能 |
| **行业生命周期** | `industry-policy-lifecycle-analysis` — 政策环境与行业生命周期，B无对应 |
| **供应链分析** | `supply-chain-integration-assessment`, `company-bargaining-power-assessment` |
| **公司治理** | `major-shareholder-harm-detection` — 大股东侵害识别 |
| **工具性技能** | 分级基金、可转债、资产证券化、期权、ETF等具体产品分析 |
| **现场调研** | `field-research-and-interview` — 实地调研方法论 |

### 4.2 系统B独有内容（系统A缺失）

| 差距领域 | 说明 |
|--------|------|
| **投资决策框架** | 格雷厄姆标准、芒格决策清单、巴菲特护城河等经典框架，A仅有茅台案例 |
| **认知偏差检测** | 卡尼曼25种认知偏差识别与干预，A完全缺失 |
| **第二层思维** | 霍华德·马克斯第二层思维训练 |
| **资产配置** | 生命周期配置、耶鲁模式、全球分散，B有完整体系 |
| **中国大师系列** | 李录、邱国鹭、段永平、吴军等中国投资者思想，A仅有茅台案例 |
| **市场经济专利** | 林森池《投资王道》独特概念，A无对应 |
| **千里马筛选** | 林森池七准则筛选器 |
| **风险评估** | 独立风险评估技能（已规划未实现） |
| **市场情绪** | 情绪分析技能（已规划未实现） |

### 4.3 两系统共同缺失（与MangoView对比）

| 缺失领域 | MangoView需求 | 说明 |
|---------|-------------|------|
| **宏观→行业→个股自上而下流程** | 设计文档明确要求"自上而下，看清每一笔投资" | 两系统均缺乏将该流程标准化的技能 |
| **统一输出格式** | MangoView需要标准化数据展示 | 当前两系统输出格式不统一 |
| **投资组合层面** | 多股票组合分析/对比 | 两系统均聚焦单股票分析 |
| **风险管理量化** | 止损/仓位管理/风险敞口 | 两系统均偏定性分析 |

---

## 5. 统一分类法提案

基于两系统互补性与MangoView设计原则，建议建立以下统一顶层分类：

### 5.1 一级分类（5大类）

```
┌─────────────────────────────────────────────────────┐
│              投资分析技能统一 Taxonomy                │
├─────────────────────────────────────────────────────┤
│  L1 宏观层（Macro）                                   │
│  L1  行业层（Industry）  ← 新增 ljg-rank             │
│  L1  公司层（Company）  ← 新增 ljg-invest           │
│  L1  组合层（Portfolio）                             │
│  L1  工具层（Tools）     ← 缺失较多，待补             │
└─────────────────────────────────────────────────────┘
```

### 5.2 新增：ljg-rank → 行业层（降秩引擎）

| 名称 | 描述 | 层级 |
|------|------|------|
| `ljg-rank` | 输入一个领域，输出它的秩（独立生成器数量）。十几个现象砍到不可再少的生成器。触发词：降秩/找秩/秩是什么/背后是什么。 | L1-行业层 |

**核心逻辑**：生成性×最小性×独立性×预测力，四条心内判据。不是关键要素，而是真正独立的生成器。

---

### 5.3 新增：ljg-invest → 公司层（秩序创造机器判定）

| 名称 | 描述 | 层级 |
|------|------|------|
| `ljg-invest` | 投资分析报告生成器，核心判断项目是否是"秩序创造机器"。不是传统估值——看飞轮、冲击后变强、资源自引。触发词：投资报告/投资分析/写投资报告。 | L1-公司层 |

**核心逻辑**：不称重，看相——不問值多少钱，问机器转不转得起来。五个区块：这是什么/秩序创造机器判定/创生公式/市场看见的vs我们看见的/换不换。

---

### 5.4 二级分类与技能归属（修订版）

#### L1-宏观层（Macro）

| L2 | 技能来源 | 具体技能 |
|----|---------|---------|
| 经济周期 | B | `cycle-locator` |
| 宏观趋势 | A | `macroeconomic-cycle-analysis`, `three-economic-drivers-framework` |
| 债券市场 | A | `macroeconomic-bond-market-analysis` |
| 货币信贷 | A | `money-credit-system-analysis` |
| 未来预测 | B | `future-forecaster` |

#### L1-行业层（Industry）

| L2 | 技能来源 | 具体技能 |
|----|---------|---------|
| 行业分析框架 | A+B | A: `industry-analysis-framework`, B: `industry-analyst` |
| 行业特解指标 | B | `industry-specialist` |
| 细分行业 | A | 160个技能中的行业技能（5G/水泥/煤炭/白酒等） |
| 产业链分析 | A | `industry-business-model-analysis`, `industry-competitive-landscape-analysis` |
| 政策生命周期 | A | `industry-policy-lifecycle-analysis` |
| AI趋势 | B | `ai-trend-analyzer` |
| 降秩引擎 | 新增 | `ljg-rank` — 领域独立生成器分解 |

#### L1-公司层（Company）

| L2 | 技能来源 | 具体技能 |
|----|---------|---------|
| 价值分析 | B | `value-analyzer` |
| 护城河评估 | B | `moat-evaluator` |
| 内在价值 | B | `intrinsic-value-calculator` |
| 估值分析 | A+B | A: `stock-valuation-methods`, B: `valuation-analyzer` |
| 财务质量 | A+B | A: `financial-ratio-and-dupont-analysis`, B: `quality-analyzer` |
| 市场经济专利 | B | `market-patent-evaluator` |
| 千里马筛选 | B | `thousand-mile-horse-screener` |
| 定价能力 | A | `pricing-power-analysis` |
| 供应链议价 | A | `company-bargaining-power-assessment` |
| 大股东治理 | A | `major-shareholder-harm-detection` |
| 增长策略评估 | A | `growth-strategy-feasibility-assessment` |
| 秩序创造机器 | 新增 | `ljg-invest` — 投资报告生成，判断项目是否创造新秩序 |

#### L1-组合层（Portfolio）

| L2 | 技能来源 | 具体技能 |
|----|---------|---------|
| 选股 | B | `stock-picker` |
| 资产配置 | B | `asset-allocator`, `global-allocator` |
| 组合设计 | B | `portfolio-designer` |
| 简单投资 | B | `simple-investor` |
| 长期持有检查 | B | `longterm-checker` |

#### L1-工具层（Tools）← 缺失较多，待补

| L2 | 技能来源 | 具体技能 | 状态 |
|----|---------|---------|------|
| 数据收集 | A | `industry-research-data-collection`, `data-analysis-three-steps` | ✅ 已有 |
| 决策检查 | B | `decision-checklist`, `bias-detector` | ✅ 已有 |
| 第二层思维 | B | `second-level-thinker` | ✅ 已有 |
| 中国大师 | B | `china-masters`, `li-lu`, `qiu-guolu`, `duan-yongping`, `wu-jun` | ✅ 已有 |
| 现场调研 | A | `field-research-and-interview` | ✅ 已有 |
| 数据驱动 | A+B | A: `data-analysis-pitfalls-and-avoidance`, B: `data-driven-investor` | ✅ 已有 |
| 非基本面 | A | `non-fundamental-stock-research` | ✅ 已有 |
| 产品设计 | A | `passive-index-investing-product-design`, `structured-product-design` | ✅ 已有 |
| **事件研判** | B系统 | `fanli-analyzer` — 范蠡商情四步心法（采集/选择/判定/分析） | 🆕 待整合 |
| **基金分析** | B系统 | `fund-analyzer-pro` — 基金深度分析+且慢MCP+天天基金API | 🆕 待整合 |
| **基金持仓** | B系统 | `fund-holding-analyzer` — 持仓分析 | 🆕 待整合 |
| **风险量化** | B | `risk-assessor`（规划中未实现） | ❌ 缺失 |
| **情绪分析** | B | `sentiment-analyzer`（规划中未实现） | ❌ 缺失 |
| **回测** | B | `backtester`（规划中未实现） | ❌ 缺失 |
| **宏观数据获取** | A | `get_consumer_macro_summary`等data_utils函数 | ⚠️ 数据函数非skill |
| **研报复现** | A | `industry-report-reading-and-writing` | ⚠️ 偏写作 |
| **数据陷阱识别** | A | `data-analysis-pitfalls-and-avoidance` | ✅ 已有 |
| **MangoView接入** | 新设计 | 统一JSON输出+前端展示 | ❌ 未建立 |

### 5.5 工具层缺口详解

**B系统规划但未实现的技能**：
- `risk-assessor` — 独立风险量化（VaR/止损/仓位）
- `sentiment-analyzer` — 市场情绪分析（涨跌家数/杠杆资金/北向资金）
- `backtester` — 策略回测框架

**A系统缺失的工具性技能**：
- 没有与B系统 `fanli-analyzer`（事件研判）对应的技能
- 没有系统化的基金分析技能（`fund-analyzer-pro`）
- 数据层（`data_utils.py`）是函数不是skill，无法被路由调用

**建议补充优先级**：

| 优先级 | 技能 | 说明 |
|--------|------|------|
| P0 | `fanli-analyzer` | 事件研判，范蠡四步心法，已存在于B系统 |
| P0 | 数据函数→skill | 将 `get_consumer_macro_summary` 等封装为skill |
| P1 | `fund-analyzer-pro` | 基金分析，且慢MCP+天天基金 |
| P1 | `risk-assessor` | 风险量化，VaR/止损/仓位管理 |
| P2 | `sentiment-analyzer` | 市场情绪，跟踪资金/涨跌家数 |
| P2 | `backtester` | 策略回测框架 |
| P3 | 统一输出格式 | JSON Schema + MangoView接入 |

### 5.6 统一路由器架构

```
investment-assistant (主路由器)
├── macro-route → 宏观层技能组
│   ├── cycle-locator
│   ├── macroeconomic-cycle-analysis
│   └── future-forecaster
├── industry-route → 行业层技能组
│   ├── ljg-rank                    ← 降秩引擎（新增）
│   ├── industry-analyst (通用框架)
│   ├── industry-specialist (特解指标)
│   └── [细分行业技能池] ← A系统160个技能按行业分组
├── company-route → 公司层技能组
│   ├── ljg-invest                  ← 秩序创造机器判定（新增）
│   ├── value-analyzer
│   ├── moat-evaluator
│   ├── intrinsic-value-calculator
│   ├── valuation-analyzer
│   └── quality-analyzer
├── portfolio-route → 组合层技能组
│   ├── stock-picker
│   ├── asset-allocator
│   └── portfolio-designer
└── tools-route → 工具层技能组
    ├── fanli-analyzer              ← 事件研判（待整合）
    ├── decision-checklist
    ├── bias-detector
    ├── fund-analyzer-pro           ← 基金分析（待整合）
    ├── risk-assessor               ← 风险量化（待实现）
    ├── sentiment-analyzer          ← 情绪分析（待实现）
    └── [数据获取skill]             ← data_utils封装（待实现）
```

---

## 6. 整合建议

### 6.1 整合优先级

| 优先级 | 整合项 | 方案 |
|--------|-------|------|
| **P0** | 统一输出格式 | JSON Schema，两系统强制遵循 |
| **P0** | 建立主路由器 | 以B系统 `investment-framework-skill` 为主路由器 |
| **P0** | fanli-analyzer整合 | 事件研判四步心法，已有，直接并入tools-route |
| **P0** | 数据函数→skill | 将 `data_utils.py` 封装为可路由的数据获取skill |
| **P1** | A系统行业技能接入 | A系统160个技能作为 `industry-route` 行业技能池 |
| **P1** | ljg-rank/ljg-invest | 已有，直接并入对应层级 |
| **P1** | fund-analyzer-pro | 基金分析技能，已有直接并入 |
| **P1** | risk-assessor | 实现缺失的风险量化skill |
| **P2** | 决策框架补全 | 在行业分析流程中强制嵌入决策检查节点 |
| **P2** | sentiment-analyzer | 实现缺失的情绪分析skill |
| **P2** | backtester | 实现缺失的回测skill |
| **P3** | MangoView对接 | 统一JSON输出+前端展示 |

### 6.2 整合实施路径

**阶段1：架构统一（1-2周）**
- 确定统一Taxonomy（采纳第5节提案）
- 建立主路由器，定义L1-L2调用规范
- 统一输出JSON Schema

**阶段2：技能映射（2-4周）**
- 将A系统行业技能映射到 `industry-route`
- 将B系统决策技能映射到对应层级
- 建立技能交叉引用表

**阶段3：数据整合（2-4周）**
- 合并数据层API
- 建立统一数据缓存层
- 消除数据重复获取

**阶段4：流程嵌入（持续）**
- 在A系统行业分析流程中嵌入B系统决策检查节点
- 在B系统决策流程中嵌入A系统行业验证节点
- 与MangoView设计系统对接

### 6.3 关键风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|-----|---------|
| 技能数量过多导致路由混乱 | 用户请求无法正确匹配技能 | 建立清晰的技能注册表+意图识别训练 |
| 两系统输出格式不统一 | 下游系统难以处理 | 定义标准JSON Schema，两系统强制遵循 |
| 行业技能与决策框架脱节 | 分析结果无法落地 | 在主路由器层强制执行"行业验证+决策检查"联合流程 |
| 数据源冲突 | 同一指标数据不一致 | 建立单一数据真相源（Single Source of Truth） |

---

## 附录：关键文件索引

| 文件 | 路径 |
|-----|------|
| ranbing技能索引 | `D:\ranbing skill\full_chunks_skus\generated_skills\index.md` |
| investment-framework技能清单 | `C:\tmp\investment-framework-skill\COMPLETE_SKILLS_INVENTORY.md` |
| investment-framework主技能 | `C:\tmp\investment-framework-skill\SKILL.md` |
| MangoView设计文档 | `C:\tmp\mangoview\DESIGN.md` |
| ljg-rank | `D:\claudework\cc skill\skills\skills\ljg-rank\SKILL.md` |
| ljg-invest | `D:\claudework\cc skill\skills\skills\ljg-invest\SKILL.md` |
| fanli-analyzer | `C:\tmp\investment-framework-skill\skills\event-analyzer\SKILL.md` |
| data_utils（数据层） | `D:\ranbing skill\data_utils.py` |

---

**分析结论**：

四系统定位互补性大于竞争性。A系统擅长细分行业深度，B系统擅长决策框架广度，C系统（D:\ranbing skill）补充pdf2skills行业知识，D系统（ljg-rank/ljg-invest）提供原创降秩与秩序创造机器方法论。整合关键：

1. 以B系统（`investment-framework-skill`）为主路由器，接入A系统160个行业技能池
2. 行业层新增 `ljg-rank`（降秩引擎），公司层新增 `ljg-invest`（秩序创造机器）
3. 工具层优先整合 `fanli-analyzer`（事件研判）和 `fund-analyzer-pro`（基金分析）
4. 工具层缺口最大：risk-assessor、sentiment-analyzer、backtester、数据获取skill均未实现
5. 建立统一JSON Schema，对齐MangoView自上而下设计原则

整合后建议技能总数：~200个
- A系统（ranbing skill）：160个（细分行业）→ industry-route
- B系统（investment-framework）：~30个（决策框架）→ 主路由器+各层
- C系统（ljg-rank/ljg-invest）：2个（降秩+秩序判定）→ 各归其层
- 待实现工具skill：5个（risk/sentiment/backtester等）
- 数据获取skill：1个（data_utils封装）→ tools-route
