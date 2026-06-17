# Mangofolio Inventory 索引

> 来源：`D:\claudework\workspace\mangofolio\PROJECT_INVENTORY.md`（2026-06-10 拆分）
> 拆分目的：按主题垂直切分，后续查阅/更新更有针对性
> 原文件：保留作为"未拆分版"，不再更新

---

## 速查索引

| # | 文件 | 主题 | 关键内容 |
|---|------|------|----------|
| 01 | [01-brand.md](./01-brand.md) | 品牌架构 | 三端定位（个人/投顾/超级站）+ 对标 Vanguard |
| 02 | [02-architecture.md](./02-architecture.md) | 系统架构图 | ASCII 整体架构图 |
| 03 | [03-super-station.md](./03-super-station.md) | 超级系统站 | 知识系统 / 通用能力 / 数据系统 |
| 04 | [04-analysis-engine.md](./04-analysis-engine.md) | 分析引擎 | 三层框架（天时/地利/人和）+ 七层架构 + 付费分层 |
| 05 | [05-signal-system.md](./05-signal-system.md) | 信号系统 | Signal 模型 + 聚合 + API + 有效期 |
| 06 | [06-layer-macro.md](./06-layer-macro.md) | 天时层 | 宏观六步 + 周期判断 + 行业信号 |
| 07 | [07-layer-event.md](./07-layer-event.md) | 地利层 | 事件六步 + 叙事识别 |
| 08 | [08-layer-entity.md](./08-layer-entity.md) | 人和层 | 公司 + 基金六步 |
| 09 | [09-skill-chains.md](./09-skill-chains.md) | Skill 串接 | 引擎 + Schema + 降级策略 |
| 10 | [10-billing.md](./10-billing.md) | 付费分层 | 层级模型 + 访问控制 + 转化触发 |
| 11 | [11-contracts.md](./11-contracts.md) | 数据契约 | JSON Schema + 提炼传递 + 版本管理 |
| 12 | [12-products.md](./12-products.md) | 三端产品 | C/B/超级站产品形态 |
| 13 | [13-memory.md](./13-memory.md) | 记忆系统 | 个人版 + 投顾版（隔离） |
| 14 | [14-skills.md](./14-skills.md) | Skill 清单 | 通用 Skill + 专用 Skill + 大师库 |
| 15 | [15-paths.md](./15-paths.md) | 路径速查 | 所有文件位置 |
| 16 | [16-tech.md](./16-tech.md) | 技术实现 | API 分层 + 加密 + 同步 + 部署 |
| 17 | [17-decisions.md](./17-decisions.md) | 已确认决策 | 决策清单 + 权限模型 |
| 18 | [18-next-steps.md](./18-next-steps.md) | 下一步 | 待办清单 |
| 19 | [19-component-map.md](./19-component-map.md) | 组件落地映射 | 合并自 `core/engine/COMPONENT_MAP.md` |

---

## 已确认决策（一站式）

| 决策点 | 确认方案 |
|--------|---------|
| API 协议 | to Agent (MCP) + to Human (REST) 双轨并存 |
| 密钥管理 | 微信扫码社交登录 |
| 投顾数据归属 | 归投顾私有，服务端加密存储 |
| 终端迁移 | 自动从云端下载（微信登录后） |
| 同步冲突 | 最后写入胜出 |
| 投顾助手权限 | 需投顾授权才能访问客户数据 |
| 分析引擎生命周期 | 与核心引擎 `core/engine/` 同级，不单独部署 |
| 与 B 端 pipeline 关系 | pipeline 通过 HTTP 或 import 调分析引擎 API |
| 三层分析同步/异步 | 三层之间异步（独立分析），层内六步同步（串行流） |
| Skill 调用方式 | 复用 `skill_interface.py` 注册机制 |
| 付费拦截位置 | API 入口层（返回前过滤字段），不污染分析逻辑 |
| Schema 版本兼容 | 接收方忽略不识别字段，必须字段缺失时回退 |

---

## 关联文档

- 拆分源（未拆分原版）：`D:\claudework\workspace\mangofolio\PROJECT_INVENTORY.md`
- 组件落地映射源：`D:\claudework\workspace\mangofolio\core\engine\COMPONENT_MAP.md`
- 系统设计源：`D:\claudework\workspace\mangoview\SYSTEM_PROMPT.md`

---

**维护原则**：
- 改 inventory 内某文件 → **不需要**改原 PROJECT_INVENTORY.md
- 新增主题 → 新增 N+1 文件，索引表加一行
- 决策变化 → 改对应主题文件 + 同步改本文件的"已确认决策"表
