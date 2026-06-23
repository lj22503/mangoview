# PRD: 数据层真实接入（Reports + Portfolio）

> 创建日期：2026-06-22
> 状态：待审批
> Triage：ready-for-agent

---

## Problem Statement

当前 MangoView 有两个核心页面展示的是硬编码假数据，无法提供投资参考价值：

1. **扫描报告页**（`/reports`）— 日报、周报、月报全部是固定 mock 文案，不读取任何真实市场数据
2. **配置中心**（`/portfolio`）— 资产配置比例由三个 if/else 分支写死，不调用已完成的 analysis engine，用户得到的是假建议

数据库里连 `Report` 表都不存在。前端页面已就绪，但后端数据管道是断裂的。

## Solution

完成从"假数据占位"到"真实数据驱动"的最后一步：建表 → 写生成逻辑 → 替换 mock。

| 维度 | 现状 | 目标 |
|------|------|------|
| 报告存储 | 无表，代码内硬编码 | SQLite `Report` 表，支持 CRUD |
| 报告内容 | 循环生成的固定文案 | 从 `market_service` 取宏观/北向/行业数据，按模板组装 |
| 报告生成 | 无 | 数据采集完成后自动生成（定时任务） + 手动触发 API |
| 配置中心 | 3 个 if/else 分支 | 调用 analysis engine 的 `asset_allocation`，随周期动态变化 |

## User Stories

1. 作为普通用户，我想要每天早上看到基于最新宏观数据的日报，以便了解当前市场状态
2. 作为普通用户，我想要每周一看到总结了本周趋势和北向资金动向的周报，以便做周度调仓决策
3. 作为付费用户，我想要每月底看到完整的行业估值分析和配置建议月报，以便做月度配置调整
4. 作为普通用户，我想要在配置中心输入投资金额和风险偏好后，得到基于当前周期定位的真实资产配置建议，而不是固定比例
5. 作为普通用户，我想要在报告页区分哪些是免费可看的摘要、哪些需要付费解锁完整版，以便决定是否订阅
6. 作为开发者，我想要一个手动触发生成报告的 API，以便调试和补发报告
7. 作为运维人员，我想要每日数据采集脚本自动触发报告生成，以便减少人工操作

## Implementation Decisions

### M1: Report 数据模型

- 新增 `Report` ORM 类，字段：`id`（自增）、`type`（daily/weekly/monthly）、`report_date`、`title`、`summary`、`full_content`、`is_locked`、`created_at`
- `is_locked` 语义：月报为 `True`（需付费），日报/周报为 `False`
- `summary` 对外免费可见，`full_content` 仅付费用户可查看详情
- 建表使用 SQLAlchemy `Base.metadata.create_all`，与现有 9 张表保持一致

### M2: 报告生成服务

- 新建 `ReportService`，提供 `generate_report(type, db)` 方法
- 日报模板：PMI/CPI/北向资金净额 + 一句话解读
- 周报模板：本周宏观指标变化方向 + 行业涨幅 Top3/Bottom3 + 北向累计 + 信号摘要
- 月报模板：月报 = 周报内容 + 行业 PE 分位 + 四周期定位 + 配置建议（免费用户看到摘要，付费看全部）
- 数据来源全部走 `market_service` 现有接口（`fetch_macro_indicators` / `fetch_north_money` / `fetch_industries`）
- 解读文案用简单的条件判断生成（如 PMI > 50 → "制造业景气"，< 50 → "制造业收缩"），不引入 LLM

### M3: Reports API 重构

- `GET /v1/reports` — 从 DB 查报告列表，支持 `type` + `page` + `limit` 参数
- `GET /v1/reports/{id}` — 报告详情，付费用户返回 `full_content`，免费用户返回 `null`
- `POST /v1/reports/generate` — 手动触发报告生成（仅管理员/开发用）
- 去掉当前全部硬编码 mock 逻辑

### M4: Portfolio 接 Engine

- 调用 nalysis.py 的 sset-allocation 端点 POST /v1/analysis/asset-allocation（该端点已返回数字比例，无需额外开发）
- 在对接层做 commodity→gold 映射（engine 用 commodity 表示商品/黄金，前端展示为 gold）
- 删掉当前 3 个 if/else 硬编码分支
- 保留用户输入（`risk_profile` / `investable_amount` / `familiar_industries`）作为 engine 输入

### M5: 采集脚本扩展

- 在 `scripts/daily_collector.py` 末尾加一步：采集完成后调用 `ReportService.generate_report("daily")`
- 周报/月报暂时手动触发（后续加 cron 表达式）

## API Contracts

### `GET /v1/reports?type=daily&page=1&limit=10`

```json
{
  "code": 0,
  "data": {
    "reports": [{
      "id": 1,
      "type": "daily",
      "report_date": "2026-06-22",
      "title": "2026-06-22 日报",
      "summary": "PMI 50.2, 北向净流入 12.3 亿",
      "is_locked": false,
      "created_at": "2026-06-22T09:00:00"
    }],
    "total": 15,
    "page": 1,
    "limit": 10
  }
}
```

### `GET /v1/reports/{id}`
```json
{
  "code": 0,
  "data": {
    "report": {
      "id": 1,
      "type": "daily",
      "summary": "...",
      "full_content": "## 宏观快照\n...",
      "is_locked": false
    }
  }
}
```

### `POST /v1/reports/generate`
```json
{ "code": 0, "data": { "report_id": 1, "type": "daily" } }
```

### `POST /v1/portfolio/generate`（接口不变，内部逻辑替换）

已有接口签名：`POST /v1/portfolio/generate`，入参 `PortfolioRequest`（`risk_profile` / `investable_amount` / `familiar_industries`），出参 `{ strategy: { logic, allocation }, tactics: {...} }`

## Testing Decisions

- **测试什么**：只测外部行为，不测实现细节
  - `ReportService.generate_report("daily", db)` 返回的 report 对象字段完整且有意义
  - `GET /v1/reports` 从有数据的 DB 返回正确分页
  - `POST /v1/portfolio/generate` 返回的 `allocation` 之和 ≈ 1.0，且 `logic` 字段非空
- **不测试什么**：文案具体内容、模板拼装细节、DB ORM 细节
- **测试框架**：沿用现有 `pytest` + `conftest.py`（backend/core/engine/tests/ 下已有 86 个用例）
- **需写测试的模块**：M2（ReportService）、M3（Reports API）、M4（Portfolio）
- **参考测试**：`test_analysis_engine.py` 的 mock engine + db fixture 模式

## Out of Scope

- LLM 生成报告内容（当前用规则模板）
- 报告推送通知（飞书/微信）
- 前端详情页 UI 改造（现有列表页已足够）
- 周报/月报的定时自动生成（手动 API + 日报自动生成先行）

## Further Notes

- Portfolio 的 engine 调用已有完整实现（`analysis.py:cycle-locator`），本 PRD 只做"对接"，不重复开发 engine
- 报告模板文案暂时用条件判断生成，后续可替换为 LLM 生成，接口不变
- 月报的 `full_content` 字段随数据积累可逐步丰富，当前 MVP 版本不低于周报水平即可
