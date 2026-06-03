# MangoView

> **Slogan**: 自上而下，看清每一笔投资  
> **定位**: 基于经典框架的 SaaS 投资辅助工具  
> **域名**: view.mangofolio.com  
> **MVP 目标**: 2026-06-17（2 周）  

---

## 项目结构

```
mangoview/
├── docs/                      # 文档
│   ├── SPEC.md               # 技术规格
│   ├── DESIGN.md             # 设计规范
│   └── DATA_TEST_REPORT.md   # 数据测试报告
├── frontend/                  # 前端项目（Next.js 14）
│   ├── src/
│   │   ├── app/              # App Router
│   │   │   ├── page.tsx      # 首页
│   │   │   ├── market/       # 市场看版
│   │   │   ├── tools/        # 工具集
│   │   │   ├── portfolio/    # 配置中心
│   │   │   └── reports/      # 扫描报告
│   │   ├── components/       # 公共组件
│   │   └── lib/              # 工具函数
│   └── package.json
├── backend/                   # 后端项目（FastAPI）
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── api/              # API 路由
│   │   ├── services/         # 业务逻辑
│   │   ├── models/           # 数据模型
│   │   └── utils/            # 工具函数
│   └── scripts/              # 数据采集脚本
├── data/                      # 数据（SQLite）
└── README.md
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14 + Tailwind CSS |
| 后端 | Python FastAPI |
| 数据库 | SQLite |
| 数据源 | akshare + tushare |
| 部署 | PM2 + Cloudflare Tunnel |

---

## 时间线

| Phase | 时间 | 内容 |
|-------|------|------|
| Phase 1 | 3 天 | 基础设施 + 数据采集 |
| Phase 2 | 5 天 | 核心功能开发 |
| Phase 3 | 4 天 | 测试 + 部署 |
| **MVP 上线** | **12 天** | **2026-06-17** |

---

## 团队分工

| 角色 | 负责人 | 内容 |
|------|--------|------|
| 产品/设计 | 燃冰 | 需求定义、设计审核 |
| 需求文档 | ant | 编写需求文档、技术规格 |
| 开发 | 开发团队 | 前端/后端开发 |
| 测试 | 燃冰 | 功能测试、用户体验 |
| 部署/运维 | ant | 服务器配置、域名解析 |

---

## 快速开始

```bash
# 后端
cd backend
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

---

*最后更新：2026-06-03*
