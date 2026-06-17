"""
人和层：商业模式 + 基金风格分类器

按 PROJECT_INVENTORY.md 需求 4.1-4.2 实现。
"""

from typing import Dict, List, Optional, Tuple


# ── 商业模式分类 ──────────────────────────────────────────────

BUSINESS_MODELS = {
    "SaaS": {
        "keywords": ["SaaS", "软件即服务", "云服务", "订阅", "年费", "月费"],
        "metrics": ["ARR", "MRR", "churn_rate", "LTV", "CAC"],
        "valuation_methods": ["PS", "EV/ARR", "DCF"],
        "description": "订阅制软件服务，收入可预测性强",
    },
    "平台": {
        "keywords": ["平台", "电商", "撮合", "佣金", "交易量", "GMV"],
        "metrics": ["GMV", "take_rate", "活跃用户", "复购率"],
        "valuation_methods": ["PS", "EV/GMV", "DCF"],
        "description": "双边/多边市场平台，网络效应驱动",
    },
    "制造": {
        "keywords": ["制造", "生产", "工厂", "产能", "工业"],
        "metrics": ["产能利用率", "毛利率", "存货周转", "ROIC"],
        "valuation_methods": ["PE", "PB", "EV/EBITDA"],
        "description": "实体生产制造，重资产运营",
    },
    "银行": {
        "keywords": ["银行", "信贷", "存款", "贷款", "息差", "NIM"],
        "metrics": ["NIM", "不良率", "拨备覆盖率", "资本充足率"],
        "valuation_methods": ["PB", "PE"],
        "description": "利差收入为主，信用风险管控为核心",
    },
    "消费零售": {
        "keywords": ["零售", "消费品", "品牌", "门店", "快消"],
        "metrics": ["同店增长", "坪效", "存货周转", "客单价"],
        "valuation_methods": ["PE", "EV/EBITDA", "DCF"],
        "description": "面向终端消费者，品牌和渠道驱动",
    },
    "医药": {
        "keywords": ["医药", "生物", "创新药", "医疗器械", "CXO"],
        "metrics": ["管线价值", "研发费用率", "获批数量", "专利"],
        "valuation_methods": ["PE", "DCF", "rNPV"],
        "description": "研发驱动，专利保护和管线价值为核心",
    },
    "能源资源": {
        "keywords": ["能源", "石油", "煤炭", "电力", "新能源"],
        "metrics": ["产能", "资源储量", "开采成本", "价格弹性"],
        "valuation_methods": ["PE", "EV/EBITDA", "NAV"],
        "description": "资源禀赋驱动，价格周期性强",
    },
    "金融科技": {
        "keywords": ["金融科技", "支付", "网贷", "数字银行", "保险科技"],
        "metrics": ["交易量", "用户规模", "风险损失率", "技术投入"],
        "valuation_methods": ["PS", "PE", "DCF"],
        "description": "技术赋能金融服务，监管敏感度高",
    },
}


def classify_business_model(
    company_description: str,
    industry: Optional[str] = None,
    revenue_model: Optional[str] = None,
) -> Dict:
    """
    对公司进行商业模式分类

    Args:
        company_description: 公司业务描述
        industry: 所属行业（可选）
        revenue_model: 收入模式（可选）

    Returns:
        分类结果
    """
    text = f"{industry or ''} {company_description} {revenue_model or ''}"

    matches = []
    for model_id, config in BUSINESS_MODELS.items():
        score = 0
        matched_kw = []
        for kw in config["keywords"]:
            if kw in text:
                score += 20
                matched_kw.append(kw)

        if score > 0:
            matches.append({
                "model_id": model_id,
                "model_name": model_id,
                "description": config["description"],
                "confidence": min(score / 100, 0.95),
                "matched_keywords": matched_kw,
                "valuation_methods": config["valuation_methods"],
                "key_metrics": config["metrics"],
            })

    matches.sort(key=lambda m: m["confidence"], reverse=True)

    if not matches:
        return {
            "model_id": "通用",
            "model_name": "通用企业",
            "confidence": 0.3,
            "description": "未匹配到特定商业模式，按通用企业处理",
            "valuation_methods": ["PE", "PB"],
            "key_metrics": ["营收增速", "净利润", "ROE"],
        }

    return matches[0]


# ── 基金风格分类 ──────────────────────────────────────────────

FUND_STYLES = {
    "成长型": {
        "conditions": {
            "pe_quantile": lambda v: v is not None and v > 60,
            "holding_style": lambda v: v in ("成长", "成长价值"),
            "turnover_rate": lambda v: v is not None and v > 200,
        },
        "description": "高估值 + 高换手，追逐高增长标的",
    },
    "价值型": {
        "conditions": {
            "pe_quantile": lambda v: v is not None and v < 40,
            "dividend_yield": lambda v: v is not None and v > 2,
            "holding_style": lambda v: v in ("价值", "深度价值"),
        },
        "description": "低估值 + 高股息，追求安全边际",
    },
    "平衡型": {
        "conditions": {
            "pe_quantile": lambda v: v is not None and 40 <= v <= 60,
            "bond_allocation": lambda v: v is not None and 20 <= v <= 80,
        },
        "description": "股债均衡配置，攻守兼备",
    },
    "行业主题型": {
        "conditions": {
            "sector_concentration": lambda v: v is not None and v > 50,
            "holding_style": lambda v: v in ("行业", "主题"),
        },
        "description": "集中持仓单一行业或主题",
    },
    "指数型": {
        "conditions": {
            "tracking_error": lambda v: v is not None and v < 2,
            "holding_count": lambda v: v is not None and v > 50,
        },
        "description": "被动跟踪指数，费率低",
    },
    "量化型": {
        "conditions": {
            "holding_count": lambda v: v is not None and v > 100,
            "turnover_rate": lambda v: v is not None and v > 500,
        },
        "description": "程序化交易，持仓分散，高换手",
    },
}


def classify_fund_style(fund_data: Dict) -> Dict:
    """
    对基金进行风格分类

    Args:
        fund_data: 基金数据，包含风格相关指标

    Returns:
        风格分类结果
    """
    scores = {}
    for style, config in FUND_STYLES.items():
        match_count = 0
        total = len(config["conditions"])
        matched_conditions = []

        for cond_key, condition in config["conditions"].items():
            value = fund_data.get(cond_key)
            try:
                if condition(value):
                    match_count += 1
                    matched_conditions.append(cond_key)
            except (TypeError, ValueError):
                pass

        if total > 0 and match_count > 0:
            scores[style] = {
                "score": match_count / total,
                "matched": match_count,
                "total": total,
                "matched_conditions": matched_conditions,
            }

    if not scores:
        return {
            "primary_style": "未分类",
            "confidence": 0.2,
            "description": "数据不足以判断基金风格",
            "all_scores": {},
        }

    best = max(scores, key=lambda s: scores[s]["score"])
    best_score = scores[best]["score"]

    # 次要风格（得分 > 0.5 且不是最优的）
    secondary = [
        {"style": s, "score": v["score"]}
        for s, v in scores.items()
        if s != best and v["score"] >= 0.4
    ]
    secondary.sort(key=lambda x: x["score"], reverse=True)

    confidence = best_score * 0.9 if best_score >= 0.75 else best_score * 0.7

    return {
        "primary_style": best,
        "confidence": min(confidence + 0.1, 0.95),
        "description": FUND_STYLES[best]["description"],
        "all_scores": {s: v["score"] for s, v in scores.items()},
        "secondary_styles": secondary[:2],
    }


# ── 财务健康评分 ──────────────────────────────────────────────

def score_financial_health(financials: Dict) -> Dict:
    """
    四层财务健康评分

    Args:
        financials: 财务数据（利润表/资产负债表/现金流）

    Returns:
        健康评分
    """
    scores = {}

    # 1. 盈利能力
    profit_score = 0
    if financials.get("gross_margin") is not None:
        gm = financials["gross_margin"]
        profit_score += 30 if gm > 60 else 20 if gm > 40 else 10 if gm > 20 else 5
    if financials.get("net_margin") is not None:
        nm = financials["net_margin"]
        profit_score += 30 if nm > 20 else 20 if nm > 10 else 10 if nm > 5 else 5
    if financials.get("roe") is not None:
        roe = financials["roe"]
        profit_score += 40 if roe > 20 else 30 if roe > 15 else 15 if roe > 8 else 5

    scores["profitability"] = min(profit_score, 100)

    # 2. 偿债能力
    debt_score = 0
    if financials.get("debt_ratio") is not None:
        dr = financials["debt_ratio"]
        debt_score += 40 if dr < 30 else 30 if dr < 50 else 15 if dr < 70 else 5
    if financials.get("current_ratio") is not None:
        cr = financials["current_ratio"]
        debt_score += 30 if cr > 2 else 20 if cr > 1.5 else 10 if cr > 1 else 5
    if financials.get("interest_coverage") is not None:
        ic = financials["interest_coverage"]
        debt_score += 30 if ic > 10 else 20 if ic > 5 else 10 if ic > 2 else 5

    scores["debt_safety"] = min(debt_score, 100)

    # 3. 运营效率
    ops_score = 0
    if financials.get("inventory_turnover") is not None:
        ops_score += 30 if financials["inventory_turnover"] > 5 else 20
    if financials.get("asset_turnover") is not None:
        ops_score += 35 if financials["asset_turnover"] > 1 else 20
    if financials.get("receivable_turnover") is not None:
        ops_score += 35 if financials["receivable_turnover"] > 10 else 20

    scores["operational_efficiency"] = min(ops_score, 100)

    # 4. 成长性
    growth_score = 0
    if financials.get("revenue_growth") is not None:
        rg = financials["revenue_growth"]
        growth_score += 35 if rg > 30 else 25 if rg > 15 else 15 if rg > 5 else 5
    if financials.get("profit_growth") is not None:
        pg = financials["profit_growth"]
        growth_score += 35 if pg > 30 else 25 if pg > 15 else 15 if pg > 5 else 5
    if financials.get("cash_flow_growth") is not None:
        growth_score += 30 if financials["cash_flow_growth"] > 0 else 10

    scores["growth"] = min(growth_score, 100)

    # 综合得分
    weights = {"profitability": 0.35, "debt_safety": 0.25, "operational_efficiency": 0.20, "growth": 0.20}
    total = sum(scores[k] * weights[k] for k in weights if k in scores)

    if total >= 75:
        rating = "优秀"
    elif total >= 55:
        rating = "良好"
    elif total >= 35:
        rating = "一般"
    else:
        rating = "较差"

    return {
        "total_score": round(total, 1),
        "rating": rating,
        "dimensions": scores,
        "weights": weights,
        "confidence": 0.75 if all(k in financials for k in ["gross_margin", "net_margin", "roe"]) else 0.5,
    }
