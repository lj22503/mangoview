# 🏛️ Mangoview — A Good Investment Decision Needs Only 3 Checks

> **One-liner**: A good decision needs only three checks — Is the timing right? Is the company solid? Are you being stupid?

## What problem does this solve?

Investors often get carried away by narratives, act without discipline, and regret afterwards. Mangoview forces a structured 3-layer × 6-step analysis before any decision.

## The 3 Checks (天时 / 地利 / 人和)

| Check | Translation | Question |
|---|---|---|
| 天时 | Timing | Is the macro cycle / industry rotation favorable? |
| 地利 | Company | Are the fundamentals sound? |
| 人和 | Self-bias | Are you being objective, or just emotional? |

## Core Capabilities

| Feature | Location | Status |
|---|---|---|
| 3-Layer × 6-Step Analysis Engine | `backend/core/engine/` | ✅ Phase 1-3 done |
| Signal System | `backend/core/engine/signals/` | ✅ 8 API endpoints |
| Data Collectors | `backend/core/data/providers/` | ✅ AKShare / 东方财富 / 天天基金 / 新浪 / tushare |
| FastAPI Backend | `backend/app/` | ✅ market / tools / portfolio / reports / analysis |
| Next.js Frontend | `frontend/` | ✅ Next.js 14, full page structure |
| 86+ Unit Tests | `backend/core/engine/tests/` | ✅ |

## Quick Start

```bash
# 1. Backend deps
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env, fill in DEEPSEEK_API_KEY / TUSHARE_TOKEN / etc.

# 2. Start backend
python api_server.py
# Open http://localhost:8000/docs

# 3. Start frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Architecture

```
mangoview/
├── backend/                      ← FastAPI
│   ├── app/api/v1/               ← market / tools / portfolio / reports / analysis
│   ├── app/models/
│   ├── app/services/
│   ├── core/
│   │   ├── engine/               ← Analysis engine (3 layers × 6 steps)
│   │   │   ├── analysis/         ← 天时 / 地利 / 人和
│   │   │   ├── signals/         ← Signal system
│   │   │   ├── contract/        ← Data contracts
│   │   │   ├── middleware/      ← Paywall interceptor
│   │   │   └── tests/           ← 86+ tests
│   │   └── data/providers/       ← AKShare / 东方财富 / 天天基金 / 新浪 / tushare
│   └── scripts/                  ← Data collection scripts
├── frontend/                     ← Next.js 14 + Tailwind + Recharts/ECharts
│   └── src/
│       ├── app/
│       │   ├── (app)/            ← Authed pages (market/cycle, market/industry, market/events, tools, portfolio, reports, about)
│       │   └── (landing)/        ← Landing page
│       ├── components/           ← Market component library
│       └── lib/                  ← API client
├── skills/                       ← investment-framework-skill (git submodule)
└── docs/
    ├── inventory/                 ← Design docs (19 files)
    └── SPEC.md                    ← Product spec
```

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Frontend**: Next.js 14 + Tailwind + Recharts / ECharts
- **Data Sources**: AKShare, 东方财富, 天天基金, 新浪, tushare
- **Knowledge Base**: investment-framework-skill (submodule)

## 3-Layer × 6-Step Pipeline

### Layer 1: 天时 (Timing)
- Macro cycle (Merrill clock / Kondratieff)
- Industry rotation signals
- Market sentiment

### Layer 2: 地利 (Company)
- Fundamentals (revenue / profit / cash flow)
- Competitive position
- Valuation (DCF / relative)

### Layer 3: 人和 (Self-bias)
- Loss aversion detection
- Herding / FOMO check
- Overconfidence guard
- Decision history review

### 6 Steps
1. **Collect** multi-source data
2. **Filter** signal noise
3. **Judge** direction (long / short / wait)
4. **Analyze** company fundamentals
5. **Self-check** bias
6. **Decide** with audit trail

## License

MIT License — Free to use, please credit source.

---

**Version**: v1.0 (Phase 1-3 complete)
**Live demo**: https://mangoview.vercel.app
**GitHub**: https://github.com/lj22503/mangoview
**Other languages**: [简体中文](README.md)