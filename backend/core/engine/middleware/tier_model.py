"""
Mangofolio 用户层级模型

按 PROJECT_INVENTORY.md 需求 6.1 定义。
"""

from enum import Enum
from typing import Optional


class UserTier(str, Enum):
    GUEST = "GUEST"
    FREE = "FREE"
    BASIC = "BASIC"
    VIP = "VIP"


_TIER_RANK = {
    UserTier.GUEST: 0,
    UserTier.FREE: 1,
    UserTier.BASIC: 2,
    UserTier.VIP: 3,
}


def tier_rank(tier: UserTier) -> int:
    return _TIER_RANK.get(tier, 0)


def has_access(user_tier: UserTier, required_tier: UserTier) -> bool:
    """检查用户是否有权访问某层级内容"""
    return tier_rank(user_tier) >= tier_rank(required_tier)
