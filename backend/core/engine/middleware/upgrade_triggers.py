"""
Mangofolio 升级转化逻辑

按需在免费用户触达限制时，生成上下文相关的升级引导。
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from .tier_model import UserTier, tier_rank

logger = logging.getLogger(__name__)

# ── 升级时机规则 ──────────────────────────────────────────────

UPGRADE_RULES = {
    UserTier.FREE: {
        "next_tier": UserTier.BASIC,
        "triggers": [
            {
                "reason": "daily_limit",
                "condition": lambda ctx: ctx.get("daily_views", 0) >= 8,
                "message": "今日已查看 {daily_views} 次信号，免费版每日限 10 次。升级 BASIC 解锁无限查看。",
                "priority": 1,
            },
            {
                "reason": "deep_analysis",
                "condition": lambda ctx: ctx.get("monthly_analyses", 0) >= 2,
                "message": "本月已使用 {monthly_analyses} 次深度分析，免费版每月限 3 次。升级 BASIC 获取更多额度。",
                "priority": 2,
            },
            {
                "reason": "monitor_limit",
                "condition": lambda ctx: ctx.get("active_monitors", 0) >= 2,
                "message": "当前监控 {active_monitors} 个信号，免费版限 3 个。升级 VIP 获得无限监控。",
                "priority": 3,
            },
        ],
        "benefits": [
            "完整六步分析报告",
            "每日无限信号查看",
            "月度 30 次深度分析",
        ],
    },
    UserTier.BASIC: {
        "next_tier": UserTier.VIP,
        "triggers": [
            {
                "reason": "monitor_limit",
                "condition": lambda ctx: ctx.get("active_monitors", 0) >= 8,
                "message": "当前监控 {active_monitors} 个信号，BASIC 限 10 个。升级 VIP 获得无限监控。",
                "priority": 1,
            },
            {
                "reason": "advanced_features",
                "condition": lambda ctx: ctx.get("requested_feature") in ("portfolio", "backtest", "api_access"),
                "message": "BASIC 版不含 {requested_feature} 功能。升级 VIP 解锁全部高级功能。",
                "priority": 2,
            },
        ],
        "benefits": [
            "无限信号监控",
            "投资组合分析",
            "回测功能",
            "API 访问",
        ],
    },
}

# ── 使用追踪（内存实现） ──────────────────────────────────────

class UsageTracker:
    """使用量追踪器（进程内内存，生产环境应替换为 Redis/DB）"""

    def __init__(self):
        self._daily: Dict[str, int] = {}
        self._monthly: Dict[str, int] = {}
        self._date: str = ""

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _month_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def record_view(self, user_id: str):
        d = self._today()
        if self._date != d:
            self._daily.clear()
            self._date = d
        self._daily[user_id] = self._daily.get(user_id, 0) + 1

    def record_analysis(self, user_id: str):
        m = self._month_key()
        self._monthly[user_id] = self._monthly.get(user_id, 0) + 1

    def get_daily_views(self, user_id: str) -> int:
        if self._date != self._today():
            return 0
        return self._daily.get(user_id, 0)

    def get_monthly_analyses(self, user_id: str) -> int:
        return self._monthly.get(user_id, 0)

    def reset(self):
        self._daily.clear()
        self._monthly.clear()


# 全局单例
_default_tracker: Optional[UsageTracker] = None


def get_tracker() -> UsageTracker:
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = UsageTracker()
    return _default_tracker


def reset_tracker():
    """重置追踪器（测试用）"""
    global _default_tracker
    _default_tracker = None


# ── 升级判断 ──────────────────────────────────────────────────

def evaluate_upgrade(
    user_tier: UserTier,
    context: Optional[Dict] = None,
) -> Optional[Dict]:
    """
    判断当前用户是否应触发升级引导

    Args:
        user_tier: 当前用户层级
        context: 使用上下文（daily_views, monthly_analyses, active_monitors 等）

    Returns:
        升级建议（含原因、推荐层级、权益对比），无触发时返回 None
    """
    if user_tier == UserTier.VIP:
        return None  # VIP 无进一步升级

    rule_set = UPGRADE_RULES.get(user_tier)
    if not rule_set:
        return None

    ctx = context or {}
    triggers = sorted(rule_set["triggers"], key=lambda t: t["priority"])

    for trigger in triggers:
        try:
            if trigger["condition"](ctx):
                message = trigger["message"].format(**ctx)
                return {
                    "current_tier": user_tier.value,
                    "recommended_tier": rule_set["next_tier"].value,
                    "reason": trigger["reason"],
                    "message": message,
                    "benefits": rule_set["benefits"],
                }
        except Exception:
            continue

    return None


def format_upgrade_prompt(upgrade_info: Optional[Dict]) -> Optional[str]:
    """
    将升级信息格式化为展示文本

    Args:
        upgrade_info: evaluate_upgrade 的返回值

    Returns:
        格式化后的升级提示文本
    """
    if not upgrade_info:
        return None

    benefits = "\n".join(f"  • {b}" for b in upgrade_info["benefits"])
    return (
        f"💡 {upgrade_info['message']}\n\n"
        f"推荐升级至 **{upgrade_info['recommended_tier']}**，享以下权益：\n"
        f"{benefits}"
    )
