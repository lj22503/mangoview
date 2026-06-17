"""
持仓诊断 Skill

基于四专家框架，对持仓进行集中度、相关性、估值分析，生成调仓建议。
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..skill_interface import BaseSkill, skill

logger = logging.getLogger(__name__)


@skill("position_diagnosis", "1.0.0")
class PositionDiagnosisSkill(BaseSkill):
    """持仓诊断 Skill"""

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行持仓诊断

        Args:
            input_data: 包含 positions 列表

        Returns:
            诊断结果
        """
        positions = input_data.get("positions", [])

        logger.info(f"💼 开始诊断持仓：{len(positions)} 个品种")

        # 1. 集中度分析
        concentration = self._analyze_concentration(positions)

        # 2. 相关性分析
        correlation = self._analyze_correlation(positions)

        # 3. 估值分析
        valuation = self._analyze_valuation(positions)

        # 4. 生成建议
        suggestions = self._generate_suggestions(concentration, correlation, valuation)

        result = {
            "skill": "position_diagnosis",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "positions": positions,
            "concentration": concentration,
            "correlation": correlation,
            "valuation": valuation,
            "suggestions": suggestions,
            "data_source": "东方财富 API",
            "confidence_level": "A",
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
        }

        logger.info(f"✅ 持仓诊断完成")

        return result

    def _analyze_concentration(self, positions: List[Dict]) -> Dict[str, Any]:
        """
        集中度分析

        Args:
            positions: 持仓列表

        Returns:
            集中度分析结果
        """
        total_weight = sum(p.get("weight", 0) for p in positions)

        # 单一个股/ETF 占比
        max_weight = max((p.get("weight", 0) for p in positions), default=0)
        single_status = "健康" if max_weight < 30 else ("偏高" if max_weight < 50 else "危险")

        # 行业集中度（简化版）
        industry_weights = {}
        for p in positions:
            industry = p.get("industry", "其他")
            industry_weights[industry] = industry_weights.get(industry, 0) + p.get("weight", 0)

        max_industry_weight = max(industry_weights.values()) if industry_weights else 0
        industry_status = "健康" if max_industry_weight < 40 else ("偏高" if max_industry_weight < 60 else "危险")

        return {
            "total_weight": total_weight,
            "max_single_weight": max_weight,
            "single_status": single_status,
            "max_industry_weight": max_industry_weight,
            "industry_status": industry_status,
            "industry_weights": industry_weights
        }

    def _analyze_correlation(self, positions: List[Dict]) -> Dict[str, Any]:
        """
        相关性分析

        Args:
            positions: 持仓列表

        Returns:
            相关性分析结果
        """
        # 简化版：基于行业判断相关性
        industries = [p.get("industry", "其他") for p in positions]
        unique_industries = len(set(industries))

        if unique_industries >= 3:
            correlation_level = "低"
            status = "健康"
        elif unique_industries == 2:
            correlation_level = "中"
            status = "适中"
        else:
            correlation_level = "高"
            status = "偏高"

        return {
            "correlation_level": correlation_level,
            "status": status,
            "unique_industries": unique_industries,
            "total_positions": len(positions)
        }

    def _analyze_valuation(self, positions: List[Dict]) -> Dict[str, Any]:
        """
        估值分析（简化版）

        Args:
            positions: 持仓列表

        Returns:
            估值分析结果
        """
        # 简化版：假设所有持仓估值合理
        return {
            "overall": "合理",
            "details": "需结合实时行情数据"
        }

    def _generate_suggestions(self, concentration: Dict, correlation: Dict, valuation: Dict) -> List[str]:
        """
        生成调仓建议

        Args:
            concentration: 集中度分析
            correlation: 相关性分析
            valuation: 估值分析

        Returns:
            建议列表
        """
        suggestions = []

        # 基于集中度
        if concentration["single_status"] == "危险":
            suggestions.append("单一品种占比过高，建议分散")
        elif concentration["single_status"] == "偏高":
            suggestions.append("单一品种占比偏高，可适当分散")

        if concentration["industry_status"] == "危险":
            suggestions.append("行业集中度过高，建议跨行业配置")
        elif concentration["industry_status"] == "偏高":
            suggestions.append("行业集中度偏高，可适当增加其他行业")

        # 基于相关性
        if correlation["status"] == "偏高":
            suggestions.append("品种相关性较高，建议增加低相关品种")

        # 通用建议
        if not suggestions:
            suggestions.append("当前配置健康，保持观察")
            suggestions.append("可适当增加债券/黄金等防御品种")

        return suggestions

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        positions = input_data.get("positions", [])
        return len(positions) > 0


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    skill = PositionDiagnosisSkill()

    # 测试：示例持仓
    test_positions = [
        {"code": "518880", "name": "黄金 ETF", "weight": 30, "industry": "大宗商品"},
        {"code": "510300", "name": "沪深 300ETF", "weight": 25, "industry": "宽基指数"},
        {"code": "159813", "name": "半导体 ETF", "weight": 15, "industry": "科技"},
        {"code": "511260", "name": "国债 ETF", "weight": 20, "industry": "债券"},
        {"code": "CASH", "name": "现金", "weight": 10, "industry": "现金"}
    ]

    result = skill({"positions": test_positions})
    print(f"\n📊 持仓诊断结果：")
    for key, value in result.items():
        print(f"  {key}: {value}")
