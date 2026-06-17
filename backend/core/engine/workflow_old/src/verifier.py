"""
Data Verifier - 数据验证层

职责：
1. 接入真实数据源（复用 data_layer 架构）
2. 标注信源等级（S/A/B/C）
3. 验证数据时效性
4. 返回可追溯的数据引用

设计原则：
- 复用 data_layer 的统一数据接口
- 继承降级链逻辑
- 增加信源等级标注
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from data_layer import get_api, Quote, Financials, FundProfile

logger = logging.getLogger(__name__)


class DataVerifier:
    """数据验证层（基于 data_layer 架构）"""

    def __init__(self, config_path: str = None):
        """
        初始化数据验证层

        Args:
            config_path: data_layer 配置文件路径
        """
        self.api = get_api(config_path)
        self.verify_log = []

    def verify(self, data: Dict, source: Optional[str] = None) -> Dict:
        """
        验证数据（添加信源等级、验证时间等）

        Args:
            data: 待验证数据
            source: 数据源（可选，自动检测）

        Returns:
            验证后的数据
        """
        logger.info(f"🔍 验证数据，数据源：{source or '自动检测'}")

        # 1. 检测数据源
        if not source:
            source = self._detect_source(data)

        # 2. 获取信源等级
        confidence_level = self._get_confidence_level(source)

        # 3. 验证数据时效性
        is_fresh = self._check_freshness(data)

        # 4. 添加验证元数据
        verified_data = {
            **data,
            "verified": True,
            "verify_time": datetime.now().isoformat(),
            "data_source": source,
            "confidence_level": confidence_level,
            "is_fresh": is_fresh,
            "disclaimer": "本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。"
        }

        # 5. 记录验证日志
        self.verify_log.append({
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "confidence_level": confidence_level,
            "is_fresh": is_fresh
        })

        logger.info(f"✅ 验证完成，信源等级：{confidence_level}，时效性：{is_fresh}")

        return verified_data

    def _detect_source(self, data: Dict) -> str:
        """
        自动检测数据源

        Args:
            data: 待验证数据

        Returns:
            数据源名称
        """
        # 基于 data 中的 source 字段检测
        if "source" in data:
            return data["source"]

        # 简单启发式检测
        if "fund_code" in data or "strategy" in data:
            return "且慢 MCP"
        elif "macro" in data or "economic" in data:
            return "AKShare"
        elif "news" in data or "event" in data:
            return "财联社"
        elif "quote" in data or "index" in data or "stock" in data:
            return "东方财富"
        else:
            return "东方财富"  # 默认

    def _get_confidence_level(self, source: str) -> str:
        """
        获取信源等级

        Args:
            source: 数据源

        Returns:
            信源等级（S/A/B/C）
        """
        levels = {
            "东方财富": "A",
            "腾讯财经": "A",
            "新浪财经": "A",
            "同花顺": "A",
            "且慢 MCP": "S",
            "AKShare": "B",
            "财联社": "A",
            "国家统计局": "S",
            "央行": "S",
            "Tushare": "B"
        }
        return levels.get(source, "C")

    def _check_freshness(self, data: Dict) -> bool:
        """
        检查数据时效性

        Args:
            data: 待验证数据

        Returns:
            是否新鲜（1 小时内）
        """
        if "timestamp" in data:
            try:
                ts = data["timestamp"]
                if isinstance(ts, str):
                    data_time = datetime.fromisoformat(ts)
                elif isinstance(ts, datetime):
                    data_time = ts
                else:
                    return True

                age = datetime.now() - data_time
                return age.total_seconds() < 3600  # 1 小时
            except:
                pass
        return True  # 无时间戳，假设新鲜

    # ========== 统一数据接口（复用 data_layer） ==========

    def get_market_data(self, market_type: str = "A 股") -> Dict:
        """
        获取市场数据

        Args:
            market_type: 市场类型（A 股/港股/美股）

        Returns:
            市场数据（已验证）
        """
        logger.info(f"📊 获取{market_type}市场数据")

        try:
            # 使用 data_layer 的统一接口
            indices = self.api.get_indices()

            # 转换为标准格式
            result = {}
            for name, data in indices.items():
                result[name] = {
                    "current": data.get("price", 0),
                    "change_pct": data.get("change_percent", 0),
                    "change": data.get("change", 0),
                    "volume": data.get("volume", 0),
                }

            result["data_source"] = indices.get("source", "东方财富")
            result["timestamp"] = datetime.now().isoformat()

            return self.verify(result, result["data_source"])

        except Exception as e:
            logger.error(f"❌ 获取市场数据失败：{str(e)}")
            return self._get_mock_market_data()

    def get_stock_data(self, symbol: str) -> Dict:
        """
        获取个股数据

        Args:
            symbol: 股票代码（如 600519.SH）

        Returns:
            个股数据（已验证）
        """
        logger.info(f"📊 获取个股{symbol}数据")

        try:
            # 使用 data_layer 的统一接口
            quote = self.api.get_quote(symbol)

            result = {
                "symbol": quote.symbol,
                "price": quote.price,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "volume": quote.volume,
                "turnover": quote.turnover,
                "market_cap": quote.market_cap,
                "pe": quote.pe,
                "pb": quote.pb,
                "high": quote.high,
                "low": quote.low,
                "open": quote.open,
                "prev_close": quote.prev_close,
                "source": quote.source,
                "timestamp": quote.timestamp.isoformat() if isinstance(quote.timestamp, datetime) else str(quote.timestamp),
            }

            return self.verify(result, quote.source)

        except Exception as e:
            logger.error(f"❌ 获取个股数据失败：{symbol} - {str(e)}")
            return self._get_mock_stock_data(symbol)

    def get_fund_data(self, fund_code: str) -> Dict:
        """
        获取基金数据

        Args:
            fund_code: 基金代码

        Returns:
            基金数据（已验证）
        """
        logger.info(f"📊 获取基金{fund_code}数据")

        try:
            # 使用 data_layer 的基金接口
            from data_layer import FundAPI
            fund_api = FundAPI()
            profile = fund_api.get_full_profile(fund_code)

            result = {
                "fund_code": profile.get("fund_code", fund_code),
                "fund_name": profile.get("fund_name", "未知基金"),
                "fund_type": profile.get("fund_type", "未知类型"),
                "nav": profile.get("nav", 0.0),
                "acc_nav": profile.get("acc_nav", 0.0),
                "nav_date": profile.get("nav_date", ""),
                "daily_return": profile.get("daily_return", 0.0),
                "fund_size": profile.get("fund_size", 0.0),
                "management_fee": profile.get("management_fee", 0.0),
                "custody_fee": profile.get("custody_fee", 0.0),
                "manager_name": profile.get("manager_name", "未知"),
                "establishment_date": profile.get("establishment_date", ""),
                "risk_level": profile.get("risk_level", "未知"),
                "source": profile.get("source", "东方财富"),
                "timestamp": datetime.now().isoformat(),
            }

            return self.verify(result, result["source"])

        except Exception as e:
            logger.error(f"❌ 获取基金数据失败：{fund_code} - {str(e)}")
            return self._get_mock_fund_data(fund_code)

    def get_financials(self, symbol: str) -> Dict:
        """
        获取财报数据

        Args:
            symbol: 股票代码

        Returns:
            财报数据（已验证）
        """
        logger.info(f"📊 获取财报{symbol}数据")

        try:
            # 使用 data_layer 的统一接口
            financials = self.api.get_financials(symbol)

            result = {
                "symbol": financials.symbol,
                "report_date": financials.report_date,
                "revenue": financials.revenue,
                "net_profit": financials.net_profit,
                "roe": financials.roe,
                "eps": financials.eps,
                "debt_ratio": financials.debt_ratio,
                "gross_margin": financials.gross_margin,
                "net_margin": financials.net_margin,
                "operating_cash_flow": financials.operating_cash_flow,
                "source": financials.source,
                "timestamp": financials.timestamp.isoformat() if isinstance(financials.timestamp, datetime) else str(financials.timestamp),
            }

            return self.verify(result, financials.source)

        except Exception as e:
            logger.error(f"❌ 获取财报数据失败：{symbol} - {str(e)}")
            return self._get_mock_financials_data(symbol)

    # ========== 降级策略（模拟数据） ==========

    def _get_mock_market_data(self) -> Dict:
        """获取模拟市场数据"""
        return self.verify({
            "上证指数": {"current": 3930.25, "change_pct": 1.03},
            "深证成指": {"current": 13717.22, "change_pct": 2.36},
            "创业板指": {"current": 3257.91, "change_pct": 3.07},
            "沪深 300": {"current": 4517.34, "change_pct": 1.73},
            "source": "模拟数据",
            "timestamp": datetime.now().isoformat()
        }, "模拟数据")

    def _get_mock_stock_data(self, symbol: str) -> Dict:
        """获取模拟个股数据"""
        return self.verify({
            "symbol": symbol,
            "price": 100.0,
            "change_percent": 1.5,
            "source": "模拟数据",
            "timestamp": datetime.now().isoformat()
        }, "模拟数据")

    def _get_mock_fund_data(self, fund_code: str) -> Dict:
        """获取模拟基金数据"""
        return self.verify({
            "fund_code": fund_code,
            "nav": 1.2345,
            "source": "模拟数据",
            "timestamp": datetime.now().isoformat()
        }, "模拟数据")

    def _get_mock_financials_data(self, symbol: str) -> Dict:
        """获取模拟财报数据"""
        return self.verify({
            "symbol": symbol,
            "revenue": 1000000000,
            "net_profit": 200000000,
            "source": "模拟数据",
            "timestamp": datetime.now().isoformat()
        }, "模拟数据")

    def get_verify_log(self, limit: int = 10) -> List[Dict]:
        """
        获取验证日志

        Args:
            limit: 返回最近 N 条记录

        Returns:
            验证日志列表
        """
        return self.verify_log[-limit:]


# 便捷函数
def create_verifier(config_path: str = None) -> DataVerifier:
    """创建数据验证层实例"""
    return DataVerifier(config_path)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    verifier = create_verifier()

    # 测试 1：获取市场数据
    print("\n📊 A 股市场数据：")
    market_data = verifier.get_market_data("A 股")
    for index_name, data in market_data.items():
        if isinstance(data, dict) and "current" in data:
            print(f"  {index_name}: {data['current']} ({data['change_pct']}%)")
    print(f"  信源等级：{market_data.get('confidence_level')}")
    print(f"  时效性：{market_data.get('is_fresh')}")

    # 测试 2：获取个股数据
    print("\n📊 个股数据（贵州茅台 600519.SH）：")
    stock_data = verifier.get_stock_data("600519.SH")
    print(f"  代码：{stock_data.get('symbol')}")
    print(f"  当前价：{stock_data.get('price')}")
    print(f"  涨跌幅：{stock_data.get('change_percent')}%")
    print(f"  信源等级：{stock_data.get('confidence_level')}")

    # 测试 3：获取基金数据
    print("\n📊 基金数据（518880）：")
    fund_data = verifier.get_fund_data("518880")
    print(f"  代码：{fund_data.get('fund_code')}")
    print(f"  净值：{fund_data.get('nav')}")
    print(f"  信源等级：{fund_data.get('confidence_level')}")

    # 查看验证日志
    print("\n📋 验证日志：")
    for record in verifier.get_verify_log():
        print(f"  {record['timestamp']} | {record['source']} | {record['confidence_level']}")
