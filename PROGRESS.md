# PROGRESS.md - MangoView MVP

> 最后更新：2026-06-17

## MVP 目标

**上线时间**：2026-06-17（进行中）

---

## 已完成

### 系统设计
- [x] **SYSTEM_PROMPT.md** — 基于 ai system.txt 方法论设计的完整系统 prompt
- [x] **docs/SPEC.md** — 产品规格文档（品牌/页面/设计规范）
- [x] **CLAUDE.md** — 融入 Superpowers 七阶段流程
- [x] **docs/inventory/** — 19 个设计文档（品牌/架构/分析引擎/信号系统等）

### Phase 1: 基础设施
- [x] 前端项目初始化（Next.js 14 + Tailwind + Recharts/ECharts）
- [x] 后端项目初始化（FastAPI + 路由骨架）
- [x] 数据库 schema（SQLite 9张表）
- [x] 数据采集脚本（akshare 宏观 + 北向资金）
- [x] skills 知识库骨架（investment-framework-skill git submodule）

### Phase 2: 核心功能
- [x] 首页 / (landing)（含 Hero、三类投资者对比、三层漏斗）
- [x] 市场看版 /market（含 Tab 导航 + 三大子页面）
  - `/market/cycle` — 周期定位（四周期卡片 + 宏观指标表）
  - `/market/industry` — 行业大图（周期色块 + 四象限矩阵）
  - `/market/events` — 事件跟踪（北向资金 + 信号 + 热点事件）
- [x] 工具集 /tools（10 个工具卡片 + 周期定位器弹窗）
- [x] 配置中心 /portfolio（用户画像 + 引擎推演）
- [x] 扫描报告 /reports（报告列表）
- [x] 说明页 /about（框架说明 + 合规声明）

### 分析引擎 Phase 1-3（backend/core/engine/）
- [x] 天时层（tianshi）— 宏观周期 + 情景分析
- [x] 地利层（dili）— 事件驱动分析
- [x] 人和层（renhe）— 机构行为分析
- [x] 信号系统（signals）— 8 个 API 端点
- [x] 数据契约校验（contract/）
- [x] 付费拦截中间件（middleware/tier_model）
- [x] 86 个单元测试（core/engine/tests/）

### 数据层
- [x] 数据采集 providers（akshare / 东方财富 / 天天基金 / 新浪 / tushare）
- [x] `services/market_service.py` — 服务层封装
- [x] `scripts/daily_collector.py` — 每日定时采集脚本
- [x] API 改为 DB 优先降级机制（不再实时调 akshare 超时卡死）
- [x] akshare 超时控制（5秒）+ 兜底数据
- [x] `safe_float()` 处理 NaN/Inf，JSON 序列化正常
- [x] `scripts/send_to_feishu.py` — 飞书群机器人推送

### API 层
- [x] `/v1/market/*` — 宏观/北向资金/行业板块
- [x] `/v1/tools/*` — 周期定位等工具
- [x] `/v1/portfolio/*` — 配置生成
- [x] `/v1/reports/*` — 报告列表
- [x] `/v1/analysis/*` — 真实引擎对接（cycle-locator / asset-allocation / event）
- [x] `/api/health` — 健康检查

### 前端架构
- [x] Next.js 14 App Router + Tailwind CSS（Stripe 风格）
- [x] `(app)` 路由组 — 认证后页面
- [x] `(landing)` 路由组 — 落地页
- [x] `src/lib/api.ts` — 统一 API 客户端
- [x] `src/components/` — 市场组件库（layout/、market/）
- [x] 涨跌色：中国习惯（红涨绿跌）
- [x] mango orange 品牌色系统

---

## 进行中（未 commit）

### 待提交代码
- [x] 前端 Next.js 完整结构（`(app)/`、`(landing)/`、`src/lib/`、`src/components/`）
- [x] 后端 FastAPI 完整结构（`app/api/`、`app/models/`、`app/services/`、`app/utils/`）
- [x] 核心引擎（`core/engine/` 分析层/信号/契约/中间件）
- [x] 数据采集（`core/data/` providers）
- [x] `requirements.txt`（backend/ 和 core/）
- [x] 配置文件（`check-status.sh`、`kill-old.ps1`）

---

## 待进行

### Phase 3: 测试 + 部署
- [ ] 功能测试 + 修复
- [ ] 部署到阿里云（PM2 + Cloudflare Tunnel）
- [ ] 域名解析到 view.mangofolio.com
- [ ] Windows 定时任务：每日 08:00 数据采集
- [ ] 飞书推送定时任务：每日 09:00

### 数据层（后续）
- [ ] 行业估值数据（PE/PB）- 当前 IP 被限制
- [ ] 自动化数据采集定时任务

### 技术债务
- [ ] 清理 `backend/core/engine/workflow_old/` 废弃代码
- [ ] 统一两个 `requirements.txt`（backend/ 和 core/）
- [ ] 修复 `current_phase` 硬编码 bug（`backend/app/api/v1/analysis.py:277`）
- [ ] 修复 `main.py` 硬编码 Windows 路径 `C:/tmp/mangoview/data`
- [ ] 安装 pytest 并运行测试
- [ ] skills submodule 初始化

---

## 已知问题

1. 阿里云服务器 IP 被东方财富限制，指数/个股行情/行业估值无法获取
2. `workflow_old/` 废弃代码未清理
3. skills submodule 未初始化
4. CORS 在生产环境需限制为特定域名

---

## Superpowers 管理规范

### 七阶段流程
```
brainstorming → writing-plans → subagent-dev → tdd → code-review → debug → finishing
```

### 硬性约束
- 需求不明，不动手
- 设计方案未审批，不写代码
- 不先写测试，不写代码
- 审查通过才能继续下一任务

### 任务粒度
- 每个任务 2-5 分钟
- 有明确输入输出
- 有验证标准

---

## 文件清单

| 文件 | 状态 |
|------|------|
| `docs/SPEC.md` | ✅ 更新到最新设计 |
| `CLAUDE.md` | ✅ 融入 Superpowers 机制 |
| `PROGRESS.md` | ✅ 更新到 v2（2026-06-17） |
| `README.md` | ⚠️ 需同步更新 |
