"""
数据提供者模块

所有数据源的统一接口
"""

from .eastmoney import EastMoneyProvider

__all__ = ["EastMoneyProvider"]
