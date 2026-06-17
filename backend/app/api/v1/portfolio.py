from fastapi import APIRouter
from ...models.schemas import PortfolioRequest

router = APIRouter(prefix="/v1/portfolio", tags=["portfolio"])


@router.post("/generate")
async def generate_portfolio(request: PortfolioRequest):
    """生成配置方案（展示逻辑，锁定结果）"""

    risk = request.risk_profile
    amount = request.investable_amount
    industries = request.familiar_industries

    # 战略配置逻辑（展示）
    if risk == "conservative":
        equity_ratio = 0.4
        bond_ratio = 0.4
        gold_ratio = 0.1
        cash_ratio = 0.1
        strategy_logic = f"基于您的保守型偏好，结合当前宏观周期定位，建议股债均衡配置，降低股市波动影响。"
    elif risk == "aggressive":
        equity_ratio = 0.7
        bond_ratio = 0.2
        gold_ratio = 0.05
        cash_ratio = 0.05
        strategy_logic = f"基于您的积极型偏好，结合当前宏观周期定位，建议超配权益资产，把握周期复苏机会。"
    else:
        equity_ratio = 0.55
        bond_ratio = 0.3
        gold_ratio = 0.05
        cash_ratio = 0.1
        strategy_logic = f"基于您的平衡型偏好，结合当前宏观周期定位，建议股债平衡，略偏权益。"

    # 具体比例锁定
    return {
        "code": 0,
        "data": {
            "strategy": {
                "logic": strategy_logic,
                "allocation": {
                    "equity": {"value": equity_ratio, "locked": True, "display": f"{int(equity_ratio * 100)}%"},
                    "bond": {"value": bond_ratio, "locked": True, "display": f"{int(bond_ratio * 100)}%"},
                    "gold": {"value": gold_ratio, "locked": True, "display": f"{int(gold_ratio * 100)}%"},
                    "cash": {"value": cash_ratio, "locked": True, "display": f"{int(cash_ratio * 100)}%"}
                }
            },
            "tactics": {
                "logic": f"基于您熟悉的行业（{', '.join(industries)}），结合行业周期阶段进行个股选择。",
                "targets": {"locked": True}
            },
            "requires_subscription": True
        }
    }