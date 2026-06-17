"""
Skill Router - Skill 路由器

职责：
1. 根据用户输入（关键词/意图）路由到对应 Skill 链
2. 维护 Skill 链映射表
3. 支持正则匹配和关键词匹配
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillRouter:
    """Skill 路由器"""

    def __init__(self):
        """初始化路由器，加载 Skill 链映射表"""
        self.skill_chains = self._load_skill_chains()
        self.route_history = []

    def _load_skill_chains(self) -> Dict[str, Dict]:
        """
        加载 Skill 链映射表

        Returns:
            Skill 链字典 {场景名：{触发词，Skill 链，描述}}
        """
        return {
            "事件分析": {
                "keywords": ["事件", "分析", "闸门", "管道", "背离", "范蠡"],
                "regex": [r"分析.*事件", r".*闸门.*", r".*管道.*", r".*背离.*"],
                "chain": ["event_analysis"],
                "description": "事件分析工作流"
            },
            "持仓诊断": {
                "keywords": ["持仓", "诊断", "调仓", "组合", "复盘"],
                "regex": [r"诊断.*持仓", r"我的.*组合", r".*调仓.*"],
                "chain": ["position_diagnosis"],
                "description": "持仓诊断工作流"
            },
            "内容生产": {
                "keywords": ["写", "文章", "内容", "发布", "雪球", "公众号"],
                "regex": [r"写.*文章", r".*内容.*", r"发布.*"],
                "chain": ["event_analysis", "content_generation"],
                "description": "内容生产工作流"
            },
            "人格测试": {
                "keywords": ["测试", "人格", "宠物", "投资风格"],
                "regex": [r"测试.*人格", r".*宠物.*", r"投资.*风格"],
                "chain": ["personality_test"],
                "description": "投资人格测试工作流"
            },
            "完整投顾": {
                "keywords": ["投顾", "建议", "配置", "方案", "怎么办"],
                "regex": [r"投顾.*", r".*建议.*", r".*配置.*", r"怎么办"],
                "chain": ["personality_test", "position_diagnosis", "event_analysis"],
                "description": "完整投顾工作流（人格测试 → 持仓诊断 → 事件分析）"
            }
        }

    def route(self, user_input: str) -> List[str]:
        """
        路由用户输入到对应 Skill 链

        Args:
            user_input: 用户输入（自然语言）

        Returns:
            Skill 链列表
        """
        logger.info(f"📍 路由用户输入：{user_input}")

        # 1. 关键词匹配
        matched_scenarios = self._match_keywords(user_input)

        # 2. 正则匹配（优先级更高）
        regex_matches = self._match_regex(user_input)

        # 3. 合并结果（正则匹配优先）
        if regex_matches:
            selected_scenario = regex_matches[0]
        elif matched_scenarios:
            selected_scenario = matched_scenarios[0]
        else:
            # 默认路由到完整投顾
            selected_scenario = "完整投顾"
            logger.warning(f"⚠️ 未匹配到场景，使用默认：{selected_scenario}")

        # 4. 获取 Skill 链
        skill_chain = self.skill_chains[selected_scenario]["chain"]

        # 5. 解析持仓数据（如果是持仓诊断）
        if "position_diagnosis" in skill_chain:
            positions = self._parse_positions(user_input)
            # 将解析结果存储到上下文中
            self._last_positions = positions

        # 6. 记录路由历史
        self.route_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "matched_scenario": selected_scenario,
            "skill_chain": skill_chain
        })

        logger.info(f"✅ 路由到：{selected_scenario} → {skill_chain}")

        return skill_chain

    def _parse_positions(self, user_input: str) -> List[Dict]:
        """
        解析持仓文本

        Args:
            user_input: 用户输入

        Returns:
            持仓列表
        """
        import re

        positions = []

        # 匹配模式：代码 名称 比例%
        # 例如：518880 黄金 ETF 30%, 510300 沪深 300ETF 25%
        pattern = r'(\d+)\s*([^\d,]+?)\s*(\d+)%'
        matches = re.findall(pattern, user_input)

        for code, name, weight in matches:
            positions.append({
                "code": code.strip(),
                "name": name.strip(),
                "weight": int(weight),
                "industry": self._infer_industry(name.strip())
            })

        # 匹配现金
        if "现金" in user_input:
            cash_match = re.search(r'现金\s*(\d+)%', user_input)
            if cash_match:
                positions.append({
                    "code": "CASH",
                    "name": "现金",
                    "weight": int(cash_match.group(1)),
                    "industry": "现金"
                })

        logger.info(f"📊 解析到 {len(positions)} 个持仓")

        return positions

    def _infer_industry(self, name: str) -> str:
        """
        推断行业

        Args:
            name: 品种名称

        Returns:
            行业名称
        """
        if any(kw in name for kw in ["黄金", "白银", "商品"]):
            return "大宗商品"
        elif any(kw in name for kw in ["沪深", "中证", "创业板", "宽基"]):
            return "宽基指数"
        elif any(kw in name for kw in ["半导体", "芯片", "科技", "AI"]):
            return "科技"
        elif any(kw in name for kw in ["国债", "债券", "利率"]):
            return "债券"
        elif any(kw in name for kw in ["消费", "食品", "医药"]):
            return "消费"
        elif any(kw in name for kw in ["金融", "银行", "保险"]):
            return "金融"
        else:
            return "其他"

    def get_last_positions(self) -> List[Dict]:
        """
        获取最近解析的持仓数据

        Returns:
            持仓列表
        """
        return getattr(self, '_last_positions', [])

    def _match_keywords(self, user_input: str) -> List[str]:
        """
        关键词匹配

        Args:
            user_input: 用户输入

        Returns:
            匹配的场景列表
        """
        matched = []
        for scenario_name, scenario_config in self.skill_chains.items():
            keywords = scenario_config.get("keywords", [])
            for keyword in keywords:
                if keyword in user_input:
                    matched.append(scenario_name)
                    break
        return matched

    def _match_regex(self, user_input: str) -> List[str]:
        """
        正则匹配

        Args:
            user_input: 用户输入

        Returns:
            匹配的场景列表
        """
        matched = []
        for scenario_name, scenario_config in self.skill_chains.items():
            regex_patterns = scenario_config.get("regex", [])
            for pattern in regex_patterns:
                if re.search(pattern, user_input):
                    matched.append(scenario_name)
                    break
        return matched

    def add_skill_chain(self, scenario_name: str, config: Dict):
        """
        动态添加 Skill 链

        Args:
            scenario_name: 场景名称
            config: 场景配置 {keywords, regex, chain, description}
        """
        self.skill_chains[scenario_name] = config
        logger.info(f"➕ 新增 Skill 链：{scenario_name}")

    def get_available_chains(self) -> Dict[str, str]:
        """
        获取所有可用的 Skill 链

        Returns:
            {场景名：描述}
        """
        return {
            name: config["description"]
            for name, config in self.skill_chains.items()
        }

    def get_route_history(self, limit: int = 10) -> List[Dict]:
        """
        获取路由历史

        Args:
            limit: 返回最近 N 条记录

        Returns:
            路由历史列表
        """
        return self.route_history[-limit:]


# 便捷函数
def create_router() -> SkillRouter:
    """创建路由器实例"""
    return SkillRouter()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    router = create_router()

    # 测试路由
    test_inputs = [
        "帮我分析一下 QFII 国债期货事件",
        "诊断我的持仓",
        "写一篇关于 AI 的文章",
        "测试我的投资人格",
        "给我一些投资建议",
        "未知输入"
    ]

    for user_input in test_inputs:
        print(f"\n📥 输入：{user_input}")
        skill_chain = router.route(user_input)
        print(f"📤 路由：{skill_chain}")

    # 查看路由历史
    print("\n📋 路由历史：")
    for record in router.get_route_history():
        print(f"  {record['timestamp']} | {record['input']} → {record['matched_scenario']}")
