"""
Mangofolio 信号聚合器

按需求 1.2 定义的聚合算法实现：
1. 同向信号叠加
2. 反向信号抵消
3. 优先级规则（人和 > 地利 > 天时）
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .signal_model import (
    SignalModel, SignalLayer, SignalDirection,
    SignalIntensity, AccessTier,
)
from .signal_registry import SignalRegistry

logger = logging.getLogger(__name__)

# 强度权重映射
_INTENSITY_WEIGHT = {
    SignalIntensity.STRONG: 1.0,
    SignalIntensity.MEDIUM: 0.7,
    SignalIntensity.WEAK: 0.3,
}

# 层优先级（数字越小优先级越高）
_LAYER_PRIORITY = {
    SignalLayer.RENHE: 0,
    SignalLayer.DILI: 1,
    SignalLayer.TIANSHI: 2,
}


@dataclass
class AggregateSignal:
    """聚合信号结果"""
    direction: SignalDirection
    intensity: SignalIntensity
    confidence: float
    component_signals: List[str]
    conflict_detected: bool
    conflict_resolution: Optional[str] = None


def _score_direction(signals: List[SignalModel]) -> Dict[str, float]:
    """计算各方向的总得分"""
    scores = {"BULLISH": 0.0, "BEARISH": 0.0, "NEUTRAL": 0.0}
    for s in signals:
        weight = _INTENSITY_WEIGHT.get(s.intensity, 0.3)
        weighted = weight * s.confidence
        scores[s.direction.value] += weighted
    return scores


def _detect_conflict(signals: List[SignalModel]) -> bool:
    """检测是否有方向冲突（同时有 BULLISH 和 BEARISH）"""
    dirs = {s.direction for s in signals}
    return SignalDirection.BULLISH in dirs and SignalDirection.BEARISH in dirs


def _resolve_conflict(signals: List[SignalModel]) -> Tuple[SignalDirection, str]:
    """
    冲突解决

    优先级规则：人和 > 地利 > 天时
    同层内：置信度高的覆盖置信度低的
    """
    # 按层分组
    by_layer: Dict[SignalLayer, List[SignalModel]] = {}
    for s in signals:
        by_layer.setdefault(s.layer, []).append(s)

    # 按优先级遍历层
    for layer in sorted(by_layer.keys(), key=lambda l: _LAYER_PRIORITY.get(l, 99)):
        layer_signals = by_layer[layer]
        # 取该层置信度最高的信号方向
        best = max(layer_signals, key=lambda s: s.confidence)
        if best.direction != SignalDirection.NEUTRAL:
            return best.direction, f"由 {layer.value} 层 {best.signal_id[:8]} 决定（conf={best.confidence:.2f}）"

    return SignalDirection.NEUTRAL, "各层均无明确方向"


def aggregate(
    signals: List[SignalModel],
    tier: Optional[AccessTier] = None,
) -> AggregateSignal:
    """
    聚合多个信号为综合判断

    Args:
        signals: 待聚合的信号列表
        tier: 用户层级（用于过滤可见信号）

    Returns:
        聚合信号结果
    """
    if not signals:
        return AggregateSignal(
            direction=SignalDirection.NEUTRAL,
            intensity=SignalIntensity.WEAK,
            confidence=0.0,
            component_signals=[],
            conflict_detected=False,
        )

    # 过滤过期信号
    active = [s for s in signals if not s.is_expired()]

    # 冲突检测
    conflict = _detect_conflict(active)

    # 冲突解决
    if conflict:
        resolved_dir, resolution = _resolve_conflict(active)
        conflict_resolution = resolution
    else:
        resolved_dir = _resolve_no_conflict(active)
        conflict_resolution = None

    # 计算聚合置信度（按强度加权平均）
    total_weight = sum(_INTENSITY_WEIGHT.get(s.intensity, 0.3) for s in active)
    weighted_conf = sum(
        s.confidence * _INTENSITY_WEIGHT.get(s.intensity, 0.3)
        for s in active
    )
    avg_confidence = weighted_conf / total_weight if total_weight > 0 else 0

    # 聚合强度
    scores = _score_direction(active)
    dominant_score = max(scores.values())
    if dominant_score >= 0.7:
        agg_intensity = SignalIntensity.STRONG
    elif dominant_score >= 0.4:
        agg_intensity = SignalIntensity.MEDIUM
    else:
        agg_intensity = SignalIntensity.WEAK

    return AggregateSignal(
        direction=resolved_dir,
        intensity=agg_intensity,
        confidence=round(min(avg_confidence, 1.0), 2),
        component_signals=[s.signal_id for s in active],
        conflict_detected=conflict,
        conflict_resolution=conflict_resolution,
    )


def _resolve_no_conflict(signals: List[SignalModel]) -> SignalDirection:
    """无冲突时，按强度叠加决定方向"""
    scores = _score_direction(signals)
    max_dir = max(scores, key=scores.get)
    return SignalDirection(max_dir)


def aggregate_by_layer(
    registry: SignalRegistry,
    tier: Optional[AccessTier] = None,
) -> Dict[str, AggregateSignal]:
    """
    按层分别聚合信号

    Returns:
        { "TIANSHI": AggregateSignal, "DILI": ..., "RENHE": ... }
    """
    result = {}
    for layer in SignalLayer:
        signals = registry.list_by_layer(layer, tier=tier)
        result[layer.value] = aggregate(signals, tier)
    return result


def aggregate_all(
    registry: SignalRegistry,
    tier: Optional[AccessTier] = None,
) -> AggregateSignal:
    """
    聚合所有层的信号为最终判断
    """
    all_signals = registry.list_active(tier=tier)
    return aggregate(all_signals, tier)
