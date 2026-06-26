"""市场数据服务 - DB优先 + 东方财富，新鲜度校验驱动"""
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import math
from datetime import datetime, date
from sqlalchemy.orm import Session

from ..models.database import (
    MacroIndicator, NorthMoneyFlow, IndustryInfo, IndustryFinancials,
    IndustryValuation
)
import importlib.util, sys, os
_eastmoney_path = os.path.join(os.path.dirname(__file__), "..", "..", "core", "data", "providers", "eastmoney.py")
_spec = importlib.util.spec_from_file_location("eastmoney_macro", _eastmoney_path)
_eastmoney_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_eastmoney_mod)
EastMoneyMacroFetcher = _eastmoney_mod.EastMoneyMacroFetcher


def safe_float(val, default=0.0):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def _is_fresh_monthly(date_str: str) -> bool:
    """
    判断月度数据是否新鲜：必须在当前月或上月。
    date_str 格式如 "2026-05-01" 或 "2026-05"
    """
    try:
        if not date_str:
            return False
        # 取年月部分
        ym = date_str[:7]  # "2026-05"
        data_month = datetime.strptime(ym, "%Y-%m")
        now = datetime.now()
        current_month = datetime(now.year, now.month, 1)
        last_month = datetime(
            (now.month == 1 and now.year - 1 or now.year),
            (now.month == 1 and 12 or now.month - 1),
            1
        )
        return data_month >= last_month
    except (ValueError, TypeError):
        return False


# 全局线程池（复用，避免遗留 daemon 线程）
_executor = ThreadPoolExecutor(max_workers=2)


def fetch_with_timeout(func, timeout=5, default=None):
    future = _executor.submit(func)
    try:
        return future.result(timeout=timeout), False
    except FutureTimeoutError:
        return default, True
    except Exception:
        return default, False


def fetch_macro_indicators(db: Session) -> dict:
    """
    从 DB 读宏观指标，无数据/数据过期时走东方财富。
    返回的每个指标包含 available 字段，标识数据是否新鲜（当前月或上月）。
    """
    codes = ['PMI', 'CPI', 'PPI', 'GDP', 'M2', '社融', '社零', '出口', '固投']

    # 先从 DB 读最新记录
    db_recs = db.query(MacroIndicator).order_by(
        MacroIndicator.data_date.desc()
    ).limit(9).all()

    indicator_map = {r.indicator_code: r for r in db_recs}
    have_all = all(c in indicator_map for c in codes)

    if have_all:
        indicators = []
        for code in codes:
            r = indicator_map[code]
            date_str = str(r.data_date)[:10]
            is_fresh = _is_fresh_monthly(date_str)
            indicators.append({
                "name": r.indicator_name,
                "current": r.current_value,
                "previous": r.previous_value,
                "direction": r.direction,
                "percentile": r.historical_percentile,
                "date": date_str,
                "source": r.source,
                "available": is_fresh,
            })
        return {"indicators": indicators, "updated_at": datetime.now().isoformat()}

    # DB 数据不全或过期，降级到东方财富
    raw = EastMoneyMacroFetcher.fetch_all()

    indicator_meta = [
        ("制造业PMI", "PMI",   "国家统计局"),
        ("CPI",       "CPI",   "国家统计局"),
        ("PPI",       "PPI",   "国家统计局"),
        ("GDP增速",   "GDP",   "国家统计局"),
        ("M2增速",    "M2",    "中国人民银行"),
        ("社融增量",  "社融",  "中国人民银行"),
        ("社零增速",  "社零",  "国家统计局"),
        ("出口增速",  "出口",  "海关总署"),
        ("固投增速",  "固投",  "国家统计局"),
    ]

    indicators = []
    for name, key, source in indicator_meta:
        data = raw.get(key)
        is_fresh = data and data.get("value") is not None and _is_fresh_monthly(data.get("date", ""))

        if data and data.get("value") is not None and is_fresh:
            current = data["value"]
            previous = data["prev_value"]
            direction = "up" if current > previous else ("down" if current < previous else "flat")
            indicators.append({
                "name": name,
                "current": current,
                "previous": previous,
                "direction": direction,
                "percentile": 50.0,
                "date": data.get("date", ""),
                "source": source,
                "available": True,
            })
        else:
            # 生产环境禁止硬编码：数据不可用时返回 available=False
            indicators.append({
                "name": name,
                "current": None,
                "previous": None,
                "direction": "flat",
                "percentile": None,
                "date": data.get("date", "") if data else "",
                "source": source,
                "available": False,
            })

    return {"indicators": indicators, "updated_at": datetime.now().isoformat()}


def fetch_north_money(db: Session) -> dict:
    """从 DB 读北向资金，无数据时降级"""
    # 从 DB 读最新记录
    latest = db.query(NorthMoneyFlow).filter(
        NorthMoneyFlow.net_buy != None
    ).order_by(NorthMoneyFlow.date.desc()).first()

    if latest:
        # 聚合今日所有北向记录
        today_records = db.query(NorthMoneyFlow).filter(
            NorthMoneyFlow.date == latest.date,
            NorthMoneyFlow.net_buy != None
        ).all()
        net_buy = sum(r.net_buy for r in today_records)
        buy_amount = sum(r.buy_amount or 0 for r in today_records)
        sell_amount = sum(r.sell_amount or 0 for r in today_records)
        hs300_change = latest.hs300_change or 0.0
        return {
            "date": str(latest.date),
            "net_buy": net_buy,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "cumulative_net_buy": latest.cumulative_net_buy or 0.0,
            "hs300_change": hs300_change,
            "updated_at": datetime.now().isoformat()
        }

    # DB 空，降级到 akshare 北向资金
    import akshare as ak
    val, timed_out = fetch_with_timeout(
        lambda: ak.stock_hsgt_hist_em(), timeout=8
    )
    if val is not None and not timed_out and len(val) > 0:
        for _, row in val.iloc[::-1].iterrows():
            net = safe_float(row.get('当日成交净买额'))
            if net is not None and net != 0:
                return {
                    "date": str(row['日期'])[:10],
                    "net_buy": net,
                    "buy_amount": safe_float(row.get('买入成交额')),
                    "sell_amount": safe_float(row.get('卖出成交额')),
                    "cumulative_net_buy": safe_float(row.get('历史累计净买额')),
                    "hs300_change": safe_float(row.get('沪深300-涨跌幅')),
                    "updated_at": datetime.now().isoformat()
                }

    # 北向资金也无法获取时，available=False
    return {
        "date": "",
        "net_buy": None,
        "buy_amount": None,
        "sell_amount": None,
        "cumulative_net_buy": None,
        "hs300_change": None,
        "available": False,
        "updated_at": datetime.now().isoformat()
    }


def fetch_industries(db: Session) -> dict:
    """行业板块数据 — DB 优先，无数据时返回 available=False"""
    # 1. DB 优先
    db_industries = db.query(IndustryInfo).all()
    if db_industries:
        result = []
        for info in db_industries:
            fin = db.query(IndustryFinancials).filter(
                IndustryFinancials.industry_code == info.industry_code
            ).order_by(IndustryFinancials.year.desc(), IndustryFinancials.quarter.desc()).first()
            val = db.query(IndustryValuation).filter(
                IndustryValuation.industry_code == info.industry_code
            ).order_by(IndustryValuation.stat_date.desc()).first()
            result.append({
                "code": info.industry_code,
                "name": info.industry_name,
                "cycle_stage": info.cycle_stage or "未知",
                "penetration": info.penetration or 0.0,
                "cr3": info.cr3 or 0.0,
                "pe_percentile": val.pe_percentile if val else 0.0,
                "net_profit_growth": fin.net_profit_growth if fin else 0.0,
                "weight": round(1.0 / len(db_industries), 4)
            })
        return {"industries": result, "updated_at": datetime.now().isoformat()}

    # 2. DB 无数据：禁止硬编码，返回 available=False
    return {"industries": [], "available": False, "updated_at": datetime.now().isoformat()}
