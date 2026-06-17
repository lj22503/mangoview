# Mangoview 前后端联调深度审查报告

> 审查时间：2026-06-16
> 前后端版本：前端 Next.js 14.2.5 + 后端 FastAPI (uvicorn on 8003)

---

## 🔴 核心发现：前后端完全断连

**问题定性：前后端架构断连，不是数据问题，是系统对接问题**

项目里存在**两套独立的后端**，它们之间没有任何调用关系：

```
┌─────────────────────────────────────────────────────────┐
│  前端 Next.js (localhost:3000)                        │
│  调用: http://127.0.0.1:8003/v1/*                     │
└────────────────┬──────────────────────────────────────┘
                 │ HTTP (已连通)
                 ▼
┌─────────────────────────────────────────────────────────┐
│  backend/app/main.py (Simple API - 端口 8003)           │
│  实现: 硬编码逻辑 + mock数据                            │
│  ├── /v1/market/macro      → 简单DB查询/akshare降级    │
│  ├── /v1/market/north-money → 简单DB查询               │
│  ├── /v1/tools/cycle-locator → if/else硬编码（20行）   │
│  └── /v1/portfolio/generate → 固定比例配置             │
│                                                         │
│  ❌ 从未调用 core/engine/                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  backend/core/ (Real Engine - 端口??? 未运行)           │
│  实现: 六步分析框架 + 信号系统                          │
│  ├── /api/v1/analyze      → 真实天时/地利/人和分析     │
│  ├── /api/v1/analyze/auto → 自动取数+分析               │
│  ├── /api/v1/signals      → 信号系统                   │
│  └── /api/v1/fetch        → 数据获取                   │
│                                                         │
│  ✅ 完整引擎，但从未被 app/ 调用                        │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ 已完成修复（2026-06-15）

### 1. 端口不一致
- `frontend/src/lib/api.ts` — `8015` → `8003`
- `frontend/src/app/tools/page.tsx` — 硬编码 fetch 的 API URL `8015` → `8003`

### 2. 北向资金数据模型不匹配
- 前端 `NorthMoneyData` 期望 `{today, recent_days}`，后端返回 flat `{date, net_buy, ...}`
- 修复：`frontend/src/lib/api.ts` + `frontend/src/app/market/events/page.tsx`

### 3. Tailwind SWC 语法错误
- `bg-[#10b981]/10` 在 Next.js 14.2.5 SWC 报错 → 改用 `bg-green-100 text-green-600`

### 4. portfolio/page.tsx 无效 dark mode 类名
- 移除所有 `dark:` 前缀类名（layout.tsx 未配置 dark mode）

---

## ✅ 新增：真实引擎对接（2026-06-16）

### 新建文件
- `backend/app/api/v1/analysis.py` — **核心改造**，新增 4 个 API 端点

### 新增端点

| 端点 | 方法 | 功能 | 对接 engine |
|------|------|------|-------------|
| `/v1/analysis/cycle-locator` | POST | 周期定位（真） | `engine.analyze("tianshi")` 六步 |
| `/v1/analysis/asset-allocation` | POST | 资产配置建议 | `determine_economic_cycle()` |
| `/v1/analysis/macro-data` | GET | 获取宏观数据 | `data_fetcher.for_tianshi()` |
| `/v1/analysis/event` | POST | 事件分析 | `engine.analyze("dili")` |

### 数据流设计

```
前端 cycle-locator
  ↓ 发送 {pmi: 52, ppi: -2.1, fixed_asset: 6, new_start: 2}

analysis.py POST /v1/analysis/cycle-locator
  ↓ transform_indicators_to_macro_data()
  ↓ macro_data = {pmi_trend: "up", cpi_trend: "down_or_stable", monetary: "loose", credit: "expanding"}

engine.analyze(layer="tianshi", input_data={macro_data, ...})
  ↓ 六步分析（Step0~Step6）
  ↓ Step4 输出 cycle_phase + scenario
  ↓ Step5 输出 base_action + 配置方向
  ↓ Step6 输出 exit_signals

analysis.py
  ↓ map_cycle_phase_to_four_cycles()
  ↓ {cycle_position: {kitchin, juglar, kuznets, kondratieff}, allocation_suggestion, ...}

前端 cycle-locator 页面
```

### 关键转换函数

`transform_indicators_to_macro_data()` — 将前端原始指标转换为 engine 所需的趋势字段：
- `pmi >= 50` → `pmi_trend = "up"`
- `ppi >= 0` → `cpi_trend = "up"`，否则 `"down_or_stable"`
- `fixed_asset > 5` → `monetary = "loose"`, `credit = "expanding"`
- `fixed_asset 2-5` → `monetary = "tightening"`, `credit = "still_expanding"`
- `fixed_asset < 2` → `monetary = "tight"`, `credit = "contracting"`

`map_cycle_phase_to_four_cycles()` — 将 engine 的经济周期 phase 映射为四周期：
- 复苏 → 基钦=复苏早期, 朱格拉=扩张期, 库兹涅茨=上升期, 康波=萧条期
- 扩张 → 基钦=复苏晚期, 朱格拉=扩张期, 库兹涅茨=上升期, 康波=萧条期
- 放缓 → 基钦=衰退期, 朱格拉=收缩期, 库兹涅茨=下降期, 康波=萧条期
- 衰退 → 基钦=衰退后期, 朱格拉=收缩期, 库兹涅茨=下降期, 康波=萧条期

---

## 📋 仍存在的问题（设计决策）

### A. 周期阶段仍写死在前端
- `/market/cycle/page.tsx` 的四个周期当前值仍为静态
- 后端 `/v1/analysis/cycle-locator` 已能返回真实分析，但页面未调用

### B. 行业数据仍是 mock
- `fetch_industries()` 只返回 3 个固定行业：`消费、科技、医药`
- 阻塞：行业大图页面 `/market/industry`

### C. portfolio 接口未使用 time_horizon
- 前端传 `time_horizon: "3-5 年"` 字符串，后端直接透传
- 需确认：是否需要实现此参数逻辑

### D. PPI 数据总是走 akshare fallback
- `market_service.py` 查询 `codes = ['PMI', 'CPI', 'GDP', 'PPI']`，但 akshare fallback 只有 PMI/CPI/GDP
- DB 数据永远不会被使用（`have_all` 永远 False）

### E. 两套后端并存
- `app/main.py` 和 `core/serve.py` 是两套独立的 FastAPI 服务
- 当前只运行了 `app/main.py`（端口 8003）
- `core/serve.py` 的 engine API 从未被前端调用

---

## 🔧 修改文件清单（2026-06-15 ~ 2026-06-16）

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/lib/api.ts` | 端口 8015→8003；NorthMoneyData 改为 flat；新增 Analysis API 接口 |
| `frontend/src/app/tools/page.tsx` | API URL 8015→8003；Tailwind /10 修复；对接新 analysis API |
| `frontend/src/app/market/events/page.tsx` | 北向资金引用改为后端实际字段 |
| `frontend/src/app/portfolio/page.tsx` | 移除无效 dark: 类名 |
| `backend/app/main.py` | 注册 analysis.router |
| `backend/app/api/v1/analysis.py` | **新建**：真实引擎对接层（4个端点） |

---

## 下一步建议

1. **验证 engine 联调** — 重启后端 `python -m app.main`，测试 `POST /v1/analysis/cycle-locator`
2. **前端 /market/cycle 页面** — 接入 `/v1/analysis/cycle-locator` 替代静态数据
3. **行业数据** — 真实行业数据接入（akshare 行业板块接口）
4. **portfolio time_horizon** — 确认是否需要实现此参数逻辑
5. **测试验证** — 启动前端 `npm run dev`，确认各页面数据加载正常