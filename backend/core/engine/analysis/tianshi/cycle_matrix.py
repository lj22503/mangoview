"""
天时层：经济/行业周期判断矩阵

按 PROJECT_INVENTORY.md 需求 2.2-2.3 定义的规则实现。
"""

from typing import Dict, List, Optional, Tuple


# ── 四周期定位表 ──────────────────────────────────────────────

CYCLE_MATRIX = {
    "复苏": {
        "conditions": {
            "pmi_trend": "up",
            "cpi_trend": "down_or_stable",
            "monetary": "loose",
            "credit": "expanding",
        },
        "description": "PMI↑ + CPI↓/平稳 + 货币宽松 + 信用扩张",
        "asset_allocation": {
            "equity": "overweight",
            "bond": "neutral",
            "commodity": "underweight",
            "cash": "underweight",
        },
    },
    "扩张": {
        "conditions": {
            "pmi_level": "high",
            "cpi_trend": "up",
            "monetary": "tightening",
            "credit": "still_expanding",
        },
        "description": "PMI高位 + CPI↑ + 货币边际收紧 + 信用持续扩张",
        "asset_allocation": {
            "equity": "overweight",
            "bond": "underweight",
            "commodity": "overweight",
            "cash": "neutral",
        },
    },
    "放缓": {
        "conditions": {
            "pmi_trend": "down",
            "cpi_trend": "up",
            "monetary": "tight",
            "credit": "contracting",
        },
        "description": "PMI↓ + CPI↑ + 货币收紧 + 信用收缩",
        "asset_allocation": {
            "equity": "neutral",
            "bond": "overweight",
            "commodity": "neutral",
            "cash": "overweight",
        },
    },
    "衰退": {
        "conditions": {
            "pmi_level": "very_low",
            "cpi_trend": "down",
            "monetary": "loosening",
            "credit": "contracted",
        },
        "description": "PMI↓↓ + CPI↓ + 信用收缩 + 失业率↑",
        "asset_allocation": {
            "equity": "underweight",
            "bond": "overweight",
            "commodity": "underweight",
            "cash": "overweight",
        },
    },
}

# ── 行业周期定位表 ────────────────────────────────────────────

INDUSTRY_CYCLE_POSITIONS = {
    "机会区（领先）": {
        "conditions": {
            "valuation_percentile": "low",     # PE/PB 历史分位低位
            "macro_sensitivity": "high",        # 对宏观敏感
            "momentum": "turning_positive",     # 动量转正
        },
        "action": "关注，适合逐步建仓",
        "confidence_boost": 0.2,
    },
    "中性": {
        "conditions": {
            "valuation_percentile": "medium",
            "macro_sensitivity": "medium",
        },
        "action": "持有或观望",
        "confidence_boost": 0.0,
    },
    "风险区（滞后）": {
        "conditions": {
            "valuation_percentile": "high",
            "macro_sensitivity": "high",
            "momentum": "negative",
        },
        "action": "减仓或回避",
        "confidence_boost": -0.2,
    },
}


def determine_economic_cycle(macro_data: Dict) -> Tuple[str, float, str]:
    """
    判断当前经济周期位置

    Args:
        macro_data: 宏观数据，需包含 pmi_trend, cpi_trend, monetary, credit 等字段

    Returns:
        (cycle_phase, confidence, reasoning)
    """
    scores = {}
    for phase, config in CYCLE_MATRIX.items():
        conditions = config["conditions"]
        match_count = 0
        total = len(conditions)
        details = []

        for cond_key, expected in conditions.items():
            actual = macro_data.get(cond_key)
            if actual == expected:
                match_count += 1
                details.append(f"{cond_key}=✅")
            elif actual is not None:
                details.append(f"{cond_key}=❌(get {actual}, want {expected})")
            else:
                details.append(f"{cond_key}=❓(missing)")

        score = match_count / total if total > 0 else 0
        scores[phase] = {
            "score": score,
            "detail": "; ".join(details),
        }

    best_phase = max(scores, key=lambda p: scores[p]["score"])
    best_score = scores[best_phase]["score"]

    if best_score >= 0.75:
        confidence = 0.85
    elif best_score >= 0.5:
        confidence = 0.65
    else:
        confidence = 0.4

    scores_str = ", ".join(
        f"{k}={v['score']:.0%}" for k, v in scores.items()
    )
    reasoning = (
        f"最佳匹配：{best_phase}（匹配度 {best_score:.0%}）\n"
        f"判断依据：{CYCLE_MATRIX[best_phase]['description']}\n"
        f"各周期得分：{scores_str}"
    )

    return best_phase, confidence, reasoning


def get_asset_allocation(cycle_phase: str) -> Dict:
    """根据经济周期获取建议配置"""
    config = CYCLE_MATRIX.get(cycle_phase, {})
    return config.get("asset_allocation", {})


def get_industry_cycle_position(
    valuation_percentile: float,
    macro_sensitivity: str,
    momentum: Optional[str] = None,
) -> Tuple[str, str, float]:
    """
    判断行业周期位置

    Args:
        valuation_percentile: 估值分位 0-100
        macro_sensitivity: 宏观敏感度 "high" / "medium" / "low"
        momentum: 动量方向

    Returns:
        (position, action, confidence_boost)
    """
    # 估值分位映射
    if valuation_percentile < 30:
        val_level = "low"
    elif valuation_percentile < 70:
        val_level = "medium"
    else:
        val_level = "high"

    for position, config in INDUSTRY_CYCLE_POSITIONS.items():
        cond = config["conditions"]
        if (val_level == cond.get("valuation_percentile") and
                macro_sensitivity == cond.get("macro_sensitivity")):
            # 检查动量（如果有）
            expected_momentum = cond.get("momentum")
            if expected_momentum:
                if momentum == expected_momentum or momentum is None:
                    return position, config["action"], config["confidence_boost"]
            else:
                return position, config["action"], config["confidence_boost"]

    return "中性", "持有或观望", 0.0


# ── 行业信号扫描 ──────────────────────────────────────────────

def scan_industry_signals(
    industry_data: List[Dict],
    momentum_data: Optional[Dict] = None,
) -> List[Dict]:
    """
    扫描行业信号

    Args:
        industry_data: 行业数据列表，每个含 industry_code, valuation_percentile, macro_sensitivity
        momentum_data: 动量数据 {industry_code: momentum_value}

    Returns:
        行业信号列表
    """
    signals = []
    for industry in industry_data:
        code = industry.get("industry_code", "")
        val_pct = industry.get("valuation_percentile", 50)
        sensitivity = industry.get("macro_sensitivity", "medium")
        momentum = None
        if momentum_data:
            val = momentum_data.get(code, 0)
            momentum = "turning_positive" if val > 0 else "negative"

        position, action, boost = get_industry_cycle_position(
            val_pct, sensitivity, momentum
        )

        signals.append({
            "industry_code": code,
            "industry_name": industry.get("industry_name", ""),
            "position": position,
            "action": action,
            "confidence_boost": boost,
            "valuation_percentile": val_pct,
        })

    # 按机会区优先排序
    signals.sort(key=lambda s: (
        0 if s["position"] == "机会区（领先）" else
        1 if s["position"] == "中性" else 2
    ))

    return signals
