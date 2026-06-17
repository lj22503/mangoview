"""
Mangofolio API 访问控制

按 PROJECT_INVENTORY.md 需求 6.2-6.4 实现。
"""

import logging
from typing import Any, Dict, Optional

from .tier_model import UserTier, has_access

logger = logging.getLogger(__name__)


def filter_signal_by_tier(
    signal: Dict,
    user_tier: UserTier,
) -> Dict:
    """
    根据用户层级过滤信号返回值

    - GUEST/FREE：只返回基础信息 + 3 句话总结
    - BASIC：返回完整信号
    - VIP：完整 + 监控配置 + 关联信号
    """
    if user_tier in (UserTier.GUEST, UserTier.FREE):
        return {
            "signal_type": signal.get("signal_type", ""),
            "direction": signal.get("direction", ""),
            "intensity": signal.get("intensity", ""),
            "simple_conclusion": _generate_simple_conclusion(signal),
            "access_tier_required": "BASIC",
            "_upgrade_prompt": "升级到付费版查看完整六步分析",
        }

    if user_tier == UserTier.BASIC:
        # 返回完整信号
        result = dict(signal)
        result.pop("_upgrade_prompt", None)
        return result

    if user_tier == UserTier.VIP:
        # 完整 + 监控 + 关联
        return {
            **signal,
            "monitoring_config": signal.get("monitoring_config", {}),
            "related_signals": signal.get("related_signals", []),
        }

    # GUEST fallback
    return filter_signal_by_tier(signal, UserTier.FREE)


def _generate_simple_conclusion(signal: Dict) -> str:
    """
    生成"简单结论"

    按需求 6.4 定义：
    - ≤ 3 句话（100 字以内）
    - 仅数据陈述，不含分析推导
    - 不含信号方向/置信度/行动建议
    """
    signal_type = signal.get("signal_type", "")
    layer = signal.get("layer", "")
    key_vars = signal.get("key_variables", [])

    parts = []
    if signal_type:
        parts.append(f"当前{signal_type}信号已触发。")

    for var in key_vars[:2]:
        if isinstance(var, dict):
            name = var.get("name", "")
            value = var.get("value", "")
            if name and value:
                parts.append(f"{name}: {value}。")

    conclusion = " ".join(parts)
    if len(conclusion) > 100:
        conclusion = conclusion[:97] + "..."

    return conclusion


def check_daily_limit(
    user_tier: UserTier,
    daily_signal_views: int,
    monthly_deep_analyses: int,
    active_monitor_count: int,
) -> Optional[str]:
    """
    检查免费额度硬边界

    Returns:
        None = 允许
        str = 拒绝原因和升级引导
    """
    if user_tier in (UserTier.GUEST, UserTier.FREE):
        if daily_signal_views >= 10:
            return "每日信号摘要查看已达上限（10 次/天），升级付费版解锁无限查看"

        if monthly_deep_analyses >= 3:
            return "月度深度分析调用已达上限（3 次/月），升级付费版获取更多调用额度"

        if active_monitor_count >= 3:
            return "实时监控信号已达上限（3 个），升级 VIP 获取无限信号监控"

    return None
