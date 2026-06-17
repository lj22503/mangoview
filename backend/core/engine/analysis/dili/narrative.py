"""
地利层：叙事识别

识别当前市场在交易的核心叙事。
按 PROJECT_INVENTORY.md 需求 3.2 的叙事识别规则实现。
"""

from typing import Dict, List, Optional, Tuple


# ── 常见叙事模板库 ────────────────────────────────────────────

NARRATIVE_TEMPLATES = [
    {
        "id": "rate_cut",
        "name": "降息预期",
        "keywords": ["降息", "利率", "宽松", "流动性"],
        "related_assets": ["债券", "成长股", "科技"],
    },
    {
        "id": "inflation",
        "name": "通胀交易",
        "keywords": ["通胀", "CPI", "PPI", "物价"],
        "related_assets": ["商品", "能源", "黄金"],
    },
    {
        "id": "recovery",
        "name": "复苏交易",
        "keywords": ["复苏", "PMI", "消费", "补库"],
        "related_assets": ["周期股", "消费", "工业"],
    },
    {
        "id": "geopolitical",
        "name": "地缘风险",
        "keywords": ["地缘", "冲突", "制裁", "关税", "贸易"],
        "related_assets": ["黄金", "能源", "军工", "避险"],
    },
    {
        "id": "tech_revolution",
        "name": "科技革命",
        "keywords": ["AI", "人工智能", "大模型", "半导体", "芯片", "机器人"],
        "related_assets": ["科技股", "半导体", "AI 概念"],
    },
    {
        "id": "regulatory",
        "name": "监管变化",
        "keywords": ["监管", "政策", "法规", "合规", "反垄断"],
        "related_assets": ["受监管行业", "金融"],
    },
    {
        "id": "deleveraging",
        "name": "去杠杆",
        "keywords": ["去杠杆", "债务", "违约", "信用"],
        "related_assets": ["债券", "银行", "高股息"],
    },
    {
        "id": "china_stimulus",
        "name": "中国刺激",
        "keywords": ["刺激", "财政", "专项债", "基建"],
        "related_assets": ["A股", "商品", "基建"],
    },
]


def identify_narrative(
    event_description: str,
    top_assets: Optional[List[str]] = None,
    fund_flow: Optional[Dict] = None,
) -> List[Dict]:
    """
    识别事件关联的叙事

    Args:
        event_description: 事件描述文本
        top_assets: 近期涨幅最大的资产列表
        fund_flow: 资金流向数据

    Returns:
        匹配的叙事列表（按置信度排序，最多 2 个）
    """
    matches = []

    for template in NARRATIVE_TEMPLATES:
        score = 0
        matched_keywords = []

        # 关键词匹配
        for kw in template["keywords"]:
            if kw in event_description:
                score += 20
                matched_keywords.append(kw)

        # 资产匹配
        if top_assets:
            for asset in top_assets:
                for related in template["related_assets"]:
                    if related in asset or any(kw in asset for kw in template["keywords"]):
                        score += 15
                        break

        if score > 0:
            matches.append({
                "narrative_id": template["id"],
                "narrative_name": template["name"],
                "confidence": min(score / 100, 0.95),
                "matched_keywords": matched_keywords,
                "related_assets": template["related_assets"],
            })

    # 按置信度排序，取 top 2
    matches.sort(key=lambda m: m["confidence"], reverse=True)
    return matches[:2]


# ── 事件类型分类 ──────────────────────────────────────────────

def classify_event_type(event_description: str) -> Dict:
    """
    将事件分类为闸门/管道/背离

    闸门：规则改变
    管道：资金流向
    背离：价格与价值的偏差
    """
    gate_keywords = ["规则", "政策", "准入", "获准", "批准", "开放", "禁止", "限制"]
    pipe_keywords = ["资金", "流入", "流出", "北向", "南向", "成交", "放量"]
    deviation_keywords = ["背离", "偏离", "泡沫", "低估", "高估", "溢价", "折价"]

    scores = {
        "gate": sum(1 for kw in gate_keywords if kw in event_description),
        "pipe": sum(1 for kw in pipe_keywords if kw in event_description),
        "deviation": sum(1 for kw in deviation_keywords if kw in event_description),
    }

    total = sum(scores.values()) or 1
    primary = max(scores, key=scores.get)

    return {
        "classification": primary,
        "scores": scores,
        "is_gate": scores["gate"] > 0,
        "is_pipe": scores["pipe"] > 0,
        "is_deviation": scores["deviation"] > 0,
        "confidence": max(scores.values()) / total,
    }
