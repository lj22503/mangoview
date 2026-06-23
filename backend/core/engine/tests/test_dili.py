"""
地利层（事件深度解读）单元测试

覆盖：
1. 7 步分析处理器（handlers）
2. 叙事识别（narrative）
3. Scale 事件筛选（scale_filter）
"""

from engine.analysis.dili.handlers import get_handlers
from engine.analysis.dili.narrative import (
    identify_narrative, classify_event_type, NARRATIVE_TEMPLATES,
)
from engine.analysis.dili.scale_filter import (
    scale_filter_events, score_event_three_rulers, EventPriority,
)


# ── 七步处理器测试 ──────────────────────────────────────────────

def test_dili_step0_verify():
    """Step 0 校验：事件来源画像"""
    handlers = get_handlers()
    # 官方来源
    result = handlers[0]({"raw_data": {"data_source": "国家统计局", "event": "PMI 数据发布"}})
    assert result["source_credibility"] >= 0.7
    assert result["final_rating"] == "直接使用"

    # 未知来源
    result2 = handlers[0]({"raw_data": {"source": "未知来源", "event": "普通事件"}})
    assert result2["source_credibility"] < 0.6


def test_dili_step1_decompose():
    """Step 1 拆解：事件核心变量"""
    handlers = get_handlers()
    result = handlers[1]({
        "raw_data": {
            "event": "央行降息 25bp，LPR 下调",
            "irreversibility": 8,
            "impact_radius": 7,
        }
    })
    assert len(result["core_variables"]) <= 5
    assert "event_classification" in result
    assert "narratives" in result
    assert result["confidence"] > 0


def test_dili_step2_transmit():
    """Step 2 传导：事件影响路径"""
    handlers = get_handlers()
    result = handlers[2]({
        "core_variables": [
            {"name": "事件类型", "value": "gate", "importance": "HIGH"},
            {"name": "叙事-降息预期", "value": "rate_cut", "importance": "HIGH"},
        ]
    })
    assert "causal_chain" in result
    assert len(result["causal_chain"]) > 0
    assert "transmission_strength" in result


def test_dili_step3_history():
    """Step 3 历史：相似事件"""
    handlers = get_handlers()
    result = handlers[3]({
        "core_variables": [
            {"name": "叙事-降息预期", "value": "rate_cut"},
            {"name": "事件类型", "value": "gate"},
        ]
    })
    assert len(result["similar_cases"]) > 0
    assert "similarity" in result
    assert "confidence" in result


def test_dili_step4_scenario():
    """Step 4 情景：事件三种情景"""
    handlers = get_handlers()
    result = handlers[4]({})
    assert "base_case" in result
    assert "bull_case" in result
    assert "bear_case" in result
    assert "key_bifurcation" in result


def test_dili_step5_action():
    """Step 5 行动：事件策略建议"""
    handlers = get_handlers()
    result = handlers[5]({
        "core_variables": [
            {"name": "事件类型", "value": "闸门", "importance": "HIGH"},
        ]
    })
    assert "base_action" in result
    assert result["base_action"]["direction"] in ("买入", "观望")
    assert "constraint_check" in result


def test_dili_step6_invalidation():
    """Step 6 失效：事件退出条件"""
    handlers = get_handlers()
    result = handlers[6]({})
    assert len(result["exit_signals"]) >= 1
    assert "monitoring_frequency" in result


def test_dili_all_steps_registered():
    """验证 7 步全部注册"""
    handlers = get_handlers()
    for step in range(0, 7):
        assert step in handlers, f"Step {step} 未注册"
        assert callable(handlers[step]), f"Step {step} 不可调用"


# ── 叙事识别测试 ──────────────────────────────────────────────

def test_identify_narrative():
    """验证叙事识别"""
    result = identify_narrative("央行降息，流动性宽松")
    assert len(result) >= 1
    assert any(n["narrative_id"] == "rate_cut" for n in result)
    assert result[0]["confidence"] > 0

    # 无匹配
    result2 = identify_narrative("今天天气不错")
    assert len(result2) == 0


def test_identify_narrative_with_assets():
    """带资产数据的叙事识别"""
    result = identify_narrative("AI 大模型发布", top_assets=["NVDA", "科技股"])
    tech_narratives = [n for n in result if n["narrative_id"] == "tech_revolution"]
    assert len(tech_narratives) >= 1


def test_classify_event_type():
    """验证事件类型分类"""
    # 闸门事件
    result = classify_event_type("央行批准外资准入")
    assert result["is_gate"] is True
    assert result["classification"] == "gate"

    # 资金事件
    result2 = classify_event_type("北向资金大幅流入")
    assert result2["is_pipe"] is True

    # 无匹配
    result3 = classify_event_type("普通新闻")
    assert result3["confidence"] < 0.5


# ── Scale 事件筛选测试 ──────────────────────────────────────────

def test_scale_filter_high_priority():
    """高优先级事件筛选"""
    events = [
        {"event_id": "e1", "title": "央行加息", "confirmed_by_official": True, "involves_major_industry": True},
        {"event_id": "e2", "title": "普通新闻", "event": "日常", "source": "自媒体"},
    ]
    result = scale_filter_events(events)
    assert len(result) >= 1
    assert result[0]["priority"] == "high"


def test_scale_filter_rate_change():
    """利率变动触发"""
    events = [
        {"event_id": "e1", "event": "利率决议", "rate_change_bp": 25, "balance_sheet_change": 600},
    ]
    result = scale_filter_events(events)
    assert len(result) >= 1
    assert result[0]["priority"] == "high"


def test_scale_filter_medium_priority():
    """中优先级事件"""
    events = [
        {"event_id": "e1", "event": "财报", "event_category": "earnings"},
    ]
    result = scale_filter_events(events)
    assert len(result) >= 1
    assert result[0]["priority"] == "medium"


def test_scale_filter_low_priority():
    """低优先级被过滤"""
    events = [
        {"event_id": "e1", "event": "常规数据", "source": "未知"},
    ]
    result = scale_filter_events(events)
    assert len(result) == 0  # 低优先级被过滤


def test_scale_filter_empty():
    """空事件列表"""
    result = scale_filter_events([])
    assert result == []


def test_score_event_three_rulers():
    """三把尺子评分"""
    result = score_event_three_rulers({"irreversibility": 8, "impact_radius": 7, "cognitive_gap": 6})
    assert result["total_score"] >= 60
    assert "高价值事件" in result["conclusion"]

    # 低价值
    result2 = score_event_three_rulers({"irreversibility": 2, "impact_radius": 3, "cognitive_gap": 2})
    assert result2["total_score"] < 35
    assert "低价值事件" in result2["conclusion"]

    # 默认值
    result3 = score_event_three_rulers({})
    assert result3["total_score"] == 55.6  # 默认 5+5+5 → (15/27)*100
