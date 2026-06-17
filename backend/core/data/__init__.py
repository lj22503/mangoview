# data-layer package
"""
统一数据获取层 v2.2 (整合 akshare MCP)

所有项目共用，不跟项目走。
数据问题在这里一次性解决。

v2.2 变更:
- 新增 akshare provider（零 API Key）
- 通过 mcp-aktools 获取 A 股/港股/美股/ETF/加密货币数据
"""

from data_layer.data_api import DataAPI, get_api
from data_layer.fund_api import FundAPI
from data_layer.providers.fund_fetcher import FundFetcher
from data_layer.models import Quote, Financials, FundProfile
from data_layer.cache import CacheManager
from data_layer.config import load_config, save_config, get_api_key
from data_layer.exceptions import DataFetchError, ProviderError, ConfigError, APIKeyError, CacheError

__version__ = '2.2.0'
__all__ = [
    'DataAPI', 'get_api',
    'FundAPI',
    'FundFetcher',
    'Quote', 'Financials', 'FundProfile',
    'CacheManager',
    'load_config', 'save_config', 'get_api_key',
    'DataFetchError', 'ProviderError', 'ConfigError', 'APIKeyError', 'CacheError',
]
