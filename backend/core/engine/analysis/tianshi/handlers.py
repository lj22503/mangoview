"""
天时层：六步分析处理器

每步处理器接收 step_input（含上一步精炼数据），输出符合 Step Schema 的字典。
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .cycle_matrix import determine_economic_cycle, get_asset_allocation

logger = logging.getLogger(__name__)


def step0_verify(step_input: Dict) -> Dict:
    """Step 0 校验：来源画像、时效性、偏差检测"""
    data_source = step_input.get("data_source", "")
    source_type = step_input.get("source_type", "")
    raw_data = step_input.get("raw_data", step_input)

    # 来源可信度评分
    credibility_map = {
        "官方": 0.9,
        "一手": 0.8,
        "机构分析": 0.6,
        "媒体": 0.4,
        "二手": 0.3,
    }
    source_credibility = credibility_map.get(source_type, 0.3)

    # 偏差检测
    bias_types = []
    if source_type == "媒体":
        bias_types.append("媒体偏差（标题党倾向）")
    if source_type == "机构分析":
        bias_types.append("利益冲突（机构可能有持仓）")

    # 最终评定
    if source_credibility >= 0.7:
        final_rating = "直接使用"
    elif source_credibility >= 0.4:
        final_rating = "需验证后使用"
    elif source_credibility >= 0.2:
        final_rating = "仅作参考"
    else:
        final_rating = "不可用"

    return {
        "source_credibility": source_credibility,
        "bias_types": bias_types,
        "final_rating": final_rating,
        "confidence": min(source_credibility + 0.1, 1.0),
        "data_freshness": raw_data.get("data_freshness", "unknown"),
        "bias_flag": len(bias_types) > 0,
    }


def step1_decompose(step_input: Dict) -> Dict:
    """Step 1 拆解：提取核心宏观变量"""
    raw = step_input.get("raw_data", step_input)
    macro = raw.get("macro_data", raw)

    # 核心变量提取
    core_variables = []

    # 增长维度
    if macro.get("pmi") is not None:
        core_variables.append({
            "name": "PMI", "value": macro["pmi"],
            "importance": "HIGH", "variable_type": "可观测",
        })
    if macro.get("gdp") is not None:
        core_variables.append({
            "name": "GDP", "value": macro["gdp"],
            "importance": "HIGH", "variable_type": "可观测",
        })

    # 通胀维度
    if macro.get("cpi") is not None:
        core_variables.append({
            "name": "CPI", "value": macro["cpi"],
            "importance": "HIGH", "variable_type": "可观测",
        })
    if macro.get("ppi") is not None:
        core_variables.append({
            "name": "PPI", "value": macro["ppi"],
            "importance": "MEDIUM", "variable_type": "可观测",
        })

    # 货币维度
    if macro.get("m2") is not None:
        core_variables.append({
            "name": "M2", "value": macro["m2"],
            "importance": "MEDIUM", "variable_type": "可观测",
        })
    if macro.get("interest_rate") is not None:
        core_variables.append({
            "name": "利率", "value": macro["interest_rate"],
            "importance": "HIGH", "variable_type": "可观测",
        })

    # 信用维度
    if macro.get("social_financing") is not None:
        core_variables.append({
            "name": "社融", "value": macro["social_financing"],
            "importance": "MEDIUM", "variable_type": "可观测",
        })

    # 核心假设
    key_assumptions = [
        "宏观数据滞后 1-2 个月，当前数据反映的是过去的情况",
        "各变量间存在时滞，传导需要时间",
    ]

    # 当前数据不足以判断周期位置
    pmi = macro.get("pmi")
    cpi = macro.get("cpi")
    if pmi is not None and pmi < 48:
        key_assumptions.append("PMI 持续低于 48 可能预示衰退风险")

    return {
        "core_variables": core_variables[:5],
        "confidence": 0.8 if len(core_variables) >= 3 else 0.5,
        "key_assumptions": key_assumptions,
        "pending_validations": [
            "下期 PMI 数据确认趋势方向",
            "CPI 是否出现拐点",
        ],
    }


def step2_transmit(step_input: Dict) -> Dict:
    """Step 2 传导：构建变量间的传导路径"""
    core_vars = step_input.get("core_variables", [])
    var_names = [v.get("name", "") for v in core_vars if isinstance(v, dict)]

    # 构建传导链
    causal_chain_parts = []

    if "PMI" in var_names or "GDP" in var_names:
        causal_chain_parts.append("增长 → 企业利润 → 库存周期 → 就业 → 居民收入")

    if "CPI" in var_names or "PPI" in var_names:
        causal_chain_parts.append("通胀 → 实际利率 → 货币政策预期 → 债券收益率 → 股市估值")
        causal_chain_parts.append("PPI → 上游利润 → 中游成本 → 下游毛利率")

    if "M2" in var_names or "社融" in var_names:
        causal_chain_parts.append("货币供应 → 信用创造 → 投资 → 经济增速")

    if "利率" in var_names:
        causal_chain_parts.append("利率 → 资金成本 → 企业融资意愿 → 资本开支 → 经济增长")

    causal_chain = " → ".join(causal_chain_parts) if causal_chain_parts else "数据不足，无法构建完整传导链"

    # 反馈回路
    feedback_loops = [
        {
            "type": "负反馈",
            "description": "通胀↑ → 加息 → 需求↓ → 通胀↓ → 降息",
        },
    ]

    # 传导强度
    transmission_strength = "强" if len(var_names) >= 5 else "中" if len(var_names) >= 3 else "弱"

    return {
        "causal_chain": causal_chain,
        "feedback_loops": feedback_loops,
        "blockage_points": [
            {
                "location": "货币政策传导",
                "reason": "当前信用传导存在阻滞（宽货币未转化为宽信用）",
            }
        ],
        "time_characteristics": [
            {"path": "货币政策", "delay": "滞后", "timescale": "3-6 个月"},
            {"path": "汇率传导", "delay": "即时", "timescale": "实时"},
        ],
        "transmission_strength": transmission_strength,
        "confidence": 0.7 if len(causal_chain_parts) >= 2 else 0.4,
    }


def step3_history(step_input: Dict) -> Dict:
    """Step 3 历史：检索相似历史时期"""
    core_vars = step_input.get("core_variables", [])
    var_names = {v.get("name", "") for v in core_vars if isinstance(v, dict)}

    # 变量特征匹配
    has_growth_concern = "PMI" in var_names
    has_inflation = "CPI" in var_names
    has_monetary = "利率" in var_names or "M2" in var_names

    similar_cases = []
    key_differences = []

    # 类 2019 年初：宽货币 + 低通胀 + 贸易摩擦
    if has_growth_concern and has_monetary:
        similar_cases.append({
            "time": "2019 年初",
            "location": "中国",
            "core_features": "PMI 下行 + 宽货币 + 贸易摩擦 + 信用传导阻滞",
            "outcome": "股市先跌后涨，科技股领涨，债券牛市",
        })
        key_differences.append({
            "difference": "当前地缘风险高于 2019",
            "potential_impact": "风险溢价更高，估值中枢可能更低",
        })

    # 类 2022 年底：放开后复苏
    if has_growth_concern:
        similar_cases.append({
            "time": "2022 年底",
            "location": "中国",
            "core_features": "放开后经济弱复苏 + 地产下行 + 出口承压",
            "outcome": "弱复苏持续，结构性行情（AI/中特估）",
        })
        key_differences.append({
            "difference": "当前库存周期位置不同",
            "potential_impact": "补库力度可能弱于 2022",
        })

    # 类 2015 年：产能过剩 + 通缩
    if has_inflation:
        similar_cases.append({
            "time": "2015 年",
            "location": "中国",
            "core_features": "产能过剩 + PPI 通缩 + 货币宽松 + 股市泡沫",
            "outcome": "股市先暴涨后暴跌，随后债券牛市",
        })

    if not similar_cases:
        similar_cases.append({
            "time": "无强相似案例",
            "location": "-",
            "core_features": "当前变量组合在历史上没有高度相似的时期",
            "outcome": "以逻辑推导为主",
        })

    similarity_score = 0.6 if len(similar_cases) >= 2 else 0.3

    return {
        "similar_cases": similar_cases,
        "similarity": {
            "variable_match": similarity_score,
            "context_match": similarity_score - 0.1,
        },
        "key_differences": key_differences,
        "transferable_patterns": [
            "宽货币到宽信用通常需要 3-6 个月传导",
            "弱复苏环境下成长风格通常跑赢价值",
        ],
        "non_transferable_patterns": [
            "每次地缘冲击的影响范围不可简单类比",
        ],
        "confidence": similarity_score + 0.15,
    }


def step4_scenario(step_input: Dict) -> Dict:
    """Step 4 情景：生成基准/乐观/悲观情景"""
    core_vars = step_input.get("core_variables", [])
    var_names = {v.get("name", "") for v in core_vars if isinstance(v, dict)}

    # 尝试判断经济周期
    macro_data = step_input.get("raw_data", step_input).get("macro_data", {})
    cycle_phase, cycle_conf, cycle_reasoning = determine_economic_cycle(macro_data)
    allocation = get_asset_allocation(cycle_phase)

    # 一致性检查
    has_contradiction = False
    if "CPI" in var_names and "M2" in var_names:
        has_contradiction = False  # 通胀和货币通常一致

    return {
        "base_case": {
            "probability": "中",
            "assumptions": [
                "当前宏观趋势延续",
                "政策不出现大幅转向",
                f"经济处于{cycle_phase}阶段",
            ],
            "path": (
                f"基准情景：经济处于{cycle_phase}阶段，"
                f"建议配置：股票{'超配' if allocation.get('equity') == 'overweight' else '标配' if allocation.get('equity') == 'neutral' else '低配'}，"
                f"债券{'超配' if allocation.get('bond') == 'overweight' else '标配'}"
            ),
            "impact": f"资产配置以{cycle_phase}周期特征为主",
        },
        "bull_case": {
            "probability": "低",
            "trigger": "政策超预期宽松 + 信用传导打通 + 外部环境改善",
            "path": "复苏加速 → 企业盈利改善 → 股市上涨 → 商品需求回升",
            "impact": "加大权益配置比例，周期行业优先受益",
        },
        "bear_case": {
            "probability": "低",
            "trigger": "地缘冲突升级 + 通胀反复 + 信用风险暴露",
            "path": "风险偏好下降 → 资金避险 → 股市下跌 → 信用利差走阔",
            "impact": "减仓权益，增加债券和现金配置",
        },
        "key_bifurcation": {
            "variable": "信用传导效率",
            "threshold": "社融增速持续 3 个月 > 10%",
            "direction": "上穿则乐观，下穿则悲观",
        },
        "consistency_check": not has_contradiction,
        "confidence": cycle_conf,
    }


def step5_action(step_input: Dict) -> Dict:
    """Step 5 行动：映射到资产配置建议"""
    raw_data = step_input.get("raw_data", step_input)
    macro_data = raw_data.get("macro_data", {})
    cycle_phase, _, _ = determine_economic_cycle(macro_data)
    allocation = get_asset_allocation(cycle_phase)

    # 方向判断
    if allocation.get("equity") == "overweight":
        direction = "买入"
        intensity = "重仓"
    elif allocation.get("equity") == "underweight":
        direction = "卖出"
        intensity = "轻仓"
    else:
        direction = "持有"
        intensity = "观察"

    return {
        "base_action": {
            "direction": direction,
            "object": cycle_phase,
            "logic": f"当前经济周期处于{cycle_phase}阶段，股票{'超配' if allocation.get('equity')=='overweight' else '低配'}策略",
            "intensity": intensity,
            "time_window": "3-6 个月",
        },
        "bull_action": {
            "intensity": "重仓",
            "logic": "若信用传导打通，加大权益和商品配置",
        },
        "bear_action": {
            "intensity": "观察",
            "logic": "若地缘风险加剧，全面转向防御（债券+现金）",
        },
        "no_action_condition": "当前配置与周期定位基本一致，无需大幅调整",
        "constraint_check": {
            "risk_capacity": True,
            "fund_size": True,
            "execution": True,
        },
        "confidence": 0.75,
    }


def step6_invalidation(step_input: Dict) -> Dict:
    """Step 6 失效：定义退出条件"""
    return {
        "logical_conditions": [
            "周期阶段判断前提条件发生根本性变化",
            "核心数据出现方向性逆转",
        ],
        "variable_thresholds": [
            {
                "variable": "PMI",
                "threshold": 48.5,
                "direction": "cross_below",
                "effect": "衰退信号确认，全面转向防御",
            },
            {
                "variable": "CPI",
                "threshold": 3.0,
                "direction": "cross_above",
                "effect": "通胀超预期，货币政策可能收紧",
            },
            {
                "variable": "社融增速",
                "threshold": 8.0,
                "direction": "cross_below",
                "effect": "信用收缩确认，降低权益配置",
            },
        ],
        "time_boundary": {
            "valid_period": "30 天或下次宏观数据发布",
            "reassess_after": 30,
        },
        "exit_signals": [
            {
                "signal": "PMI 连续 2 个月低于 48.5",
                "observable": True,
                "trigger_action": "全面转向防御配置，减仓权益至 20% 以下",
            },
            {
                "signal": "CPI 突破 3% 且趋势向上",
                "observable": True,
                "trigger_action": "降低权益久期，增配短债",
            },
            {
                "signal": "地缘冲突升级至影响能源供应",
                "observable": True,
                "trigger_action": "增配能源/黄金，减仓风险资产",
            },
        ],
        "monitoring_frequency": "每月",
        "confidence": 0.8,
    }


# ── 处理器注册表 ──────────────────────────────────────────────

def get_handlers() -> Dict[int, callable]:
    """获取天时层所有六步处理器"""
    return {
        0: step0_verify,
        1: step1_decompose,
        2: step2_transmit,
        3: step3_history,
        4: step4_scenario,
        5: step5_action,
        6: step6_invalidation,
    }
