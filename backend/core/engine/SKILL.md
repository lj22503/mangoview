---
name: mangofolio-core-engine
version: 1.0.0
description: "Mangofolio 核心工作流引擎 - Skill 链式调度"
author: 燃冰 + ant
created: 2026-05-08
skill_type: 核心🔴
allowed-tools: [Bash, Read, Write, Exec]
tags: [工作流，引擎，调度，Mangofolio]
---

# mangofolio-core-engine: 核心工作流引擎 ⚙️

## 📋 功能描述

Mangofolio 的核心工作流引擎，实现 Skill 的链式调用和调度。

**核心能力：**
- 自然语言路由
- Skill 链式调用
- 数据验证层
- 格式化输出

**边界条件：**
- 需要配合具体 Skill 使用
- 数据验证依赖 data_layer
- 输出包含署名和免责声明

**免责声明：**
> ⚠️ 本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。

---

## 🎯 核心模块

### 调度引擎
- `Orchestrator` - 核心调度器
- `SkillRouter` - 技能路由器
- `DataVerifier` - 数据验证器
- `OutputFormatter` - 输出格式化器

### Skill 接口
- `BaseSkill` - 基础 Skill 类
- `@skill` 装饰器 - Skill 注册
- `get_skill` / `list_skills` - Skill 管理

### 内置 Skill
- `event_analysis` - 事件分析
- `position_diagnosis` - 持仓诊断
- `personality_test` - 人格测试
- `content_generation` - 内容生成

---

## 🚀 快速开始

```bash
# 执行工作流
python3 -m src "帮我分析一下 QFII 国债期货事件"
```

---

**版本**: v1.0.0  
**最后更新**: 2026-05-08
