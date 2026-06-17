"""
基金数据获取器

基于统一数据接入层（data_fetcher），专门获取基金数据
复用已有的缓存、配置、异常机制，不重复造轮子
"""

from typing import Optional, List, Dict
from datetime import datetime

from data_layer.config import load_config
from data_layer.cache import CacheManager
from data_layer.exceptions import DataFetchError
from data_layer.providers import fund_eastmoney


class FundDataFetcher:
    """
    基金数据统一获取接口
    
    复用 investment-framework 的数据接入层：
    - 缓存（CacheManager）
    - 配置（config.yaml）
    - 异常（DataFetchError）
    - Provider 降级机制
    
    用法：
        fetcher = FundDataFetcher()
        
        # 基金估值（盘中实时）
        gz = fetcher.get_estimated_nav('005827')
        
        # 基金详情（名称、经理、费率等）
        detail = fetcher.get_detail('005827')
        
        # 阶段收益 + 排名
        perf = fetcher.get_performance('005827')
        
        # 历史净值
        nav = fetcher.get_nav_history('005827', page_size=30)
        
        # 重仓股
        holdings = fetcher.get_holdings('005827')
        
        # 资产配置（股债比）
        alloc = fetcher.get_asset_allocation('005827')
        
        # 搜索基金
        results = fetcher.search('沪深300')
        
        # 一键获取完整基金档案
        profile = fetcher.get_full_profile('005827')
    """
    
    # 缓存 TTL（秒）
    CACHE_TTL = {
        'estimated_nav': 60,       # 估值：1 分钟（盘中频繁变化）
        'detail': 3600,            # 详情：1 小时（变化慢）
        'performance': 1800,       # 业绩：30 分钟
        'nav_history': 600,        # 净值：10 分钟
        'holdings': 86400,         # 持仓：1 天（季度更新）
        'asset_allocation': 86400, # 配置：1 天（季度更新）
        'search': 3600,            # 搜索：1 小时
    }
    
    def __init__(self, config_path: str = None):
        """
        初始化基金数据获取器
        
        Args:
            config_path: 配置文件路径，默认复用 data_fetcher 的配置
        """
        self.config = load_config(config_path)
        self.cache = CacheManager(
            ttl=self.config['fallback']['cache_ttl'],
            use_file_cache=False,
        )
        self.timeout = self.config['fallback']['timeout']
    
    def get_estimated_nav(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        获取基金实时估值
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            估值数据 dict
        """
        cache_key = f"fund:gz:{fund_code}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_estimated_nav(fund_code, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['estimated_nav'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}估值失败: {e}")
    
    def get_detail(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        获取基金详情
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            详情数据 dict
        """
        cache_key = f"fund:detail:{fund_code}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_detail(fund_code, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['detail'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}详情失败: {e}")
    
    def get_performance(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        获取基金阶段收益 + 排名
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            业绩数据 dict
        """
        cache_key = f"fund:perf:{fund_code}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_performance(fund_code, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['performance'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}业绩失败: {e}")
    
    def get_nav_history(self, fund_code: str, page_size: int = 20,
                        start_date: str = '', end_date: str = '',
                        use_cache: bool = True) -> Dict:
        """
        获取基金历史净值
        
        Args:
            fund_code: 基金代码
            page_size: 条数
            start_date: 起始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            use_cache: 是否使用缓存
        
        Returns:
            净值数据 dict
        """
        cache_key = f"fund:nav:{fund_code}:{page_size}:{start_date}:{end_date}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_nav_history(
                fund_code, page_size, start_date, end_date, self.timeout
            )
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['nav_history'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}净值失败: {e}")
    
    def get_holdings(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        获取基金重仓股
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            持仓数据 dict
        """
        cache_key = f"fund:holdings:{fund_code}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_holdings(fund_code, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['holdings'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}持仓失败: {e}")
    
    def get_asset_allocation(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        获取基金资产配置
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            资产配置数据 dict
        """
        cache_key = f"fund:alloc:{fund_code}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.fetch_fund_asset_allocation(fund_code, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['asset_allocation'])
            return data
        except Exception as e:
            raise DataFetchError(f"获取基金{fund_code}资产配置失败: {e}")
    
    def search(self, keyword: str, use_cache: bool = True) -> List[Dict]:
        """
        搜索基金
        
        Args:
            keyword: 关键词（代码或名称）
            use_cache: 是否使用缓存
        
        Returns:
            基金列表
        """
        cache_key = f"fund:search:{keyword}"
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = fund_eastmoney.search_fund(keyword, self.timeout)
            self.cache.set(cache_key, data, ttl=self.CACHE_TTL['search'])
            return data
        except Exception as e:
            raise DataFetchError(f"搜索基金失败: {e}")
    
    def get_full_profile(self, fund_code: str, use_cache: bool = True) -> Dict:
        """
        一键获取完整基金档案
        
        合并：详情 + 业绩 + 持仓 + 资产配置
        
        Args:
            fund_code: 基金代码
            use_cache: 是否使用缓存
        
        Returns:
            完整档案 dict
        """
        profile = {
            'fund_code': fund_code,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 逐个获取，单个失败不影响整体
        try:
            profile['detail'] = self.get_detail(fund_code, use_cache)
        except Exception as e:
            profile['detail'] = {'error': str(e)}
        
        try:
            profile['performance'] = self.get_performance(fund_code, use_cache)
        except Exception as e:
            profile['performance'] = {'error': str(e)}
        
        try:
            profile['holdings'] = self.get_holdings(fund_code, use_cache)
        except Exception as e:
            profile['holdings'] = {'error': str(e)}
        
        try:
            profile['asset_allocation'] = self.get_asset_allocation(fund_code, use_cache)
        except Exception as e:
            profile['asset_allocation'] = {'error': str(e)}
        
        try:
            profile['nav_history'] = self.get_nav_history(fund_code, page_size=10, use_cache=use_cache)
        except Exception as e:
            profile['nav_history'] = {'error': str(e)}
        
        return profile
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        return self.cache.stats()


# 别名（兼容旧代码）
FundFetcher = FundDataFetcher
