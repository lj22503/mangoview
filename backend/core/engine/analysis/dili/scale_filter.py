"""
地利层：横向 Scale 事件筛选

从海量事件流中筛选出值得深度分析的事件。
按 PROJECT_INVENTORY.md 需求 3.1 定义的规则实现。
"""

from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class EventPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── 事件筛选规则 ──────────────────────────────────────────────

EVENT_FILTER_RULES = [
    {
        "event_type": "政策事件",
        "conditions": {
            "confirmed_by_official": True,
            "involves_major_industry": True,
        },
        "priority": EventPriority.HIGH,
        "description": "官方确认 + 涉及重要行业",
    },
    {
        "event_type": "央行决议",
        "conditions": {
            "rate_change_bp": lambda v: v is not None and abs(v) >= 25,
            "balance_sheet_change": lambda v: v is not None and abs(v) > 500,
        },
        "priority": EventPriority.HIGH,
        "description": "利率变化 > 25bp 或缩表 > 500 亿",
    },
    {
        "event_type": "地缘事件",
        "conditions": {
            "involves_major_economy": True,
            "affects_trade_or_energy": True,
        },
        "priority": EventPriority.HIGH,
        "description": "涉及主要经济体 + 影响贸易/能源",
    },
    {
        "event_type": "行业事件",
        "conditions": {
            "event_category": lambda v: v in ("policy", "earnings", "competition_change"),
        },
        "priority": EventPriority.MEDIUM,
        "description": "政策+财报+竞争格局变化",
    },
    {
        "event_type": "公司事件",
        "conditions": {
            "event_category": lambda v: v in ("mega_merger", "earnings_surprise", "black_swan"),
        },
        "priority": EventPriority.MEDIUM,
        "description": "重大并购/财报超预期/黑天鹅",
    },
    {
        "event_type": "常规市场数据",
        "conditions": {},
        "priority": EventPriority.LOW,
        "description": "常规数据发布，仅记录",
    },
]


def scale_filter_events(events: List[Dict]) -> List[Dict]:
    """
    对事件流执行 Scale 筛选

    Args:
        events: 事件列表，每个事件包含描述和元数据

    Returns:
        值得深度分析的事件清单（按优先级排序）
    """
    scored = []
    for event in events:
        priority, score = _score_event(event)
        if priority != EventPriority.LOW:
            scored.append({
                "event_id": event.get("event_id", ""),
                "event_title": event.get("title", event.get("event", "")),
                "description": event.get("description", event.get("event", "")),
                "priority": priority.value,
                "score": score,
                "source": event.get("source", "unknown"),
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
            })

    # 按优先级+分数排序
    scored.sort(key=lambda e: (
        0 if e["priority"] == "high" else 1,
        -e["score"],
    ))

    return scored


def _score_event(event: Dict) -> Tuple[EventPriority, int]:
    """评分单个事件"""
    scores = []
    for rule in EVENT_FILTER_RULES:
        match = True
        match_count = 0
        for key, condition in rule["conditions"].items():
            value = event.get(key)
            if value is None:
                match = False
                break
            if callable(condition):
                try:
                    if not condition(value):
                        match = False
                        break
                except (TypeError, ValueError):
                    match = False
                    break
            elif value != condition:
                match = False
                break
            match_count += 1

        if match and match_count > 0:
            scores.append(rule["priority"])

    if not scores:
        return EventPriority.LOW, 0

    best = min(scores, key=lambda p: 0 if p == EventPriority.HIGH else 1 if p == EventPriority.MEDIUM else 2)
    score_map = {EventPriority.HIGH: 20, EventPriority.MEDIUM: 10, EventPriority.LOW: 0}
    return best, score_map.get(best, 0)


# ── 三把尺子评分 ──────────────────────────────────────────────

THREE_RULERS = {
    "irreversibility": {
        "name": "不可逆性",
        "description": "事件是否不可逆？（制度性/技术性/临时性）",
        "max_score": 9,
    },
    "impact_radius": {
        "name": "影响半径",
        "description": "影响范围多大？（全产业链/单一赛道/区域性）",
        "max_score": 9,
    },
    "cognitive_gap": {
        "name": "认知时差",
        "description": "市场认知差多大？（未定价/部分定价/充分定价）",
        "max_score": 9,
    },
}


def score_event_three_rulers(event: Dict) -> Dict:
    """
    用三把尺子给事件评分

    Args:
        event: 事件数据，需含 irreversibility/impact_radius/cognitive_gap 或描述文本

    Returns:
        评分结果
    """
    # 如果有直接评分则使用
    scores = {
        "irreversibility": event.get("irreversibility", 5),
        "impact_radius": event.get("impact_radius", 5),
        "cognitive_gap": event.get("cognitive_gap", 5),
    }

    total = sum(scores.values()) / (9 * 3) * 100

    # 综合判定
    if total >= 60:
        conclusion = "高价值事件，值得深度分析"
    elif total >= 35:
        conclusion = "中等价值事件，可纳入关注"
    else:
        conclusion = "低价值事件，仅记录"

    return {
        "scores": scores,
        "total_score": round(total, 1),
        "conclusion": conclusion,
        "details": THREE_RULERS,
    }
