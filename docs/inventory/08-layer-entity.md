# 08 人和层（实体）

> 来源：PROJECT_INVENTORY.md 需求 4
> 主题：上市公司 + 基金的六步分析
> 完成标准与回退：见末尾"自进化补充"小节

---

## 目标

上市公司和基金的六步分析

---

## 4.1 公司分析（六步 + Skill）

### Step 0 校验
- 输入：公司财报/公告/研报
- 处理：来源可信度、完整性偏差检测
- 输出：`{source_credibility, bias_types[], final_rating}`

### Step 1 拆解
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
| SaaS | ARR 增长率、净留存率(NRR)、客户获取成本(CAC)、毛利率 |
| 制造业 | 产能利用率、订单积压、库存周转、资本支出 |
| 银行 | 净息差(NIM)、存款成本、贷款增长率、不良贷款率(NPL) |
| 平台 | DAU/MAU、变现率(Take rate)、网络效应 |
| 零售 | 同店销售、库存周转、坪效 |

### Step 2 传导
- 输入：核心变量
- 处理：构建变量间传导路径
  - 收入增长 → 利润率变化 → 现金流 → 资产负债表
  - 管理层决策 → 竞争优势 → 长期价值
- 输出：因果链 + 反馈回路 + 阻滞点

### Step 3 历史
- 输入：公司历史财务数据 + 行业历史
- 处理：检索相似公司/历史时期
  - Skill 调用：`financial-report-analyzer`（财报四层分析）
- 输出：历史表现 + 关键转折点 + 可迁移模式

### Step 4 情景
- 输入：传导路径 + 历史模式 + 行业周期
- 处理：生成基准/乐观/悲观情景
  - Skill 调用：`moat-evaluator`（护城河评估）
  - Skill 调用：`intrinsic-value-calculator`（内在价值计算 DCF/DDM）
- 输出：情景概率 + 估值区间 + 分叉点

### Step 5 行动
- 输入：情景 + 估值
- 处理：vs 当前股价计算预期差
  - Skill 调用：`bias-detector`（认知偏差检测）
- 输出：信号（低估/合理/高估）+ 置信度 + 行动建议

### Step 6 失效
- 输入：情景假设
- 处理：定义失效条件 + 监控指标
- 输出：退出信号 + 监控频率

### Skill 串接规则

```
公司分析：
business-model-classifier → financial-report-analyzer → moat-evaluator
→ intrinsic-value-calculator → bias-detector → decision-checklist
```

**输出**：公司信号（低估/合理/高估）+ 目标价区间 + 置信度 + 失效条件

---

## 4.2 基金分析（六步 + Skill）

### Step 0 校验
- 输入：基金季报/年报 + 净值数据 + 持仓数据
- 处理：数据完整性、利益相关性检测
- 输出：`{source_credibility, bias_types[], final_rating}`

### Step 1 拆解
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

### Step 2 传导
- 输入：基金收益分解
- 处理：归因分析
  - 收益 = alpha + beta × 市场收益 + 行业暴露 × 行业收益 + 风格暴露 × 风格收益
  - 识别收益来源（选股/择时/行业/风格）
- 输出：收益分解 + 各因子贡献度 + 稳定性评估

### Step 3 历史
- 输入：基金历史表现 + 同类基金对比
- 处理：
  - Skill 调用：`fund-analyzer-pro`（业绩归因/风险分析/经理能力）
  - 检索同类基金表现
- 输出：历史归因 + 能力持续性 + vs 同类排名

### Step 4 情景
- 输入：当前宏观环境 + 行业周期
- 处理：判断基金策略在当前环境的适应性
- 输出：情景分析（有利/中性/不利情景概率）

### Step 5 行动
- 输入：情景分析 + 基金信号
- 处理：
  - Skill 调用：`bias-detector`
- 输出：基金信号（推荐/中性/回避）+ 理由 + 适用场景

### Step 6 失效
- 输入：情景假设
- 处理：定义经理能力失效条件、策略失效条件
- 输出：监控指标（净值回撤、换手率变化、持仓集中度）+ 退出信号

### Skill 串接规则

```
基金分析：
fund-style-classifier → fund-analyzer-pro → bias-detector → decision-checklist
```

**输出**：基金信号（推荐/中性/回避）+ 置信度 + 适用场景 + 失效条件

**验收标准**：
- 公司分析和基金分析模块独立
- 输出符合统一信号模型（需求 1 定义的数据结构）

---

## 4.3 人和层每步完成标准与回退机制（自进化补充）

| 步骤 | 通过条件 | 未通过处理 |
|------|---------|-----------|
| Step 0 校验 | source_credibility ≥ 0.5 | < 0.3 直接拒绝；0.3-0.5 标记后继续 |
| Step 1 拆解 | core_variables ≤ 5 个 + 商业模式分类置信度 ≥ 0.4 | > 5 合并；分类置信度 < 0.4 回退到 Step 0 |
| Step 2 传导 | 归因分解完整（公司：收入/利润/现金流；基金：alpha/beta/行业暴露） | 不完整回退到 Step 1 |
| Step 3 历史 | 相似案例 ≥ 1 个或归因数据完整 | 无数据则标注"缺乏历史参考" |
| Step 4 情景 | 估值区间完整（bull/base/bear 三个值） | 数据不足则仅输出基准情景 |
| Step 5 行动 | 信号方向明确 + 约束自检通过 | 约束不通过输出"条件不具备，等待" |
| Step 6 失效 | exit_signals ≥ 1 条 | 0 条标"未定义退出条件，风险上升" |

---

## 关联

- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 信号系统：见 [05-signal-system.md](./05-signal-system.md)
- 天时层：见 [06-layer-macro.md](./06-layer-macro.md)
- 地利层：见 [07-layer-event.md](./07-layer-event.md)
- Skill 串接详细 Schema：见 [09-skill-chains.md](./09-skill-chains.md)
