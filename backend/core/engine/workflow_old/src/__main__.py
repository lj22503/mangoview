"""
Mangofolio 工作流引擎 - 主入口

用法：
    python -m src "帮我分析一下 QFII 国债期货事件"
    python -m src --help
"""

import sys
import json
import logging
from typing import Optional

# 导入工作流引擎
from .orchestrator import Orchestrator
from .skills import EventAnalysisSkill, PositionDiagnosisSkill


def main(user_input: Optional[str] = None):
    """
    主函数

    Args:
        user_input: 用户输入（可选，从命令行读取）
    """
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # 创建引擎
    engine = Orchestrator()

    # 获取用户输入
    if not user_input:
        if len(sys.argv) > 1:
            user_input = " ".join(sys.argv[1:])
        else:
            print("🥭 Mangofolio 工作流引擎")
            print("=" * 50)
            print()
            print("用法：")
            print('  python -m src "帮我分析一下 QFII 国债期货事件"')
            print('  python -m src "诊断我的持仓：518880 30%, 510300 25%"')
            print()
            print("可用 Skill：")
            from .skill_interface import list_skills
            for name, version in list_skills().items():
                print(f"  - {name} v{version}")
            print()
            return

    # 执行工作流
    result = engine.execute(user_input)

    # 输出结果
    print("\n" + "=" * 50)
    print(f"📥 输入：{user_input}")
    print(f"📤 状态：{result['status']}")
    print(f"⏱️  耗时：{result.get('execution_time', 0):.2f} 秒")
    print(f"🔗 Skill 链：{' → '.join(result.get('skill_chain', []))}")
    print("=" * 50)

    if result["status"] == "success":
        print("\n📝 输出：")
        print(result["output"])
    else:
        print(f"\n❌ 错误：{result.get('error', '未知错误')}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
