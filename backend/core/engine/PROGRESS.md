# Mangofolio 分析引擎进度

> 更新：2026-06-12
> 构建顺序参照 `COMPONENT_MAP.md` 的 DAG

---

## 当前阶段：Phase 3 完成 ✅

### Phase 1 — 核心骨架 ✅
| 组件 | 状态 |
|------|------|
| `contract/` — Schema 定义 + 校验器 + 提炼传递 | ✅ |
| `signals/` — 信号模型 + 注册表 + 聚合器 | ✅ |
| `analysis/` — 六步执行器 + 完成检测 + 回退管理 | ✅ |
| `orchestrator.py` — 主调度器 | ✅ |

### Phase 2 — 三层内容 ✅
| 组件 | 状态 |
|------|------|
| `analysis/tianshi/` — 7 步 handler + 周期矩阵 + Scale 筛选 | ✅ |
| `analysis/dili/` — 7 步 handler + 叙事识别 + Scale 筛选 | ✅ |
| `analysis/renhe/` — 公司/基金 handler + 分类器 | ✅ |

### Phase 3 — 工程化 ✅
| 组件 | 状态 | 说明 |
|------|------|------|
| `middleware/upgrade_triggers.py` | ✅ | 升级转化逻辑（触发规则 + 使用追踪 + 提示格式化） |
| `signals/signal_api.py` | ✅ | FastAPI 路由（8 个端点，含自动取数+分析） |
| `data_fetcher.py` | ✅ | 统一数据获取层（天时/地利/人和，三级降级） |
| `tests/test_phase3.py` | ✅ | 18 个测试（升级触发 + API 端到端） |

---

## 组件总览

```
engine/
├── contract/          # 数据契约 ✅
├── signals/           # 信号系统 + FastAPI 路由 ✅
├── analysis/          # 六步分析框架（三层）✅
│   ├── tianshi/       # 天时（宏观）
│   ├── dili/          # 地利（事件）
│   └── renhe/         # 人和（公司/基金）
├── data_fetcher.py    # 统一数据获取层 ✅
├── middleware/        # 付费拦截 + 升级转化 ✅
├── tests/             # 86 个测试 ✅
├── orchestrator.py    # 主调度器 ✅
├── CLAUDE.md          # 项目规范 ✅
└── PROGRESS.md        # 本文件 ✅
```

## 测试概况

| 指标 | 值 |
|------|----|
| 测试总数 | **86**（pytest） |
| 测试文件 | 5 个 |
| 零警告 | ✅（`utcnow` 全部清理） |
| 运行方式 | `python -m pytest tests/` |

## 已建 API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/analyze` | 单层分析（手动传 input_data） |
| POST | `/api/v1/analyze/multi` | 多层聚合分析 |
| POST | `/api/v1/analyze/auto` | 自动取数+分析（一步到位） |
| POST | `/api/v1/fetch` | 预览数据获取结果 |
| GET | `/api/v1/signals` | 信号列表 |
| GET | `/api/v1/signals/{id}` | 信号详情 |
| GET | `/api/v1/stats` | 引擎统计 |
| GET | `/api/v1/aggregate` | 聚合结果 |

Header: `X-User-Tier: FREE / BASIC / VIP`, `X-User-Id: <user_id>`

## 明天可继续的方向

1. **本地起服务测试** — `uvicorn` 加载 `signal_api.py` 验证端到端
2. **数据接入层** — `data_providers/` 对接真实行情/宏观数据源
3. **前端绑定** — B 端 pipeline 调 API

## 部署配置 ✅ (2026-06-12)

| 文件 | 说明 |
|------|------|
| `core/requirements.txt` | 部署用依赖（从 engine/ 提至 core/ 层） |
| `core/.env.example` | 环境变量模板 |
| `Dockerfile` | 多阶段构建（python:3.11-slim） |
| `docker-compose.yml` | 一键启动 |
| `.dockerignore` | 构建上下文排除规则 |

---

## 运行方式

```bash
cd D:\claudework\workspace\mangofolio\core\engine
python -m pytest tests/ -v                # 全量测试
python -m pytest tests/test_phase3.py -v  # Phase 3 专项
```
