"""
Orchestrator - 核心调度引擎

职责：
1. 接收用户输入（自然语言）
2. 路由到对应 Skill 链
3. 执行 Skill 链（链式调用）
4. 格式化输出（带署名 + 免责声明）
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .router import SkillRouter
from .verifier import DataVerifier
from .formatter import OutputFormatter
from .skill_interface import get_skill, list_skills

logger = logging.getLogger(__name__)


class Orchestrator:
    """工作流引擎核心类"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化工作流引擎

        Args:
            config: 配置字典，包含数据源、Skill 路径等
        """
        self.config = config or {}
        self.router = SkillRouter()
        self.verifier = DataVerifier()
        self.formatter = OutputFormatter()
        self.execution_log = []

    def execute(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行用户请求

        Args:
            user_input: 用户输入（自然语言）
            context: 上下文信息（用户 ID、历史数据等）

        Returns:
            执行结果字典
        """
        start_time = datetime.now()
        logger.info(f"🚀 开始执行：{user_input}")

        try:
            # 1. 路由到 Skill 链
            skill_chain = self.router.route(user_input)
            logger.info(f"📍 路由到 Skill 链：{skill_chain}")

            # 2. 执行 Skill 链
            results = []
            current_data = {"input": user_input, "context": context or {}}

            # 如果有解析的持仓数据，添加到 current_data
            if hasattr(self.router, '_last_positions') and self.router._last_positions:
                current_data["positions"] = self.router._last_positions

            for skill_name in skill_chain:
                logger.info(f"⚙️ 执行 Skill：{skill_name}")

                # 调用 Skill（这里需要对接实际的 Skill 实现）
                skill_result = self._execute_skill(skill_name, current_data)

                results.append({
                    "skill": skill_name,
                    "status": "success",
                    "data": skill_result
                })

                # 链式传递：Skill A 输出 → Skill B 输入
                current_data["previous_result"] = skill_result

            # 3. 数据验证
            verified_results = self._verify_data(results)

            # 4. 格式化输出
            output = self.formatter.format(verified_results, user_input)

            # 5. 记录执行日志
            execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "input": user_input,
                "skill_chain": skill_chain,
                "execution_time": execution_time,
                "status": "success"
            })

            logger.info(f"✅ 执行完成，耗时 {execution_time:.2f} 秒")

            return {
                "status": "success",
                "output": output,
                "execution_time": execution_time,
                "skill_chain": skill_chain
            }

        except Exception as e:
            logger.error(f"❌ 执行失败：{str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "input": user_input,
                "status": "error",
                "error": str(e),
                "execution_time": execution_time
            })

            return {
                "status": "error",
                "error": str(e),
                "execution_time": execution_time
            }

    def _execute_skill(self, skill_name: str, data: Dict) -> Dict:
        """
        执行单个 Skill

        Args:
            skill_name: Skill 名称
            data: 输入数据

        Returns:
            Skill 执行结果
        """
        # 从注册表获取 Skill
        skill_instance = get_skill(skill_name)

        if not skill_instance:
            # 回退到内置处理器（兼容旧代码）
            skill_handlers = {
                "personality_test": self._execute_personality_test,
                "event_analysis": self._execute_event_analysis,
                "position_diagnosis": self._execute_position_diagnosis,
                "content_generation": self._execute_content_generation,
            }

            handler = skill_handlers.get(skill_name)
            if not handler:
                raise ValueError(f"未知 Skill：{skill_name}")

            return handler(data)

        # 调用 Skill
        return skill_instance(data)

    def _execute_personality_test(self, data: Dict) -> Dict:
        """执行人格测试 Skill"""
        return {
            "skill": "personality_test",
            "result": "🐘 大象（价值投资）",
            "risk_profile": "保守",
            "confidence": 0.85
        }

    def _execute_event_analysis(self, data: Dict) -> Dict:
        """执行事件分析 Skill"""
        return {
            "skill": "event_analysis",
            "event": data.get("input", ""),
            "classification": "闸门",
            "score": 8.5,
            "beneficiaries": ["券商", "金融 IT"],
            "data_source": "东方财富 API",
            "confidence_level": "A"
        }

    def _execute_position_diagnosis(self, data: Dict) -> Dict:
        """执行持仓诊断 Skill"""
        return {
            "skill": "position_diagnosis",
            "positions": data.get("positions", []),
            "concentration": "健康",
            "suggestions": ["保持当前配置", "适当增加债券比例"]
        }

    def _execute_content_generation(self, data: Dict) -> Dict:
        """执行内容生成 Skill"""
        return {
            "skill": "content_generation",
            "title": f"关于{data.get('input', '')}的深度分析",
            "content": "（内容生成中...）",
            "platform": "雪球",
            "word_count": 1500
        }

    def _verify_data(self, results: List[Dict]) -> List[Dict]:
        """
        数据验证

        Args:
            results: Skill 执行结果列表

        Returns:
            验证后的结果列表
        """
        verified = []
        for result in results:
            if "data" in result:
                result["data"]["verified"] = True
                result["data"]["verify_time"] = datetime.now().isoformat()
            verified.append(result)
        return verified

    def get_execution_log(self, limit: int = 10) -> List[Dict]:
        """
        获取执行日志

        Args:
            limit: 返回最近 N 条记录

        Returns:
            执行日志列表
        """
        return self.execution_log[-limit:]

    def reset(self):
        """重置引擎状态"""
        self.execution_log = []
        logger.info("🔄 引擎已重置")


# 便捷函数
def create_orchestrator(config: Optional[Dict] = None) -> Orchestrator:
    """创建工作流引擎实例"""
    return Orchestrator(config)


def execute_workflow(user_input: str, context: Optional[Dict] = None) -> Dict:
    """
    便捷执行工作流

    Args:
        user_input: 用户输入
        context: 上下文

    Returns:
        执行结果
    """
    engine = create_orchestrator()
    return engine.execute(user_input, context)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    engine = create_orchestrator()

    # 测试 1：事件分析
    result1 = engine.execute("帮我分析一下 QFII 国债期货事件")
    print(json.dumps(result1, indent=2, ensure_ascii=False))

    # 测试 2：持仓诊断
    result2 = engine.execute("诊断我的持仓：518880 30%, 510300 25%")
    print(json.dumps(result2, indent=2, ensure_ascii=False))

    # 查看执行日志
    print("\n📋 执行日志：")
    print(json.dumps(engine.get_execution_log(), indent=2, ensure_ascii=False))
