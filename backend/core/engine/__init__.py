"""
Mangofolio 分析引擎
六步分析框架（天时/地利/人和）+ 信号系统 + 付费中间件 + 数据契约
"""

__version__ = "2.0.0"
__author__ = "燃冰 & ant"

from .orchestrator import AnalysisEngine
from .analysis.step_executor import StepExecutor, LayerType
from .analysis.completion_checker import check_step
from .signals.signal_model import (
    SignalModel, SignalLayer, SignalDirection,
    SignalIntensity, AccessTier,
)
from .signals.signal_registry import get_registry
from .signals.signal_aggregator import aggregate
from .middleware.tier_model import UserTier
from .contract.schema_definitions import SCHEMA_VERSION, list_schemas
from .contract.schema_validator import validate_step_data
from .contract.refined_transfer import build_refined_output


def create_engine(register_all: bool = True) -> AnalysisEngine:
    """
    创建分析引擎实例，可选自动注册所有三层处理器

    Args:
        register_all: 是否自动注册天时/地利/人和三层处理器

    Returns:
        配置好的 AnalysisEngine 实例
    """
    engine = AnalysisEngine()

    if register_all:
        # 天时层
        from .analysis.tianshi.handlers import get_handlers as get_tianshi
        engine.register_layer_handlers("tianshi", get_tianshi())

        # 地利层
        from .analysis.dili.handlers import get_handlers as get_dili
        engine.register_layer_handlers("dili", get_dili())

        # 人和层-公司
        from .analysis.renhe.company_handlers import get_company_handlers
        engine.register_layer_handlers("renhe_company", get_company_handlers())

        # 人和层-基金
        from .analysis.renhe.fund_handlers import get_fund_handlers
        engine.register_layer_handlers("renhe_fund", get_fund_handlers())

    return engine
