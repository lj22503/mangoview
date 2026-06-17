"""
Mangofolio 每步完成标准校验

按 PROJECT_INVENTORY.md 自进化补充定义的阈值实现。
"""

import logging
from typing import Dict, Any, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class LayerType(str, Enum):
    TIANSHI = "tianshi"
    DILI = "dili"
    RENHE = "renhe"


# ── 各层各步的通过条件 ─────────────────────────────────────────

THRESHOLDS = {
    LayerType.TIANSHI: {
        0: {"source_credibility": 0.5},
        1: {"core_variables_max": 5},
        2: {"impact_pathways_min": 2},
        3: {"similarity_min": 0.3},
        4: {"consistency_check": True},
        5: {"position_side_required": True},
        6: {"exit_signals_min": 1},
    },
    LayerType.DILI: {
        0: {"source_credibility": 0.5},
        1: {"core_variables_max": 5},
        2: {"impact_pathways_min": 2},
        3: {"similar_cases_min": 1, "similarity_min": 0.3},
        4: {"consistency_check": True},
        5: {"position_side_required": True, "constraint_check": True},
        6: {"exit_signals_min": 1},
    },
    LayerType.RENHE: {
        0: {"source_credibility": 0.5},
        1: {"core_variables_max": 5, "classification_confidence_min": 0.4},
        2: {"attribution_complete": True},
        3: {"cases_or_data_complete": True},
        4: {"valuation_range_complete": True},
        5: {"position_side_required": True, "constraint_check": True},
        6: {"exit_signals_min": 1},
    },
}


def check_step(
    layer: LayerType,
    step: int,
    step_output: Dict[str, Any],
) -> Tuple[bool, Optional[str]]:
    """
    校验某步是否通过完成标准

    Args:
        layer: 天时/地利/人和
        step: 步骤编号 0-6
        step_output: 该步的输出数据

    Returns:
        (passed, fail_reason)
    """
    thresholds = THRESHOLDS.get(layer, {}).get(step, {})
    if not thresholds:
        return True, None

    for key, threshold in thresholds.items():
        passed, reason = _check_single(key, threshold, step_output)
        if not passed:
            logger.info(
                "[%s Step %d] 未通过: %s (阈值=%s)",
                layer.value, step, reason, threshold
            )
            return False, reason

    return True, None


def _check_single(
    key: str, threshold: Any, output: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """校验单个阈值条件"""
    checkers = {
        "source_credibility": _check_source_credibility,
        "core_variables_max": _check_core_variables_max,
        "impact_pathways_min": _check_impact_pathways_min,
        "similarity_min": _check_similarity_min,
        "similar_cases_min": _check_similar_cases_min,
        "consistency_check": _check_consistency,
        "position_side_required": _check_position_side,
        "constraint_check": _check_constraint,
        "exit_signals_min": _check_exit_signals_min,
        "classification_confidence_min": _check_classification_confidence,
        "attribution_complete": _check_attribution_complete,
        "cases_or_data_complete": _check_cases_or_data,
        "valuation_range_complete": _check_valuation_range,
    }

    checker = checkers.get(key)
    if checker is None:
        return True, None

    return checker(threshold, output)


def _check_source_credibility(threshold: float, output: Dict) -> Tuple[bool, Optional[str]]:
    val = output.get("source_credibility", 0)
    if val < threshold:
        return False, f"信源可信度 {val:.2f} < {threshold}"
    return True, None


def _check_core_variables_max(threshold: int, output: Dict) -> Tuple[bool, Optional[str]]:
    vars_list = output.get("core_variables", [])
    if len(vars_list) > threshold:
        return False, f"核心变量 {len(vars_list)} > {threshold}"
    return True, None


def _check_impact_pathways_min(threshold: int, output: Dict) -> Tuple[bool, Optional[str]]:
    pathways = output.get("impact_pathways", output.get("causal_chain", ""))
    if isinstance(pathways, str):
        count = len([p for p in pathways.split("；") if p.strip()])
    elif isinstance(pathways, list):
        count = len(pathways)
    else:
        count = 0
    if count < threshold:
        return False, f"传导路径 {count} < {threshold}"
    return True, None


def _check_similarity_min(threshold: float, output: Dict) -> Tuple[bool, Optional[str]]:
    similarity = output.get("similarity", {})
    if isinstance(similarity, dict):
        vm = similarity.get("variable_match", 0)
    elif isinstance(similarity, (int, float)):
        vm = similarity
    else:
        vm = 0
    if vm < threshold:
        return False, f"相似度 {vm:.2f} < {threshold}"
    return True, None


def _check_similar_cases_min(threshold: int, output: Dict) -> Tuple[bool, Optional[str]]:
    cases = output.get("similar_cases", [])
    if len(cases) < threshold:
        return False, f"相似案例 {len(cases)} < {threshold}"
    return True, None


def _check_consistency(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    passed = output.get("consistency_check", False)
    if not passed:
        return False, "情景一致性检查未通过"
    return True, None


def _check_position_side(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    action = output.get("base_action", {})
    direction = action.get("direction", "") if isinstance(action, dict) else ""
    if not direction or direction == "观望":
        return False, "未明确方向（base_action.direction 为空或'观望'）"
    return True, None


def _check_constraint(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    constraint = output.get("constraint_check", {})
    if isinstance(constraint, dict):
        passed = all(constraint.get(k, False) for k in ["risk_capacity", "fund_size"])
    elif isinstance(constraint, bool):
        passed = constraint
    else:
        passed = False
    if not passed:
        return False, "约束自检未全部通过"
    return True, None


def _check_exit_signals_min(threshold: int, output: Dict) -> Tuple[bool, Optional[str]]:
    signals = output.get("exit_signals", [])
    if len(signals) < threshold:
        return False, f"退出信号 {len(signals)} < {threshold}"
    return True, None


def _check_classification_confidence(threshold: float, output: Dict) -> Tuple[bool, Optional[str]]:
    conf = output.get("classification_confidence",
                      output.get("confidence", 0))
    if conf < threshold:
        return False, f"分类置信度 {conf:.2f} < {threshold}"
    return True, None


def _check_attribution_complete(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    # 检查归因分解是否完整（公司：收入/利润/现金流；基金：alpha/beta/行业）
    attribution = output.get("return_attribution", output.get("attribution", {}))
    if not attribution:
        return False, "归因分解缺失"
    return True, None


def _check_cases_or_data(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    cases = output.get("similar_cases", [])
    attribution = output.get("return_attribution", output.get("attribution", {}))
    if not cases and not attribution:
        return False, "既无相似案例，也无归因数据"
    return True, None


def _check_valuation_range(threshold: bool, output: Dict) -> Tuple[bool, Optional[str]]:
    scenario = output.get("scenario_analysis", output.get("valuation_range", {}))
    if isinstance(scenario, dict):
        has_all = all(k in scenario for k in ["bull_case", "base_case", "bear_case"])
        if not has_all:
            return False, "估值区间不完整（需包含 bull/base/bear）"
    return True, None


def get_step_summary(layer: LayerType, step: int) -> Dict:
    """获取某步的通过条件说明"""
    return {
        "layer": layer.value,
        "step": step,
        "conditions": THRESHOLDS.get(layer, {}).get(step, {}),
    }
