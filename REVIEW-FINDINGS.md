# MangoView 代码审查报告

> 审查日期：2026-06-17
> 审查范围：~20 个核心源文件（后端 API + 引擎 + 前端页面）
> 项目定位：基于经典框架的 SaaS 投资辅助工具（FastAPI + Next.js 14）

---

## 高危（会直接导致功能不可用）

### 1. `analysis.py` 引擎结果被硬编码覆盖 → 分析引擎白跑了

**文件：** `backend/app/api/v1/analysis.py:278`

```python
current_phase = "扩张"  # ← 硬编码！完全无视 engine 返回的 cycle_phase
```

`analyze_cycle_locator` 调用 engine 完成六步分析后，`cycle_phase` 变量存了真实结果，但紧接着第 278 行 `current_phase = "扩张"` 直接覆盖。四周期映射、配置建议、历史对照全部基于"扩张"而非引擎真实输出。

**PROGRESS.md 已标记为技术债务但未修复。**

---

### 2. 数据库路径硬编码 Windows 绝对路径

**文件：** `backend/app/models/database.py:113`

```python
DATABASE_URL = "sqlite:///C:/tmp/mangoview/data/mangoview.db"
```

部署到 Linux（阿�的阿里云目标平台）时路径不存在，服务启动直接报错。应改为环境变量或相对路径。`startup_event` 里的 `os.makedirs("C:/tmp/mangoview/data")` 同理。

---

### 3. `/v1/tools/cycle-locator` 与 `/v1/analysis/cycle-locator` 重复端点 + schema 不一致

- `backend/app/api/v1/tools.py` — POST `/v1/tools/cycle-locator`，接收 `CyclePositionRequest`（含 `new_start_area`），用本地 if/else 判断
- `backend/app/api/v1/analysis.py` — POST `/v1/analysis/cycle-locator`，接收 `CycleLocatorRequest`（无 `new_start_area`），对接 engine
- 前端 `api.ts` 有两个客户端函数：`postCycleLocator` (tools) 和 `postAnalysisCycleLocator` (analysis)
- 前端 `tools/page.tsx` 使用 `postAnalysisCycleLocator`，路径正确
- 但 `api.ts` 中 `postCycleLocator` 是死代码

两个端点输入输出格式不同（tools 版返回 `allocation_suggestion: {equity: "适度"}`，analysis 版返回 `{equity: "优先"}`），如果前端切错了端点，直接显示错误的配置建议。

---

### 4. `market_service.py` 兜底数据指标全是假数据

**文件：** `backend/app/services/market_service.py:118-134`

当 akshare 全部拉取失败时，返回硬编码的 PMI=50.0, CPI=102.3, GDP=5.2。`percentile` 固定 60%/58%/62%，`direction` 固定 "up"——无论真实经济状态如何，永远显示"好转中"。

对应的 TOP_INDICATORS 列表（`market/page.tsx`）有 9 个指标，API 只返回 3-4 个，其余全显示"暂无"。前端用户看到 6/9 的指标写"暂无"。

---

### 5. `industry/page.tsx` 的 topGrowers / bottomGrowers 逻辑完全相同

**文件：** `frontend/src/app/(app)/market/industry/page.tsx:36-40`

```typescript
const topGrowers = [...industries.industries]
  .sort((a, b) => b.net_profit_growth - a.net_profit_growth).slice(0, 3)
const bottomGrowers = [...industries.industries]
  .sort((a, b) => a.net_profit_growth - b.net_profit_growth).slice(0, 3)
```

两个排序逻辑完全一致（都是增速从高到低取前 3），`bottomGrowers` 显示的三个行业和 `topGrowers` 一模一样。"增速领跌"区块展示的是最高增速的三个行业，用户被严重误导。`market/page.tsx` 有同样的问题。

---

### 6. `fetch_industries()` 永远返回仅 3 个硬编码行业

**文件：** `backend/app/services/market_service.py:195-210`

行业 API 不访问数据库、不调用 akshare，直接返回手动写的消费/科技/医药三行数据。`industry/page.tsx` 宣称"覆盖申万 31 个一级行业"但与实际不符。

---

## 中危

### 7. `portfolio/page.tsx` 结果始终显示 locked

**文件：** `frontend/src/app/(app)/portfolio/page.tsx:105`

```typescript
{val.locked ? '--- ' + val.display : val.display}
```

后端 `portfolio.py` 返回的 allocation 中 `locked` 恒为 `True`，导致配置比例永远显示为 `--- 55%`（带破折号）而非直接显示数字。用户即使生成配置也看不出具体比例。

---

### 8. `cycle/page.tsx` 展示 9 个指标但 API 只返回 3-4 个

**文件：** `frontend/src/app/(app)/market/cycle/page.tsx:81-91`

`macroRows` 列表包含 GDP/CPI/PPI/PMI/M2/社融/社零/出口/固投 9 个指标，但后端 `market_service.py` 的 `fetch_macro_indicators` 只返回 PMI/CPI/GDP/PPI 四个。其余 5 个指标全部显示"暂无"，宏观数据快照表空了一大半。

---

### 9. 所有 API 的 Mock 数据来自硬编码，非真实数据源

- `reports.py` — 报告 API 全部硬编码 mock，无数据库读
- `portfolio.py` — 配置建议基于三个 if/else 分支，不调用 engine
- `market_service.py:195` — 行业数据硬编码 3 行

**影响：** 用户在这些页面看到的"分析结果"全是假数据。对于定位为"提供数据参考"的产品，这是核心功能缺失。

---

### 10. Thread 超时模式缺少清理

**文件：** `backend/app/services/market_service.py:24-38`

```python
def fetch_with_timeout(func, timeout=5, default=None):
    ...
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return default, True  # 线程仍在运行但被"丢弃"
```

超时后线程在后台继续运行（daemon 线程在进程退出时才强制终止）。高并发下可能积累大量遗留线程直到内存耗尽。

---

### 11. CORS `*` 生产环境安全漏洞

**文件：** `backend/app/main.py:17`

```python
allow_origins=["*"],
allow_credentials=True,
```

`credentials=True` 配合 `*` origin 违反 CORS 规范，部分浏览器会拒绝请求。生产环境应限制为前端实际域名。

---

### 12. `analysis.py` 使用 `sys.path.insert` 导入模块

**文件：** `backend/app/api/v1/analysis.py:21`

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from core.engine import create_engine
```

通过硬编码相对路径修改 `sys.path` 来导入 engine 模块。在打包部署或 pytest 环境下路径计算可能出错。应改为标准 Python 包管理（setup.py/pyproject.toml 或 PYTHONPATH）。

---

## 低危

### 13. 废弃 `workflow_old/` 目录未清理

`backend/core/engine/workflow_old/src/` 包含 ~20 个与 `core/engine/` 几乎相同的文件副本（orchestrator.py、router.py、data_providers/ 等）。PROGRESS.md 已标记为待清理。

---

### 14. `reports/page.tsx` 报告的 `is_locked` 锁定逻辑不一致

`backed/reports.py` 中日报/周报 `is_locked: False`，月报 `is_locked: True`。但前端 `reports/page.tsx` 未根据 `is_locked` 做任何 UI 区分——所有报告可查看，付费墙未生效。

---

### 15. `cycle/page.tsx` "趋势验证"区块是占位符

```typescript
<p className="text-text-muted text-sm">PMI / PPI / CPI 近 24 个月走势图（数据加载中...）</p>
```

图表从未加载，永远显示"数据加载中..."。用户看到假 loading 提示。

---

### 16. `cycle/page.tsx` "顶部定调"卡片数据与"周期定位"卡片重复调用

`market/page.tsx` 和 `cycle/page.tsx` 各自独立调用 `getMacroData()`，同一页面加载两个请求。`getMacroData` 无缓存层，重复调 akshare。

---

### 17. 前端目录中 `page_20260616_*` 备份文件未清理

`frontend/src/app/(app)/market/cycle/page_20260616_205100_680.tsx` 等 3 个备份文件留在源码目录中。Next.js App Router 会尝试将它们当作页面路由。

---

## 建议修复优先级

| 优先级 | 编号 | 问题 | 工时 |
|--------|------|------|------|
| P0 | #1 | `current_phase` 硬编码 | 5min |
| P0 | #2 | 数据库路径改为环境变量 | 10min |
| P0 | #5 | `bottomGrowers` 排序修正 | 5min |
| P1 | #3 | 清理重复 cycle-locator 端点 | 30min |
| P1 | #4 | 兜底数据加入不确定性标注 | 20min |
| P1 | #6 | 行业数据接入数据库 | 1h |
| P1 | #7 | 前端 locked 状态与后端对齐 | 15min |
| P1 | #8 | cycle页 9指标 vs 3-4 不对齐 | 30min |
| P2 | #9 | reports/portfolio 接入真实数据 | 2h |
| P2 | #10 | Thread 改 ThreadPoolExecutor | 30min |
| P2 | #11 | CORS 限制域名 | 5min |
| P2 | #12 | sys.path 改包管理 | 30min |
| P2 | #13-#17 | 清理/文档/UI修正 | 1.5h |

---

## 正面评价

1. **架构设计完整** — 引擎六步分析（天时/地利/人和）+ 信号系统 + 付费拦截 + 数据契约校验，设计层级清晰
2. **前端设计质量高** — Stripe 风格统一，lucide-react 图标规范，mobile 响应式考虑周全
3. **测试覆盖扎实** — 86 个单元测试（engine/tests/），conftest 配置规范
4. **PR 文档齐全** — SPEC.md / PROGRESS.md / CLAUDE.md / DESIGN.md / SYSTEM_PROMPT.md 设计链完整
5. **数据层降级策略** — DB 优先 → akshare 降级 → 兜底数据，超时控制 5 秒机制设计合理
