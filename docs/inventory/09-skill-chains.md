# 09 Skill 串接

> 来源：PROJECT_INVENTORY.md 需求 5
> 主题：Skill 调用引擎 + 串接规则配置化 + 核心 Skill Schema + 降级策略

---

## 5.1 Skill 调用引擎

### 核心设计

- Skill 是独立的能力单元，有标准输入/输出
- 串接规则配置化，支持流程编排
- 支持条件分支（根据上一步结果决定下一步调用哪个 Skill）

### 配置结构

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

### 调用流程

1. 解析串接规则
2. 按顺序执行 Skill
3. 每步 Skill 输出作为下一步输入的一部分
4. 错误处理：某步失败可选择跳过或终止
5. 记录调用日志（输入/输出/耗时/错误）

---

## 5.2 Skill 输入/输出 Schema（核心 Skills）

### business-model-classifier

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

### financial-report-analyzer

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

### moat-evaluator

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

### intrinsic-value-calculator

```json
// 输入
{"company_id": "string", "method": "DCF|DDM", "assumptions": {}}

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

### fund-analyzer-pro

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

---

## 5.3 Skill 调用超时与降级策略（自进化补充）

### 超时配置

| Skill 类型 | 默认超时 | 重试策略 |
|-----------|---------|---------|
| 数据校验类（data_validator） | 10s | 重试 1 次 |
| 分类识别类（business-model, fund-style） | 15s | 重试 1 次 |
| 分析推理类（moat, intrinsic-value, financial-report） | 30s | 重试 1 次 |
| 复杂计算类（fund-analyzer-pro） | 45s | 不重试，直接降级 |

### 降级策略

| 失败场景 | 处理方式 |
|---------|---------|
| 超时 | 标记该步"超时"，使用默认值/缓存值继续 |
| 数据不足 | 跳过该步，标注"数据不足，推理受限" |
| 模型不可用 | 回退到上一步，等待恢复后重试 |
| 输出格式错误 | 重试 1 次，仍失败则标记"格式异常" |

### 调用链保护

- 最大链式深度：6 步（与六步分析一致）
- 单次完整分析总超时上限：300s
- 失败累计 > 2 步时，终止整条链，输出"分析不完整"

---

## 关联

- 引擎核心代码：`D:\claudework\workspace\mangofolio\core\engine\`
- 引擎落地映射：见 [19-component-map.md](./19-component-map.md)
- 三层六步：见 [06-layer-macro.md](./06-layer-macro.md) / [07-layer-event.md](./07-layer-event.md) / [08-layer-entity.md](./08-layer-entity.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- Skill 清单：见 [14-skills.md](./14-skills.md)
