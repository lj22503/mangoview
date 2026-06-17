"""
东方财富 API 数据提供者

数据源：东方财富
信源等级：A
说明：实时行情、指数数据、资金流向
"""

import requests
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EastMoneyProvider:
    """东方财富数据提供者"""

    def __init__(self, cache_ttl: int = 300):
        """
        初始化

        Args:
            cache_ttl: 缓存时间（秒），默认 5 分钟
        """
        self.base_url = "https://push2.eastmoney.com"
        self.cache = {}
        self.cache_ttl = cache_ttl

    def get_market_index(self, indices: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取大盘指数数据

        Args:
            indices: 指数列表，默认 ['1.000001', '0.399001', '0.399006', '1.000300']

        Returns:
            指数数据字典
        """
        if indices is None:
            indices = ['1.000001', '0.399001', '0.399006', '1.000300']

        # 检查缓存
        cache_key = f"market_index_{','.join(indices)}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]

        try:
            # 东方财富 API
            url = f"{self.base_url}/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "fields": "f2,f3,f4,f12,f14",
                "secids": ",".join(indices)
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("data") and data["data"].get("diff"):
                result = self._parse_index_data(data["data"]["diff"])
                result["data_source"] = "东方财富"
                result["confidence_level"] = "A"
                result["verify_time"] = datetime.now().isoformat()
                result["disclaimer"] = "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"

                # 缓存结果
                self._cache_result(cache_key, result)

                logger.info(f"📊 获取大盘指数成功：{len(result)} 个指数")
                return result
            else:
                logger.warning("⚠️ 东方财富 API 返回数据为空")
                return self._get_mock_index_data()

        except Exception as e:
            logger.error(f"❌ 获取大盘指数失败：{str(e)}")
            return self._get_mock_index_data()

    def _parse_index_data(self, diff: List[Dict]) -> Dict[str, Any]:
        """
        解析指数数据

        Args:
            diff: API 返回的 diff 列表

        Returns:
            解析后的数据
        """
        index_names = {
            "1.000001": "上证指数",
            "0.399001": "深证成指",
            "0.399006": "创业板指",
            "1.000300": "沪深 300"
        }

        result = {}
        for item in diff:
            secid = item.get("f12", "")
            name = index_names.get(secid, secid)

            result[name] = {
                "current": item.get("f2", 0),  # 当前价
                "change_pct": item.get("f3", 0),  # 涨跌幅
                "change": item.get("f4", 0),  # 涨跌额
                "volume": item.get("f13", 0),  # 成交量
                "amount": item.get("f14", 0),  # 成交额
            }

        return result

    def _get_mock_index_data(self) -> Dict[str, Any]:
        """
        获取模拟数据（API 失败时降级）

        Returns:
            模拟指数数据
        """
        return {
            "上证指数": {"current": 3930.25, "change_pct": 1.03},
            "深证成指": {"current": 13717.22, "change_pct": 2.36},
            "创业板指": {"current": 3257.91, "change_pct": 3.07},
            "沪深 300": {"current": 4517.34, "change_pct": 1.73},
            "data_source": "东方财富（模拟数据）",
            "confidence_level": "C",
            "verify_time": datetime.now().isoformat(),
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
        }

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        获取个股行情

        Args:
            stock_code: 股票代码（如 600519）

        Returns:
            个股行情数据
        """
        # 检查缓存
        cache_key = f"stock_quote_{stock_code}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]

        try:
            # 判断市场
            if stock_code.startswith('6'):
                secid = f"1.{stock_code}"
            else:
                secid = f"0.{stock_code}"

            url = f"{self.base_url}/api/qt/stock/get"
            params = {
                "fltt": 2,
                "fields": "f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18",
                "secid": secid
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("data"):
                result = self._parse_stock_data(data["data"])
                result["data_source"] = "东方财富"
                result["confidence_level"] = "A"
                result["verify_time"] = datetime.now().isoformat()
                result["disclaimer"] = "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"

                # 缓存结果
                self._cache_result(cache_key, result)

                logger.info(f"📊 获取个股行情成功：{stock_code}")
                return result
            else:
                logger.warning(f"⚠️ 东方财富 API 返回数据为空：{stock_code}")
                return self._get_mock_stock_data(stock_code)

        except Exception as e:
            logger.error(f"❌ 获取个股行情失败：{stock_code} - {str(e)}")
            return self._get_mock_stock_data(stock_code)

    def _parse_stock_data(self, data: Dict) -> Dict[str, Any]:
        """
        解析个股数据

        Args:
            data: API 返回的数据

        Returns:
            解析后的数据
        """
        return {
            "code": data.get("f12", ""),
            "name": data.get("f14", ""),
            "current": data.get("f2", 0),
            "change_pct": data.get("f3", 0),
            "change": data.get("f4", 0),
            "volume": data.get("f5", 0),
            "amount": data.get("f6", 0),
            "open": data.get("f17", 0),
            "high": data.get("f15", 0),
            "low": data.get("f16", 0),
            "prev_close": data.get("f18", 0),
        }

    def _get_mock_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取模拟个股数据

        Args:
            stock_code: 股票代码

        Returns:
            模拟数据
        """
        return {
            "code": stock_code,
            "name": f"股票{stock_code}",
            "current": 100.0,
            "change_pct": 1.5,
            "data_source": "东方财富（模拟数据）",
            "confidence_level": "C",
            "verify_time": datetime.now().isoformat(),
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
        }

    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        检查缓存是否有效

        Args:
            cache_key: 缓存键

        Returns:
            是否有效
        """
        if cache_key not in self.cache:
            return False

        cache_time = self.cache[cache_key]["time"]
        return (time.time() - cache_time) < self.cache_ttl

    def _cache_result(self, cache_key: str, data: Dict):
        """
        缓存结果

        Args:
            cache_key: 缓存键
            data: 数据
        """
        self.cache[cache_key] = {
            "data": data,
            "time": time.time()
        }

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("🔄 东方财富缓存已清空")


# 便捷函数
def create_eastmoney_provider(cache_ttl: int = 300) -> EastMoneyProvider:
    """创建东方财富数据提供者"""
    return EastMoneyProvider(cache_ttl)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    provider = create_eastmoney_provider()

    # 测试 1：获取大盘指数
    print("\n📊 大盘指数数据：")
    market_data = provider.get_market_index()
    for index_name, data in market_data.items():
        if isinstance(data, dict) and "current" in data:
            print(f"  {index_name}: {data['current']} ({data['change_pct']}%)")

    # 测试 2：获取个股行情
    print("\n📊 个股行情（贵州茅台 600519）：")
    stock_data = provider.get_stock_quote("600519")
    print(f"  代码：{stock_data.get('code')}")
    print(f"  名称：{stock_data.get('name')}")
    print(f"  当前价：{stock_data.get('current')}")
    print(f"  涨跌幅：{stock_data.get('change_pct')}%")
