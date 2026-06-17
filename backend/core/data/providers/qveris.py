#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QVeris 数据源 - 北向资金、宏观经济、行业资金流向"""

import os
import json
import requests

QVERIS_BASE_URL = 'https://open.qveris.com/api/v1'

def _get_api_key():
    key = os.environ.get('QVERIS_API_KEY', '')
    if not key:
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('QVERIS_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        break
    return key


def _call_tool(tool_name, params):
    """调用 QVeris 工具 API
    
    Args:
        tool_name: 工具名称
        params: 参数字典
    
    Returns:
        dict: API 响应
    """
    api_key = _get_api_key()
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'tool': tool_name,
        'params': params
    }
    resp = requests.post(
        f'{QVERIS_BASE_URL}/tools/call',
        headers=headers,
        json=payload,
        timeout=30
    )
    return resp.json()


def get_northbound(date=None):
    """获取北向资金数据（沪深港通）
    
    Args:
        date: 日期，默认最近交易日
    
    Returns:
        dict: 北向资金数据
    """
    params = {}
    if date:
        params['date'] = date
    return _call_tool('ths_ifind.hk_connect_stats.v1', params)


def get_macro(indicator, start_date=None, end_date=None):
    """获取宏观经济数据
    
    Args:
        indicator: 指标名（gdp/cpi/pmi 等）
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        dict: 宏观数据
    """
    params = {'indicator': indicator}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    return _call_tool('ths_ifind.macro_china.v1', params)


def get_industry_flow(scope='sector'):
    """获取行业资金流向
    
    Args:
        scope: 范围（sector/stock）
    
    Returns:
        dict: 资金流向数据
    """
    return _call_tool('ths_ifind.money_flow.v1', {'scope': scope})


def get_stock_history(code, start_date, end_date):
    """获取个股历史行情
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        dict: 历史行情数据
    """
    return _call_tool('fast_fin.history_quotation.v1', {
        'code': code,
        'start_date': start_date,
        'end_date': end_date
    })


if __name__ == '__main__':
    print('=== 北向资金 ===')
    data = get_northbound()
    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
