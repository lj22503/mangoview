"""
Mangofolio 分析引擎 pytest 配置

处理：
- 模块路径（engine 作为包导入）
- 忽略损坏的 superclaude 插件
"""
import sys
import os

# 添加 core 目录到 sys.path（engine 作为包导入）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
