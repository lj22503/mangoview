"""
分析引擎 Phase 1 集成测试

验证：
1. 数据契约 schema 定义 + 校验
2. 信号模型创建 + 注册 + 查询
3. 信号聚合算法
4. 六步执行器模板
5. 付费中间件过滤
"""

import sys
import os
# 添加 engine 的父目录到 sys.path（engine 作为包导入，修正相对导入问题）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.contract.schema_definitions import (
    list_schemas, check_version_compatibility, get_schema,
)
from engine.contract.schema_validator import (
    validate_step_data, validate_refined_transfer,
    sanitize_for_transfer,
)
from engine.contract.refined_transfer import build_refined_output, limit_variables
from engine.signals.signal_model import (
    SignalModel, SignalLayer, SignalDirection,
    SignalIntensity, AccessTier,
)
from engine.signals.signal_registry import SignalRegistry
from engine.signals.signal_aggregator import aggregate, AggregateSignal
from engine.analysis.step_executor import StepExecutor, LayerType
from engine.analysis.completion_checker import check_step, LayerType as ComplLayer
from engine.analysis.fallback_manager import FallbackTracker, determine_fallback
from engine.middleware.tier_model import UserTier, has_access
from engine.middleware.access_control import filter_signal_by_tier, check_daily_limit

# 人和层模块
from engine.analysis.renhe.classifiers import (
    classify_business_model, classify_fund_style, score_financial_health,
)
from engine.analysis.renhe.company_handlers import get_company_handlers
from engine.analysis.renhe.fund_handlers import get_fund_handlers

# 引擎工厂
from engine import create_engine


def test_schema_definitions():
    """验证所有 Schema 已注册"""
    schemas = list_schemas()
    assert len(schemas) == 9, f"应有 9 个 Schema，当前 {len(schemas)}"
    for key, ver in schemas.items():
        assert ver == "1.0.0", f"{key} 版本应为 1.0.0"

    # 验证 step0 schema 有 required
    s0 = get_schema("step0")
    assert "required" in s0
    assert "output" in s0["properties"]

    print("✅ schema_definitions")


def test_version_compatibility():
    """验证版本兼容矩阵"""
    assert check_version_compatibility("v1.0.0", "v1.0.0") == "compatible"
    assert check_version_compatibility("v1.1.0", "v1.0.0") == "compatible_with_warnings"
    assert check_version_compatibility("v2.0.0", "v1.0.0") == "incompatible"
    assert check_version_compatibility("v1.0.0", "v2.0.0") == "incompatible"
    print("✅ version_compatibility")


def test_schema_validation():
    """验证 step 数据校验"""
    valid_data = {
        "step": 0,
        "input": {"data_source": "国家统计局", "source_type": "官方"},
        "output": {
            "source_credibility": 0.85,
            "final_rating": "直接使用",
            "confidence": 0.8,
        }
    }
    is_valid, errors = validate_step_data(0, valid_data)
    assert is_valid, f"有效数据应通过校验: {errors}"

    # 超出变量的 step1
    invalid_data = {
        "step": 1,
        "input": {"raw_data": {}},
        "output": {
            "core_variables": [
                {"name": f"var{i}", "importance": "HIGH"}
                for i in range(10)
            ],
            "confidence": 0.5,
        }
    }
    is_valid, errors = validate_step_data(1, invalid_data)
    assert not is_valid
    assert any("超出最大数量" in e for e in errors)

    # 提炼传递校验
    valid_refined = {
        "schema_version": "v1.0.0",
        "step": 1,
        "refined_data": {
            "core_variables": [{"name": "PMI", "importance": "HIGH"}],
            "confidence": 0.8,
        },
        "pass_timestamp": "2026-06-10T00:00:00",
    }
    ok, errs = validate_refined_transfer(valid_refined)
    assert ok, f"{errs}"

    print("✅ schema_validation")


def test_signal_model():
    """验证信号模型创建和序列化"""
    signal = SignalModel(
        layer=SignalLayer.TIANSHI,
        signal_type="经济周期",
        direction=SignalDirection.BULLISH,
        intensity=SignalIntensity.STRONG,
        confidence=0.85,
        key_variables=[{"name": "PMI", "value": 50.8, "importance": "HIGH"}],
        step_completed=6,
    )
    signal.set_validity(30)

    d = signal.to_dict()
    assert d["layer"] == "TIANSHI"
    assert d["direction"] == "BULLISH"
    assert d["confidence"] == 0.85
    assert "valid_until" in d

    # 反序列化
    restored = SignalModel.from_dict(d)
    assert restored.layer == SignalLayer.TIANSHI
    assert restored.direction == SignalDirection.BULLISH
    assert not restored.is_expired()

    print("✅ signal_model")


def test_signal_registry():
    """验证信号注册和查询"""
    registry = SignalRegistry()

    s1 = SignalModel(layer=SignalLayer.TIANSHI, signal_type="宏观",
                     confidence=0.8, step_completed=6)
    s2 = SignalModel(layer=SignalLayer.DILI, signal_type="事件",
                     confidence=0.6, step_completed=6)
    s3 = SignalModel(layer=SignalLayer.RENHE, signal_type="个股",
                     confidence=0.9, step_completed=6)

    ids = registry.register_batch([s1, s2, s3])
    assert len(ids) == 3
    assert registry.count() == 3

    counts = registry.count_by_layer()
    assert counts["TIANSHI"] == 1
    assert counts["DILI"] == 1
    assert counts["RENHE"] == 1

    tianshi_signals = registry.list_by_layer(SignalLayer.TIANSHI)
    assert len(tianshi_signals) == 1

    registry.clear()
    assert registry.count() == 0

    print("✅ signal_registry")


def test_signal_aggregation():
    """验证信号聚合算法"""
    signals = [
        SignalModel(layer=SignalLayer.TIANSHI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.STRONG, confidence=0.8, step_completed=6),
        SignalModel(layer=SignalLayer.DILI, direction=SignalDirection.BULLISH,
                    intensity=SignalIntensity.MEDIUM, confidence=0.7, step_completed=6),
    ]

    result = aggregate(signals)
    assert result.direction == SignalDirection.BULLISH
    assert result.intensity == SignalIntensity.STRONG
    assert result.confidence > 0.7
    assert not result.conflict_detected

    # 添加反向信号
    signals.append(
        SignalModel(layer=SignalLayer.RENHE, direction=SignalDirection.BEARISH,
                    intensity=SignalIntensity.STRONG, confidence=0.9, step_completed=6)
    )
    result = aggregate(signals)
    assert result.conflict_detected
    # 人和层优先级最高
    assert result.direction == SignalDirection.BEARISH

    print("✅ signal_aggregation")


def test_completion_checker():
    """验证完成标准校验"""
    # Step 0 通过
    passed, reason = check_step(ComplLayer.TIANSHI, 0,
                                {"source_credibility": 0.8})
    assert passed

    # Step 0 不通过
    passed, reason = check_step(ComplLayer.TIANSHI, 0,
                                {"source_credibility": 0.2})
    assert not passed
    assert "信源可信度" in reason

    # Step 1 变量超出
    passed, reason = check_step(ComplLayer.TIANSHI, 1,
                                {"core_variables": [{"name": f"x{i}"} for i in range(10)]})
    assert not passed
    assert "核心变量" in reason

    print("✅ completion_checker")


def test_fallback():
    """验证回退机制"""
    tracker = FallbackTracker()
    to_step, action = determine_fallback(
        ComplLayer.TIANSHI, 1, "core_variables 超出", tracker
    )
    assert to_step == 0
    assert action is not None

    # 超限测试
    for _ in range(3):
        tracker.record("tianshi", 1)
    assert tracker.exceeded_limit("tianshi", 1)

    print("✅ fallback")


def test_refined_transfer():
    """验证提炼传递"""
    packet = build_refined_output(
        step=1,
        core_variables=[{"name": "PMI", "value": 50.8, "importance": "HIGH"}],
        confidence=0.85,
        key_assumptions=["数据滞后 1 个月", "季节性调整"],
        pending_validations=["下期数据确认"],
    )
    assert packet["schema_version"] == "1.0.0"
    assert packet["step"] == 1
    assert packet["refined_data"]["confidence"] == 0.85
    assert len(packet["refined_data"]["core_variables"]) == 1

    # 变量限制
    too_many = [{"name": f"x{i}", "importance": "LOW"} for i in range(10)]
    limited = limit_variables(too_many)
    assert len(limited) <= 5

    print("✅ refined_transfer")


def test_tier_access():
    """验证付费层级"""
    assert has_access(UserTier.FREE, UserTier.FREE)
    assert has_access(UserTier.BASIC, UserTier.FREE)
    assert not has_access(UserTier.FREE, UserTier.BASIC)
    assert not has_access(UserTier.GUEST, UserTier.BASIC)
    assert has_access(UserTier.VIP, UserTier.BASIC)

    print("✅ tier_access")


# ── 人和层：分类器测试 ──────────────────────────────────────────

def test_classify_business_model():
    """验证商业模式分类"""
    result = classify_business_model(
        company_description="SaaS 云服务，年费订阅模式",
        industry="科技",
        revenue_model="月费",
    )
    assert result["model_id"] == "SaaS"
    assert result["confidence"] > 0.3
    assert "PS" in result["valuation_methods"]

    # 未匹配的情况
    result2 = classify_business_model(
        company_description="某小型贸易公司",
        industry="贸易",
    )
    assert result2["model_id"] == "通用"
    assert result2["confidence"] < 0.5

    print("✅ classify_business_model")


def test_classify_fund_style():
    """验证基金风格分类"""
    fund_data = {
        "pe_quantile": 75,
        "holding_style": "成长",
        "turnover_rate": 250,
    }
    result = classify_fund_style(fund_data)
    assert result["primary_style"] == "成长型"
    assert result["confidence"] > 0.5

    # 数据不足
    result2 = classify_fund_style({})
    assert result2["primary_style"] == "未分类"
    assert result2["confidence"] < 0.5

    print("✅ classify_fund_style")


def test_financial_health():
    """验证财务健康评分"""
    financials = {
        "gross_margin": 65,
        "net_margin": 22,
        "roe": 25,
        "debt_ratio": 25,
        "current_ratio": 2.5,
        "revenue_growth": 35,
        "profit_growth": 30,
    }
    result = score_financial_health(financials)
    assert result["total_score"] >= 60
    assert result["rating"] in ("优秀", "良好")
    assert "profitability" in result["dimensions"]

    # 差的基本面
    result2 = score_financial_health({
        "gross_margin": 10,
        "net_margin": 2,
        "debt_ratio": 85,
    })
    assert result2["total_score"] < 40
    assert result2["rating"] == "较差"

    print("✅ financial_health")


# ── 人和层：六步处理器测试 ──────────────────────────────────────

def test_company_handlers_verify():
    """验证公司 Step 0"""
    handlers = get_company_handlers()
    result = handlers[0]({"data_source": "年报", "company_name": "腾讯"})
    assert result["source_credibility"] >= 0.7
    assert result["final_rating"] == "直接使用"
    assert "data_completeness" in result

    result2 = handlers[0]({"data_source": "论坛", "company_name": "某公司"})
    assert result2["source_credibility"] < 0.5
    assert "非官方" in str(result2["bias_types"]) or "媒体" in str(result2["bias_types"])

    print("✅ company_handlers step0")


def test_company_handlers_decompose():
    """验证公司 Step 1"""
    handlers = get_company_handlers()
    result = handlers[1]({
        "business_description": "SaaS 云服务平台",
        "industry": "科技",
        "financials": {"gross_margin": 70, "net_margin": 25, "roe": 20},
    })
    assert len(result["core_variables"]) <= 5
    assert result["classification_confidence"] > 0.3
    assert result["business_model"]["model_id"] == "SaaS"
    assert result["financial_health"]["total_score"] > 0

    print("✅ company_handlers step1")


def test_company_handlers_complete():
    """验证公司六步完整执行"""
    handlers = get_company_handlers()
    step_input = {
        "company": "腾讯",
        "industry": "互联网",
        "business_description": "平台型互联网公司",
        "financials": {"gross_margin": 45, "net_margin": 25, "roe": 18, "debt_ratio": 40},
    }

    prev = {}
    for step in range(0, 7):
        handler = handlers[step]
        merged_input = {**step_input, **prev}
        output = handler(merged_input)

        # 检查每步关键字段
        if step == 0:
            assert "source_credibility" in output
        elif step == 2:
            assert output.get("return_attribution") or output.get("attribution"), \
                f"Step {step} 缺少归因字段"
        elif step == 4:
            assert "scenario_analysis" in output or "valuation_range" in output
        elif step == 5:
            assert "base_action" in output
            assert "constraint_check" in output
        elif step == 6:
            assert len(output.get("exit_signals", [])) >= 1

        prev = {"core_variables": output.get("core_variables", [])}

    print("✅ company_handlers 六步完整")


def test_fund_handlers_decompose():
    """验证基金 Step 1"""
    handlers = get_fund_handlers()
    result = handlers[1]({
        "fund_name": "某成长基金",
        "fund_type": "股票型",
        "pe_quantile": 75,
        "holding_style": "成长",
        "turnover_rate": 300,
        "return_1y": 15.5,
        "sharpe_ratio": 1.2,
        "max_drawdown": -12,
    })
    assert len(result["core_variables"]) <= 5
    assert result["classification_confidence"] > 0.5
    assert result["fund_style"]["primary_style"] == "成长型"
    assert "returns" in result
    assert "risk_metrics" in result

    print("✅ fund_handlers step1")


def test_fund_handlers_complete():
    """验证基金六步完整执行"""
    handlers = get_fund_handlers()
    step_input = {
        "fund_name": "某成长基金",
        "fund_type": "股票型",
        "pe_quantile": 70,
        "holding_style": "成长",
        "turnover_rate": 250,
        "return_1y": 20.0,
        "sharpe_ratio": 1.5,
        "max_drawdown": -10,
    }

    prev = {}
    for step in range(0, 7):
        handler = handlers[step]
        merged_input = {**step_input, **prev}
        output = handler(merged_input)

        if step == 0:
            assert "source_credibility" in output
        elif step == 2:
            assert output.get("return_attribution") or output.get("attribution")
        elif step == 5:
            assert "base_action" in output
            assert "constraint_check" in output
        elif step == 6:
            assert len(output.get("exit_signals", [])) >= 1

        prev = {"core_variables": output.get("core_variables", [])}

    print("✅ fund_handlers 六步完整")


# ── 集成测试 ──────────────────────────────────────────────────

def test_create_engine():
    """验证引擎工厂"""
    engine = create_engine()
    stats = engine.get_stats()
    assert "tianshi" in stats["registered_layers"]
    assert "dili" in stats["registered_layers"]
    assert "renhe_company" in stats["registered_layers"]
    assert "renhe_fund" in stats["registered_layers"]
    assert len(stats["registered_layers"]) == 4

    print("✅ create_engine 自动注册")


def test_renhe_company_integration():
    """验证人和层-公司完整分析"""
    engine = create_engine()
    result = engine.analyze(
        layer="renhe_company",
        input_data={
            "company": "腾讯控股",
            "industry": "互联网",
            "business_description": "平台型互联网公司，SaaS 云服务",
            "financials": {"gross_margin": 45, "net_margin": 20, "roe": 18},
            "data_source": "Wind",
        },
        user_tier=UserTier.BASIC,
    )
    assert result["completed"], f"分析未完成: {result.get('error')}"
    assert "signal_id" in result
    assert result["signal"]["layer"] == "RENHE"

    print("✅ renhe_company 集成分析")


def test_renhe_fund_integration():
    """验证人和层-基金完整分析"""
    engine = create_engine()
    result = engine.analyze(
        layer="renhe_fund",
        input_data={
            "fund_name": "中欧医疗健康",
            "fund_type": "股票型",
            "pe_quantile": 65,
            "holding_style": "成长",
            "turnover_rate": 200,
            "return_1y": 12.5,
            "sharpe_ratio": 0.8,
            "max_drawdown": -15,
            "data_source": "天天基金",
        },
        user_tier=UserTier.BASIC,
    )
    assert result["completed"], f"分析未完成: {result.get('error')}"
    assert "signal_id" in result
    assert result["signal"]["layer"] == "RENHE"

    print("✅ renhe_fund 集成分析")


def test_signal_filtering():
    """验证付费信号过滤"""
    signal = {
        "signal_type": "经济周期",
        "direction": "BULLISH",
        "intensity": "STRONG",
        "confidence": 0.85,
        "key_variables": [{"name": "PMI", "value": 50.8}],
        "base_action": {"direction": "买入", "intensity": "重仓"},
    }

    free_result = filter_signal_by_tier(signal, UserTier.FREE)
    assert "simple_conclusion" in free_result
    assert "base_action" not in free_result
    assert free_result.get("access_tier_required") == "BASIC"

    basic_result = filter_signal_by_tier(signal, UserTier.BASIC)
    assert "base_action" in basic_result
    assert "simple_conclusion" not in basic_result

    limit_result = check_daily_limit(UserTier.FREE, 15, 1, 1)
    assert limit_result is not None
    assert "已达上限" in limit_result

    no_limit = check_daily_limit(UserTier.FREE, 5, 1, 1)
    assert no_limit is None

    print("✅ signal_filtering")


if __name__ == "__main__":
    # Phase 1
    test_schema_definitions()
    test_version_compatibility()
    test_schema_validation()
    test_signal_model()
    test_signal_registry()
    test_signal_aggregation()
    test_completion_checker()
    test_fallback()
    test_refined_transfer()
    test_tier_access()
    test_signal_filtering()

    # Phase 2 - 人和层
    test_classify_business_model()
    test_classify_fund_style()
    test_financial_health()
    test_company_handlers_verify()
    test_company_handlers_decompose()
    test_company_handlers_complete()
    test_fund_handlers_decompose()
    test_fund_handlers_complete()

    # Phase 2 - 集成
    test_create_engine()
    test_renhe_company_integration()
    test_renhe_fund_integration()

    print("\n🎉 Phase 2 全部测试通过（天时 + 地利 + 人和 + 集成）")
