"""
Mangofolio 信号注册表

内存中的信号存储，支持按层/实体/时间检索。
生产环境可替换为 Redis/SQLite 存储。
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .signal_model import SignalModel, SignalLayer, AccessTier

logger = logging.getLogger(__name__)


class SignalRegistry:
    """信号注册表（内存实现）"""

    def __init__(self):
        self._signals: Dict[str, SignalModel] = {}

    # ── 增删 ──

    def register(self, signal: SignalModel) -> str:
        """注册一个信号"""
        self._signals[signal.signal_id] = signal
        logger.info(
            "信号注册: %s [%s] %s (conf=%.2f)",
            signal.signal_id[:8], signal.layer.value, signal.signal_type, signal.confidence
        )
        return signal.signal_id

    def register_batch(self, signals: List[SignalModel]) -> List[str]:
        """批量注册"""
        return [self.register(s) for s in signals]

    def remove(self, signal_id: str) -> bool:
        """删除信号"""
        if signal_id in self._signals:
            del self._signals[signal_id]
            return True
        return False

    # ── 查询 ──

    def get(self, signal_id: str) -> Optional[SignalModel]:
        """按 ID 获取信号"""
        return self._signals.get(signal_id)

    def list_by_layer(
        self,
        layer: SignalLayer,
        min_confidence: float = 0.0,
        tier: Optional[AccessTier] = None,
    ) -> List[SignalModel]:
        """按层列出信号"""
        result = []
        for signal in self._signals.values():
            if signal.layer != layer:
                continue
            if signal.confidence < min_confidence:
                continue
            if tier and _tier_rank(signal.access_tier) > _tier_rank(tier):
                continue
            result.append(signal)
        return sorted(result, key=lambda s: s.confidence, reverse=True)

    def list_by_entity(
        self,
        entity_id: str,
        entity_type: Optional[str] = None,
    ) -> List[SignalModel]:
        """按实体列出信号"""
        result = []
        for signal in self._signals.values():
            if signal.entity_id != entity_id:
                continue
            if entity_type and signal.entity_type != entity_type:
                continue
            result.append(signal)
        return sorted(result, key=lambda s: s.analysis_timestamp, reverse=True)

    def list_active(self, tier: Optional[AccessTier] = None) -> List[SignalModel]:
        """列出所有未过期信号"""
        result = []
        for signal in self._signals.values():
            if signal.is_expired():
                continue
            if tier and _tier_rank(signal.access_tier) > _tier_rank(tier):
                continue
            result.append(signal)
        return result

    def list_by_since(self, since: datetime) -> List[SignalModel]:
        """列出指定时间后的信号"""
        result = []
        for signal in self._signals.values():
            try:
                ts = datetime.fromisoformat(signal.analysis_timestamp)
                if ts >= since:
                    result.append(signal)
            except (ValueError, TypeError):
                pass
        return result

    # ── 统计 ──

    def count(self) -> int:
        return len(self._signals)

    def count_by_layer(self) -> Dict[str, int]:
        counts = {"TIANSHI": 0, "DILI": 0, "RENHE": 0}
        for s in self._signals.values():
            key = s.layer.value
            if key in counts:
                counts[key] += 1
        return counts

    def clear(self):
        """清空所有信号"""
        self._signals.clear()
        logger.info("信号注册表已清空")


def _tier_rank(tier: AccessTier) -> int:
    """层级权限排名（数值越高可访问内容越多）"""
    return {
        AccessTier.FREE: 0,
        AccessTier.BASIC: 1,
        AccessTier.VIP: 2,
    }.get(tier, 0)


# 全局单例
_default_registry: Optional[SignalRegistry] = None


def get_registry() -> SignalRegistry:
    """获取全局信号注册表实例"""
    global _default_registry
    if _default_registry is None:
        _default_registry = SignalRegistry()
    return _default_registry


def reset_registry():
    """重置全局注册表（测试用）"""
    global _default_registry
    _default_registry = None
