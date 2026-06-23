"""
分析引擎集成测试

覆盖：
1. analyze_multi_layer 多层聚合
2. aggregate_by_layer / aggregate_all
3. 天时层完整集成分析
4. 地利层完整集成分析
5. StepExecutor 回退场景
"""

from engine import create_engine
from engine.signals.signal_model import (
    SignalModel, SignalLayer, SignalDirection, SignalIntensity,
)
from engine.signals.signal_registry import get_registry
from engine.signals.signal_aggregator import (
    aggregate, aggregate_by_layer, aggregate_all,
)
from engine.analysis.step_executor import StepExecutor, LayerType
from engine.middleware.tier_model import UserTier
from engine.middleware.access_control import filter_signal_by_tier, check_daily_limit


# ── 信号聚合测试 ──────────────────────────────────────────────

def test_aggregate_by_layer():
    """验证分层聚合"""
    registry = get_registry()
    registry.clear()

    signals = [
        SignalModel(layer=SignalLayer.TIANSHI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.STRONG, confidence=0.8, step_completed=6),
        SignalModel(layer=SignalLayer.TIANSHI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.MEDIUM, confidence=0.6, step_completed=6),
        SignalModel(layer=SignalLayer.DILI, direction=SignalDirection.NEUTRAL,
                    intensity=SignalIntensity.WEAK, confidence=0.5, step_completed=6),
    ]
    registry.register_batch(signals)

    by_layer = aggregate_by_layer(registry)
    assert "TIANSHI" in by_layer
    assert "DILI" in by_layer
    assert by_layer["TIANSHI"].direction == SignalDirection.BULLISH


def test_aggregate_all():
    """验证全量聚合"""
    registry = get_registry()
    registry.clear()

    signals = [
        SignalModel(layer=SignalLayer.TIANSHI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.STRONG, confidence=0.8, step_completed=6),
        SignalModel(layer=SignalLayer.DILI, direction=SignalDirection.BEARISH,
                    intensity=SignalIntensity.MEDIUM, confidence=0.7, step_completed=6),
    ]
    registry.register_batch(signals)

    result = aggregate_all(registry)
    assert result.direction in (SignalDirection.BULLISH, SignalDirection.BEARISH)
    assert result.confidence > 0
    assert "conflict_detected" in result.__dict__


def test_aggregate_conflict_resolution():
    """验证信号冲突时人和层优先"""
    signals = [
        SignalModel(layer=SignalLayer.TIANSHI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.STRONG, confidence=0.8, step_completed=6),
        SignalModel(layer=SignalLayer.DILI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.MEDIUM, confidence=0.7, step_completed=6),
        SignalModel(layer=SignalLayer.RENHE, direction=SignalDirection.BEARISH,
                    intensity=SignalIntensity.STRONG, confidence=0.9, step_completed=6),
    ]
    result = aggregate(signals)
    assert result.conflict_detected
    assert result.direction == SignalDirection.BEARISH  # 人和层优先级最高
    assert "RENHE" in result.conflict_resolution


# ── 多层聚合集成测试 ──────────────────────────────────────────

def test_analyze_multi_layer():
    """验证多层聚合分析"""
    engine = create_engine()

    # 清理 registry
    from engine.signals.signal_registry import get_registry
    get_registry().clear()

    result = engine.analyze_multi_layer(
        layers=["tianshi", "dili"],
        input_data={
            "tianshi": {
                "data_source": "Wind",
                "source_type": "官方",
                "raw_data": {
                    "macro_data": {
                        "pmi": 50.2, "gdp": 5.0, "cpi": 2.1,
                        "m2": 10.5, "interest_rate": 3.1,
                    },
                },
            },
            "dili": {
                "data_source": "新华社",
                "raw_data": {
                    "event": "央行降息 25bp",
                    "irreversibility": 8,
                    "impact_radius": 7,
                },
            },
        },
        user_tier=UserTier.BASIC,
    )

    assert "layers" in result
    assert "aggregate" in result
    assert "tianshi" in result["layers"]
    assert "dili" in result["layers"]
    assert result["aggregate"]["component_count"] >= 1
    assert result["aggregate"]["direction"] in ("BULLISH", "BEARISH", "NEUTRAL")


def test_analyze_multi_layer_free_tier():
    """免费用户多层聚合（结果被过滤）"""
    engine = create_engine()
    get_registry().clear()

    result = engine.analyze_multi_layer(
        layers=["tianshi"],
        input_data={
            "tianshi": {
                "data_source": "Wind",
                "source_type": "官方",
                "raw_data": {"macro_data": {"pmi": 50.0}},
            },
        },
        user_tier=UserTier.FREE,
    )

    # 免费用户看不到详细信号
    if "signal" in result["layers"].get("tianshi", {}):
        signal = result["layers"]["tianshi"]["signal"]
        assert "simple_conclusion" in signal or signal.get("_tier_filtered")


# ── 天时层集成测试 ────────────────────────────────────────────

def test_tianshi_integration():
    """天时层完整分析"""
    engine = create_engine()
    result = engine.analyze(
        layer="tianshi",
        input_data={
            "data_source": "国家统计局",
            "source_type": "官方",
            "raw_data": {
                "macro_data": {
                    "pmi": 50.2, "gdp": 5.0, "cpi": 2.1,
                    "m2": 10.5, "ppi": -1.5, "interest_rate": 3.1,
                    "social_financing": 30000,
                },
            },
        },
        user_tier=UserTier.BASIC,
    )
    assert result["completed"], f"天时层分析未完成: {result.get('error')}"
    assert "signal_id" in result
    assert "signal" in result
    assert result["signal"]["layer"] == "TIANSHI"


def test_tianshi_integration_with_fallback():
    """天时层分析含回退"""
    engine = create_engine()
    # 数据不足应触发回退
    result = engine.analyze(
        layer="tianshi",
        input_data={
            "data_source": "未知来源",
            "source_type": "二手",
            "raw_data": {"macro_data": {"pmi": 50.0}},
        },
        user_tier=UserTier.BASIC,
    )
    # 即使数据不足，也应完成（可能含回退）
    assert result["completed"] or result.get("error") is not None


# ── 地利层集成测试 ────────────────────────────────────────────

def test_dili_integration():
    """地利层完整分析"""
    engine = create_engine()
    result = engine.analyze(
        layer="dili",
        input_data={
            "data_source": "新华社",
            "source_type": "官方",
            "raw_data": {
                "event": "央行降息 25bp，LPR 下调",
                "irreversibility": 8,
                "impact_radius": 7,
                "cognitive_gap": 6,
            },
        },
        user_tier=UserTier.BASIC,
    )
    assert result["completed"], f"地利层分析未完成: {result.get('error')}"
    assert "signal_id" in result
    assert result["signal"]["layer"] == "DILI"


# ── StepExecutor 回退测试 ──────────────────────────────────────

def test_step_executor_fallback():
    """StepExecutor 回退流程"""
    executor = StepExecutor()
    from engine.analysis.tianshi.handlers import get_handlers

    handlers = get_handlers()
    result = executor.execute(
        layer=LayerType.TIANSHI,
        raw_input={"data_source": "未知", "source_type": "二手"},
        step_handlers=handlers,
    )
    # 应至少执行几步
    assert len(result["results"]) > 0


def test_step_executor_empty_handlers():
    """无 handler 时报错"""
    executor = StepExecutor()
    result = executor.execute(
        layer=LayerType.TIANSHI,
        raw_input={},
        step_handlers={},
    )
    assert result["completed"] is False
    assert result["error"] is not None


# ── 付费中间件集成测试 ──────────────────────────────────────────

def test_daily_limit_edge_cases():
    """付费限制边界"""
    # GUEST 用户 3 次上限
    assert check_daily_limit(UserTier.GUEST, 3, 1, 1) is None
    assert check_daily_limit(UserTier.GUEST, 3, 4, 1) is not None

    # VIP 无限
    assert check_daily_limit(UserTier.VIP, 999, 1, 1) is None

    # FREE 用户 5 次上限
    assert check_daily_limit(UserTier.FREE, 5, 6, 1) is not None
