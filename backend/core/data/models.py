"""
统一数据模型

所有 provider 返回的数据统一为这些结构
"""

from datetime import datetime
from typing import Optional, List, Dict


def _parse_timestamp(val):
    """兼容 Python 3.6 的时间戳解析"""
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
    return datetime.now()


# Python 3.6 没有 dataclasses，用简单 class 替代
try:
    from dataclasses import dataclass
except ImportError:
    # 极简 fallback
    def dataclass(cls):
        return cls


@dataclass
class Quote:
    """股价行情数据"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    turnover: float
    market_cap: float
    pe: float
    pb: float
    high: float
    low: float
    open: float
    prev_close: float
    source: str
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'Quote':
        return cls(
            symbol=data.get('symbol', ''),
            price=data.get('price', 0.0),
            change=data.get('change', 0.0),
            change_percent=data.get('change_percent', 0.0),
            volume=data.get('volume', 0),
            turnover=data.get('turnover', 0.0),
            market_cap=data.get('market_cap', 0.0),
            pe=data.get('pe', 0.0),
            pb=data.get('pb', 0.0),
            high=data.get('high', 0.0),
            low=data.get('low', 0.0),
            open=data.get('open', 0.0),
            prev_close=data.get('prev_close', 0.0),
            source=data.get('source', 'unknown'),
            timestamp=_parse_timestamp(data.get('timestamp')),
        )

    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'turnover': self.turnover,
            'market_cap': self.market_cap,
            'pe': self.pe,
            'pb': self.pb,
            'high': self.high,
            'low': self.low,
            'open': self.open,
            'prev_close': self.prev_close,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
        }


@dataclass
class Financials:
    """财报数据"""
    symbol: str
    report_date: str
    revenue: float
    net_profit: float
    roe: float
    eps: float
    debt_ratio: float
    gross_margin: float
    net_margin: float
    operating_cash_flow: float
    source: str
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'Financials':
        return cls(
            symbol=data.get('symbol', ''),
            report_date=data.get('report_date', ''),
            revenue=data.get('revenue', 0.0),
            net_profit=data.get('net_profit', 0.0),
            roe=data.get('roe', 0.0),
            eps=data.get('eps', 0.0),
            debt_ratio=data.get('debt_ratio', 0.0),
            gross_margin=data.get('gross_margin', 0.0),
            net_margin=data.get('net_margin', 0.0),
            operating_cash_flow=data.get('operating_cash_flow', 0.0),
            source=data.get('source', 'unknown'),
            timestamp=_parse_timestamp(data.get('timestamp')),
        )

    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'report_date': self.report_date,
            'revenue': self.revenue,
            'net_profit': self.net_profit,
            'roe': self.roe,
            'eps': self.eps,
            'debt_ratio': self.debt_ratio,
            'gross_margin': self.gross_margin,
            'net_margin': self.net_margin,
            'operating_cash_flow': self.operating_cash_flow,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
        }


@dataclass
class FundProfile:
    """基金基本档案"""
    fund_code: str
    fund_name: str
    fund_type: str
    nav: float
    acc_nav: float
    nav_date: str
    daily_return: float
    fund_size: float
    management_fee: float
    custody_fee: float
    manager_name: str
    establishment_date: str
    risk_level: str
    source: str
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'FundProfile':
        return cls(
            fund_code=data.get('fund_code', ''),
            fund_name=data.get('fund_name', ''),
            fund_type=data.get('fund_type', ''),
            nav=data.get('nav', 0.0),
            acc_nav=data.get('acc_nav', 0.0),
            nav_date=data.get('nav_date', ''),
            daily_return=data.get('daily_return', 0.0),
            fund_size=data.get('fund_size', 0.0),
            management_fee=data.get('management_fee', 0.0),
            custody_fee=data.get('custody_fee', 0.0),
            manager_name=data.get('manager_name', ''),
            establishment_date=data.get('establishment_date', ''),
            risk_level=data.get('risk_level', ''),
            source=data.get('source', 'unknown'),
            timestamp=_parse_timestamp(data.get('timestamp')),
        )

    def to_dict(self) -> dict:
        return {
            'fund_code': self.fund_code,
            'fund_name': self.fund_name,
            'fund_type': self.fund_type,
            'nav': self.nav,
            'acc_nav': self.acc_nav,
            'nav_date': self.nav_date,
            'daily_return': self.daily_return,
            'fund_size': self.fund_size,
            'management_fee': self.management_fee,
            'custody_fee': self.custody_fee,
            'manager_name': self.manager_name,
            'establishment_date': self.establishment_date,
            'risk_level': self.risk_level,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
        }
