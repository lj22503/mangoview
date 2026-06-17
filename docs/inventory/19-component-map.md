# 19 组件落地映射

> 来源：`D:\claudework\workspace\mangofolio\core\engine\COMPONENT_MAP.md`（合并到 inventory）
> 原文件保留：作为 `core/engine/` 模块的本地索引
> 目的：回答"每个新组件放哪、依赖谁、先建谁"
> 更新日期：2026-06-10

---

## 一、现有基础盘点

| 现有代码 | 用途 | 复用程度 |
|---------|------|---------|
| `core/engine/orchestrator.py` | 核心调度器，串行执行 Skill 链 | ⚙️ 改造：扩展为六步调度 |
| `core/engine/router.py` | 关键词/正则路由到 Skill 链 | ⚙️ 改造：路由加新分析链 |
| `core/engine/skill_interface.py` | Skill 抽象基类 + 注册表 | ✅ 直接复用 |
| `core/engine/verifier.py` | 数据验证 | ⚙️ 改造：接入数据契约校验 |
| `core/engine/formatter.py` | 输出格式化 | ✅ 直接复用 |
| `b-end/pipeline/pipeline_orchestrator.py` | B 端工作流引擎 | 🔗 调用分析引擎，不改动 |
| `b-end/modules/event/scripts/event_analyzer.py` | 事件分析脚本 | 🔗 作为地利层 Skill 被调用 |
| `b-end/modules/fund/scripts/fund_diagnosis.py` | 基金诊断脚本 | 🔗 作为人和层 Skill 被调用 |

---

## 二、新组件目录结构

```
core/engine/
├── __init__.py
├── orchestrator.py        ← 改造：支持六步调度 + 付费拦截
├── router.py              ← 改造：注册分析链路由
├── skill_interface.py     ← 复用
├── verifier.py            ← 改造：套数据契约校验
├── formatter.py           ← 复用
│
├── analysis/              ← 🆕 六步分析框架（三层共用）
│   ├── step_executor.py   ← 六步执行器（Step 0-6 模板方法）
│   ├── completion_checker.py  ← 每步完成标准校验（注入阈值）
│   ├── fallback_manager.py    ← 回退机制管理
│   │
│   ├── tianshi/           ← 🆕 天时层
│   │   ├── scale_filter.py    ← 横向 Scale 筛选
│   │   ├── steps/              ← 六步各步拆分（可选）
│   │   │   ├── step0_verify.py
│   │   │   ├── step1_decompose.py
│   │   │   └── ...
│   │   └── cycle_matrix.py     ← 经济/行业周期判断矩阵
│   │
│   ├── dili/              ← 🆕 地利层
│   │   ├── scale_filter.py    ← 横向事件筛选
│   │   ├── steps/
│   │   └── narrative.py       ← 叙事识别
│   │
│   └── renhe/             ← 🆕 人和层
│       ├── steps/
│       ├── business_model_classifier.py  ← 商业模式分类
│       └── fund_style_classifier.py      ← 基金风格分类
│
├── signal/                ← 🆕 信号系统
│   ├── signal_model.py    ← Signal 数据模型
│   ├── signal_aggregator.py   ← 信号聚合算法
│   ├── signal_registry.py     ← 信号注册/检索
│   └── signal_api.py          ← FastAPI 路由（被外部调用）
│
├── contract/              ← 🆕 数据契约
│   ├── schema_definitions.py  ← 六步 JSON Schema 定义
│   ├── schema_validator.py    ← Schema 校验器（版本感知）
│   └── refined_transfer.py    ← 提炼传递工具
│
└── middleware/            ← 🆕 付费拦截
    ├── tier_model.py      ← 用户层级定义
    ├── access_control.py  ← API 访问控制
    └── upgrade_triggers.py    ← 升级转化逻辑
```

**不动的目录**：
- `b-end/modules/pipeline/` — 通过 API 调用分析引擎，内部不动
- `b-end/modules/event/`, `b-end/modules/fund/` — 作为下层 Skill 被分析引擎调用

---

## 三、依赖关系（DAG）

```
构建顺序  组件              依赖
────────────────────────────────────────────
1️⃣      contract/         无（纯 Schema 定义）
2️⃣      signal/           contract/（信号模型校验）
3️⃣      analysis/         contract/ + signal/
4️⃣        └ tianshi/      signal/（产出天时信号）
5️⃣        └ dili/         signal/（产出地利信号）
6️⃣        └ renhe/        signal/（产出人和信号）
7️⃣      middleware/        signal/（控制信号可见性）
8️⃣      orchestrator 改造  analysis/ + middleware/
```

**实际构建顺序**：1 → 2 → 3 → 7 → 8（三层分析模块并行开发，但先搭框架再填内容）

---

## 四、接口边界定义

### 4.1 层间调用约定

```
外部调用者（Pipeline / API）
    │
    ▼
core/engine/orchestrator.py
    │
    ├── middleware/access_control.py  ← 先过付费拦截
    │
    ├── analysis/step_executor.py     ← 选层 + 执行六步
    │   ├── completion_checker.py     ← 每步完后校验
    │   ├── fallback_manager.py       ← 不通过时回退
    │   └── {tianshi|dili|renhe}/     ← 具体分析逻辑
    │
    ├── signal/signal_aggregator.py   ← 聚合三层信号
    │
    └── contract/refined_transfer.py  ← 提炼传递
```

### 4.2 Signal 数据契约（跨层边界）

```python
# analysis 层 → signal 层 的输出契约
{
    "layer": "TIANSHI|DILI|RENHE",
    "step_completed": 0-6,
    "signal": SignalModel,  # 符合需求1定义的17字段模型
    "refined": RefinedOutput  # 符合需求7定义的提炼传递格式
}
```

### 4.3 六步内部契约

```python
# step N → step N+1 的边界
{
    "step": 0-6,
    "core_variables": [...],      # ≤5个
    "key_assumptions": [...],     # ≤3条
    "pending_validations": [...], # ≤3项
    "confidence": 0-1,
    "passed": bool,               # 完成标准是否通过
    "fallback": None|"字符串"       # 回退说明（如果有）
}
```

---

## 五、构建优先级（分阶段）

### Phase 1（核心骨架）— 先能跑通一条路径

| 优先级 | 组件 | 产出 | 工作量 |
|--------|------|------|--------|
| P0 | `contract/schema_definitions.py` | 六步 Schema + 提炼传递定义 | 小 |
| P0 | `contract/schema_validator.py` | 版本感知校验器 | 小 |
| P0 | `signal/signal_model.py` | Signal 数据模型 + 基本 CRUD | 中 |
| P0 | `analysis/step_executor.py` | 六步模板执行器 | 中 |
| P0 | `analysis/completion_checker.py` | 完成标准 + 回退逻辑 | 中 |
| P0 | `orchestrator.py` 改造 | 接入六步流程 + 信号聚合 | 中 |

### Phase 2（三层内容）— 并行开发

| 优先级 | 组件 | 产出 | 工作量 |
|--------|------|------|--------|
| P1 | `analysis/tianshi/` | 天时六步 + 周期矩阵 | 大 |
| P1 | `analysis/dili/` | 地利六步 + 叙事识别 | 大（重用 event） |
| P1 | `analysis/renhe/` | 人和六步 + 公司/基金分类 | 大（重用 fund） |
| P1 | `signal/signal_aggregator.py` | 三层信号聚合算法 | 中 |

### Phase 3（工程化）— 上线准备

| 优先级 | 组件 | 产出 | 工作量 |
|--------|------|------|--------|
| P2 | `middleware/` | 付费拦截 + 简单结论过滤 | 中 |
| P2 | `signal/signal_api.py` | FastAPI 路由 + API 文档 | 中 |
| P2 | 集成测试 | 各层联调 + 边界测试 | 中 |

---

## 六、关键决策

| 决策 | 方案 |
|------|------|
| 分析引擎生命周期 | 与核心引擎 `core/engine/` 同级，不单独部署 |
| 与 B 端 pipeline 关系 | pipeline 通过 HTTP 或 import 调分析引擎 API |
| 三层分析同步/异步 | 三层之间异步（独立分析），层内六步同步（串行流） |
| Skill 调用方式 | 复用 `skill_interface.py` 注册机制，现有 Skill 注册为分析步骤 |
| 付费拦截位置 | API 入口层（返回前过滤字段），不污染分析逻辑 |
| Schema 版本向前兼容 | 接收方忽略不识别字段，必须字段缺失时回退 |

---

## 关联

- 引擎根目录：`D:\claudework\workspace\mangofolio\core\engine\`
- 原组件落地映射（保留）：`core/engine/COMPONENT_MAP.md`
- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 信号系统：见 [05-signal-system.md](./05-signal-system.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- 付费分层：见 [10-billing.md](./10-billing.md)
- 路径速查：见 [15-paths.md](./15-paths.md)
- 下一步：见 [18-next-steps.md](./18-next-steps.md)
