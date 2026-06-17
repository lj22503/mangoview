# Mangofolio 分析引擎

## 开工流程
1. 读 `COMPONENT_MAP.md` — 了解组件结构和 DAG
2. 读 `PROGRESS.md` — 了解当前进度和待办
3. 运行 `python -m pytest tests/` 确认基线通过

## 产出标准
- 新功能必须带测试
- 修改后全量测试通过（当前 68 个）
- 更新 `PROGRESS.md` 记录变更

## 项目结构
```
engine/             # Python 包，分析引擎
├── contract/       # 数据契约（Schema）
├── signals/        # 信号系统
├── analysis/       # 六步分析框架
│   ├── tianshi/    # 天时层（宏观）
│   ├── dili/       # 地利层（事件）
│   └── renhe/      # 人和层（公司/基金）
├── middleware/     # 付费拦截
├── tests/          # 测试（pytest）
└── orchestrator.py # 主调度器
```

## 测试
```bash
cd engine && python -m pytest tests/ -v
```
