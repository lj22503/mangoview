"""
天时层（宏观分析）

包含 Scale 筛选、经济周期矩阵、六步分析处理器。
"""

from .scale_filter import scale_filter, has_trigger, MACRO_INDICATORS_TEMPLATE
from .cycle_matrix import (
    determine_economic_cycle, get_asset_allocation,
    get_industry_cycle_position, scan_industry_signals,
)
from .handlers import get_handlers
