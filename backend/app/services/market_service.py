"""市场数据服务 - DB优先 + 多源爬虫，新鲜度校验驱动"""
import math
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from ..models.database import (
    MacroIndicator, NorthMoneyFlow, IndustryInfo, IndustryFinancials,
    IndustryValuation
)


def safe_float(val, default=0.0):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def _is_fresh_monthly(date_str: str, lookback_months: int = 2) -> bool:
    """
    判断月度数据是否新鲜：数据月份 >= (当前月份 - lookback_months)。
    默认为 2 个月：PMI/CPI 等月频数据发布滞后1-2个月，
    所以4月数据到6月仍视为正常可用。
    date_str 格式如 "2026-05-01" 或 "2026-05"
    """
    try:
        if not date_str:
            return False
        ym = date_str[:7]
        data_month = datetime.strptime(ym, "%Y-%m")
        now = datetime.now()
        # 计算 (当前月 - lookback_months)
        target_month = now.month - lookback_months
        target_year = now.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        threshold = datetime(target_year, target_month, 1)
        return data_month >= threshold
    except (ValueError, TypeError):
        return False


def _is_fresh_quarterly(date_str: str) -> bool:
    """
    判断季度数据是否新鲜：本季度或上一季度。
    date_str 格式如 "2026-03-01"（Q1）或 "2026-Q1"
    季度数据由国家统计局发布，通常滞后1-2个月。
    """
    try:
        if not date_str:
            return False
        # 取年月
        ym = date_str[:7]
        data_month = datetime.strptime(ym, "%Y-%m")
        now = datetime.now()
        # 当前季度
        current_q_month = ((now.month - 1) // 3) * 3 + 1
        current_q = datetime(now.year, current_q_month, 1)
        # 上一季度
        prev_q_month = current_q_month - 3
        prev_q_year = current_q.year
        if prev_q_month <= 0:
            prev_q_month += 12
            prev_q_year -= 1
        prev_q = datetime(prev_q_year, prev_q_month, 1)
        return data_month >= prev_q
    except (ValueError, TypeError):
        return False


def _is_fresh_ndays(date_str: str, days: int = 7) -> bool:
    """判断数据是否在最近 N 天内。"""
    try:
        if not date_str:
            return False
        data_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        diff = (datetime.now() - data_date).days
        return 0 <= diff <= days
    except (ValueError, TypeError):
        return False


# ============================================================
# 东方财富宏观数据爬虫（内联，避免 data_layer 导入冲突）
# ============================================================
import importlib.util, os, sys

_eastmoney_path = os.path.join(os.path.dirname(__file__), "..", "..", "core", "data", "providers", "eastmoney.py")
_spec = importlib.util.spec_from_file_location("_eastmoney_fetcher", _eastmoney_path)
_em_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_em_mod)
_EastMoneyMacroFetcher = _em_mod.EastMoneyMacroFetcher


# ============================================================
# 宏观指标
# ============================================================

def fetch_macro_indicators(db: Session) -> dict:
    """
    从 DB 读宏观指标，无数据/数据过期时走东方财富 + akshare。
    每个指标返回 available 字段，标识数据是否新鲜。
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
            is_fresh = _is_fresh_monthly(date_str) or _is_fresh_quarterly(date_str)
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
    raw = _EastMoneyMacroFetcher.fetch_all()

    indicator_meta = [
        ("制造业PMI", "PMI",   "国家统计局",  _is_fresh_monthly),
        ("CPI",       "CPI",   "国家统计局",  _is_fresh_monthly),
        ("PPI",       "PPI",   "国家统计局",  _is_fresh_monthly),
        ("GDP增速",   "GDP",   "国家统计局",  _is_fresh_quarterly),
        ("M2增速",    "M2",    "中国人民银行", _is_fresh_monthly),
        ("社融增量",  "社融",  "中国人民银行", _is_fresh_monthly),
        ("社零增速",  "社零",  "国家统计局",  _is_fresh_monthly),
        ("出口增速",  "出口",  "海关总署",    _is_fresh_monthly),
        ("固投增速",  "固投",  "国家统计局",  _is_fresh_monthly),
    ]

    # 补充社融数据（akshare）
    social_financing_data = _fetch_social_financing()

    indicators = []
    for name, key, source, fresh_check in indicator_meta:
        # 社融单独处理
        if key == "社融":
            data = social_financing_data
        else:
            data = raw.get(key)

        is_fresh = data and data.get("value") is not None and fresh_check(data.get("date", ""))

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


def _fetch_social_financing() -> Optional[dict]:
    """
    通过 akshare 获取社融数据（东方财富无此指标）。
    社会融资规模增量：月末余额变动额近似用 当月值近似。
    """
    try:
        import akshare as ak
        import pandas as pd
        df = ak.macro_china_shrzgm()
        if df is None or len(df) == 0:
            return None
        # 列名：月份, 社会融资规模, ...
        # 取最新两行
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        date_str = str(latest.iloc[0])  # "202604"
        # 转换为 YYYY-MM-01
        if len(date_str) == 6:
            y = int(date_str[:4])
            m = int(date_str[4:6])
            date_fmt = f"{y}-{m:02d}-01"
        else:
            date_fmt = date_str[:10]
        # 社会融资规模在第2列
        current = safe_float(latest.iloc[1])
        previous = safe_float(prev.iloc[1])
        return {"date": date_fmt, "value": current, "prev_value": previous}
    except Exception:
        return None


# ============================================================
# 北向资金
# ============================================================

def fetch_north_money(db: Session) -> dict:
    """从 DB 读北向资金，无数据时降级到 akshare，7天内才算新鲜"""
    # 从 DB 读最新记录
    latest = db.query(NorthMoneyFlow).filter(
        NorthMoneyFlow.net_buy != None
    ).order_by(NorthMoneyFlow.date.desc()).first()

    if latest:
        today_records = db.query(NorthMoneyFlow).filter(
            NorthMoneyFlow.date == latest.date,
            NorthMoneyFlow.net_buy != None
        ).all()
        net_buy = sum(r.net_buy for r in today_records)
        buy_amount = sum(r.buy_amount or 0 for r in today_records)
        sell_amount = sum(r.sell_amount or 0 for r in today_records)
        return {
            "date": str(latest.date),
            "net_buy": net_buy,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "cumulative_net_buy": latest.cumulative_net_buy or 0.0,
            "hs300_change": latest.hs300_change or 0.0,
            "available": _is_fresh_ndays(str(latest.date), days=7),
            "updated_at": datetime.now().isoformat()
        }

    # DB 空，降级到 akshare
    try:
        import akshare as ak
        import pandas as pd
        val = ak.stock_hsgt_hist_em()
        if val is not None and len(val) > 0:
            for _, row in val.iloc[::-1].iterrows():
                net = safe_float(row.get('当日成交净买额'))
                date_str = str(row.iloc[0])[:10]
                if net is not None and net != 0:
                    return {
                        "date": date_str,
                        "net_buy": net,
                        "buy_amount": safe_float(row.get('买入成交额')),
                        "sell_amount": safe_float(row.get('卖出成交额')),
                        "cumulative_net_buy": safe_float(row.get('历史累计净买额')),
                        "hs300_change": safe_float(row.get('沪深300-涨跌幅')),
                        "available": _is_fresh_ndays(date_str, days=7),
                        "updated_at": datetime.now().isoformat()
                    }
    except Exception:
        pass

    # 7天内都没有数据 → available=False
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


# ============================================================
# 行业数据
# ============================================================

def fetch_industries(db: Session) -> dict:
    """行业板块数据 — DB 优先，无数据时返回 available=False"""
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

    # DB 无数据：禁止硬编码
    return {"industries": [], "available": False, "updated_at": datetime.now().isoformat()}
