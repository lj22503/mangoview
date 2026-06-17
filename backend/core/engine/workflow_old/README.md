# Mangofolio 工作流引擎 · Orchestrator

**版本**：v0.1.0  
**创建时间**：2026-05-06  
**状态**：🚧 开发中  
**负责人**：燃冰 & ant

---

## 一、项目定义

### 一句话定义
**Mangofolio 工作流引擎 = 让 Skill 链式调用，用户说一句自然语言，自动串联多个 Skill**

### 核心价值
- **对用户**：自然语言输入 → 自动执行多个 Skill → 输出完整分析
- **对燃冰**：Skill 复用率提升，内容生产效率提升

### 设计原则
- **Skill 即插件**：每个 Skill 是独立插件，可插拔
- **链式调用**：Skill A 输出 → Skill B 输入 → Skill C 输出
- **自然语言路由**：用户说人话，引擎自动路由到对应 Skill 链
- **数据可追溯**：每个输出标注数据来源 + 信源等级

---

## 二、架构设计

### 整体架构

```
用户输入（自然语言）
    ↓
工作流引擎（Orchestrator）
    ↓
Skill 路由 → Skill A → Skill B → Skill C
    ↓
数据验证层（Data Verifier）
    ↓
输出（带署名 + 免责声明）
```

### 数据验证层架构（基于 data_layer）

```
DataVerifier
    ↓
统一数据接口（DataAPI）
    ↓
降级链：腾讯 → 新浪 → 东方财富
    ↓
缓存层（CacheManager）
    ↓
返回验证后的数据（Every number is verifiable）
```

### 核心组件

| 组件 | 职责 | 状态 |
|------|------|------|
| **Orchestrator** | 接收用户输入，路由到 Skill 链 | ✅ 完成 |
| **Skill Router** | 根据关键词/意图路由到对应 Skill | ✅ 完成 |
| **Data Verifier** | 数据验证层（基于 data_layer 架构） | ✅ 完成 |
| **Output Formatter** | 格式化输出，添加署名 + 免责声明 | ✅ 完成 |

### Skill 链设计

| 场景 | Skill 链 | 触发词 |
|------|---------|--------|
| 事件分析 | 人格测试 → 事件分析 → 条件单配置 | "分析这个事件" |
| 持仓诊断 | 持仓诊断 → 投顾建议 → 复盘报告 | "诊断我的持仓" |
| 内容生产 | 热点扫描 → 事件分析 → 内容官 → 署名 | "写一篇关于 XX 的文章" |

---

## 三、技术实现

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **Orchestrator** | Python 3.10+ | 核心调度引擎 |
| **Skill Router** | 正则 + 关键词匹配 | 简单高效 |
| **Data Verifier** | data_layer 架构 | 统一数据接口 + 降级链 |
| **Output Formatter** | Jinja2 模板 | 格式化输出 |

### 目录结构

```
mangofolio-workflow-engine/
├── src/
│   ├── __init__.py
│   ├── orchestrator.py      # 核心调度引擎
│   ├── router.py            # Skill 路由器
│   ├── verifier.py          # 数据验证层
│   └── formatter.py         # 输出格式化
├── tests/
│   ├── test_orchestrator.py
│   └── test_router.py
├── docs/
│   └── architecture.md
├── output/
│   └── (工作流输出)
├── README.md
└── requirements.txt
```

---

## 四、里程碑

| 日期 | 任务 | 负责人 | 产出 |
|------|------|--------|------|
| 5/6 | 架构设计 + 目录搭建 | ant | 本文档 + 目录结构 | ✅ 完成 |
| 5/6 | Skill 接口规范 | ant | skill_interface.py | ✅ 完成 |
| 5/6 | 事件分析 Skill | ant | skills/event_analysis.py | ✅ 完成 |
| 5/6 | 持仓诊断 Skill | ant | skills/position_diagnosis.py | ✅ 完成 |
| 5/6 | Orchestrator 对接 Skill | ant | orchestrator.py 更新 | ✅ 完成 |
| 5/6 | Router 持仓解析 | ant | router.py 更新 | ✅ 完成 |
| 5/6 | Data Verifier 基于 data_layer | ant | verifier.py | ✅ 完成 |
| 5/7 | 基金数据接口优化 | ant | fund_fix.py | ✅ 完成 |
| 5/7 | 涨跌幅字段修复 | ant | tencent_fix.py | ✅ 完成 |
| 5/8 | 完整工作流测试 | ant + 燃冰 | test_workflow.py | ✅ 完成 |
| 5/8 | 性能优化 | ant | 缓存命中率提升 | ✅ 完成 |

---

## 五、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| Skill 接口不统一 | 高 | 高 | 制定 Skill 接口规范 |
| 数据 API 受限 | 中 | 高 | 多数据源备用 |
| 链式调用超时 | 中 | 中 | 超时降级策略 |

---

**创建时间**：2026-05-06  
**版本**：v0.1.0  
**状态**：🚧 开发中  
**下一步**：编写 Orchestrator 核心代码
