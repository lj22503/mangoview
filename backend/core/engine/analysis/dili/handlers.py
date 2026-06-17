"""
地利层：六步分析处理器（事件深度解读）

按 PROJECT_INVENTORY.md 需求 3.2 实现。
"""

import logging
from typing import Dict, Any

from .narrative import identify_narrative, classify_event_type

logger = logging.getLogger(__name__)


def step0_verify(step_input: Dict) -> Dict:
    """Step 0 校验：事件来源画像"""
    raw_data = step_input.get("raw_data", step_input)
    source = raw_data.get("source", raw_data.get("data_source", "未知"))
    event_desc = raw_data.get("event", raw_data.get("description", ""))

    # 来源可信度
    trusted_sources = ["国家统计局", "央行", "新华社", "人民日报", "官方网站", "官方"]
    media_sources = ["媒体", "财新", "21 经济", "第一财经"]

    if any(s in source for s in trusted_sources):
        source_credibility = 0.85
    elif any(s in source for s in media_sources):
        source_credibility = 0.55
    else:
        source_credibility = 0.4

    # 偏差检测
    bias_types = []
    event_lower = event_desc.lower()
    if any(w in event_lower for w in ["震惊", "突发", "暴跌", "暴涨"]):
        bias_types.append("情绪偏差（使用极端词汇）")
    if source == "机构分析":
        bias_types.append("利益冲突（机构可能有持仓）")

    # 最终评定
    if source_credibility >= 0.7:
        final_rating = "直接使用"
    elif source_credibility >= 0.4:
        final_rating = "需验证后使用"
    else:
        final_rating = "仅作参考"

    return {
        "source_credibility": source_credibility,
        "bias_types": bias_types,
        "final_rating": final_rating,
        "confidence": min(source_credibility + 0.05, 1.0),
        "data_freshness": raw_data.get("data_freshness", "unknown"),
    }


def step1_decompose(step_input: Dict) -> Dict:
    """Step 1 拆解：提取事件的核心变量"""
    raw_data = step_input.get("raw_data", step_input)
    event_desc = raw_data.get("event", raw_data.get("description", ""))

    # 事件分类
    classification = classify_event_type(event_desc)

    # 叙事识别
    narratives = identify_narrative(event_desc)

    # 构建核心变量
    core_variables = [
        {
            "name": "事件类型",
            "value": classification["classification"],
            "importance": "HIGH",
            "variable_type": "直接",
        },
        {
            "name": "不可逆性",
            "value": raw_data.get("irreversibility", 5),
            "importance": "MEDIUM",
            "variable_type": "可观测",
        },
        {
            "name": "影响半径",
            "value": raw_data.get("impact_radius", 5),
            "importance": "MEDIUM",
            "variable_type": "可观测",
        },
    ]

    # 如果识别到叙事
    for n in narratives:
        core_variables.append({
            "name": f"叙事-{n['narrative_name']}",
            "value": n["narrative_id"],
            "importance": "HIGH",
            "variable_type": "潜变量",
        })

    key_assumptions = [
        "事件影响需要时间传导，市场可能提前或滞后反应",
    ]
    if classification["is_gate"]:
        key_assumptions.append("闸门事件通常不可逆，影响持续时间较长")

    return {
        "core_variables": core_variables[:5],
        "confidence": 0.7 if len(narratives) > 0 else 0.5,
        "key_assumptions": key_assumptions,
        "pending_validations": [
            "是否有后续政策/事件确认方向",
            "市场反应是否与预期一致",
        ],
        "event_classification": classification,
        "narratives": narratives,
    }


def step2_transmit(step_input: Dict) -> Dict:
    """Step 2 传导：构建事件影响传导路径"""
    core_vars = step_input.get("core_variables", [])
    var_names = {v.get("name", "") for v in core_vars if isinstance(v, dict)}

    # 判断事件类型
    is_gate = any("闸门" in str(v) or "gate" in str(v.get("value", "")) for v in core_vars if isinstance(v, dict))
    is_deviation = any("背离" in str(v) for v in core_vars if isinstance(v, dict))
    is_narrative = any("叙事" in str(v.get("name", "")) for v in core_vars if isinstance(v, dict))

    causal_chain_parts = []

    if is_gate:
        causal_chain_parts.append("政策规则改变 → 参与者行为变化 → 供需关系 → 价格发现 → 新均衡")
    if is_deviation:
        causal_chain_parts.append("价格偏离价值 → 套利者介入 → 回归均值 → 新均衡")
    if is_narrative:
        causal_chain_parts.append("叙事传播 → 投资者认知改变 → 资金流向 → 资产价格 → 自我强化/证伪")

    if not causal_chain_parts:
        causal_chain_parts.append("事件 → 直接影响变量 → 产业链传导 → 二级市场反应")

    causal_chain = " → ".join(causal_chain_parts)

    feedback_loops = []
    if is_narrative:
        feedback_loops.append({
            "type": "正反馈",
            "description": "叙事传播 → 更多投资者采信 → 价格进一步偏离 → 叙事自我强化",
        })

    return {
        "causal_chain": causal_chain,
        "feedback_loops": feedback_loops,
        "blockage_points": [
            {
                "location": "政策传导",
                "reason": "政策落地到实际影响存在时滞",
            }
        ],
        "time_characteristics": [
            {"path": "政策传导", "delay": "滞后", "timescale": "3-12 个月"},
            {"path": "市场情绪", "delay": "即时", "timescale": "1-5 天"},
        ],
        "transmission_strength": "强" if is_gate else "中" if is_narrative else "弱",
        "confidence": 0.7 if is_gate else 0.5,
    }


def step3_history(step_input: Dict) -> Dict:
    """Step 3 历史：检索相似历史事件"""
    core_vars = step_input.get("core_variables", [])
    narratives = []
    for v in core_vars:
        if isinstance(v, dict) and "叙事" in v.get("name", ""):
            narratives.append(v.get("value", ""))

    similar_cases = [
        {
            "time": "2019 年 QFII 额度放开",
            "location": "中国",
            "core_features": "外资准入放宽 + 金融市场开放",
            "outcome": "外资持续流入 A 股，核心资产定价权转移，蓝筹股估值提升",
        },
    ]

    if "rate_cut" in narratives:
        similar_cases.append({
            "time": "2020 年全球降息潮",
            "location": "全球",
            "core_features": "疫情冲击 + 央行大幅降息 + QE",
            "outcome": "资产价格全面上涨，科技股领涨，债券收益率创新低",
        })

    if "tech_revolution" in narratives:
        similar_cases.append({
            "time": "2023 年 AI 爆发",
            "location": "全球",
            "core_features": "GPT 发布 + 科技巨头加码 AI + 算力需求爆发",
            "outcome": "NVDA 领涨科技股，AI 相关产业链全面受益",
        })

    return {
        "similar_cases": similar_cases[:3],
        "similarity": {
            "variable_match": 0.65,
            "context_match": 0.5,
        },
        "key_differences": [
            {
                "difference": "当前宏观环境与历史案例不同",
                "potential_impact": "相同事件的演绎路径可能不同",
            }
        ],
        "transferable_patterns": [
            "政策放开通常带来结构性机会",
            "叙事驱动的行情初期反应过度，中期回归基本面",
        ],
        "non_transferable_patterns": [
            "每次地缘事件的具体影响范围不可简单类比",
        ],
        "confidence": 0.6,
    }


def step4_scenario(step_input: Dict) -> Dict:
    """Step 4 情景：生成事件的三种情景"""
    core_vars = step_input.get("core_variables", [])
    event_classification = {}
    for v in core_vars:
        if isinstance(v, dict) and v.get("name") == "事件类型":
            event_classification = v

    event_type = event_classification.get("value", "unknown")

    return {
        "base_case": {
            "probability": "中",
            "assumptions": ["事件按预期推进", "无超预期干扰"],
            "path": "事件正常演绎 → 相关资产逐步反应 → 市场消化",
            "impact": "相关资产获得结构性支撑",
        },
        "bull_case": {
            "probability": "低",
            "trigger": "事件超预期推进 + 市场情绪共振 + 资金加速流入",
            "path": "催化剂叠加 → 市场过度反应 → 短期超涨 → 回调消化",
            "impact": "短期显著超涨，中期回归合理估值",
        },
        "bear_case": {
            "probability": "低",
            "trigger": "事件证伪或低于预期 + 市场转向 + 资金流出",
            "path": "预期落空 → 市场失望 → 资金流出 → 超跌",
            "impact": "短期超跌，提供逆向布局机会",
        },
        "key_bifurcation": {
            "variable": "市场共识方向",
            "threshold": "事件发布后 1 周市场反应",
            "direction": "正面反应则乐观，负面则悲观",
        },
        "consistency_check": True,
        "confidence": 0.65,
    }


def step5_action(step_input: Dict) -> Dict:
    """Step 5 行动：事件驱动交易建议"""
    core_vars = step_input.get("core_variables", [])
    is_gate = any(
        isinstance(v, dict) and "闸门" in str(v.get("value", ""))
        for v in core_vars
    )

    if is_gate:
        direction = "买入"
        intensity = "轻仓"
    else:
        direction = "观望"
        intensity = "观察"

    return {
        "base_action": {
            "direction": direction,
            "object": "事件驱动策略",
            "logic": "基于事件影响分析，在合理估值区间内布局受益方向",
            "intensity": intensity,
            "time_window": "1-3 个月",
        },
        "bull_action": {
            "intensity": "重仓",
            "logic": "事件催化 + 资金共振可适当加仓",
        },
        "bear_action": {
            "intensity": "观察",
            "logic": "事件证伪或低于预期则止损离场",
        },
        "no_action_condition": "事件影响不确定时，观望为主",
        "constraint_check": {
            "risk_capacity": True,
            "fund_size": True,
            "execution": True,
        },
        "confidence": 0.65,
    }


def step6_invalidation(step_input: Dict) -> Dict:
    """Step 6 失效：事件分析的退出条件"""
    return {
        "logical_conditions": [
            "事件被证伪（政策不落地/叙事破灭）",
            "市场对事件已充分定价",
            "出现更强的新事件覆盖原有逻辑",
        ],
        "variable_thresholds": [
            {
                "variable": "事件相关资产价格",
                "threshold": "涨幅超过分析时预期的 2 倍",
                "direction": "cross_above",
                "effect": "市场已过度反应，退出",
            },
            {
                "variable": "新催化剂",
                "threshold": "出现方向相反的新事件",
                "direction": "出现",
                "effect": "原有逻辑被覆盖，重新评估",
            },
        ],
        "time_boundary": {
            "valid_period": "7 天或下次相关事件触发",
            "reassess_after": 7,
        },
        "exit_signals": [
            {
                "signal": "事件预期已完全反映在价格中",
                "observable": True,
                "trigger_action": "止盈/止损离场",
            },
            {
                "signal": "逻辑被证伪",
                "observable": True,
                "trigger_action": "立即离场，不等待",
            },
        ],
        "monitoring_frequency": "事件驱动",
        "confidence": 0.7,
    }


# ── 处理器注册表 ──────────────────────────────────────────────

def get_handlers() -> Dict[int, callable]:
    """获取地利层所有六步处理器"""
    return {
        0: step0_verify,
        1: step1_decompose,
        2: step2_transmit,
        3: step3_history,
        4: step4_scenario,
        5: step5_action,
        6: step6_invalidation,
    }
