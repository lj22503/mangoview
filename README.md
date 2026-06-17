# 🏛️ Mangoview — 超级系统站

> **定位**：超级系统站（OS层），被个人版/投顾版/超级站前端调用
> **Slogan**：自上而下，看清每一笔投资
> **组成**：分析引擎 + 数据采集 + FastAPI + Next.js 前端 + Skills 知识库

---

## 三端架构

```
┌─────────────────────────────────────────────────────────────┐
│                     超级系统站（mangoview）                    │
│  知识系统 / 通用能力 / 数据系统 / 分析引擎                     │
└─────────────────────────────────────────────────────────────┘
           ↑ 被调用              ↑ 被调用              ↑ 被调用
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │  个人版      │      │  投顾版      │      │  超级站前端  │
    │(investment-   │      │(mangofolio) │      │ (mangoview) │
    │ assistant)    │      │    B端      │      │              │
    └──────────────┘      └──────────────┘      └──────────────┘
```

---

## 目录结构

```
mangoview/
├── backend/
│   ├── app/                  ← FastAPI
│   │   ├── api/v1/          ← market / tools / portfolio / reports / analysis
│   │   ├── models/
│   │   └── services/
│   ├── core/
│   │   ├── engine/          ← 分析引擎（Phase 1-3 完成）
│   │   │   ├── analysis/     ← 天时/地利/人和
│   │   │   ├── signals/     ← 信号系统
│   │   │   ├── contract/   ← 数据契约
│   │   │   ├── middleware/  ← 付费拦截
│   │   │   └── tests/      ← 86 个测试
│   │   └── data/            ← 数据采集
│   │       └── providers/    ← AKShare / 东方财富 / 天天基金 / 新浪 / tushare
│   ├── scripts/             ← 数据采集脚本
│   └── requirements.txt
├── frontend/                 ← Next.js 14 + Tailwind + Recharts/ECharts
│   └── src/
│       ├── app/
│       │   ├── (app)/       ← 认证后页面（market/cycle, market/industry, market/events, tools, portfolio, reports, about）
│       │   └── (landing)/   ← 落地首页
│       ├── components/      ← 市场组件库
│       └── lib/            ← API 客户端
├── skills/                   ← investment-framework-skill（git submodule）
└── docs/
    ├── inventory/            ← 设计文档（19个文件）
    └── SPEC.md               ← 产品规格
```

---

## 核心能力

| 能力 | 位置 | 状态 |
|------|------|------|
| 三层六步分析引擎 | backend/core/engine/ | ✅ Phase 1-3 完成 |
| 信号系统 | backend/core/engine/signals/ | ✅ 8个API端点 |
| 数据采集 | backend/core/data/providers/ | ✅ AKShare/东方财富/天天基金 |
| FastAPI | backend/app/ | ✅ market/tools/portfolio/reports/analysis |
| 前端 | frontend/ | ✅ Next.js 14，完整页面结构 |

---

## 快速开始

```bash
# 1. 后端依赖
cd backend
pip install -r requirements.txt

# 2. 启动 FastAPI
cd backend
uvicorn app.main:app --reload --port 8003

# 3. 前端依赖
cd frontend
npm install

# 4. 启动前端
cd frontend
npm run dev

# 5. 数据采集（可选）
cd backend/scripts
python daily_collector.py
```

---

## API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/v1/market/macro` | 宏观指标 |
| GET | `/v1/market/north-money` | 北向资金 |
| GET | `/v1/market/industries` | 行业板块 |
| POST | `/v1/analysis/cycle-locator` | 周期定位（引擎） |
| POST | `/v1/analysis/asset-allocation` | 资产配置（引擎） |
| POST | `/v1/analysis/event` | 事件分析（引擎） |
| GET | `/v1/analysis/macro-data` | 宏观数据（引擎） |
| GET | `/api/health` | 健康检查 |

---

## 前端页面

| 路径 | 功能 |
|------|------|
| `/` | 落地页（Hero + 三类投资者 + 三层漏斗） |
| `/market/cycle` | 周期定位（四周期卡片 + 宏观指标表） |
| `/market/industry` | 行业大图（周期色块 + 四象限矩阵） |
| `/market/events` | 事件跟踪（北向资金 + 信号 + 热点事件） |
| `/tools` | 工具集 |
| `/portfolio` | 配置中心 |
| `/reports` | 扫描报告 |
| `/about` | 说明页 |

---

## Skills 清单

skills/ 目录含 investment-framework-skill 子模块，包括：

| Skill | 功能 |
|-------|------|
| asset-allocator | 资产配置 |
| bias-detector | 认知偏差检测 |
| cycle-locator | 周期定位 |
| china-masters/duan-yongping | 段永平"本分"分析 |
| china-masters/li-lu | 李录价值投资 |
| china-masters/qiu-guolu | 邱国麓估值分析 |
| china-masters/wu-jun | 吴军AI趋势 |

---

## 技术栈

- **前端**：Next.js 14 + Tailwind CSS + Recharts + ECharts
- **后端**：Python FastAPI + SQLAlchemy + Pydantic
- **数据源**：akshare / 东方财富 / 天天基金 / 新浪 / tushare
- **数据库**：SQLite
- **部署**：PM2 + Cloudflare Tunnel（阿里云）

---

**版本**: v0.2.0
**创建时间**: 2026-06-03
**最后更新**: 2026-06-17（三端拆分完成，核心引擎迁入，全部代码已提交）
