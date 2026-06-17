#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取层 - 统一入口

所有项目通过这一个文件获取数据，不直接调用各 provider。
数据源切换、缓存、降级逻辑全部在这里处理。

v2.0 整合 data_fetcher，新增：个股行情、财报、基金数据
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from data_layer.cache import CacheManager
from data_layer.config import load_config, get_api_key
from data_layer.exceptions import DataFetchError, ProviderError
from data_layer.models import Quote, Financials

# Provider imports（按需，延迟导入避免启动开销）
from data_layer.providers import tencent, searxng

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')


class DataAPI:
    """统一数据接口（全局唯一入口）"""

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        self._cache = CacheManager(
            ttl=self.config['fallback'].get('cache_ttl', 300),
            use_file_cache=self.config.get('cache', {}).get('use_file_cache', True),
            cache_dir=CACHE_DIR,
        )
        self.timeout = self.config['fallback'].get('timeout', 10)

    # ========== 大盘指数（实时） ==========

    def get_indices(self, codes=None, force_refresh=False):
        """获取大盘指数实时行情

        主数据源：腾讯财经（不缓存）

        Returns:
            dict: {指数名: {price, change_pct, ...}}
        """
        return tencent.get_indices(codes)

    # ========== 个股行情 ==========

    def get_quote(self, symbol: str, use_cache: bool = True) -> Quote:
        """获取个股实时行情

        降级链：腾讯 → 新浪 → 东方财富

        Args:
            symbol: 股票代码（如 600519.SH, 000001.SZ）
            use_cache: 是否使用缓存

        Returns:
            Quote 对象
        """
        cache_key = f"quote:{symbol}"

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return Quote.from_dict(cached)

        providers = [
            ('tencent', self._get_quote_tencent),
            ('eastmoney', self._get_quote_eastmoney),
            ('sina', self._get_quote_sina),
        ]

        last_error = None
        for name, fn in providers:
            try:
                data = fn(symbol)
                self._cache.set(cache_key, data, ttl=300)
                return Quote.from_dict(data)
            except Exception as e:
                last_error = e
                continue

        raise DataFetchError(f"获取 {symbol} 行情失败，所有数据源均失败。最后错误: {last_error}")

    def _get_quote_tencent(self, symbol: str) -> dict:
        from data_layer.providers import tencent as tencent_mod
        return tencent_mod.get_quote(symbol, self.timeout)

    def _get_quote_sina(self, symbol: str) -> dict:
        from data_layer.providers import sina
        return sina.get_quote(symbol, self.timeout)

    def _get_quote_eastmoney(self, symbol: str) -> dict:
        from data_layer.providers import eastmoney
        return eastmoney.get_quote(symbol, self.timeout)

    # ========== 财报数据 ==========

    def get_financials(self, symbol: str, use_cache: bool = True) -> Financials:
        """获取财报数据

        主数据源：东方财富

        Args:
            symbol: 股票代码

        Returns:
            Financials 对象
        """
        cache_key = f"financials:{symbol}"

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return Financials.from_dict(cached)

        try:
            from data_layer.providers import eastmoney
            data = eastmoney.get_financials(symbol, self.timeout)
            self._cache.set(cache_key, data, ttl=3600)
            return Financials.from_dict(data)
        except Exception as e:
            raise DataFetchError(f"获取 {symbol} 财报失败: {e}")

    # ========== 个股日线 ==========

    def get_daily(self, ts_code, start, end, force_refresh=False):
        """获取个股日线行情

        主数据源：Tushare → 降级 QVeris
        缓存：1 天
        """
        cache_key = f"daily:{ts_code}:{start}:{end}"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                import pandas as pd
                return pd.DataFrame(cached)

        try:
            from data_layer.providers import tushare_api
            df = tushare_api.get_daily(ts_code, start, end)
            if df is not None and len(df) > 0:
                self._cache.set(cache_key, df.to_dict('records'), ttl=86400)
                return df
        except Exception as e:
            print(f"Tushare daily 失败: {e}")

        try:
            from data_layer.providers import qveris
            return qveris.get_stock_history(ts_code, start, end)
        except Exception as e:
            print(f"QVeris 降级也失败: {e}")

        return None

    # ========== 涨跌停 ==========

    def get_limit_list(self, trade_date, limit_type='U', force_refresh=False):
        """获取涨跌停统计（Tushare）"""
        cache_key = f"limit:{trade_date}:{limit_type}"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                import pandas as pd
                return pd.DataFrame(cached)

        from data_layer.providers import tushare_api
        df = tushare_api.get_limit_list(trade_date, limit_type)
        if df is not None and len(df) > 0:
            self._cache.set(cache_key, df.to_dict('records'), ttl=86400)
        return df

    # ========== 北向资金 ==========

    def get_northbound(self, start=None, end=None, force_refresh=False):
        """获取北向资金（Tushare → QVeris 降级）"""
        if start is None:
            end = datetime.now().strftime('%Y%m%d')
            start = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')

        cache_key = f"northbound:{start}:{end}"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                import pandas as pd
                return pd.DataFrame(cached)

        try:
            from data_layer.providers import tushare_api
            df = tushare_api.get_northbound(start, end)
            if df is not None and len(df) > 0:
                self._cache.set(cache_key, df.to_dict('records'), ttl=86400)
                return df
        except Exception as e:
            print(f"Tushare 北向资金失败: {e}")

        try:
            from data_layer.providers import qveris
            return qveris.get_northbound()
        except Exception as e:
            print(f"QVeris 降级也失败: {e}")

        return None

    # ========== 宏观经济 ==========

    def get_macro(self, indicator, start=None, end=None, force_refresh=False):
        """获取宏观经济数据（QVeris，缓存 7 天）"""
        cache_key = f"macro:{indicator}"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        from data_layer.providers import qveris
        data = qveris.get_macro(indicator, start, end)
        if data:
            self._cache.set(cache_key, data, ttl=604800)  # 7 天
        return data

    # ========== 行业资金流向 ==========

    def get_industry_flow(self, force_refresh=False):
        """获取行业资金流向（QVeris，缓存 7 天）"""
        cache_key = "industry_flow"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        from data_layer.providers import qveris
        data = qveris.get_industry_flow()
        if data:
            self._cache.set(cache_key, data, ttl=604800)
        return data

    # ========== 行业板块行情 ==========

    def get_sector_performance(self, force_refresh=False):
        """获取行业板块涨跌幅排行（东方财富，缓存 10 分钟）"""
        cache_key = "sector_performance"

        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        from data_layer.providers import eastmoney
        data = eastmoney.fetch_sector_performance()
        if data and not data.get('error'):
            self._cache.set(cache_key, data, ttl=600)
        return data

    # ========== 新闻搜索 ==========

    def search_news(self, topic):
        """搜索财经新闻（SearXNG，不缓存）"""
        return searxng.search_news(topic)

    def search_policy(self, topic):
        """搜索政策信息（SearXNG，不缓存）"""
        return searxng.search_policy(topic)

    # ========== 缓存管理 ==========

    def clear_cache(self):
        self._cache.clear()

    def cache_stats(self):
        return self._cache.stats()


# 便捷单例
_default_api = None

def get_api(config_path: str = None) -> DataAPI:
    global _default_api
    if _default_api is None:
        _default_api = DataAPI(config_path)
    return _default_api


# ========== AKShare 数据源（零 API Key） ==========

    def search_stock(self, keyword: str):
        """搜索股票代码（AKShare）

        Args:
            keyword: 股票名称/公司简称

        Returns:
            List[Dict]: 搜索结果
        """
        from data_layer.providers import akshare
        return akshare.search_stock(keyword)

    def get_stock_info_ak(self, symbol: str, market: str = 'sh'):
        """获取股票基本信息（AKShare）

        Args:
            symbol: 股票代码
            market: 市场

        Returns:
            Dict: 股票信息
        """
        from data_layer.providers import akshare
        return akshare.get_stock_info(symbol, market)

    def get_stock_prices_ak(self, symbol: str, market: str = 'sh', period: str = 'daily'):
        """获取股票历史价格（AKShare）

        Args:
            symbol: 股票代码
            market: 市场
            period: 周期

        Returns:
            List[Dict]: 价格数据
        """
        from data_layer.providers import akshare
        return akshare.get_stock_prices(symbol, market, period)

    def get_stock_indicators_ak(self, symbol: str):
        """获取 A 股财务指标（AKShare）

        Args:
            symbol: 股票代码

        Returns:
            List[Dict]: 财务指标
        """
        from data_layer.providers import akshare
        return akshare.get_stock_indicators_a(symbol)

    def get_zt_pool_ak(self):
        """获取涨停池（AKShare）

        Returns:
            List[Dict]: 涨停股列表
        """
        from data_layer.providers import akshare
        return akshare.get_zt_pool()

    def get_strong_pool_ak(self):
        """获取强势股池（AKShare）

        Returns:
            List[Dict]: 强势股列表
        """
        from data_layer.providers import akshare
        return akshare.get_strong_pool()

    def get_lhb_ak(self):
        """获取龙虎榜（AKShare）

        Returns:
            List[Dict]: 龙虎榜列表
        """
        from data_layer.providers import akshare
        return akshare.get_lhb()

    def get_stock_news_ak(self, symbol: str):
        """获取个股新闻（AKShare）

        Args:
            symbol: 股票代码

        Returns:
            List[Dict]: 新闻列表
        """
        from data_layer.providers import akshare
        return akshare.get_stock_news(symbol)

    def get_global_news_ak(self):
        """获取全球财经快讯（AKShare）

        Returns:
            List[Dict]: 新闻列表
        """
        from data_layer.providers import akshare
        return akshare.get_global_news()

    def get_trading_suggest_ak(self, symbol: str, market: str = 'sh'):
        """获取交易建议（AKShare）

        Args:
            symbol: 股票代码
            market: 市场

        Returns:
            Dict: 交易建议
        """
        from data_layer.providers import akshare
        return akshare.get_trading_suggest(symbol, market)
