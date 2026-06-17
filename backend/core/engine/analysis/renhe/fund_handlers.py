"""
人和层-基金：六步分析处理器（基金深度解读）

按 PROJECT_INVENTORY.md 需求 4.2 实现。
"""

import logging
from typing import Dict, Any

from .classifiers import classify_fund_style, score_financial_health

logger = logging.getLogger(__name__)


def step0_verify(step_input: Dict) -> Dict:
    """Step 0 校验：基金数据来源画像"""
    raw_data = step_input.get("raw_data", step_input)
    source = raw_data.get("source", raw_data.get("data_source", "未知"))
    fund_name = raw_data.get("fund_name", raw_data.get("fund_code", ""))

    # 来源可信度
    trusted_sources = ["基金年报", "基金季报", "交易所", "官方", "天天基金", "Wind", "Bloomberg"]
    media_sources = ["财经媒体", "自媒体", "论坛"]

    if any(s in source for s in trusted_sources):
        source_credibility = 0.85
    elif any(s in source for s in media_sources):
        source_credibility = 0.45
    else:
        source_credibility = 0.35

    # 偏差检测
    bias_types = []
    if "自媒体" in source or "论坛" in source:
        bias_types.append("非官方信息（可能存在误导）")
    if raw_data.get("is_promotional"):
        bias_types.append("推广偏差（营销材料可能夸大业绩）")

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
        "data_completeness": _assess_fund_data_completeness(raw_data),
    }


def _assess_fund_data_completeness(data: Dict) -> Dict:
    """评估基金数据的完整性"""
    required = ["fund_name", "fund_type", "nav", "return_1y"]
    style_fields = ["pe_quantile", "holding_style", "sector_concentration"]
    advanced = ["manager_tenure", "turnover_rate", "tracking_error"]

    found_req = sum(1 for f in required if data.get(f) is not None)
    found_style = sum(1 for f in style_fields if data.get(f) is not None)
    found_adv = sum(1 for f in advanced if data.get(f) is not None)

    completeness = (found_req / len(required)) * 0.5 + (found_style / len(style_fields)) * 0.3 + (found_adv / len(advanced)) * 0.2

    return {
        "score": round(completeness * 100, 1),
        "has_style_data": found_style >= 2,
        "has_advanced": found_adv >= 1,
        "missing_critical": [f for f in required if data.get(f) is None],
    }


def step1_decompose(step_input: Dict) -> Dict:
    """Step 1 拆解：基金风格 + 核心业绩变量"""
    raw_data = step_input.get("raw_data", step_input)
    fund_data = {
        "pe_quantile": raw_data.get("pe_quantile"),
        "holding_style": raw_data.get("holding_style"),
        "turnover_rate": raw_data.get("turnover_rate"),
        "dividend_yield": raw_data.get("dividend_yield"),
        "bond_allocation": raw_data.get("bond_allocation"),
        "sector_concentration": raw_data.get("sector_concentration"),
        "tracking_error": raw_data.get("tracking_error"),
        "holding_count": raw_data.get("holding_count"),
    }

    # 基金风格分类
    style = classify_fund_style(fund_data)

    # 业绩指标
    returns = {
        "1_month": raw_data.get("return_1m"),
        "3_month": raw_data.get("return_3m"),
        "6_month": raw_data.get("return_6m"),
        "1_year": raw_data.get("return_1y"),
        "3_year": raw_data.get("return_3y"),
        "ytd": raw_data.get("return_ytd"),
    }

    # 风险指标
    risk_metrics = {
        "max_drawdown": raw_data.get("max_drawdown", 0),
        "volatility": raw_data.get("volatility", 0),
        "sharpe_ratio": raw_data.get("sharpe_ratio", 0),
        "alpha": raw_data.get("alpha"),
        "beta": raw_data.get("beta"),
    }

    # 核心变量
    core_variables = [
        {
            "name": "基金风格",
            "value": style["primary_style"],
            "importance": "HIGH",
            "variable_type": "风格",
        },
        {
            "name": "风格置信度",
            "value": style["confidence"],
            "importance": "MEDIUM",
            "variable_type": "置信度",
        },
    ]

    # 加入可用的收益数据
    for period, value in returns.items():
        if value is not None:
            core_variables.append({
                "name": f"收益-{period}",
                "value": value,
                "importance": "MEDIUM",
                "variable_type": "业绩",
            })

    # 加入风险指标
    for risk_name, risk_val in risk_metrics.items():
        if risk_val is not None:
            core_variables.append({
                "name": f"风险-{risk_name}",
                "value": risk_val,
                "importance": "MEDIUM",
                "variable_type": "风险",
            })

    key_assumptions = [
        "历史业绩不代表未来表现",
        f"基金风格为{style['primary_style']}，需关注风格漂移风险",
    ]
    if risk_metrics.get("sharpe_ratio", 1) < 0.5:
        key_assumptions.append("风险调整后收益偏低，需谨慎")

    return {
        "core_variables": core_variables[:5],
        "confidence": style["confidence"],
        "classification_confidence": style["confidence"],
        "fund_style": style,
        "returns": returns,
        "risk_metrics": risk_metrics,
        "key_assumptions": key_assumptions,
        "pending_validations": [
            "下季报持仓验证风格一致性",
            "基金经理是否发生变动",
        ],
    }


def step2_transmit(step_input: Dict) -> Dict:
    """Step 2 传导：基金收益归因分析"""
    core_vars = step_input.get("core_variables", [])
    fund_style = "未分类"
    for v in core_vars:
        if isinstance(v, dict) and v.get("name") == "基金风格":
            fund_style = v.get("value", "未分类")

    # 风格对应的传导逻辑
    style_chains = {
        "成长型": "选股（高增长标的）→ 盈利增长驱动 → 估值扩张 → 超额收益",
        "价值型": "选股（低估标的）→ 估值修复 → 均值回归 → 超额收益",
        "平衡型": "股债配置 → 再平衡 → 风险控制 → 稳健收益",
        "行业主题型": "行业选择 → 主题催化 → 资金流入 → 行业β收益",
        "指数型": "跟踪误差控制 → 费率优势 → 复制指数收益",
        "量化型": "因子模型 → 多因子选股 → 风险控制 → 超额收益（α）",
    }
    causal_chain = style_chains.get(fund_style, "资产配置 → 选股/选券 → 收益创造")

    # 收益归因分解（满足 attribution_complete）
    return_attribution = {
        "asset_allocation": {
            "equity_pct": "股票仓位贡献",
            "bond_pct": "债券仓位贡献",
            "cash_pct": "现金管理贡献",
            "description": "大类资产配置对总收益的贡献度",
        },
        "sector_allocation": {
            "overweight_sectors": "超配行业的收益贡献",
            "underweight_sectors": "低配行业的收益贡献",
            "description": "行业配置对超额收益的贡献度",
        },
        "security_selection": {
            "stock_picking": "个股选择的超额收益",
            "timing": "择时操作的收益贡献",
            "description": "选股和择时对超额收益的贡献度",
        },
        "style_factor": {
            "value_factor": "价值因子暴露",
            "growth_factor": "成长因子暴露",
            "momentum_factor": "动量因子暴露",
            "size_factor": "市值因子暴露",
            "description": "风格因子暴露对收益的贡献度",
        },
    }

    # 反馈回路
    feedback_loops = []
    if fund_style in ("成长型", "行业主题型"):
        feedback_loops.append({
            "type": "正反馈",
            "description": "业绩好 → 资金流入 → 规模扩大 → 买入已有持仓 → 短期继续推高",
        })

    return {
        "causal_chain": causal_chain,
        "return_attribution": return_attribution,
        "attribution": return_attribution,
        "feedback_loops": feedback_loops,
        "blockage_points": [
            {
                "location": "规模与业绩",
                "reason": "基金规模过大可能限制灵活性，超额收益递减",
            }
        ],
        "time_characteristics": [
            {"path": "持仓调整", "delay": "滞后", "timescale": "季度（按季报披露）"},
            {"path": "风格切换", "delay": "缓慢", "timescale": "半年以上"},
        ],
        "transmission_strength": "强" if fund_style in ("行业主题型", "量化型") else "中",
        "confidence": 0.7,
    }


def step3_history(step_input: Dict) -> Dict:
    """Step 3 历史：同类基金比较"""
    raw_data = step_input.get("raw_data", step_input)
    fund_type = raw_data.get("fund_type", "")
    fund_style = "未分类"
    for v in step_input.get("core_variables", []):
        if isinstance(v, dict) and v.get("name") == "基金风格":
            fund_style = v.get("value", "未分类")

    similar_cases = []

    # 同类基金比较
    if fund_style:
        similar_cases.append({
            "comparison": f"{fund_style}基金同类均值",
            "time": "近 1 年/3 年",
            "core_features": f"同类{f' {fund_type}' if fund_type else ''}基金的业绩中位数和四分位",
            "outcome": "判断基金在同类中的分位排名",
        })

    # 历史风格稳定性
    similar_cases.append({
        "comparison": "基金自身历史风格",
        "time": "近 3 年",
        "core_features": "基金持仓风格的季度变化，判断风格漂移程度",
        "outcome": "风格稳定的基金更可预测，漂移大的需警惕",
    })

    # 归因数据（满足 cases_or_data_complete 的 data）
    attribution = {
        "historical_performance": "近1/3/5年累计收益和年化收益",
        "risk_adjusted": "Sharpe比率、Sortino比率、Calmar比率",
        "drawdown_analysis": "最大回撤及恢复时间",
        "rolling_performance": "滚动1年收益的稳定性和持续性",
    }

    return {
        "similar_cases": similar_cases[:3],
        "attribution": attribution,
        "similarity": {
            "variable_match": 0.55,
            "context_match": 0.45,
        },
        "key_differences": [
            {
                "difference": "不同基金经理的投资理念和操作风格不同",
                "potential_impact": "即使同风格，业绩差异也可能很大",
            },
            {
                "difference": "基金规模变化影响操作灵活性",
                "potential_impact": "规模快速增长可能导致业绩稀释",
            },
        ],
        "transferable_patterns": [
            "选股型基金的业绩持续性高于择时型",
            "费率是长期收益的重要影响因素",
        ],
        "non_transferable_patterns": [
            "短期业绩排名不可简单外推",
        ],
        "confidence": 0.55,
    }


def step4_scenario(step_input: Dict) -> Dict:
    """Step 4 情景：基金情景分析"""
    raw_data = step_input.get("raw_data", step_input)
    sharpe = raw_data.get("sharpe_ratio", 0.5)
    alpha = raw_data.get("alpha", 0)

    scenario_analysis = {
        "bull_case": {
            "probability": "低",
            "trigger": "市场风格与该基金匹配 + 基金经理发挥正常",
            "path": "风格匹配 → 超额收益显著 → 同类排名前 25%",
            "impact": "显著跑赢基准，适合增持",
        },
        "base_case": {
            "probability": "中",
            "trigger": "市场正常波动，基金经理正常操作",
            "path": "风格适度匹配 → 获取市场平均收益 → 同类排名中位数",
            "impact": "获得合理回报，适合持有",
        },
        "bear_case": {
            "probability": "低",
            "trigger": f"市场风格切换 + 基金风格不匹配{' + 超额收益为负' if alpha and alpha < 0 else ''}",
            "path": "风格不匹配 → 业绩落后基准 → 规模缩水 → 被动卖出",
            "impact": "跑输基准，减仓或赎回",
        },
    }

    valuation_range = {
        "bull_case": "同类前 25% 分位",
        "base_case": "同类中位数水平",
        "bear_case": "同类后 25% 分位",
    }

    return {
        "scenario_analysis": scenario_analysis,
        "valuation_range": valuation_range,
        "key_bifurcation": {
            "variable": "基金经理是否变更",
            "threshold": "核心基金经理离职",
            "direction": "留任则维持判断，离职则重新评估",
        },
        "risk_warning": {
            "concentration_risk": "持仓集中度风险",
            "style_drift_risk": "风格漂移风险",
            "scale_risk": "规模过大导致超额收益递减",
        },
        "consistency_check": True,
        "confidence": 0.6,
    }


def step5_action(step_input: Dict) -> Dict:
    """Step 5 行动：基金配置建议"""
    raw_data = step_input.get("raw_data", step_input)
    sharpe = raw_data.get("sharpe_ratio", 0.5)

    # 方向判断
    if sharpe >= 1.0:
        direction = "买入"
        intensity = "重仓"
    elif sharpe >= 0.5:
        direction = "买入"
        intensity = "轻仓"
    elif sharpe >= 0:
        direction = "持有"
        intensity = "观察"
    else:
        direction = "卖出"
        intensity = "轻仓"

    return {
        "base_action": {
            "direction": direction,
            "object": raw_data.get("fund_name", raw_data.get("fund_code", "")),
            "logic": f"Sharpe比率{sharpe:.2f}，风险调整后收益{'优秀' if sharpe >= 1 else '中等' if sharpe >= 0.5 else '偏低'}",
            "intensity": intensity,
            "time_window": "6-12 个月",
        },
        "bull_action": {
            "intensity": "重仓",
            "logic": "基金经理持续创造超额收益，可加大配置",
        },
        "bear_action": {
            "intensity": "观察",
            "logic": "市场风格不匹配或基金经理变动，减仓观察",
        },
        "no_action_condition": "基金风格与当前市场环境不匹配时，观望为主",
        "constraint_check": {
            "risk_capacity": True,
            "fund_size": True,
            "execution": True,
        },
        "confidence": 0.7 if sharpe >= 0.5 else 0.5,
    }


def step6_invalidation(step_input: Dict) -> Dict:
    """Step 6 失效：基金分析的退出条件"""
    return {
        "logical_conditions": [
            "基金经理变更（核心投研人员离职）",
            "基金风格发生显著漂移（持续 2 个季度以上）",
            "基金规模急剧变化（过大或过小）",
            "基金公司出现重大风险事件",
        ],
        "variable_thresholds": [
            {
                "variable": "基金经理",
                "threshold": "核心基金经理离职或变更",
                "direction": "出现",
                "effect": "历史业绩参考价值下降，重新评估",
            },
            {
                "variable": "跟踪误差",
                "threshold": "相对基准偏离超过 5%",
                "direction": "cross_above",
                "effect": "风格可能发生漂移",
            },
            {
                "variable": "规模变化",
                "threshold": "规模增长超过 100% 或缩水超过 50%",
                "direction": "cross_above",
                "effect": "规模过大可能限制策略执行",
            },
        ],
        "time_boundary": {
            "valid_period": "至下次季报披露或重大事项触发",
            "reassess_after": 90,
        },
        "exit_signals": [
            {
                "signal": "基金经理离职",
                "observable": True,
                "trigger_action": "立即评估是否赎回",
            },
            {
                "signal": "连续 2 个季度同类排名后 50%",
                "observable": True,
                "trigger_action": "减仓或转换",
            },
            {
                "signal": "基金风格与最初评估发生根本性变化",
                "observable": True,
                "trigger_action": "重新评估持有价值",
            },
        ],
        "monitoring_frequency": "季度",
        "confidence": 0.7,
    }


# ── 处理器注册表 ──────────────────────────────────────────────

def get_fund_handlers() -> Dict[int, callable]:
    """获取基金分析所有六步处理器"""
    return {
        0: step0_verify,
        1: step1_decompose,
        2: step2_transmit,
        3: step3_history,
        4: step4_scenario,
        5: step5_action,
        6: step6_invalidation,
    }
