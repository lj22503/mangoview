from fastapi import APIRouter
from ...models.schemas import CyclePositionRequest, CyclePositionResponse

router = APIRouter(prefix="/v1/tools", tags=["tools"])


@router.post("/cycle-locator")
async def cycle_locator(request: CyclePositionRequest):
    """周期定位器 - 基于达利欧债务周期理论"""

    pmi = request.indicators.get("pmi", 50.0)
    ppi = request.indicators.get("ppi", -2.0)
    fixed_asset = request.indicators.get("fixed_asset_investment", 4.0)
    new_start = request.indicators.get("new_start_area", -5.0)

    # 基钦周期判断（短周期，约 40 个月）
    if pmi > 50 and ppi > 0:
        kitchin = "复苏早期"
    elif pmi > 50 and ppi < 0:
        kitchin = "复苏晚期"
    elif pmi < 50 and ppi < 0:
        kitchin = "衰退期"
    else:
        kitchin = "衰退后期"

    # 朱格拉周期判断（中周期，约 8-10 年）
    if fixed_asset > 5:
        juglar = "扩张期"
    elif fixed_asset > 2:
        juglar = "平稳期"
    else:
        juglar = "收缩期"

    # 库兹涅茨周期（建筑周期，约 15-20 年）
    if new_start > 0:
        kuznets = "上升期"
    else:
        kuznets = "下降期"

    # 康波周期（技术创新周期，约 50 年）- 简化判断
    kuznets_cycle = "萧条期"  # 默认萧条期

    # 历史对照
    historical_comparison = [
        {"period": "2012-2013", "similarity": 0.78},
        {"period": "2015-2016", "similarity": 0.65}
    ]

    # 配置建议（简化版）
    if kitchin in ["复苏早期", "复苏晚期"]:
        allocation = {"equity": "适度", "bond": "优先", "gold": "适度", "cash": "回避"}
    elif kitchin == "衰退期":
        allocation = {"equity": "回避", "bond": "优先", "gold": "适度", "cash": "优先"}
    else:
        allocation = {"equity": "观察", "bond": "适度", "gold": "优先", "cash": "优先"}

    return {
        "code": 0,
        "data": {
            "cycle_position": {
                "kitchin": kitchin,
                "juglar": juglar,
                "kuznets": kuznets,
                "kondratieff": kuznets_cycle
            },
            "historical_comparison": historical_comparison,
            "allocation_suggestion": allocation
        }
    }