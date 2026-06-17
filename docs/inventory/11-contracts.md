# 11 数据契约

> 来源：PROJECT_INVENTORY.md 需求 7
> 主题：六步分析 JSON Schema + 提炼传递 + 多 Agent 契约 + Schema 版本管理

---

## 目标

为将来拆分为多 Agent 管道预留接口标准

---

## 7.1 六步分析 JSON Schema

### Step 0 校验

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

### Step 1 拆解

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

### Step 2 传导

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

### Step 3 历史

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

### Step 4 情景

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

### Step 5 行动

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

### Step 6 失效

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

---

## 7.2 提炼传递规则

### 核心原则

**只传递判断结果，不传递分析过程**

| 传递内容 | 是否传递 | 说明 |
|----------|---------|------|
| 核心变量 + 取值 | ✅ | 用于下游推理 |
| 置信度 | ✅ | 下游判断是否采信 |
| 关键假设 | ✅ | 下游评估风险 |
| 待验证项 | ✅ | 下游决定是否补充 |
| 完整分析文本 | ❌ | 浪费 token，下游不需要 |
| 中间计算过程 | ❌ | 只需要最终判断 |

### 传递格式

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

---

## 7.3 Agent 间数据传递（多 Agent 演进后）

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

### 演进检查点

- 当某步成为瓶颈（耗时过长）时，考虑拆分为独立 Agent
- 当某步需要不同模型时（简单校验 vs 复杂推理），拆分
- 拆分后的 Agent 必须符合上述数据契约

---

## 7.4 提炼传递量化标准与版本管理（自进化补充）

### 提炼传递量化规则

| 传递项 | 最大数量 | 超出处理 |
|-------|---------|---------|
| core_variables | ≤ 5 个 | 按重要性排序截断 |
| key_assumptions | ≤ 3 条 | 保留最关键假设 |
| pending_validations | ≤ 3 项 | 保留最高优先级 |
| 传给下一步的 assumptions | ≤ 2 条 | 仅传递直接影响下一步的 |

### Schema 版本管理

- 格式：`v{大版本}.{小版本}.{补丁}`（SemVer）
- 大版本增长：字段增删或类型变更（不向下兼容）
- 小版本增长：新增可选字段（向下兼容）
- 补丁版本增长：描述/注释/示例更新
- **当前版本：`v1.0.0`**
- Agent 间传递时必须携带 `schema_version` 字段
- 接收方校验版本兼容性，不兼容时回退到上一步

### 版本兼容矩阵

| 接收方 \ 发送方 | v1.0.x | v1.1.x | v2.0.x |
|----------------|--------|--------|--------|
| v1.0.x | ✅ 兼容 | ⚠️ 忽略额外字段 | ❌ 不兼容 |
| v1.1.x | ✅ 兼容 | ✅ 兼容 | ❌ 不兼容 |
| v2.0.x | ❌ 不兼容 | ❌ 不兼容 | ✅ 兼容 |

---

## 关联

- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 三层六步：见 [06-layer-macro.md](./06-layer-macro.md) / [07-layer-event.md](./07-layer-event.md) / [08-layer-entity.md](./08-layer-entity.md)
- Skill 串接：见 [09-skill-chains.md](./09-skill-chains.md)
- 信号系统：见 [05-signal-system.md](./05-signal-system.md)
- 引擎落地：见 [19-component-map.md](./19-component-map.md)
