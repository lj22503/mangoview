"""
Mangofolio Signal 数据模型

按 PROJECT_INVENTORY.md 需求 1.1 定义的 17 字段模型实现。
"""

import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from enum import Enum


class SignalLayer(str, Enum):
    TIANSHI = "TIANSHI"
    DILI = "DILI"
    RENHE = "RENHE"


class SignalDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class SignalIntensity(str, Enum):
    STRONG = "STRONG"
    MEDIUM = "MEDIUM"
    WEAK = "WEAK"


class MonitoringFrequency(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    EVENT_DRIVEN = "EVENT_DRIVEN"


class AccessTier(str, Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    VIP = "VIP"


@dataclass
class KeyVariable:
    name: str
    value: Any = None
    importance: str = "MEDIUM"  # HIGH | MEDIUM | LOW
    variable_type: str = "直接"  # 直接 | 间接 | 可观测 | 潜变量


@dataclass
class InvalidationCondition:
    variable: str
    threshold: Any
    direction: str  # > | < | == | cross_above | cross_below
    effect: str = ""


@dataclass
class SignalModel:
    """
    信号数据模型（17 字段）

    按需求 1.1 定义实现，包含标识、内容、置信度、失效和元信息。
    """
    # 标识
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    layer: SignalLayer = SignalLayer.TIANSHI
    sub_layer: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

    # 信号内容
    signal_type: str = ""
    direction: SignalDirection = SignalDirection.NEUTRAL
    intensity: SignalIntensity = SignalIntensity.WEAK

    # 置信度与依据
    confidence: float = 0.0
    key_variables: List[Dict] = field(default_factory=list)
    key_assumptions: List[str] = field(default_factory=list)
    pending_validations: List[str] = field(default_factory=list)

    # 失效条件
    invalidation_conditions: List[Dict] = field(default_factory=list)
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.DAILY

    # 元信息
    source_data_timestamp: Optional[str] = None
    analysis_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: Optional[str] = None
    step_completed: int = 0

    # 付费分层
    access_tier: AccessTier = AccessTier.FREE

    # 质量追踪（自进化补充）
    accuracy: Optional[float] = None  # 信号准确率（发布后回填）
    signal_delay_ms: Optional[float] = None  # 信号延迟（毫秒）

    def to_dict(self) -> Dict:
        """序列化为字典"""
        result = {}
        for k, v in asdict(self).items():
            if isinstance(v, Enum):
                result[k] = v.value
            else:
                result[k] = v
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "SignalModel":
        """从字典反序列化"""
        layer = data.get("layer", "TIANSHI")
        if isinstance(layer, str):
            data["layer"] = SignalLayer(layer)

        for enum_field in ["direction", "intensity", "monitoring_frequency", "access_tier"]:
            val = data.get(enum_field)
            if isinstance(val, str):
                enum_cls = {
                    "direction": SignalDirection,
                    "intensity": SignalIntensity,
                    "monitoring_frequency": MonitoringFrequency,
                    "access_tier": AccessTier,
                }[enum_field]
                data[enum_field] = enum_cls(val)

        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })

    def is_valid(self) -> bool:
        """检查信号是否仍在有效期内"""
        if self.valid_until:
            try:
                expiry = datetime.fromisoformat(self.valid_until)
                return datetime.now(timezone.utc) < expiry
            except (ValueError, TypeError):
                pass
        return True

    def is_expired(self) -> bool:
        return not self.is_valid()

    def set_validity(self, days: int):
        """设置有效期（从当前时间起 N 天）"""
        self.valid_until = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
