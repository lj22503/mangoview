# 18 下一步

> 来源：PROJECT_INVENTORY.md 第十一章
> 主题：待办清单（与 `core/engine/COMPONENT_MAP.md` 的 Phase 1/2/3 对齐）
> 落地优先级：见 [19-component-map.md](./19-component-map.md)

---

## 待办清单

- [ ] 细化 MCP Server 接口设计
- [ ] 设计 Skills 同步机制
- [ ] 规划数据加密实现方案
- [ ] 制定各产品的开发优先级

---

## 与引擎落地的对齐

`PROJECT_INVENTORY.md` 的"下一步"是**产品级**清单，而 `core/engine/COMPONENT_MAP.md` 已经把**引擎级**落地拆成 Phase 1/2/3：

### Phase 1（核心骨架）— 先跑通一条路径

| 优先级 | 组件 | 产出 |
|--------|------|------|
| P0 | `contract/schema_definitions.py` | 六步 Schema + 提炼传递定义 |
| P0 | `contract/schema_validator.py` | 版本感知校验器 |
| P0 | `signal/signal_model.py` | Signal 数据模型 + 基本 CRUD |
| P0 | `analysis/step_executor.py` | 六步模板执行器 |
| P0 | `analysis/completion_checker.py` | 完成标准 + 回退逻辑 |
| P0 | `orchestrator.py` 改造 | 接入六步流程 + 信号聚合 |

### Phase 2（三层内容）— 并行开发

| 优先级 | 组件 | 产出 |
|--------|------|------|
| P1 | `analysis/tianshi/` | 天时六步 + 周期矩阵 |
| P1 | `analysis/dili/` | 地利六步 + 叙事识别 |
| P1 | `analysis/renhe/` | 人和六步 + 公司/基金分类 |
| P1 | `signal/signal_aggregator.py` | 三层信号聚合算法 |

### Phase 3（工程化）— 上线准备

| 优先级 | 组件 | 产出 |
|--------|------|------|
| P2 | `middleware/` | 付费拦截 + 简单结论过滤 |
| P2 | `signal/signal_api.py` | FastAPI 路由 + API 文档 |
| P2 | 集成测试 | 各层联调 + 边界测试 |

**实际构建顺序**：1 → 2 → 3 → 7 → 8（三层分析模块并行开发，但先搭框架再填内容）

---

## 关联

- 组件落地映射：见 [19-component-map.md](./19-component-map.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- 信号系统：见 [05-signal-system.md](./05-signal-system.md)
- 付费分层：见 [10-billing.md](./10-billing.md)
