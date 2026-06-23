"""
天时层（宏观分析）单元测试

覆盖：
1. 7 步分析处理器（handlers）
2. 经济周期矩阵（cycle_matrix）
3. Scale 筛选（scale_filter）
"""

from engine.analysis.tianshi.handlers import get_handlers
from engine.analysis.tianshi.cycle_matrix import (
    determine_economic_cycle, get_asset_allocation,
    get_industry_cycle_position, scan_industry_signals,
)
from engine.analysis.tianshi.scale_filter import (
    scale_filter, has_trigger, TriggerLevel,
)


# ── 七步处理器测试 ──────────────────────────────────────────────

def test_tianshi_step0_verify():
    """Step 0 校验：来源画像"""
    handlers = get_handlers()
    result = handlers[0]({"data_source": "国家统计局", "source_type": "官方"})
    assert result["source_credibility"] >= 0.7
    assert result["final_rating"] == "直接使用"
    assert "confidence" in result

    # 低可信度来源
    result2 = handlers[0]({"data_source": "某论坛帖子", "source_type": "二手"})
    assert result2["source_credibility"] < 0.5
    assert result2["final_rating"] in ("仅作参考", "需验证后使用")


def test_tianshi_step1_decompose():
    """Step 1 拆解：核心宏观变量"""
    handlers = get_handlers()
    result = handlers[1]({
        "raw_data": {
            "macro_data": {"pmi": 50.2, "gdp": 5.0, "cpi": 2.1}
        }
    })
    assert len(result["core_variables"]) <= 5
    assert result["confidence"] >= 0.5
    assert any("PMI" in str(v) for v in result["core_variables"])
    assert any("GDP" in str(v) for v in result["core_variables"])

    # 数据不足
    result2 = handlers[1]({"raw_data": {}})
    assert result2["confidence"] < 0.7


def test_tianshi_step2_transmit():
    """Step 2 传导：构建传导路径"""
    handlers = get_handlers()
    result = handlers[2]({
        "core_variables": [
            {"name": "PMI", "importance": "HIGH"},
            {"name": "CPI", "importance": "HIGH"},
            {"name": "M2", "importance": "MEDIUM"},
        ]
    })
    assert "causal_chain" in result
    assert len(result["causal_chain"]) > 0
    assert "transmission_strength" in result
    assert "confidence" in result


def test_tianshi_step3_history():
    """Step 3 历史：相似时期"""
    handlers = get_handlers()
    result = handlers[3]({
        "core_variables": [
            {"name": "PMI", "importance": "HIGH"},
            {"name": "CPI", "importance": "HIGH"},
        ]
    })
    assert len(result["similar_cases"]) > 0
    assert "similarity" in result
    assert result["similarity"]["variable_match"] > 0


def test_tianshi_step4_scenario():
    """Step 4 情景：三种情景"""
    handlers = get_handlers()
    result = handlers[4]({
        "core_variables": [
            {"name": "PMI", "importance": "HIGH"},
            {"name": "CPI", "importance": "HIGH"},
        ]
    })
    assert "base_case" in result
    assert "bull_case" in result
    assert "bear_case" in result
    assert result["consistency_check"] is True
    assert "confidence" in result


def test_tianshi_step5_action():
    """Step 5 行动：资产配置建议"""
    handlers = get_handlers()
    result = handlers[5]({"raw_data": {"macro_data": {}}})
    assert "base_action" in result
    assert result["base_action"]["direction"] in ("买入", "卖出", "持有")
    assert result["base_action"]["intensity"] in ("重仓", "轻仓", "观察")
    assert "constraint_check" in result


def test_tianshi_step6_invalidation():
    """Step 6 失效：退出条件"""
    handlers = get_handlers()
    result = handlers[6]({})
    assert len(result["exit_signals"]) >= 1
    assert "monitoring_frequency" in result
    assert "confidence" in result


def test_tianshi_all_steps_registered():
    """验证 7 步全部注册"""
    handlers = get_handlers()
    for step in range(0, 7):
        assert step in handlers, f"Step {step} 未注册"
        assert callable(handlers[step]), f"Step {step} 不可调用"


# ── 周期性矩阵测试 ──────────────────────────────────────────────

def test_determine_economic_cycle():
    """验证经济周期判断"""
    # 衰退数据
    phase, conf, reason = determine_economic_cycle({
        "pmi_level": "very_low", "cpi_trend": "down",
        "monetary": "loosening", "credit": "contracted",
    })
    assert phase == "衰退"
    assert conf >= 0.5
    assert len(reason) > 0

    # 复苏数据
    phase2, conf2, _ = determine_economic_cycle({
        "pmi_trend": "up", "cpi_trend": "down_or_stable",
        "monetary": "loose", "credit": "expanding",
    })
    assert phase2 == "复苏"
    assert conf2 >= 0.5


def test_determine_economic_cycle_low_confidence():
    """低匹配度时置信度偏低"""
    phase, conf, _ = determine_economic_cycle({})
    assert conf < 0.5  # 无匹配数据
    assert phase in ("复苏", "扩张", "放缓", "衰退")  # 任意一个


def test_get_asset_allocation():
    """验证资产配置建议"""
    alloc = get_asset_allocation("复苏")
    assert "equity" in alloc
    assert "bond" in alloc
    assert alloc["equity"] == "overweight"

    alloc2 = get_asset_allocation("衰退")
    assert alloc2["equity"] == "underweight"

    # 未知周期返回空
    alloc3 = get_asset_allocation("未知")
    assert alloc3 == {}


def test_get_industry_cycle_position():
    """验证行业周期定位"""
    # 机会区
    pos, action, boost = get_industry_cycle_position(
        valuation_percentile=20, macro_sensitivity="high", momentum="turning_positive"
    )
    assert "机会" in pos
    assert boost > 0

    # 风险区
    pos2, action2, boost2 = get_industry_cycle_position(
        valuation_percentile=85, macro_sensitivity="high", momentum="negative"
    )
    assert "风险" in pos2
    assert boost2 < 0

    # 中性（无动量）
    pos3, action3, boost3 = get_industry_cycle_position(
        valuation_percentile=50, macro_sensitivity="medium"
    )
    assert pos3 == "中性"


def test_scan_industry_signals():
    """验证行业信号扫描"""
    industries = [
        {"industry_code": "TECH", "industry_name": "科技", "valuation_percentile": 20, "macro_sensitivity": "high"},
        {"industry_code": "ENERGY", "industry_name": "能源", "valuation_percentile": 80, "macro_sensitivity": "high"},
    ]
    momentum = {"TECH": 5.0, "ENERGY": -3.0}
    signals = scan_industry_signals(industries, momentum)

    assert len(signals) == 2
    assert signals[0]["position"] == "机会区（领先）"  # 机会区优先排序


# ── Scale 筛选测试 ──────────────────────────────────────────────

def test_scale_filter_high():
    """LEVEL1 级触发"""
    result = scale_filter({
        "interest_rate_change_bp": 25,   # > 10bp → LEVEL1
        "oil_change_pct": 5,              # > 3% → LEVEL1
        "pmi_cross_50": True,             # → LEVEL1
    })
    level1 = [r for r in result if r["level"] == "level1"]
    assert len(level1) >= 3
    assert result[0]["level"] == "level1"  # 排序优先


def test_scale_filter_level2():
    """LEVEL2 级触发"""
    result = scale_filter({
        "cpi_surprise": 1.0,                # > 0.5 → LEVEL2
        "social_financing_change": -50,     # < -30 → LEVEL2
    })
    assert len(result) == 2
    assert all(r["level"] == "level2" for r in result)


def test_scale_filter_no_trigger():
    """无触发"""
    result = scale_filter({"irrelevant_key": 123})
    assert len(result) == 0


def test_scale_filter_partial():
    """部分字段为 None 不报错"""
    result = scale_filter({
        "interest_rate_change_bp": None,
        "dxy_break": "突破",
        "oil_change_pct": None,
    })
    assert len(result) == 1
    assert result[0]["signal_type"] == "美元指数突破"


def test_has_trigger():
    """快捷检查方法"""
    triggered, details = has_trigger({"interest_rate_change_bp": 25})
    assert triggered is True
    assert len(details) >= 1

    triggered2, details2 = has_trigger({})
    assert triggered2 is False
    assert len(details2) == 0
