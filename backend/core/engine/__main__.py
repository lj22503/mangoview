"""
Mangofolio 分析引擎 - 主入口

用法：
    python -m src "帮我分析一下 QFII 国债期货事件"
    python -m src --help
    python -m src --analyze tianshi --input '{"pmi": 50.8}'
"""

import sys
import json
import logging
from typing import Optional

from . import create_engine
from .orchestrator import Orchestrator
from .skills import EventAnalysisSkill, PositionDiagnosisSkill
from .middleware.tier_model import UserTier


def main(user_input: Optional[str] = None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # 支持 --analyze 参数调新引擎
    if len(sys.argv) > 2 and sys.argv[1] == "--analyze":
        layer = sys.argv[2]
        input_str = sys.argv[3] if len(sys.argv) > 3 else "{}"
        try:
            input_data = json.loads(input_str)
        except json.JSONDecodeError:
            input_data = {"raw": input_str}

        engine = create_engine()
        result = engine.analyze(
            layer=layer,
            input_data=input_data,
            user_tier=UserTier.BASIC,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # 旧引擎（兼容）
    engine = Orchestrator()
    if not user_input:
        if len(sys.argv) > 1:
            user_input = " ".join(sys.argv[1:])
        else:
            print("🥭 Mangofolio 分析引擎 v2")
            print("=" * 50)
            print()
            print("用法：")
            print('  python -m src --analyze tianshi \'{"pmi": 50.8}\'')
            print('  python -m src --analyze dili \'{"event": "QFII 国债期货"}\'')
            print('  python -m src --analyze renhe_company \'{"company": "腾讯"}\'')
            print('  python -m src --analyze renhe_fund \'{"fund_code": "518880"}\'')
            print()
            print('  python -m src "帮我分析一下 QFII 国债期货事件"')
            print()
            return

    result = engine.execute(user_input)
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
