# PROGRESS.md - MangoView MVP

> 最后更新：2026-06-23

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
- [x] 数据库 schema（SQLite 10张表，含新增 Report 表）
- [x] 数据采集脚本（akshare 宏观 + 北向资金）+ 采集后自动生成日报
- [x] skills 知识库骨架（investment-framework-skill git submodule）

### Phase 2: 核心功能
- [x] 首页 / (landing)（含 Hero、三类投资者对比、三层漏斗）
- [x] 市场看版 /market（含 Tab 导航 + 三大子页面）
  - `/market/cycle` — 周期定位（四周期卡片 + 宏观指标表）
  - `/market/industry` — 行业大图（周期色块 + 四象限矩阵）
  - `/market/events` — 事件跟踪（北向资金 + 信号 + 热点事件）
- [x] 工具集 /tools（10 个工具卡片 + 周期定位器弹窗）
- [x] 配置中心 /portfolio（对接 analysis engine，commodity→gold 映射）
- [x] 扫描报告 /reports（DB 驱动，日报/周报/月报，支持生成 API）
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
- [x] `services/report_service.py` — 报告生成服务（日报/周报/月报模板）
- [x] `scripts/daily_collector.py` — 每日定时采集脚本 + 采集后自动生成日报
- [x] API 改为 DB 优先降级机制（不再实时调 akshare 超时卡死）
- [x] akshare 超时控制（5秒）+ 兜底数据
- [x] `safe_float()` 处理 NaN/Inf，JSON 序列化正常
- [x] `scripts/send_to_feishu.py` — 飞书群机器人推送

### API 层
- [x] `/v1/market/*` — 宏观/北向资金/行业板块
- [x] `/v1/tools/*` — 周期定位等工具
- [x] `/v1/portfolio/*` — 调用 cycle_matrix + data_fetcher，返回真实周期数据
- [x] `/v1/reports/*` — DB 驱动报告 CRUD + 手动生成端点
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
2. skills submodule 未初始化
3. CORS 在生产环境需限制为特定域名
4. `cycle_matrix` 周期匹配度当前 50%（PMI 53.0 + PPI -1.2 + 默认 fixed_asset），真实数据采集后匹配度会提升

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
| `docs/PRD-DATA-INTEGRATION.md` | ✅ 数据接入 PRD（M1-M5 已实现） |
| `CLAUDE.md` | ✅ 融入 Superpowers 机制 |
| `PROGRESS.md` | ✅ 更新到 v3（2026-06-23） |
| `README.md` | ⚠️ 需同步更新 |

---

## 代码审查修复 — 2026-06-22

### 已修复（本轮 15 项）

| # | 问题 | 文件 | 修复方式 |
|---|------|------|----------|
| 1 | `current_phase` 硬编码 | analysis.py:277 | 使用引擎结果 + fallback（已由前一 agent 确认） |
| 2 | DB 路径硬编码 | database.py:128-133 | 使用 MANGOVIEW_DATABASE_URL 环境变量（已由前一 agent 确认） |
| 3 | 重复 cycle-locator 端点 | tools.py, schemas.py, api.ts | 删除死端点 + 清理 CyclePosition 类型 |
| 4 | 兜底数据未标注 | market_service.py:111-118 | 来源改为"国家统计局（估算参考，数据源暂不可用）" |
| 5 | bottomGrowers 排序错误 | industry/page.tsx:36 | 使用升序 a-b（已由前一 agent 确认） |
| 6 | 3 个硬编码行业 | market_service.py:172-185 | 改为 DB 优先（IndustryInfo + IndustryFinancials + IndustryValuation）降级硬编码 |
| 7 | locked: True 始终 | portfolio.py | 改为 locked: False |
| 8 | 9 指标 vs 3-4 不匹配 | cycle/page.tsx | 调整为"核心宏观指标" + available 标记 |
| 10 | Thread → ThreadPoolExecutor | market_service.py:24-38 | 全局线程池 `_executor(max_workers=2)` 复用 |
| 11 | CORS * | main.py:17 | 使用 CORS_ORIGINS 环境变量 |
| 12 | sys.path.insert | analysis.py + main.py | 移至 main.py（集中管理），从 analysis.py 删除 |
| 13 | workflow_old/ 清理 | workflow_old/ | git rm -r 删除 21 个文件 |
| 15 | 趋势验证占位符 | cycle/page.tsx | 改为基于 macro 数据的摘要展示 |
| 17 | 备份文件 | page_20260616_*.tsx | 删除 3 个备份文件 |

### 已验证无需修复

| # | 问题 | 结论 |
|---|------|------|
| 14 | 报告锁定逻辑 | UI 已有 `is_locked && 完整版` badge，正常工作 |
| 16 | 重复 getMacroData | market/page.tsx 和 cycle/page.tsx 是独立路由页面，各自独立加载属正常行为 |

---

## 数据接入 — 2026-06-23

### M1-M5 全部完成

| 模块 | 内容 | 文件 |
|------|------|------|
| M1 | Report ORM 模型 | `backend/app/models/database.py` |
| M2 | ReportService 报告生成 | `backend/app/services/report_service.py`（新建） |
| M3 | Reports API 重写 | `backend/app/api/v1/reports.py` |
| M4 | Portfolio 对接 engine | `backend/app/api/v1/portfolio.py` |
| M5 | 采集后自动生成日报 | `backend/scripts/daily_collector.py` |
| PRD | 设计文档 | `docs/PRD-DATA-INTEGRATION.md` |

### 验证结果
- `POST /v1/reports/generate?type=daily` → report_id=1 ✅
- `GET /v1/reports?type=daily` → 真实 PMI/北向数据 ✅
- `POST /v1/portfolio/generate` → 复苏周期, 匹配度 50%, commodity→gold 映射 ✅
- `GET /api/health` → healthy ✅

### 剩余边界
- `commodity→gold` 映射在 portfolio.py 层完成，未改 engine
- 周期匹配度偏低（50%）因 `fetch_for_analysis` 部分字段用默认值，数据采集后改善
- 月报 `is_locked` 走知识星球外部验证，无需内置认证

---

> 最后更新：2026-06-23
