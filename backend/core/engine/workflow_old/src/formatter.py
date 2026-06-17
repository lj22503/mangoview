"""
Output Formatter - 输出格式化器

职责：
1. 格式化工作流输出
2. 添加署名信息（Powered by Mangofolio）
3. 添加免责声明
4. 支持多平台格式（雪球/公众号/微信）
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OutputFormatter:
    """输出格式化器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化格式化器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.signature = {
            "top": "Powered by Mangofolio",
            "bottom": "方法论来源：范蠡商情研判 + 四专家框架 | 版本：v1.0 | 创作者：燃冰",
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。请独立判断并自行承担风险。"
        }

    def format(self, results: List[Dict], user_input: str, platform: str = "default") -> str:
        """
        格式化输出

        Args:
            results: Skill 执行结果列表
            user_input: 用户输入
            platform: 目标平台（default/xueqiu/wechat）

        Returns:
            格式化后的文本
        """
        logger.info(f"📝 格式化输出，平台：{platform}")

        # 1. 根据平台选择模板
        if platform == "xueqiu":
            return self._format_xueqiu(results, user_input)
        elif platform == "wechat":
            return self._format_wechat(results, user_input)
        else:
            return self._format_default(results, user_input)

    def _format_default(self, results: List[Dict], user_input: str) -> str:
        """
        默认格式

        Args:
            results: Skill 执行结果列表
            user_input: 用户输入

        Returns:
            格式化文本
        """
        output = []

        # 顶部署名
        output.append(f"# {self._generate_title(user_input)}")
        output.append("")
        output.append(f"**{self.signature['top']}**")
        output.append("")
        output.append("---")
        output.append("")

        # 内容
        for result in results:
            skill_name = result.get("skill", "未知")
            data = result.get("data", {})

            output.append(f"## {self._get_skill_title(skill_name)}")
            output.append("")
            output.append(self._format_skill_data(skill_name, data))
            output.append("")

        # 底部署名
        output.append("---")
        output.append("")
        output.append(f"{self.signature['bottom']}")
        output.append("")
        output.append(f"**免责声明：** {self.signature['disclaimer']}")
        output.append("")
        output.append("---")
        output.append("")
        output.append("*Mangofolio — 种得对，等得久*")

        return "\n".join(output)

    def _format_xueqiu(self, results: List[Dict], user_input: str) -> str:
        """
        雪球格式

        Args:
            results: Skill 执行结果列表
            user_input: 用户输入

        Returns:
            格式化文本
        """
        output = []

        # 标题
        title = self._generate_title(user_input)
        output.append(f"# {title}")
        output.append("")

        # 顶部署名
        output.append(f"> Powered by Mangofolio")
        output.append("")

        # 内容（短句、段落留白）
        for result in results:
            skill_name = result.get("skill", "未知")
            data = result.get("data", {})

            output.append(f"## {self._get_skill_title(skill_name)}")
            output.append("")
            output.append(self._format_skill_data_xueqiu(skill_name, data))
            output.append("")

        # 底部署名
        output.append("---")
        output.append("")
        output.append(f"{self.signature['bottom']}")
        output.append("")
        output.append(f"**免责声明：** {self.signature['disclaimer']}")
        output.append("")
        output.append("*Mangofolio — 种得对，等得久*")

        return "\n".join(output)

    def _format_wechat(self, results: List[Dict], user_input: str) -> str:
        """
        公众号格式

        Args:
            results: Skill 执行结果列表
            user_input: 用户输入

        Returns:
            格式化文本
        """
        output = []

        # 标题
        title = self._generate_title(user_input)
        output.append(f"# {title}")
        output.append("")

        # 顶部署名
        output.append(f"> Powered by Mangofolio")
        output.append("")

        # 内容（对谈体、短句）
        for result in results:
            skill_name = result.get("skill", "未知")
            data = result.get("data", {})

            output.append(f"## {self._get_skill_title(skill_name)}")
            output.append("")
            output.append(self._format_skill_data_wechat(skill_name, data))
            output.append("")

        # 底部署名
        output.append("---")
        output.append("")
        output.append(f"{self.signature['bottom']}")
        output.append("")
        output.append(f"**免责声明：** {self.signature['disclaimer']}")
        output.append("")
        output.append("*Mangofolio — 种得对，等得久*")

        return "\n".join(output)

    def _generate_title(self, user_input: str) -> str:
        """
        生成标题

        Args:
            user_input: 用户输入

        Returns:
            标题
        """
        # 简单启发式生成
        if "事件" in user_input or "分析" in user_input:
            return f"关于{user_input[:20]}的深度分析"
        elif "持仓" in user_input or "诊断" in user_input:
            return "持仓诊断报告"
        elif "写" in user_input or "文章" in user_input:
            return f"{user_input[:20]}..."
        else:
            return "Mangofolio 分析报告"

    def _get_skill_title(self, skill_name: str) -> str:
        """
        获取 Skill 标题

        Args:
            skill_name: Skill 名称

        Returns:
            标题
        """
        titles = {
            "personality_test": "🎯 投资人格测试",
            "event_analysis": "🔍 事件分析",
            "position_diagnosis": "💼 持仓诊断",
            "content_generation": "📝 内容生成"
        }
        return titles.get(skill_name, skill_name)

    def _format_skill_data(self, skill_name: str, data: Dict) -> str:
        """
        格式化 Skill 数据（默认格式）

        Args:
            skill_name: Skill 名称
            data: Skill 数据

        Returns:
            格式化文本
        """
        if skill_name == "personality_test":
            return f"**投资人格**：{data.get('result', '未知')}\n**风险偏好**：{data.get('risk_profile', '未知')}\n**置信度**：{data.get('confidence', 0):.0%}"
        elif skill_name == "event_analysis":
            return f"**事件**：{data.get('event', '未知')}\n**分类**：{data.get('classification', '未知')}\n**评分**：{data.get('score', 0)}/10\n**受益方向**：{', '.join(data.get('beneficiaries', []))}\n**数据来源**：{data.get('data_source', '未知')} ({data.get('confidence_level', 'C')})"
        elif skill_name == "position_diagnosis":
            return f"**集中度**：{data.get('concentration', '未知')}\n**建议**：{', '.join(data.get('suggestions', []))}"
        elif skill_name == "content_generation":
            return f"**标题**：{data.get('title', '未知')}\n**字数**：{data.get('word_count', 0)} 字\n**平台**：{data.get('platform', '未知')}"
        else:
            return json.dumps(data, ensure_ascii=False, indent=2)

    def _format_skill_data_xueqiu(self, skill_name: str, data: Dict) -> str:
        """
        格式化 Skill 数据（雪球格式）

        Args:
            skill_name: Skill 名称
            data: Skill 数据

        Returns:
            格式化文本
        """
        # 雪球格式：短句、段落留白
        return self._format_skill_data(skill_name, data)

    def _format_skill_data_wechat(self, skill_name: str, data: Dict) -> str:
        """
        格式化 Skill 数据（公众号格式）

        Args:
            skill_name: Skill 名称
            data: Skill 数据

        Returns:
            格式化文本
        """
        # 公众号格式：对谈体、短句
        return self._format_skill_data(skill_name, data)


# 便捷函数
def create_formatter(config: Optional[Dict] = None) -> OutputFormatter:
    """创建格式化器实例"""
    return OutputFormatter(config)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    formatter = create_formatter()

    # 测试数据
    test_results = [
        {
            "skill": "personality_test",
            "data": {
                "result": "🐘 大象（价值投资）",
                "risk_profile": "保守",
                "confidence": 0.85
            }
        },
        {
            "skill": "event_analysis",
            "data": {
                "event": "QFII 国债期货事件",
                "classification": "闸门",
                "score": 8.5,
                "beneficiaries": ["券商", "金融 IT"],
                "data_source": "东方财富 API",
                "confidence_level": "A"
            }
        }
    ]

    # 测试格式化
    print("📝 默认格式：")
    print(formatter.format(test_results, "帮我分析一下 QFII 国债期货事件", "default"))

    print("\n\n📝 雪球格式：")
    print(formatter.format(test_results, "帮我分析一下 QFII 国债期货事件", "xueqiu"))
