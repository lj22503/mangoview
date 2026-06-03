# MangoView 技术规格文档（Claude Code 开发指南）

> **版本**: v1.0.0  
> **日期**: 2026-06-03  
> **状态**: 草案  
> **开发工具**: Claude Code  
> **MVP 目标**: 2026-06-17（2 周）  

---

## 一、项目概述

### 1.1 基本信息

| 项目 | 内容 |
|------|------|
| **产品名** | MangoView |
| **域名** | view.mangofolio.com |
| **Slogan** | 自上而下，看清每一笔投资 |
| **定位** | 基于经典框架的 SaaS 投资辅助工具 |
| **目标用户** | 个人投资者（3-5 年经验） |
| **变现模式** | 知识星球（199 元/年） |

### 1.2 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | Next.js 14 | App Router |
| 样式 | Tailwind CSS | v3 |
| UI 组件 | shadcn/ui | 最新 |
| 图表 | Recharts | 最新 |
| 后端 | FastAPI | 0.109+ |
| 数据库 | SQLite | 内置 |
| 数据源 | akshare + tushare | 最新 |
| 部署 | PM2 + Cloudflare Tunnel | - |

---

## 二、项目结构

```
mangoview/
├── docs/                      # 文档
│   ├── prd/PRD.md            # 产品需求文档
│   ├── user-stories/USER_STORIES.md  # 用户故事
│   ├── tech-spec/TECH_SPEC.md  # 本文件
│   └── DESIGN.md             # 设计规范
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   │   ├── page.tsx      # 首页
│   │   │   ├── layout.tsx    # 布局
│   │   │   ├── market/       # 市场看版
│   │   │   ├── tools/        # 工具集
│   │   │   ├── portfolio/    # 配置中心
│   │   │   ├── reports/      # 扫描报告
│   │   │   └── about/        # 说明
│   │   ├── components/       # 公共组件
│   │   │   ├── ui/           # shadcn/ui 组件
│   │   │   ├── charts/       # 图表组件
│   │   │   ├── layout/       # 布局组件
│   │   │   └── market/       # 市场看版组件
│   │   ├── lib/              # 工具函数
│   │   │   ├── api.ts        # API 客户端
│   │   │   ├── utils.ts      # 工具函数
│   │   │   └── constants.ts  # 常量
│   │   └── styles/           # 样式
│   │       └── globals.css   # 全局样式
│   ├── public/               # 静态资源
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── backend/                   # 后端项目
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── api/              # API 路由
│   │   │   ├── market.py     # 市场看版 API
│   │   │   ├── tools.py      # 工具集 API
│   │   │   ├── portfolio.py  # 配置中心 API
│   │   │   └── auth.py       # 用户系统 API
│   │   ├── services/         # 业务逻辑
│   │   │   ├── data_adapter.py  # 数据适配层
│   │   │   ├── market_service.py  # 市场服务
│   │   │   ├── tool_service.py    # 工具服务
│   │   │   └── portfolio_service.py  # 配置服务
│   │   ├── models/           # 数据模型
│   │   │   ├── database.py   # 数据库模型
│   │   │   └── schemas.py    # Pydantic 模型
│   │   └── utils/            # 工具函数
│   ├── scripts/              # 数据采集脚本
│   │   ├── fetch_macro.py    # 宏观数据采集
│   │   ├── fetch_index.py    # 指数数据采集
│   │   └── daily_update.py   # 每日更新脚本
│   ├── requirements.txt
│   └── mangofolio.db         # SQLite 数据库
├── data/                      # 数据
│   └── cache/                # 缓存数据
└── README.md
```

---

## 三、前端开发指南

### 3.1 设计规范

**参考**：`docs/DESIGN.md`

**核心设计 token**：

```css
/* 浅色主题 */
--mango-primary: #f59e0b;
--mango-secondary: #d97706;
--surface: #ffffff;
--surface-alt: #f8fafc;
--border: #e2e8f0;
--text-primary: #0f172a;
--text-secondary: #64748b;
--success: #10b981;
--danger: #ef4444;

/* 深色主题 */
--mango-primary: #fbbf24;
--surface: #1e293b;
--surface-alt: #0f172a;
--border: #334155;
--text-primary: #f1f5f9;
--text-secondary: #94a3b8;
--success: #34d399;
--danger: #f87171;
```

### 3.2 组件规范

#### 3.2.1 按钮

```tsx
// components/ui/button.tsx
import { cn } from "@/lib/utils"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ variant = 'primary', size = 'md', className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'rounded-lg font-medium transition-all',
        variant === 'primary' && 'bg-[#f59e0b] text-[#0f172a] hover:bg-[#d97706]',
        variant === 'secondary' && 'border border-[#e2e8f0] text-[#0f172a] hover:border-[#94a3b8]',
        variant === 'ghost' && 'text-[#64748b] hover:bg-[#f8fafc]',
        variant === 'danger' && 'bg-[#ef4444] text-white hover:bg-[#dc2626]',
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2',
        size === 'lg' && 'px-6 py-3 text-lg',
        className
      )}
      {...props}
    />
  )
}
```

#### 3.2.2 卡片

```tsx
// components/ui/card.tsx
import { cn } from "@/lib/utils"

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated'
}

export function Card({ variant = 'default', className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-[#e2e8f0] bg-white p-6',
        'dark:border-[#334155] dark:bg-[#1e293b]',
        variant === 'elevated' && 'shadow-[0_1px_3px_rgba(0,0,0,0.1)]',
        className
      )}
      {...props}
    />
  )
}
```

#### 3.2.3 数据表格

```tsx
// components/ui/data-table.tsx
import { cn } from "@/lib/utils"

interface DataTableProps {
  headers: string[]
  rows: (string | number)[][]
  highlightRow?: number
}

export function DataTable({ headers, rows, highlightRow }: DataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="bg-[#f8fafc] dark:bg-[#1e293b]">
            {headers.map((header, i) => (
              <th key={i} className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className={cn(
                'border-b border-[#e2e8f0] dark:border-[#334155]',
                'hover:bg-[#fef3c7] dark:hover:bg-[#451a03]',
                highlightRow === i && 'bg-[#fef3c7] dark:bg-[#451a03]'
              )}
            >
              {row.map((cell, j) => (
                <td
                  key={j}
                  className={cn(
                    'px-4 py-3 text-sm',
                    typeof cell === 'number' && 'font-mono text-right'
                  )}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### 3.3 页面规范

#### 3.3.1 市场看版（/market）

```tsx
// app/market/page.tsx
import { MacroSnapshot } from "@/components/market/macro-snapshot"
import { CyclePosition } from "@/components/market/cycle-position"
import { IndustryMatrix } from "@/components/market/industry-matrix"
import { OpportunityScan } from "@/components/market/opportunity-scan"

export default function MarketPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-semibold text-[#0f172a] dark:text-[#f1f5f9] mb-8">
        📊 市场看版
      </h1>
      
      <MacroSnapshot />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <CyclePosition />
        <IndustryMatrix />
      </div>
      
      <OpportunityScan className="mt-8" />
    </div>
  )
}
```

#### 3.3.2 工具集（/tools）

```tsx
// app/tools/page.tsx
import { ToolCard } from "@/components/tools/tool-card"

const tools = [
  { name: '周期定位器', icon: '📐', description: '四周期嵌套分析', locked: false },
  { name: '行业分析仪', icon: '📊', description: '行业估值分析', locked: false },
  { name: '价值评估器', icon: '💎', description: '个股价值评估', locked: false },
  { name: '资产配置器', icon: '⚖️', description: '大类资产配置', locked: false },
  { name: '决策清单', icon: '✅', description: '芒格清单检查', locked: false },
  { name: '降秩引擎', icon: '🔒', description: '行业配置权重', locked: true },
  { name: '事件研判器', icon: '🔒', description: '四维评分分析', locked: true },
  { name: '回测工具', icon: '🔒', description: '策略回测验证', locked: true },
]

export default function ToolsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-semibold text-[#0f172a] dark:text-[#f1f5f9] mb-8">
        🛠️ 工具集
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tools.map((tool) => (
          <ToolCard key={tool.name} {...tool} />
        ))}
      </div>
    </div>
  )
}
```

### 3.4 主题切换

```tsx
// components/layout/theme-toggle.tsx
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <Button
      variant="ghost"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? '☀️ 浅色' : '🌙 深色'}
    </Button>
  )
}
```

---

## 四、后端开发指南

### 4.1 API 规范

#### 4.1.1 统一响应格式

```python
# app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, Any

class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
```

#### 4.1.2 市场看版 API

```python
# app/api/market.py
from fastapi import APIRouter
from app.models.schemas import APIResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/api/v1/market", tags=["market"])

@router.get("/macro")
async def get_macro_data():
    """获取宏观数据"""
    data = await MarketService.get_macro_data()
    return APIResponse(data=data)

@router.get("/industries")
async def get_industry_data(quadrant: Optional[str] = None):
    """获取行业数据"""
    data = await MarketService.get_industry_data(quadrant)
    return APIResponse(data=data)

@router.get("/opportunities")
async def get_opportunities():
    """获取机会扫描"""
    data = await MarketService.get_opportunities()
    return APIResponse(data=data)
```

### 4.2 数据适配层

**参考**：`backend/app/services/data_adapter.py`

```python
# app/services/data_adapter.py
import akshare as ak
import tushare as ts
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

class DataAdapter:
    """数据适配层 - 统一数据接口"""
    
    def __init__(self, tushare_token: str, db_path: str = "mangofolio.db"):
        self.db_path = db_path
        self._init_db()
        
        # 初始化 tushare
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建缓存表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_cache (
            key TEXT PRIMARY KEY,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_macro_pmi(self) -> pd.DataFrame:
        """获取 PMI 数据"""
        try:
            return ak.macro_china_pmi()
        except Exception as e:
            print(f"PMI 数据获取失败：{e}")
            return pd.DataFrame()
    
    def get_index_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据"""
        try:
            return self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(f"指数数据获取失败：{e}")
            return pd.DataFrame()
    
    def get_north_bound(self) -> pd.DataFrame:
        """获取北向资金数据"""
        try:
            return ak.stock_hsgt_hist_em()
        except Exception as e:
            print(f"北向资金数据获取失败：{e}")
            return pd.DataFrame()
```

### 4.3 数据库模型

```python
# app/models/database.py
import sqlite3
from datetime import datetime

class Database:
    """数据库管理"""
    
    def __init__(self, db_path: str = "mangofolio.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 宏观指标表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS macro_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_name TEXT NOT NULL,
            indicator_code TEXT NOT NULL,
            current_value REAL,
            previous_value REAL,
            direction TEXT,
            historical_percentile REAL,
            data_date DATE,
            source TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 行业估值表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS industry_valuation (
            industry_code TEXT,
            stat_date DATE,
            pe_ttm REAL,
            pe_percentile REAL,
            pb_lf REAL,
            pb_percentile REAL,
            dividend_yield REAL,
            dividend_percentile REAL,
            quadrant TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (industry_code, stat_date)
        )
        ''')
        
        # 用户配置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            risk_profile TEXT,
            time_horizon TEXT,
            investable_amount REAL,
            familiar_industries TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
```

---

## 五、部署指南

### 5.1 环境准备

```bash
# 安装 Python 3.9
cd /tmp
wget https://mirrors.huaweicloud.com/python/3.9.18/Python-3.9.18.tgz
tar xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations
make -j 4
sudo make altinstall

# 安装 Node.js（已有）
node --version

# 安装 PM2
npm install pm2 -g
```

### 5.2 后端部署

```bash
# 创建虚拟环境
cd /home/admin/.openclaw/workspace/projects/mangoview/backend
python3.9 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5.3 前端部署

```bash
# 安装依赖
cd /home/admin/.openclaw/workspace/projects/mangoview/frontend
npm install

# 构建
npm run build

# 启动
npm start
```

### 5.4 PM2 配置

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'mangoview-web',
      script: 'npm',
      args: 'start',
      cwd: './frontend',
      instances: 1,
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'mangoview-api',
      script: '.venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      cwd: './backend',
      instances: 1,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
};
```

### 5.5 Cloudflare Tunnel 配置

```bash
# 创建命名隧道
cloudflared tunnel create mangoview

# 配置 DNS
cloudflared tunnel route dns mangoview view.mangofolio.com

# 创建配置文件
cat > /home/admin/.cloudflared/mangoview.yml << 'EOF'
tunnel: mangoview
credentials-file: /home/admin/.cloudflared/xxxxx-xxxxx-xxxxx.json

ingress:
  - hostname: view.mangofolio.com
    service: http://localhost:3000
  - hostname: api.mangofolio.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# 启动隧道
cloudflared tunnel run --config /home/admin/.cloudflared/mangoview.yml mangoview
```

---

## 六、开发规范

### 6.1 代码规范

- **前端**：TypeScript + ESLint + Prettier
- **后端**：Python + Black + flake8
- **提交信息**：Conventional Commits（feat/fix/docs/style/refactor）

### 6.2 Git 工作流

```bash
# 创建功能分支
git checkout -b feature/market-dashboard

# 提交代码
git add .
git commit -m "feat: 添加市场看版页面"

# 推送分支
git push origin feature/market-dashboard

# 创建 PR
# 燃冰 review → 合并到 main
```

### 6.3 测试规范

- **单元测试**：pytest（后端）+ jest（前端）
- **集成测试**：API 测试
- **E2E 测试**：Playwright（可选）

---

## 七、常见问题

### Q1: 数据获取失败怎么办？

**A**: 检查数据源状态，使用缓存数据降级。

```python
# 优先使用缓存
cached = self.cache.get(cache_key)
if cached is not None:
    return cached

# 从数据源获取
try:
    data = self.adapter.get_macro_pmi()
    self.cache.set(cache_key, data, ttl_hours=7*24)
    return data
except Exception as e:
    print(f"数据获取失败：{e}")
    return pd.DataFrame()
```

### Q2: 如何切换深色/浅色主题？

**A**: 使用 `next-themes` 库。

```tsx
import { ThemeProvider } from "next-themes"

// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="zh">
      <body>
        <ThemeProvider attribute="class">
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Q3: 如何部署到生产环境？

**A**: 使用 PM2 + Cloudflare Tunnel。

```bash
# 启动服务
pm2 start ecosystem.config.js
pm2 save

# 启动隧道
cloudflared tunnel run --config /home/admin/.cloudflared/mangoview.yml mangoview

# 访问
# https://view.mangofolio.com
```

---

## 八、参考资源（Skill 和工具）

### 8.1 投资框架 Skill

| Skill 名称 | GitHub 位置 | 用途 |
|-----------|-------------|------|
| investment-framework-skill | https://github.com/lj22503/investment-framework-skill | 核心投资框架（自上而下方法论） |
| decision-system | ~/.openclaw/workspace/skills/decision-system/ | 决策系统（时间审计/原则构建/会议优化） |
| context-manager | ~/.openclaw/workspace/skills/context-manager/ | 上下文管理（认知地图/知识整合） |

### 8.2 数据源工具

| 工具 | 位置 | 用途 |
|------|------|------|
| akshare | https://github.com/akfamily/akshare | Python 财经数据接口库（宏观/北向资金/行业列表） |
| tushare | https://tushare.pro/ | 金融数据接口（指数 K 线/个股行情） |
| 东方财富 API | https://push2his.eastmoney.com/ | 实时行情数据（备用） |

### 8.3 开发工具

| 工具 | 位置 | 用途 |
|------|------|------|
| awesome-design-md | https://github.com/VoltAgent/awesome-design-md | DESIGN.md 设计系统参考 |
| Claude Code | https://claude.ai/ | AI 编程助手 |
| PM2 | https://pm2.keymetrics.io/ | 进程管理器 |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/ | 安全隧道（域名解析） |

### 8.4 设计参考

| 设计系统 | GitHub 位置 | 用途 |
|---------|-------------|------|
| Stripe DESIGN.md | https://getdesign.md/stripe/design-md | 紫色渐变、优雅风格参考 |
| Linear DESIGN.md | https://getdesign.md/linear.app/design-md | 超极简、精确风格参考 |
| Revolut DESIGN.md | https://getdesign.md/revolut/design-md | 深色界面、金融精度参考 |

### 8.5 数据测试报告

| 文档 | 位置 | 用途 |
|------|------|------|
| 数据测试报告 | docs/DATA_TEST_REPORT.md | akshare/tushare 数据质量测试结果 |
| 数据适配层 | backend/app/services/data_adapter.py | 数据适配层实现代码 |

---

*本文档由 ant 整理生成，供 Claude Code 开发团队使用。*  
*最后更新：2026-06-03 14:05*
