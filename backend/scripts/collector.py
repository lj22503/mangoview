"""
数据采集脚本 - 基于 akshare 采集宏观/行业数据
定时任务：
- 每月 15-20 日：采集宏观数据（PMI/CPI/GDP/PPI/M2）
- 每月月末：采集行业估值数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime
import sqlite3
import os
import sys

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models.database import DATABASE_URL, init_db, SessionLocal, MacroIndicator, NorthMoneyFlow


def collect_macro_data():
    """采集宏观数据"""
    print(f"[{datetime.now()}] 开始采集宏观数据...")

    session = SessionLocal()

    try:
        # PMI
        try:
            pmi_df = ak.macro_china_pmi()
            if len(pmi_df) > 0:
                latest = pmi_df.iloc[-1]
                record = MacroIndicator(
                    indicator_name="基钦",
                    indicator_code="PMI",
                    current_value=float(latest.iloc[1]),
                    previous_value=float(pmi_df.iloc[-2].iloc[1]) if len(pmi_df) > 1 else float(latest.iloc[1]),
                    direction="up" if latest.iloc[1] > pmi_df.iloc[-2].iloc[1] else "down",
                    historical_percentile=65.0,
                    data_date=datetime.strptime(str(latest.iloc[0])[:10], "%Y-%m-%d").date(),
                    source="国家统计局"
                )
                session.add(record)
                print(f"  PMI: {latest.iloc[1]}")
        except Exception as e:
            print(f"  PMI 采集失败: {e}")

        # CPI
        try:
            cpi_df = ak.macro_china_cpi()
            if len(cpi_df) > 0:
                latest = cpi_df.iloc[-1]
                record = MacroIndicator(
                    indicator_name="通胀",
                    indicator_code="CPI",
                    current_value=float(latest.iloc[1]),
                    previous_value=float(cpi_df.iloc[-2].iloc[1]) if len(cpi_df) > 1 else float(latest.iloc[1]),
                    direction="up",
                    historical_percentile=58.0,
                    data_date=datetime.strptime(str(latest.iloc[0])[:10], "%Y-%m-%d").date(),
                    source="国家统计局"
                )
                session.add(record)
                print(f"  CPI: {latest.iloc[1]}")
        except Exception as e:
            print(f"  CPI 采集失败: {e}")

        # GDP
        try:
            gdp_df = ak.macro_china_gdp()
            if len(gdp_df) > 0:
                latest = gdp_df.iloc[-1]
                record = MacroIndicator(
                    indicator_name="增长",
                    indicator_code="GDP",
                    current_value=float(latest.iloc[1]),
                    previous_value=float(gdp_df.iloc[-2].iloc[1]) if len(gdp_df) > 1 else float(latest.iloc[1]),
                    direction="up",
                    historical_percentile=62.0,
                    data_date=datetime.now().date(),
                    source="国家统计局"
                )
                session.add(record)
                print(f"  GDP: {latest.iloc[1]}")
        except Exception as e:
            print(f"  GDP 采集失败: {e}")

        session.commit()
        print(f"[{datetime.now()}] 宏观数据采集完成")

    except Exception as e:
        session.rollback()
        print(f"[{datetime.now()}] 宏观数据采集失败: {e}")
    finally:
        session.close()


def collect_north_money():
    """采集北向资金数据"""
    print(f"[{datetime.now()}] 开始采集北向资金数据...")

    session = SessionLocal()

    try:
        df = ak.stock_hsgt_hist_em()
        if len(df) > 0:
            latest = df.iloc[-1]
            record = NorthMoneyFlow(
                date=datetime.strptime(str(latest.iloc[0])[:10], "%Y-%m-%d").date(),
                net_buy=float(latest.iloc[1]),
                buy_amount=float(latest.iloc[2]),
                sell_amount=float(latest.iloc[3]),
                cumulative_net_buy=float(latest.iloc[4]),
                hs300_change=float(latest.iloc[10]) if len(latest) > 10 else 0.0,
                source="东方财富"
            )
            session.add(record)
            session.commit()
            print(f"[{datetime.now()}] 北向资金采集完成: {latest.iloc[1]}")
        else:
            print(f"[{datetime.now()}] 北向资金数据为空")

    except Exception as e:
        session.rollback()
        print(f"[{datetime.now()}] 北向资金采集失败: {e}")
    finally:
        session.close()


def run_all():
    """运行所有采集任务"""
    init_db()
    collect_macro_data()
    collect_north_money()
    print(f"[{datetime.now()}] 所有采集任务完成")


if __name__ == "__main__":
    run_all()