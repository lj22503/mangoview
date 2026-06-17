"""
Mangofolio 分析引擎核心调度器 v2.0

集成：
- 六步分析框架（天时/地利/人和）
- 信号系统（模型/注册/聚合）
- 付费拦截中间件
- 数据契约校验
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime

from .analysis.step_executor import StepExecutor, LayerType
from .analysis.completion_checker import LayerType as ComplLayerType
from .signals.signal_model import SignalModel, SignalLayer, SignalDirection, SignalIntensity
from .signals.signal_registry import get_registry, SignalRegistry
from .signals.signal_aggregator import aggregate, aggregate_by_layer, aggregate_all
from .middleware.tier_model import UserTier, has_access
from .middleware.access_control import filter_signal_by_tier, check_daily_limit
from .contract.schema_validator import sanitize_for_transfer
from .contract.refined_transfer import build_refined_output

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """
    分析引擎主调度器

    用法：
        engine = AnalysisEngine()
        result = engine.analyze(
            layer="tianshi",
            input_data={"data_source": "...", ...},
            user_tier=UserTier.BASIC,
        )
    """

    def __init__(self):
        self.executor = StepExecutor()
        self.registry = get_registry()
        self._layer_handlers: Dict[str, Dict[int, Callable]] = {}

    # ── 注册处理器 ──

    def register_layer_handlers(
        self,
        layer: str,
        handlers: Dict[int, Callable],
    ):
        """
        注册某层的六步处理器

        Args:
            layer: "tianshi" | "dili" | "renhe"
            handlers: {step: handler_func}
        """
        self._layer_handlers[layer.lower()] = handlers
        logger.info("已注册 %s 层 %d 个处理器", layer, len(handlers))

    def register_step_handler(
        self,
        layer: str,
        step: int,
        handler: Callable,
    ):
        """注册单步处理器"""
        layer_key = layer.lower()
        if layer_key not in self._layer_handlers:
            self._layer_handlers[layer_key] = {}
        self._layer_handlers[layer_key][step] = handler
        logger.info("已注册 %s 层 Step %d 处理器", layer, step)

    # ── 核心分析接口 ──

    def analyze(
        self,
        layer: str,
        input_data: Dict,
        user_tier: UserTier = UserTier.FREE,
        layer_name: str = "",
    ) -> Dict:
        """
        执行单层六步分析

        Args:
            layer: "tianshi" | "dili" | "renhe"
            input_data: 该层的原始输入数据
            user_tier: 用户层级
            layer_name: 自定义层名（日志用）

        Returns:
            分析结果（已过付费过滤）
        """
        # 检查 handler 注册
        layer_key = layer.lower()
        handlers = self._layer_handlers.get(layer_key, {})
        if not handlers:
            return {
                "error": f"{layer} 层未注册处理器",
                "status": "not_configured",
            }

        # 修正枚举匹配（renhe_company / renhe_fund 都归为 renhe）
        _base_layer = layer_key.split("_")[0] if "_" in layer_key else layer_key
        layer_enum_map = {
            "tianshi": LayerType.TIANSHI,
            "dili": LayerType.DILI,
            "renhe": LayerType.RENHE,
        }
        layer_enum = layer_enum_map.get(_base_layer, LayerType.TIANSHI)
        compl_layer_enum = layer_enum_map.get(_base_layer, ComplLayerType.TIANSHI)

        # 执行六步
        result = self.executor.execute(
            layer=layer_enum,
            raw_input=input_data,
            step_handlers=handlers,
            layer_name=layer_name or layer_key,
        )

        # 如果分析完成且有最终信号，注册信号
        if result.get("completed") and result.get("final_signal"):
            signal = self._create_signal(layer_key, result["final_signal"], input_data)
            signal_id = self.registry.register(signal)
            result["signal_id"] = signal_id
            result["signal"] = signal.to_dict()

        # 付费过滤
        filtered = self._apply_tier_filter(result, user_tier)
        return filtered

    def analyze_multi_layer(
        self,
        layers: List[str],
        input_data: Dict,
        user_tier: UserTier = UserTier.FREE,
    ) -> Dict:
        """
        多层同时分析，聚合成最终信号

        Args:
            layers: 要分析的层列表，如 ["tianshi", "dili", "renhe"]
            input_data: 包含各层输入的数据
            user_tier: 用户层级

        Returns:
            各层独立结果 + 聚合信号
        """
        layer_results = {}
        for layer in layers:
            layer_input = input_data.get(layer, input_data)
            result = self.analyze(
                layer=layer,
                input_data=layer_input,
                user_tier=user_tier,
                layer_name=layer,
            )
            layer_results[layer] = result

        # 聚合所有层的信号
        all_signals = self.registry.list_active()
        agg = aggregate(all_signals)
        agg_by_layer = aggregate_by_layer(self.registry)

        return {
            "layers": layer_results,
            "aggregate": {
                "direction": agg.direction.value,
                "intensity": agg.intensity.value,
                "confidence": agg.confidence,
                "conflict_detected": agg.conflict_detected,
                "conflict_resolution": agg.conflict_resolution,
                "component_count": len(agg.component_signals),
            },
            "aggregate_by_layer": {
                k: {
                    "direction": v.direction.value,
                    "intensity": v.intensity.value,
                    "confidence": v.confidence,
                    "conflict_detected": v.conflict_detected,
                }
                for k, v in agg_by_layer.items()
            },
        }

    # ── 辅助方法 ──

    def _create_signal(
        self,
        layer: str,
        final_signal: Dict,
        input_data: Dict,
    ) -> SignalModel:
        """从六步分析结果创建信号"""
        _base = layer.split("_")[0] if "_" in layer else layer
        layer_map = {"tianshi": SignalLayer.TIANSHI, "dili": SignalLayer.DILI, "renhe": SignalLayer.RENHE}
        dir_map = {
            "买入": SignalDirection.BULLISH,
            "卖出": SignalDirection.BEARISH,
            "持有": SignalDirection.NEUTRAL,
            "观望": SignalDirection.NEUTRAL,
        }
        int_map = {
            "重仓": SignalIntensity.STRONG,
            "轻仓": SignalIntensity.MEDIUM,
            "观察": SignalIntensity.WEAK,
            "对冲": SignalIntensity.STRONG,
        }

        direction = dir_map.get(final_signal.get("direction", ""), SignalDirection.NEUTRAL)
        intensity = int_map.get(final_signal.get("intensity", ""), SignalIntensity.WEAK)

        signal = SignalModel(
            layer=layer_map.get(_base, SignalLayer.TIANSHI),
            signal_type=f"{layer}_analysis",
            direction=direction,
            intensity=intensity,
            confidence=final_signal.get("confidence", 0.5),
            key_variables=final_signal.get("key_variables", []),
            key_assumptions=final_signal.get("key_assumptions", []),
            step_completed=6,
        )

        # 设置有效期（天时30天，地利7天，人和30天）
        valid_days = {"tianshi": 30, "dili": 7, "renhe": 30}
        signal.set_validity(valid_days.get(_base, 30))

        return signal

    def _apply_tier_filter(self, result: Dict, user_tier: UserTier) -> Dict:
        """对结果应用付费过滤"""
        filtered = dict(result)

        if "signal" in filtered and user_tier in (UserTier.GUEST, UserTier.FREE):
            filtered["signal"] = filter_signal_by_tier(filtered["signal"], user_tier)
            filtered["_tier_filtered"] = True

        return filtered

    # ── 统计 ──

    def get_stats(self) -> Dict:
        """获取分析引擎统计"""
        return {
            "signals": {
                "total": self.registry.count(),
                "by_layer": self.registry.count_by_layer(),
            },
            "executions": {
                "total": len(self.executor.execution_log),
            },
            "registered_layers": list(self._layer_handlers.keys()),
        }
