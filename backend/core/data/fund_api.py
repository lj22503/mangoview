#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金数据 API

基于统一数据层，专门获取基金数据。
复用 cache / config / exceptions，不重复造轮子。
"""

from typing import List, Dict, Optional
from datetime import datetime

from data_layer.cache import CacheManager
from data_layer.config import load_config
from data_layer.exceptions import DataFetchError
from data_layer.providers import fund_eastmoney

# 缓存 TTL（秒）
CACHE_TTL = {
    'estimated_nav': 60,       # 估值：1 分钟
    'detail': 3600,            # 详情：1 小时
    'performance': 1800,       # 业绩：30 分钟
    'nav_history': 600,        # 净值：10 分钟
    'holdings': 86400,         # 持仓：1 天
    'asset_allocation': 86400, # 配置：1 天
    'search': 3600,            # 搜索：1 小时
}

CACHE_DIR = None  # 使用默认


class FundAPI:
    """基金数据统一获取接口

    用法：
        from data_layer import FundAPI
        fund = FundAPI()

        gz = fund.get_estimated_nav('005827')
        detail = fund.get_detail('005827')
        perf = fund.get_performance('005827')
        nav = fund.get_nav_history('005827', page_size=30)
        holdings = fund.get_holdings('005827')
        alloc = fund.get_asset_allocation('005827')
        results = fund.search('沪深300')
        profile = fund.get_full_profile('005827')
    """

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        self._cache = CacheManager(
            ttl=self.config['fallback'].get('cache_ttl', 300),
            use_file_cache=self.config.get('cache', {}).get('use_file_cache', True),
        )
        self.timeout = self.config['fallback'].get('timeout', 10)

    def get_estimated_nav(self, fund_code: str, use_cache: bool = True) -> Dict:
        """获取基金实时估值（盘中）"""
        cache_key = f"fund:gz:{fund_code}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_estimated_nav(fund_code, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['estimated_nav'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}估值失败: {e}")

    def get_detail(self, fund_code: str, use_cache: bool = True) -> Dict:
        """获取基金详情（名称、经理、费率等）"""
        cache_key = f"fund:detail:{fund_code}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_detail(fund_code, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['detail'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}详情失败: {e}")

    def get_performance(self, fund_code: str, use_cache: bool = True) -> Dict:
        """获取基金阶段收益 + 排名"""
        cache_key = f"fund:perf:{fund_code}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_performance(fund_code, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['performance'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}业绩失败: {e}")

    def get_nav_history(self, fund_code: str, page_size: int = 20,
                        start_date: str = '', end_date: str = '',
                        use_cache: bool = True) -> Dict:
        """获取基金历史净值"""
        cache_key = f"fund:nav:{fund_code}:{page_size}:{start_date}:{end_date}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_nav_history(
                fund_code, page_size, start_date, end_date, self.timeout
            )
            self._cache.set(cache_key, data, ttl=CACHE_TTL['nav_history'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}净值失败: {e}")

    def get_holdings(self, fund_code: str, use_cache: bool = True) -> Dict:
        """获取基金重仓股"""
        cache_key = f"fund:holdings:{fund_code}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_holdings(fund_code, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['holdings'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}持仓失败: {e}")

    def get_asset_allocation(self, fund_code: str, use_cache: bool = True) -> Dict:
        """获取基金资产配置（股债比）"""
        cache_key = f"fund:alloc:{fund_code}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.fetch_fund_asset_allocation(fund_code, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['asset_allocation'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}资产配置失败: {e}")

    def search(self, keyword: str, use_cache: bool = True) -> List[Dict]:
        """搜索基金（按代码或名称）"""
        cache_key = f"fund:search:{keyword}"
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        try:
            data = fund_eastmoney.search_fund(keyword, self.timeout)
            self._cache.set(cache_key, data, ttl=CACHE_TTL['search'])
            return data
        except Exception as e:
            raise DataFetchError(f"搜索基金失败: {e}")

    def get_full_profile(self, fund_code: str, use_cache: bool = True) -> Dict:
        """一键获取完整基金档案（详情+业绩+持仓+配置+净值）"""
        profile = {
            'fund_code': fund_code,
            'timestamp': datetime.now().isoformat(),
        }

        for key, fn in [
            ('detail', lambda: self.get_detail(fund_code, use_cache)),
            ('performance', lambda: self.get_performance(fund_code, use_cache)),
            ('holdings', lambda: self.get_holdings(fund_code, use_cache)),
            ('asset_allocation', lambda: self.get_asset_allocation(fund_code, use_cache)),
            ('nav_history', lambda: self.get_nav_history(fund_code, page_size=10, use_cache=use_cache)),
        ]:
            try:
                profile[key] = fn()
            except Exception as e:
                profile[key] = {'error': str(e)}

        return profile

    def clear_cache(self):
        self._cache.clear()

    def cache_stats(self):
        return self._cache.stats()


# 便捷单例
_default_fund_api = None

def get_fund_api(config_path: str = None) -> FundAPI:
    global _default_fund_api
    if _default_fund_api is None:
        _default_fund_api = FundAPI(config_path)
    return _default_fund_api
