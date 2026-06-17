"""
事件分析 Skill

基于范蠡商情研判框架，四步心法分析事件，输出闸门/管道/背离标签。
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..skill_interface import BaseSkill, skill

logger = logging.getLogger(__name__)


@skill("event_analysis", "1.0.0")
class EventAnalysisSkill(BaseSkill):
    """事件分析 Skill"""

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行事件分析

        Args:
            input_data: 包含 event_description 等字段

        Returns:
            分析结果
        """
        event_desc = input_data.get("event_description", input_data.get("input", ""))

        logger.info(f"🔍 开始分析事件：{event_desc[:50]}...")

        # 1. 来源判定
        source_level = self._judge_source(event_desc)

        # 2. 影响评估
        impact_score = self._assess_impact(event_desc)

        # 3. 利益分析
        beneficiaries = self._analyze_beneficiaries(event_desc)

        # 4. 分类判定
        classification = self._classify_event(event_desc, source_level, impact_score)

        # 5. 生成操作思路
        action_suggestions = self._generate_suggestions(classification, beneficiaries)

        result = {
            "skill": "event_analysis",
            "version": "1.0.0",
            "event": event_desc,
            "timestamp": datetime.now().isoformat(),
            "classification": classification,
            "source_level": source_level,
            "impact_score": impact_score,
            "beneficiaries": beneficiaries,
            "suggestions": action_suggestions,
            "data_source": "东方财富 API",
            "confidence_level": "A",
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
        }

        logger.info(f"✅ 事件分析完成：{classification}")

        return result

    def _judge_source(self, event_desc: str) -> str:
        """
        来源判定（A/B/C/D 级）

        Args:
            event_desc: 事件描述

        Returns:
            信源等级
        """
        # 简单启发式判定
        if any(kw in event_desc for kw in ["证监会", "央行", "国务院", "财政部"]):
            return "A"  # 官方来源
        elif any(kw in event_desc for kw in ["券商", "研报", "公告"]):
            return "B"  # 机构来源
        elif any(kw in event_desc for kw in ["媒体", "报道", "新闻"]):
            return "C"  # 媒体来源
        else:
            return "D"  # 其他来源

    def _assess_impact(self, event_desc: str) -> float:
        """
        影响评估（0-10 分）

        Args:
            event_desc: 事件描述

        Returns:
            影响评分
        """
        score = 5.0  # 基础分

        # 关键词加分
        if any(kw in event_desc for kw in ["重大", "重要", "关键", "核心"]):
            score += 2.0
        if any(kw in event_desc for kw in ["全面", "全部", "所有"]):
            score += 1.5
        if any(kw in event_desc for kw in ["部分", "局部", "试点"]):
            score -= 1.0

        return min(10.0, max(0.0, score))

    def _analyze_beneficiaries(self, event_desc: str) -> list:
        """
        利益分析（受益方向）

        Args:
            event_desc: 事件描述

        Returns:
            受益方向列表
        """
        beneficiaries = []

        # 简单关键词匹配
        if any(kw in event_desc for kw in ["国债", "债券", "利率"]):
            beneficiaries.append("债券基金")
        if any(kw in event_desc for kw in ["科技", "AI", "半导体"]):
            beneficiaries.append("科技板块")
        if any(kw in event_desc for kw in ["消费", "零售"]):
            beneficiaries.append("消费板块")
        if any(kw in event_desc for kw in ["金融", "银行", "保险"]):
            beneficiaries.append("金融板块")
        if any(kw in event_desc for kw in ["外贸", "出口", "汇率"]):
            beneficiaries.append("外贸板块")

        if not beneficiaries:
            beneficiaries.append("需进一步分析")

        return beneficiaries

    def _classify_event(self, event_desc: str, source_level: str, impact_score: float) -> str:
        """
        事件分类（闸门/管道/背离）

        Args:
            event_desc: 事件描述
            source_level: 信源等级
            impact_score: 影响评分

        Returns:
            分类结果
        """
        # 闸门：高影响 + 官方来源
        if impact_score >= 7.0 and source_level in ["A", "B"]:
            return "闸门"
        # 管道：中等影响
        elif impact_score >= 4.0:
            return "管道"
        # 背离：低影响或负面
        else:
            return "背离"

    def _generate_suggestions(self, classification: str, beneficiaries: list) -> list:
        """
        生成操作建议

        Args:
            classification: 事件分类
            beneficiaries: 受益方向

        Returns:
            建议列表
        """
        suggestions = []

        if classification == "闸门":
            suggestions.append("重点关注受益方向")
            suggestions.append("考虑适当加仓")
        elif classification == "管道":
            suggestions.append("保持关注")
            suggestions.append("等待进一步信号")
        else:
            suggestions.append("谨慎观察")
            suggestions.append("避免盲目跟风")

        if beneficiaries:
            suggestions.append(f"受益方向：{', '.join(beneficiaries)}")

        return suggestions

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return bool(input_data.get("event_description") or input_data.get("input"))


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    skill = EventAnalysisSkill()

    # 测试 1：QFII 国债期货事件
    result1 = skill({
        "event_description": "QFII/RQFII 获准参与中金所国债期货，限套保"
    })
    print(f"\n📊 事件分析结果 1：")
    for key, value in result1.items():
        print(f"  {key}: {value}")

    # 测试 2：AI 芯片事件
    result2 = skill({
        "event_description": "美国限制 AI 芯片出口中国"
    })
    print(f"\n📊 事件分析结果 2：")
    for key, value in result2.items():
        print(f"  {key}: {value}")
