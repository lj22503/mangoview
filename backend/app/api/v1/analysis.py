"""
Mangoview 分析 API — 对接 core/engine 真实分析引擎

数据流：
  前端原始指标 → transform_to_trends() → engine 所需格式
    → engine.analyze(layer="tianshi", input_data=macro_data)
    → transform_from_engine() → 前端 cycle_position 格式
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

from core.engine.analysis.tianshi.cycle_matrix import (
    determine_economic_cycle,
    get_asset_allocation,
    CYCLE_MATRIX,
)
from core.engine.data_fetcher import fetch_for_analysis
from core.engine.middleware.tier_model import UserTier

router = APIRouter(prefix="/v1/analysis", tags=["analysis"])

# ── 单例引擎 ──────────────────────────────────────────────

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


# ── 请求模型 ──────────────────────────────────────────────


class CycleLocatorRequest(BaseModel):
    """周期定位请求（来自前端 tools/page）"""
    indicators: Dict[str, float]


class AssetAllocationRequest(BaseModel):
    """资产配置请求"""
    cycle_phase: Optional[str] = None  # 不传则自动判断
    risk_profile: str = "balanced"  # conservative / balanced / aggressive
    macro_indicators: Optional[Dict[str, float]] = None


class EventAnalysisRequest(BaseModel):
    """事件分析请求"""
    event: str
    source: Optional[str] = "用户提交"


# ── 核心转换函数 ──────────────────────────────────────────


def transform_indicators_to_macro_data(indicators: Dict[str, float]) -> Dict[str, Any]:
    """
    将前端原始指标转换为 engine 的 macro_data 格式

    转换规则：
      - pmi >= 50 → pmi_trend = "up"，否则 "down"
      - ppi >= 0 → cpi_trend = "up"（通胀上行），否则 "down_or_stable"
      - fixed_asset_investment:
          > 5 → monetary = "loose"（投资旺盛时期宽松）
          2-5 → monetary = "tightening"（温和）
          < 2 → monetary = "tight"（投资萎靡）
      - credit: 基于 fixed_asset 趋势推断（投资强→信用扩张）

    Returns:
      engine 所需的 macro_data 字典（包含 pmi_trend, cpi_trend, monetary, credit）
    """
    pmi = indicators.get("pmi", 50.0)
    ppi = indicators.get("ppi", 0.0)
    fixed_asset = indicators.get("fixed_asset_investment", 4.0)
    new_start = indicators.get("new_start_area", 0.0)

    # PMI 趋势
    pmi_trend = "up" if pmi >= 50 else "down"
    pmi_level = "high" if pmi >= 52 else ("low" if pmi < 48 else "medium")

    # CPI 趋势（PPI 为负说明通胀压力小）
    if ppi >= 2:
        cpi_trend = "up"
    elif ppi >= 0:
        cpi_trend = "stable"
    else:
        cpi_trend = "down_or_stable"

    # 货币政策（基于固定资产投资）
    if fixed_asset > 5:
        monetary = "loose"
    elif fixed_asset > 2:
        monetary = "tightening"
    else:
        monetary = "tight"

    # 信用状态（与投资强度联动）
    if fixed_asset > 5:
        credit = "expanding"
    elif fixed_asset > 2:
        credit = "still_expanding"
    else:
        credit = "contracting"

    # 原始值也一并传入（engine step1 需要）
    return {
        "pmi": pmi,
        "pmi_trend": pmi_trend,
        "pmi_level": pmi_level,
        "cpi": indicators.get("cpi", None),
        "cpi_trend": cpi_trend,
        "ppi": ppi,
        "gdp": indicators.get("gdp", None),
        "m2": indicators.get("m2", None),
        "interest_rate": indicators.get("interest_rate", None),
        "social_financing": indicators.get("social_financing", None),
        "fixed_asset_investment": fixed_asset,
        "new_start_area": new_start,
        "monetary": monetary,
        "credit": credit,
    }


def map_cycle_phase_to_four_cycles(cycle_phase: str) -> Dict[str, str]:
    """
    将 engine 的经济周期 phase 映射为前端需要的四周期格式

    映射关系（简化版）：
      复苏 → 基钦=复苏早期, 朱格拉=扩张期, 库兹涅茨=上升期, 康波=回升期
      扩张 → 基钦=复苏晚期, 朱格拉=扩张期, 库兹涅茨=上升期, 康波=回升期
      放缓 → 基钦=衰退期, 朱格拉=收缩期, 库兹涅茨=下降期, 康波=萧条期
      衰退 → 基钦=衰退后期, 朱格拉=收缩期, 库兹涅茨=下降期, 康波=萧条期
    """
    mapping = {
        "复苏": {
            "kitchin": "复苏早期",
            "juglar": "扩张期",
            "kuznets": "上升期",
            "kondratieff": "回升期",
        },
        "扩张": {
            "kitchin": "复苏晚期",
            "juglar": "扩张期",
            "kuznets": "上升期",
            "kondratieff": "回升期",
        },
        "放缓": {
            "kitchin": "衰退期",
            "juglar": "收缩期",
            "kuznets": "下降期",
            "kondratieff": "萧条期",
        },
        "衰退": {
            "kitchin": "衰退后期",
            "juglar": "收缩期",
            "kuznets": "下降期",
            "kondratieff": "萧条期",
        },
    }
    return mapping.get(cycle_phase, {
        "kitchin": "观察",
        "juglar": "观察",
        "kuznets": "观察",
        "kondratieff": "萧条期",
    })


def get_allocation_suggestion(
    cycle_phase: str,
    risk_profile: str = "balanced",
) -> Dict[str, str]:
    """
    根据经济周期 + 风险偏好生成配置建议

    在 engine 的 get_asset_allocation() 基础上，
    结合前端的风险偏好做调整
    """
    base = get_asset_allocation(cycle_phase)

    # 风险调整
    risk_adjust = {
        "conservative": {"equity": "neutral", "bond": "overweight"},
        "balanced": {},
        "aggressive": {"equity": "overweight", "bond": "underweight"},
    }.get(risk_profile, {})

    allocation = {**base, **risk_adjust}

    # 转换为前端显示格式
    display_map = {
        "overweight": "优先",
        "neutral": "适度",
        "underweight": "回避",
    }

    return {
        key: display_map.get(val, "适度")
        for key, val in allocation.items()
    }


# ── API 端点 ──────────────────────────────────────────────


@router.post("/cycle-locator")
async def analyze_cycle_locator(req: CycleLocatorRequest):
    """
    周期定位分析 — 真实对接 engine

    调用 engine 的天时层六步分析，输入转换后的宏观数据，
    返回四周期定位 + 配置建议 + 历史对照 + 失效条件
    """
    # 1. 转换前端指标 → engine macro_data
    macro_data = transform_indicators_to_macro_data(req.indicators)

    # 2. 构建 engine 输入
    input_data = {
        "data_source": "用户输入",
        "source_type": "用户提交",
        "data_freshness": "实时",
        "macro_data": macro_data,
    }

    # 3. 调用 engine 分析
    engine = _get_engine()
    result = engine.analyze(
        layer="tianshi",
        input_data=input_data,
        user_tier=UserTier.BASIC,
    )

    # 4. 提取关键结果
    completed = result.get("completed", False)

    if completed:
        # 从 Step4 (情景) 获取周期判断
        step4 = result.get("results", {}).get(4, {})
        step5 = result.get("results", {}).get(5, {})

        # 经济周期 phase
        cycle_phase = step4.get("base_case", {}).get("path", "未知")
        # 从 step5 获取配置方向
        base_action = step5.get("base_action", {})
        direction = base_action.get("direction", "观望")
        intensity = base_action.get("intensity", "观察")
        logic = base_action.get("logic", "")

        # Step3 历史对照
        step3 = result.get("results", {}).get(3, {})
        similar_cases = step3.get("similar_cases", [])

        historical_comparison = [
            {
                "period": case.get("time", ""),
                "similarity": 0.65 + (0.1 if i == 0 else 0),
            }
            for i, case in enumerate(similar_cases[:2])
        ]

        # Step6 失效条件
        step6 = result.get("results", {}).get(6, {})
        exit_signals = step6.get("exit_signals", [])

        # 当前经济周期（取引擎实际判断结果，无结果时回退到本地计算）
        current_phase = cycle_phase
        if not current_phase or current_phase == "未知":
            current_phase, _, _ = determine_economic_cycle(macro_data)

        cycle_position = map_cycle_phase_to_four_cycles(current_phase)
        allocation = get_allocation_suggestion(current_phase, "balanced")

        return {
            "code": 0,
            "data": {
                "engine_result": {
                    "completed": True,
                    "cycle_phase": current_phase,
                    "direction": direction,
                    "intensity": intensity,
                    "logic": logic,
                    "confidence": step5.get("confidence", 0.7),
                    "exit_signals_count": len(exit_signals),
                },
                "cycle_position": cycle_position,
                "allocation_suggestion": allocation,
                "historical_comparison": historical_comparison,
                "exit_signals": exit_signals[:3],
                "scenario": {
                    "base": step4.get("base_case", {}).get("path", ""),
                    "bull": step4.get("bull_case", {}).get("trigger", ""),
                    "bear": step4.get("bear_case", {}).get("trigger", ""),
                },
                "macro_data_preview": {
                    "pmi": macro_data.get("pmi"),
                    "ppi": macro_data.get("ppi"),
                    "fixed_asset": macro_data.get("fixed_asset_investment"),
                    "new_start": macro_data.get("new_start_area"),
                    "monetary": macro_data.get("monetary"),
                    "credit": macro_data.get("credit"),
                },
            },
        }
    else:
        # engine 未完成，降级到本地计算
        cycle_phase, conf, reasoning = determine_economic_cycle(macro_data)
        allocation = get_asset_allocation(cycle_phase)
        cycle_position = map_cycle_phase_to_four_cycles(cycle_phase)

        return {
            "code": 0,
            "data": {
                "engine_result": {
                    "completed": False,
                    "fallback": True,
                    "reason": result.get("error", "引擎未完成"),
                },
                "cycle_position": cycle_position,
                "allocation_suggestion": {
                    k: "优先" if v == "overweight" else "适度" if v == "neutral" else "回避"
                    for k, v in allocation.items()
                },
                "historical_comparison": [
                    {"period": "2012-2013", "similarity": 0.65},
                    {"period": "2015-2016", "similarity": 0.55},
                ],
                "exit_signals": [],
                "scenario": {},
                "macro_data_preview": {},
            },
        }


@router.post("/asset-allocation")
async def analyze_asset_allocation(req: AssetAllocationRequest):
    """
    资产配置分析 — 基于天时层 + 风险偏好
    """
    # 如果没传宏观指标，自动获取
    if req.macro_indicators:
        macro_data = transform_indicators_to_macro_data(req.macro_indicators)
    else:
        # 从 data_fetcher 自动获取宏观数据
        fetched = fetch_for_analysis("tianshi", {})
        macro_data = fetched.get("macro_data", {})

    # 判断周期
    cycle_phase, conf, reasoning = determine_economic_cycle(macro_data)

    # 获取配置
    allocation = get_asset_allocation(cycle_phase)

    # 风险调整
    risk_map = {
        "conservative": {
            "equity": "neutral" if allocation.get("equity") == "overweight" else "underweight",
            "bond": "overweight",
        },
        "balanced": allocation,
        "aggressive": {
            "equity": "overweight",
            "bond": "underweight" if allocation.get("bond") == "overweight" else "neutral",
        },
    }

    final_allocation = risk_map.get(req.risk_profile, allocation)

    display_map = {
        "overweight": "优先",
        "neutral": "适度",
        "underweight": "回避",
    }

    return {
        "code": 0,
        "data": {
            "cycle_phase": cycle_phase,
            "cycle_confidence": conf,
            "cycle_reasoning": reasoning,
            "allocation": {
                key: {
                    "value": 0.4 if v == "overweight" else 0.2 if v == "underweight" else 0.3,
                    "display": display_map.get(v, "适度"),
                    "locked": True,
                }
                for key, v in final_allocation.items()
            },
            "strategy_logic": f"基于当前{cycle_phase}阶段，结合您的{risk_profile}风险偏好，建议：",
        },
    }


@router.get("/macro-data")
async def get_macro_data():
    """
    获取宏观数据（供前端预填或展示）
    """
    fetched = fetch_for_analysis("tianshi", {})
    return {
        "code": 0,
        "data": {
            "market_indices": fetched.get("market_indices", {}),
            "macro_data": fetched.get("macro_data", {}),
            "data_source": fetched.get("data_source", ""),
            "data_freshness": fetched.get("data_freshness", ""),
        },
    }


@router.post("/event")
async def analyze_event(req: EventAnalysisRequest):
    """
    事件分析 — 调用 engine 的地利层
    """
    input_data = fetch_for_analysis("dili", {
        "event": req.event,
        "source": req.source or "用户提交",
    })

    engine = _get_engine()
    result = engine.analyze(
        layer="dili",
        input_data=input_data,
        user_tier=UserTier.BASIC,
    )

    completed = result.get("completed", False)

    if completed:
        step5 = result.get("results", {}).get(5, {})
        base_action = step5.get("base_action", {})

        return {
            "code": 0,
            "data": {
                "completed": True,
                "event_analysis": {
                    "event": req.event,
                    "direction": base_action.get("direction", "观望"),
                    "logic": base_action.get("logic", ""),
                    "intensity": base_action.get("intensity", "观察"),
                    "confidence": step5.get("confidence", 0.6),
                },
                "exit_signals": result.get("results", {}).get(6, {}).get("exit_signals", []),
            },
        }
    else:
        return {
            "code": 0,
            "data": {
                "completed": False,
                "event_analysis": {
                    "event": req.event,
                    "direction": "观望",
                    "logic": "事件信息不足以支撑分析",
                    "intensity": "观察",
                    "confidence": 0.3,
                },
                "exit_signals": [],
            },
        }
