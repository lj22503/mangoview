"""配置中心 — 对接 analysis engine 真实周期数据"""
from fastapi import APIRouter
from ...models.schemas import PortfolioRequest
from core.engine.analysis.tianshi.cycle_matrix import (
    determine_economic_cycle,
    get_asset_allocation,
)
from core.engine.data_fetcher import fetch_for_analysis
from .analysis import transform_indicators_to_macro_data

router = APIRouter(prefix="/v1/portfolio", tags=["portfolio"])

RISK_ADJUST = {
    "conservative": {"equity": "underweight", "bond": "overweight"},
    "balanced": {},
    "aggressive": {"equity": "overweight", "bond": "underweight"},
}

VALUE_MAP = {"overweight": 0.55, "neutral": 0.30, "underweight": 0.15}
DISPLAY_MAP = {"overweight": "优先", "neutral": "适度", "underweight": "回避"}
ASSET_KEY_MAP = {"commodity": "gold"}


def _get_cycle_stage_logic(cycle_phase: str, risk_profile: str) -> str:
    phase_desc = {
        "复苏": "经济触底回升，PMI上行、通胀温和，适合超配权益",
        "扩张": "经济高位运行，通胀抬头、货币收紧，适合权益+商品",
        "放缓": "增长动能减弱，通胀仍高，适合增配债券和现金",
        "衰退": "经济下行，通缩压力，适合防御配置（债券+现金）",
    }
    risk_desc = {
        "conservative": "保守型偏好",
        "balanced": "均衡型偏好",
        "aggressive": "积极型偏好",
    }
    base = phase_desc.get(cycle_phase, f"当前处于{cycle_phase}阶段")
    risk = risk_desc.get(risk_profile, risk_profile)
    return f"基于{risk}，结合当前{cycle_phase}周期定位，建议如下配置："


@router.post("/generate")
async def generate_portfolio(request: PortfolioRequest):
    # 1. 获取宏观数据
    fetched = fetch_for_analysis("tianshi", {})
    macro_data = fetched.get("macro_data", {})

    # 1.5. 转换原始指标为 engine 格式
    transformed = transform_indicators_to_macro_data({
        "pmi": macro_data.get("pmi", 50.0),
        "ppi": macro_data.get("ppi", 0.0),
        "fixed_asset_investment": macro_data.get("fixed_asset_investment", 4.0),
        "new_start_area": macro_data.get("new_start_area", 0.0),
    })

    # 2. 判断周期
    cycle_phase, confidence, reasoning = determine_economic_cycle(transformed)

    # 3. 获取基础配置
    base = get_asset_allocation(cycle_phase)

    # 4. 风险偏好调整
    adjust = RISK_ADJUST.get(request.risk_profile, {})
    allocation = {**base, **adjust}

    # 5. 组装前端输出（commodity -> gold 映射）
    result_allocation = {}
    for key, weight in allocation.items():
        display_key = ASSET_KEY_MAP.get(key, key)
        result_allocation[display_key] = {
            "value": VALUE_MAP.get(weight, 0.30),
            "locked": False,
            "display": DISPLAY_MAP.get(weight, "适度"),
        }

    # 6. 策略逻辑
    strategy_logic = _get_cycle_stage_logic(cycle_phase, request.risk_profile)

    return {
        "code": 0,
        "data": {
            "strategy": {
                "logic": strategy_logic,
                "allocation": result_allocation,
            },
            "tactics": {
                "logic": f"基于您熟悉的行业（{', '.join(request.familiar_industries)}），结合行业周期阶段进行个股选择。",
                "targets": {"locked": False},
            },
            "cycle_context": {
                "phase": cycle_phase,
                "confidence": confidence,
                "reasoning": reasoning,
            },
            "requires_subscription": True,
        },
    }
