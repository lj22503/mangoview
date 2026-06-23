"""
每日数据采集脚本
每天定时跑一次，采集能稳定获取的数据存入 SQLite
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import akshare as ak
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, date
import math

from app.models.database import (
    NorthMoneyFlow, MacroIndicator, init_db, SessionLocal
)


def safe_float(val, default=None):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def fetch_with_timeout(func, timeout=5, default=None):
    result = [default]
    error = [None]

    def target():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e

    import threading
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return default, True
    if error[0]:
        return default, False
    return result[0], False


def collect_north_money(db: Session) -> int:
    """采集北向资金历史数据"""
    val, timed_out = fetch_with_timeout(
        lambda: ak.stock_hsgt_hist_em(), timeout=10
    )
    count = 0
    if val is not None and not timed_out and len(val) > 0:
        for _, row in val.iterrows():
            try:
                trade_date = pd.to_datetime(row['日期']).date()
                net_buy = safe_float(row.get('当日成交净买额'))
                if net_buy is None:
                    continue  # 数据为空跳过
                existing = db.query(NorthMoneyFlow).filter(
                    NorthMoneyFlow.date == trade_date
                ).first()
                if existing:
                    continue
                record = NorthMoneyFlow(
                    date=trade_date,
                    net_buy=net_buy,
                    buy_amount=safe_float(row.get('买入成交额')),
                    sell_amount=safe_float(row.get('卖出成交额')),
                    cumulative_net_buy=safe_float(row.get('历史累计净买额')),
                    hs300_change=safe_float(row.get('沪深300-涨跌幅')),
                    source='akshare',
                    updated_at=datetime.now()
                )
                db.add(record)
                count += 1
            except Exception:
                continue
        db.commit()
    return count


def collect_north_summary(db: Session) -> int:
    """采集北向资金汇总（最新交易日）"""
    val, timed_out = fetch_with_timeout(
        lambda: ak.stock_hsgt_fund_flow_summary_em(), timeout=5
    )
    count = 0
    if val is not None and not timed_out and len(val) > 0:
        for _, row in val.iterrows():
            try:
                trade_date = pd.to_datetime(row['交易日']).date()
                net_buy = safe_float(row.get('成交净买额'))
                if net_buy is None:
                    continue  # 数据为空才跳过，0是有效数据
                direction = row.get('资金方向', '')
                if direction != '北向':
                    continue  # 只记录北向资金
                existing = db.query(NorthMoneyFlow).filter(
                    NorthMoneyFlow.date == trade_date
                ).first()
                if existing:
                    existing.net_buy = net_buy
                    existing.hs300_change = safe_float(row.get('指数涨跌幅'))
                    existing.updated_at = datetime.now()
                    count += 1
                else:
                    record = NorthMoneyFlow(
                        date=trade_date,
                        net_buy=net_buy,
                        buy_amount=safe_float(row.get('资金净流入')),
                        sell_amount=0.0,
                        cumulative_net_buy=0.0,
                        hs300_change=safe_float(row.get('指数涨跌幅')),
                        source='akshare-summary',
                        updated_at=datetime.now()
                    )
                    db.add(record)
                    count += 1
            except Exception:
                continue
        db.commit()
    return count


def collect_macro(db: Session) -> int:
    """采集宏观数据"""
    indicators = []

    # PMI
    val, timed_out = fetch_with_timeout(lambda: ak.macro_china_pmi(), timeout=5)
    if val is not None and not timed_out and len(val) > 0:
        latest = val.iloc[-1]
        indicators.append({
            'name': 'PMI', 'code': 'PMI',
            'current': safe_float(latest.iloc[1]),
            'previous': safe_float(val.iloc[-2].iloc[1]) if len(val) > 1 else None,
            'source': '国家统计局'
        })

    # CPI
    val, timed_out = fetch_with_timeout(lambda: ak.macro_china_cpi(), timeout=5)
    if val is not None and not timed_out and len(val) > 0:
        latest = val.iloc[-1]
        indicators.append({
            'name': 'CPI', 'code': 'CPI',
            'current': safe_float(latest.iloc[1]),
            'previous': safe_float(val.iloc[-2].iloc[1]) if len(val) > 1 else None,
            'source': '国家统计局'
        })

    # GDP
    val, timed_out = fetch_with_timeout(lambda: ak.macro_china_gdp(), timeout=5)
    if val is not None and not timed_out and len(val) > 0:
        latest = val.iloc[-1]
        indicators.append({
            'name': 'GDP', 'code': 'GDP',
            'current': safe_float(latest.iloc[1]),
            'previous': safe_float(val.iloc[-2].iloc[1]) if len(val) > 1 else None,
            'source': '国家统计局'
        })

    # PPI
    val, timed_out = fetch_with_timeout(lambda: ak.macro_china_ppi(), timeout=5)
    if val is not None and not timed_out and len(val) > 0:
        latest = val.iloc[-1]
        indicators.append({
            'name': 'PPI', 'code': 'PPI',
            'current': safe_float(latest.iloc[1]),
            'previous': safe_float(val.iloc[-2].iloc[1]) if len(val) > 1 else None,
            'source': '国家统计局'
        })

    count = 0
    for ind in indicators:
        if ind['current'] is None:
            continue
        try:
            existing = db.query(MacroIndicator).filter(
                MacroIndicator.indicator_code == ind['code']
            ).order_by(MacroIndicator.data_date.desc()).first()

            if existing and existing.current_value == ind['current']:
                continue # 没更新，跳过

            record = MacroIndicator(
                indicator_name=ind['name'],
                indicator_code=ind['code'],
                current_value=ind['current'],
                previous_value=ind.get('previous',0) or 0,
                direction='up' if ind['current'] > (ind.get('previous') or 0) else 'down',
                historical_percentile=50.0,
                data_date=date.today(),
                source=ind['source'],
                updated_at=datetime.now()
            )
            db.add(record)
            count += 1
        except Exception:
            continue
    db.commit()
    return count


def main():
    init_db()
    db = SessionLocal()
    print(f"[{datetime.now().isoformat()}] 开始每日采集...")

    try:
        n1 = collect_north_money(db)
        print(f"  北向资金历史: 新增 {n1} 条")
    except Exception as e:
        print(f"  北向资金历史: 失败 - {e}")

    try:
        n2 = collect_north_summary(db)
        print(f"  北向资金汇总: 新增 {n2} 条")
    except Exception as e:
        print(f"  北向资金汇总: 失败 - {e}")

    try:
        n3 = collect_macro(db)
        print(f"  宏观指标: 新增 {n3} 条")
    except Exception as e:
        print(f"  宏观指标: 失败 - {e}")


    # ── 采集完成后自动生成日报 ──
    from app.services.report_service import generate_report
    db2 = SessionLocal()
    try:
        report = generate_report("daily", db2)
        print(f"  日报已生成: id={report.id}, title={report.title}")
    except Exception as e:
        print(f"  日报生成失败: {e}")
    finally:
        db2.close()

    db.close()
    print(f"[{datetime.now().isoformat()}] 采集完成")


    main()
