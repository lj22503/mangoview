"""
数据提供者模块

所有数据源的统一接口
"""

from .eastmoney import EastMoneyProvider
from ..data_fetcher import DataFetcher, get_fetcher, fetch_for_analysis

__all__ = ["EastMoneyProvider", "DataFetcher", "get_fetcher", "fetch_for_analysis"]
