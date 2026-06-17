# 03 超级系统站

> 来源：PROJECT_INVENTORY.md 第三章 3.1-3.3
> 主题：超级系统站的三大子系统（知识系统 / 通用能力 / 数据系统）
> 注意：分析引擎单独成篇，详见 [04-analysis-engine.md](./04-analysis-engine.md)

---

## 3.1 知识系统

**定位**：投资相关的结构化知识，可被各端查询调用

**组成**：

| 模块 | 内容 | 调用方式 |
|------|------|---------|
| 大师思想库 | 巴菲特/芒格/段永平/马克斯等的投资思想 | RAG 检索 |
| 行业知识 | 估值体系、周期模型、分析框架 | 查询 |
| 案例库 | 历史事件、情景推演结果 | 检索 |

**文件位置**：`D:\claudework\workspace\mangoview\skills\investment-framework-skill\china-masters\`

---

## 3.2 通用能力系统

**定位**：跨场景通用的分析能力，所有端都可用

| 能力 | 功能 | 特点 |
|------|------|------|
| risk-assessor | 风险评估（市场/信用/流动性） | 通用 |
| sentiment-analyzer | 市场情绪分析（贪婪恐惧/拥挤度） | 通用 |
| bias-detector | 认知偏差检测（确认偏误/损失厌恶等） | 通用 |
| decision-checklist | 芒格多元思维决策检查 | 通用 |

**文件位置**：`D:\claudework\workspace\mangoview\skills\investment-framework-skill\`

---

## 3.3 数据系统

**定位**：外部业务数据的采集、清洗、存储

**数据源**：

| 数据类型 | 来源 | 状态 |
|----------|------|------|
| 宏观数据（PMI/CPI/GDP/M2/社融） | AKShare | ✅ 已接入 |
| 北向资金 | AKShare | ✅ 已接入 |
| 行业板块 | AKShare（受限） | ⚠️ Fallback |
| 指数/个股行情 | 东方财富（IP 受限） | ❌ 待解决 |
| 基金数据 | 天天基金 | ✅ 已接入 |

**接口**：统一 API，各端通过 API 获取数据

---

## 关联

- 品牌架构：见 [01-brand.md](./01-brand.md)
- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- 路径速查：见 [15-paths.md](./15-paths.md)
