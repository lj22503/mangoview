# 15 路径速查

> 来源：PROJECT_INVENTORY.md 第七章
> 更新：2026-06-15（路径已更正）

---

## 产品 / 系统路径

| 产品/系统 | 路径 |
|----------|------|
| 个人版（C 端）| `D:\claudework\workspace\investment-assistant\` |
| 投顾版（B 端）| `D:\claudework\workspace\mangofolio\b-end\` |
| 超级系统站后端 | `D:\claudework\workspace\mangoview\backend\` |
| 超级系统站前端 | `D:\claudework\workspace\mangoview\frontend\` |
| framework-skill | `D:\claudework\workspace\mangoview\skills\investment-framework-skill\` |
| **核心引擎（OS）** | `D:\claudework\workspace\mangoview\backend\core\engine\` |
| **组件落地映射** | `D:\claudework\workspace\mangoview\backend\core\engine\COMPONENT_MAP.md` |
| **Inventory 文档** | `D:\claudework\workspace\mangoview\docs\inventory\` |

---

## 设计文档

| 文档 | 路径 |
|------|------|
| 系统设计文档 | `D:\claudework\workspace\mangoview\docs\SPEC.md` |
| 技术规格 | `D:\claudework\workspace\mangoview\docs\tech-spec\TECH_SPEC.md` |
| 项目总览 | `D:\claudework\workspace\mangoview\docs\inventory\PROJECT_INVENTORY.md` |

---

## 知识系统

| 内容 | 路径 |
|------|------|
| 大师思想库 | `D:\claudework\workspace\mangoview\skills\investment-framework-skill\china-masters\` |

---

## 引擎代码（`backend/core/engine/`）

| 文件 | 用途 |
|------|------|
| `orchestrator.py` | 核心调度器（已接入六步流程 + 信号聚合） |
| `router.py` | 关键词/正则路由到 Skill 链 |
| `skill_interface.py` | Skill 抽象基类 + 注册表（直接复用） |
| `verifier.py` | 数据验证（已接入数据契约校验） |
| `formatter.py` | 输出格式化（直接复用） |
| `COMPONENT_MAP.md` | 组件落地映射图 |

> 引擎改造详情 + 新增目录结构：见 [19-component-map.md](./19-component-map.md)

---

## 快速运行

```bash
# 分析引擎测试
cd D:\claudework\workspace\mangoview\backend\core\engine
python -m pytest tests/ -v

# 启动 FastAPI
cd D:\claudework\workspace\mangoview\backend
uvicorn app.main:app --reload --port 8003
```

---

## 关联

- 品牌架构：见 [01-brand.md](./01-brand.md)
- 三端产品：见 [12-products.md](./12-products.md)
- 组件落地：见 [19-component-map.md](./19-component-map.md)
- 下一步：见 [18-next-steps.md](./18-next-steps.md)