#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tushare 数据源 - 个股日线、涨跌停、北向资金"""

import os
import tushare as ts

_pro = None

def _get_pro():
    global _pro
    if _pro is None:
        token = os.environ.get('TUSHARE_TOKEN', '')
        if not token:
            # 尝试从 .env 文件读取
            env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('TUSHARE_TOKEN='):
                            token = line.split('=', 1)[1].strip()
                            break
        ts.set_token(token)
        _pro = ts.pro_api()
    return _pro


def get_daily(ts_code, start_date, end_date):
    """获取个股日线行情
    
    Args:
        ts_code: 股票代码（如 000001.SZ）
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    
    Returns:
        DataFrame: 日线数据
    """
    pro = _get_pro()
    return pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)


def get_limit_list(trade_date, limit_type='U'):
    """获取涨跌停统计
    
    Args:
        trade_date: 交易日期 YYYYMMDD
        limit_type: U=涨停 D=跌停
    
    Returns:
        DataFrame: 涨跌停列表
    """
    pro = _get_pro()
    return pro.limit_list_d(trade_date=trade_date, limit_type=limit_type)


def get_northbound(start_date, end_date):
    """获取北向资金数据
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    
    Returns:
        DataFrame: 北向资金数据（沪股通/深股通）
    """
    pro = _get_pro()
    return pro.moneyflow_hsgt(start_date=start_date, end_date=end_date)


def get_stock_list():
    """获取A股股票列表
    
    Returns:
        DataFrame: 股票列表（代码、名称、行业等）
    """
    pro = _get_pro()
    return pro.stock_basic(
        exchange='', list_status='L',
        fields='ts_code,symbol,name,area,industry,market,list_date'
    )


if __name__ == '__main__':
    # 测试
    print('=== 北向资金 ===')
    df = get_northbound('20260320', '20260325')
    print(df.to_string())
    
    print('\n=== 涨停股 ===')
    df = get_limit_list('20260324', 'U')
    print(f'涨停数: {len(df)}')
    print(df.head(5).to_string())
