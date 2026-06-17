"""
天时层：横向 Scale 筛选

从海量宏观数据流中筛选出值得深度分析的事件。
按 PROJECT_INVENTORY.md 需求 2.1 定义的阈值实现。
"""

from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class TriggerLevel(str, Enum):
    LEVEL1 = "level1"   # 立即分析
    LEVEL2 = "level2"   # 关注
    NONE = "none"       # 忽略


# ── 筛选规则（需求 2.1 表） ───────────────────────────────────

SCALE_RULES = [
    {
        "name": "利率变动",
        "key": "interest_rate_change_bp",
        "condition": lambda v: abs(v) > 10,
        "level": TriggerLevel.LEVEL1,
        "description": "利率单日变动 > 10bp",
    },
    {
        "name": "美元指数突破",
        "key": "dxy_break",
        "condition": lambda v: v is not None,
        "level": TriggerLevel.LEVEL1,
        "description": "美元指数突破关键位",
    },
    {
        "name": "油价异动",
        "key": "oil_change_pct",
        "condition": lambda v: abs(v) > 3,
        "level": TriggerLevel.LEVEL1,
        "description": "油价单日涨跌 > 3%",
    },
    {
        "name": "PMI穿越荣枯线",
        "key": "pmi_cross_50",
        "condition": lambda v: v is True,
        "level": TriggerLevel.LEVEL1,
        "description": "PMI 穿越荣枯线 50",
    },
    {
        "name": "VIX突破",
        "key": "vix_break",
        "condition": lambda v: v is not None and (v > 25 or v < 15),
        "level": TriggerLevel.LEVEL1,
        "description": "VIX > 25 或 < 15",
    },
    {
        "name": "行业动量反差",
        "key": "sector_momentum_gap",
        "condition": lambda v: v is not None and abs(v) > 15,
        "level": TriggerLevel.LEVEL2,
        "description": "强弱行业差距 > 15%",
    },
    {
        "name": "CPI超预期",
        "key": "cpi_surprise",
        "condition": lambda v: v is not None and abs(v) > 0.5,
        "level": TriggerLevel.LEVEL2,
        "description": "CPI 偏离预期 > 0.5%",
    },
    {
        "name": "社融断崖",
        "key": "social_financing_change",
        "condition": lambda v: v is not None and v < -30,
        "level": TriggerLevel.LEVEL2,
        "description": "社融增量环比下降 > 30%",
    },
]


def scale_filter(macro_data: Dict[str, Any]) -> List[Dict]:
    """
    对宏观数据流执行 Scale 筛选

    Args:
        macro_data: 宏观数据字典，key 为字段名

    Returns:
        触发的事件清单（按优先级排序）
    """
    triggered = []

    for rule in SCALE_RULES:
        value = macro_data.get(rule["key"])
        if value is None:
            continue

        try:
            if rule["condition"](value):
                triggered.append({
                    "signal_type": rule["name"],
                    "level": rule["level"].value,
                    "description": rule["description"],
                    "current_value": value,
                    "required_action": "立即分析" if rule["level"] == TriggerLevel.LEVEL1 else "加入关注列表",
                })
        except (TypeError, ValueError):
            continue

    # LEVEL1 优先
    triggered.sort(key=lambda t: 0 if t["level"] == "level1" else 1)

    return triggered


def has_trigger(macro_data: Dict[str, Any]) -> Tuple[bool, List[Dict]]:
    """
    检查是否有触发事件（快捷方法）

    Returns:
        (has_any, triggered_list)
    """
    triggered = scale_filter(macro_data)
    return len(triggered) > 0, triggered


# ── 常用的宏观数据模板 ────────────────────────────────────────

MACRO_INDICATORS_TEMPLATE = {
    "pmi": None,              # float
    "cpi": None,              # float
    "cpi_surprise": None,     # float
    "ppi": None,              # float
    "gdp": None,              # float
    "m2": None,               # float
    "social_financing": None, # float
    "social_financing_change": None,  # float (%)
    "interest_rate": None,    # float (%)
    "interest_rate_change_bp": None,  # float (bp)
    "dxy_break": None,        # str or None
    "oil_change_pct": None,   # float (%)
    "pmi_cross_50": None,     # bool
    "vix": None,              # float
    "vix_break": None,        # bool
    "sector_momentum_gap": None,  # float (%)
    "tenure_yield": None,     # float
    "credit_spread": None,    # float
}
