# 05 信号系统

> 来源：PROJECT_INVENTORY.md 需求 1
> 主题：Signal 数据模型 + 聚合算法 + API + 有效期/准确度

---

## 目标

建立信号系统的核心数据模型和接口标准

---

## 1.1 Signal 数据模型

```json
{
  "signal_id": "string",                          // UUID，唯一标识
  "layer": "enum[TIANSHI|DILI|RENHE]",            // 信号层
  "sub_layer": "string|null",                     // 子层，如 ECONOMIC_CYCLE/INDUSTRY/EVENT
  "entity_type": "string|null",                   // 实体类型：stock/fund/event/macro
  "entity_id": "string|null",                     // 实体标识：股票代码/基金代码等

  "signal_type": "string",                        // 信号类型：周期位置/行业机会/事件驱动
  "direction": "enum[BULLISH|BEARISH|NEUTRAL]",   // 方向
  "intensity": "enum[STRONG|MEDIUM|WEAK]",        // 强度

  "confidence": "number[0-1]",                    // 置信度 0-1
  "key_variables": [                              // 关键变量（提炼传递用）
    {"name": "string", "value": "any", "importance": "enum[HIGH|MEDIUM|LOW]"}
  ],
  "key_assumptions": ["string"],                  // 关键假设
  "pending_validations": ["string"],              // 待验证项

  "invalidation_conditions": [                    // 失效条件
    {"variable": "string", "threshold": "any", "direction": "string"}
  ],
  "monitoring_frequency": "enum[DAILY|WEEKLY|EVENT_DRIVEN]",

  "source_data_timestamp": "datetime",
  "analysis_timestamp": "datetime",
  "valid_until": "datetime|null",
  "step_completed": "number[0-6]",

  "access_tier": "enum[FREE|BASIC|VIP]"           // 可访问层级
}
```

**JSON Schema 约束**：
- `confidence` 必须是 0-1 的数字，不能是 NaN/Inf
- `key_variables` 最多 5 个
- 所有字符串字段不能为 null，必要字段不能为空数组

---

## 1.2 信号聚合层

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

---

## 1.3 信号 API

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/signal/{layer}` | GET | 获取某层信号列表 |
| `/api/v1/signal/{layer}/{entity_id}` | GET | 获取某实体信号 |
| `/api/v1/signal/aggregate` | GET | 获取聚合信号 |
| `/api/v1/signal/trigger` | POST | 触发事件分析（横向 Scale 筛选后的深度分析） |

**查询参数**：
- `tier`：过滤可见层级（FLOAT 公共 / BASIC 付费 / VIP）
- `entity_type`：过滤实体类型
- `since`：时间范围
- `min_confidence`：最低置信度

**验收标准**：
- 信号模型可序列化，无 NaN/Inf
- API 响应时间 < 500ms
- 各层信号可独立获取，也可聚合

---

## 1.4 信号质量与评估周期（自进化补充）

### 信号质量指标

| 指标 | 定义 | 计算方式 |
|------|------|---------|
| 信号准确率 | 信号发布后 30 天内市场走向是否符合预期 | 正确预测次数 / 总预测次数 |
| 信号延迟 | 从数据变点到信号生成的时间 | 分析时间戳 - 源数据时间戳 |
| 置信度校准度 | 预测置信度 vs 实际准确率的差距 | \|置信度 - 实际准确率\|，< 0.15 为良好 |

### 信号有效期

| 信号类型 | 有效期 | 重新评估触发 |
|----------|--------|-------------|
| 短期（事件驱动） | 24 小时 | 下一个相关数据发布或事件触发 |
| 中期（行业轮动） | 7 天 | 每周一例行重评 |
| 长期（经济周期） | 30 天 | 月度宏观数据发布时 |

### 准确判定标准

- **方向正确**：信号预测方向与实际走向一致
- **偏差可接受**：核心变量实际值偏离预测值 ≤ 15%
- **两个条件同时满足才算"准确"**

---

## 关联

- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 三层六步：见 [06-layer-macro.md](./06-layer-macro.md) / [07-layer-event.md](./07-layer-event.md) / [08-layer-entity.md](./08-layer-entity.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- 付费分层：见 [10-billing.md](./10-billing.md)
