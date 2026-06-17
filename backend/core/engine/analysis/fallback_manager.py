"""
Mangofolio 回退机制管理

按 PROJECT_INVENTORY.md 定义的每步回退规则实现。
"""

import logging
from typing import Tuple, Optional, Dict, Any

from .completion_checker import LayerType

logger = logging.getLogger(__name__)

# ── 回退规则定义 ──────────────────────────────────────────────
# (source_step, fail_reason_keyword) → (fallback_to_step, action)

FALLBACK_RULES = {
    # 天时层
    (LayerType.TIANSHI, 1, "core_variables"): (0, "重新校验数据源"),
    (LayerType.TIANSHI, 2, "impact_pathways"): (1, "重新拆解变量"),
    (LayerType.TIANSHI, 4, "consistency"): (2, "重分析传导路径"),
    # 地利层
    (LayerType.DILI, 1, "core_variables"): (0, "重新校验事件来源"),
    (LayerType.DILI, 2, "impact_pathways"): (1, "重新拆解事件变量"),
    (LayerType.DILI, 4, "consistency"): (2, "重分析因果链"),
    # 人和层
    (LayerType.RENHE, 1, "classification"): (0, "重新校验数据"),
    (LayerType.RENHE, 2, "attribution"): (1, "重新拆解变量"),
}

# 回退计数限制（防止无限循环）
MAX_FALLBACK_PER_STEP = 2


class FallbackTracker:
    """回退跟踪器（防止无限循环）"""

    def __init__(self):
        self._fallback_count: Dict[Tuple[str, int], int] = {}

    def record(self, layer: str, step: int) -> int:
        """记录一次回退，返回累计回退次数"""
        key = (layer, step)
        self._fallback_count[key] = self._fallback_count.get(key, 0) + 1
        return self._fallback_count[key]

    def exceeded_limit(self, layer: str, step: int) -> bool:
        """检查某步回退是否超限"""
        return self._fallback_count.get((layer, step), 0) >= MAX_FALLBACK_PER_STEP

    def reset(self):
        """重置跟踪器"""
        self._fallback_count.clear()


def determine_fallback(
    layer: LayerType,
    current_step: int,
    fail_reason: Optional[str],
    tracker: FallbackTracker,
) -> Tuple[Optional[int], Optional[str]]:
    """
    确定回退到哪一步

    Args:
        layer: 分析层
        current_step: 当前未通过的步骤
        fail_reason: 失败原因
        tracker: 回退跟踪器

    Returns:
        (fallback_to_step, action_description) 或 (None, None) 表示不超限则不回退
    """
    if not fail_reason:
        return None, None

    # 先检查是否超限
    key = (layer.value, current_step)
    count = tracker.record(layer.value, current_step)
    if count > MAX_FALLBACK_PER_STEP:
        logger.warning(
            "[%s Step %d] 回退超限（%d次），强制执行当前步",
            layer.value, current_step, count
        )
        return None, None

    # 匹配回退规则
    for (rule_layer, rule_step, keyword), (to_step, action) in FALLBACK_RULES.items():
        if rule_layer == layer and rule_step == current_step and keyword in fail_reason.lower():
            logger.info(
                "[%s Step %d] 回退到 Step %d: %s",
                layer.value, current_step, to_step, action
            )
            return to_step, action

    # 默认：标记问题但继续
    return None, None


def should_skip_step(
    layer: LayerType,
    step: int,
    fail_reason: Optional[str],
) -> bool:
    """
    判断某步失败后是否应跳过（继续下一步）

    规则：
    - Step 3 历史无强相似案例：跳过，以逻辑推导为主
    - Step 5 方向不明确：输出"观望"
    """
    if fail_reason and "相似度" in fail_reason:
        return True  # 跳过
    if fail_reason and ("方向" in fail_reason or "观望" in fail_reason):
        return True  # 输出观望
    return False
