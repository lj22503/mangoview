# 10 付费分层

> 来源：PROJECT_INVENTORY.md 需求 6
> 主题：用户层级模型 + API 访问控制 + 简单结论标准 + 升级转化

---

## 目标

基于用户层级限制分析深度

---

## 6.1 用户层级模型

| 层级 | 标识 | 定价 | 可见内容 |
|------|------|------|---------|
| 访客 | GUEST | 免费 | 数据展示 + 简单结论（无六步） |
| 免费用户 | FREE | 免费 | 数据展示 + 简单结论 |
| 付费用户 | BASIC | 按需/订阅 | 完整六步分析 + 信号 |
| VIP | VIP | 月/年订阅 | 完整分析 + 实时监控 + 多层联动 |

---

## 6.2 API 访问控制

### 实现方式

同一接口，通过 `Authorization` header 判断层级，返回不同深度

### 层级判断逻辑

```python
def get_access_tier(token):
    if not token: return "GUEST"
    # 解析 token，获取用户层级
    return user.tier  # GUEST | FREE | BASIC | VIP
```

### 返回字段控制

```python
def filter_by_tier(signal, tier):
    if tier == "GUEST" or tier == "FREE":
        # 只返回基础信息
        return {
            "signal_type": signal.signal_type,
            "direction": signal.direction,
            "simple_conclusion": signal.summary_3sentences,  # 3句话总结
            "access_tier_required": "BASIC"
        }
    elif tier == "BASIC":
        # 返回完整六步 + 信号
        return signal  # 全部字段
    elif tier == "VIP":
        # 完整 + 实时监控配置
        return {
            **signal,
            "monitoring_config": signal.get_monitoring_config(),
            "related_signals": signal.get_related_signals()
        }
```

### 付费墙展示

- 前端检测 `access_tier_required` 字段
- 若当前用户层级不足，显示付费引导

---

## 6.3 层级升级触发点

| 触发位置 | 提示文案 |
|----------|---------|
| 查看六步分析 | "升级到付费版查看完整分析" |
| 查看信号详情 | "升级到 VIP 解锁实时监控" |
| 多层联动 | "VIP 专属功能" |

### 验收标准

- 同一信号接口，不同用户看到不同深度
- 不需要多个接口，层级在返回字段中体现

---

## 6.4 "简单结论"标准与升级转化（自进化补充）

### "简单结论"定义（访客/免费用户可见）

- 字数 ≤ 3 句话（100 字以内）
- 内容范围：仅包含数据陈述（如"PMI 当前值 50.8"），不含分析推导
- 禁止输出：信号方向、置信度、行动建议、归因分析
- 含引导文案："升级后可查看完整六步分析"

### 升级转化触发指标

| 触发行为 | 转化动作 | 目标层级 |
|---------|---------|---------|
| 同一信号 7 天内查看 ≥ 3 次 | 弹出付费引导浮窗 | FREE → BASIC |
| 在付费墙页面停留 > 10s | 显示"今日特惠"卡片 | FREE → BASIC |
| 累计查看 5 个不同信号的摘要 | 推送周卡试用邀请 | FREE → BASIC |
| 连续使用 30 天（免费层） | 推送年付折扣 | BASIC → VIP |
| 触达监控信号上限（3 个免费信号） | 提示"升级获取无限信号监控" | BASIC → VIP |

### 免费额度硬边界

- 每日信号摘要查看：10 次/天
- 月度深度分析调用：3 次/月
- 实时监控信号：最多 3 个
- 超过边界统一响应 402 Payment Required + 升级引导

---

## 关联

- 分析引擎：见 [04-analysis-engine.md](./04-analysis-engine.md)
- 信号模型：见 [05-signal-system.md](./05-signal-system.md)
- 数据契约：见 [11-contracts.md](./11-contracts.md)
- 技术实现（API 分层）：见 [16-tech.md](./16-tech.md)
- 决策（付费拦截位置）：见 [17-decisions.md](./17-decisions.md)
