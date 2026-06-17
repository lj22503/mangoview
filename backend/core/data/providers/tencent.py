#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯财经数据源 - 大盘指数 + 个股行情

无需 API Key，数据实时
接口：http://qt.gtimg.cn/
"""

import re
import requests
from datetime import datetime
from typing import List, Dict
from data_layer.exceptions import ProviderError

# 指数代码映射（中文名 → 腾讯代码）
INDEX_CODES = {
    '上证指数': 'sh000001',
    '深证成指': 'sz399001',
    '创业板指': 'sz399006',
    '沪深300': 'sh000300',
    '科创50': 'sh000688',
    '中证500': 'sh000905',
    '中证1000': 'sh000852',
}

# symbol → 腾讯代码（个股/指数通用）
SYMBOL_INDEX_MAP = {
    '000001.SH': 'sh000001',
    '399001.SZ': 'sz399001',
    '399006.SZ': 'sz399006',
    '000300.SH': 'sh000300',
}


def _to_tencent_code(symbol):
    """转换为腾讯代码格式"""
    s = symbol.upper().strip()
    if s in SYMBOL_INDEX_MAP:
        return SYMBOL_INDEX_MAP[s]
    if '.SH' in s:
        return 'sh' + s.replace('.SH', '')
    elif '.SZ' in s:
        return 'sz' + s.replace('.SZ', '')
    return ('sh' + s) if s.startswith('6') else ('sz' + s)


def _parse_fields(text):
    """解析腾讯行情返回文本，提取所有 v_xxx="..." 段"""
    results = []
    for m in re.finditer(r'v_(\w+)="(.*?)"', text):
        code = m.group(1)
        fields = m.group(2).split('~')
        results.append((code, fields))
    return results


def get_indices(codes=None):
    """获取大盘指数实时行情

    Args:
        codes: 指数名称列表，默认获取全部

    Returns:
        dict: {指数名: {code, price, pre_close, open, change, change_pct, volume, source, status}}
    """
    if codes is None:
        codes = list(INDEX_CODES.keys())

    query_codes = [INDEX_CODES[name] for name in codes if name in INDEX_CODES]
    if not query_codes:
        return {}

    url = 'http://qt.gtimg.cn/q={}'.format(','.join(query_codes))
    resp = requests.get(url, timeout=10)
    resp.encoding = 'gbk'

    results = {}
    for code, parts in _parse_fields(resp.text):
        if len(parts) < 45:
            continue

        name = parts[1]
        price = float(parts[3]) if parts[3] else 0
        pre_close = float(parts[4]) if parts[4] else 0
        open_price = float(parts[5]) if parts[5] else 0
        volume = int(parts[6]) if parts[6] else 0

        change = price - pre_close if pre_close > 0 else 0
        change_pct = (change / pre_close * 100) if pre_close > 0 else 0

        results[name] = {
            'code': parts[2],
            'price': price,
            'pre_close': pre_close,
            'open': open_price,
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'volume': volume,
            'source': '腾讯财经',
            'status': 'trading' if price != pre_close else 'closed',
        }

    return results


def get_quote(symbol, timeout=10):
    """获取个股实时行情

    Args:
        symbol: 股票代码（如 600519.SH, 000001.SZ）
        timeout: 超时秒数

    Returns:
        dict: {symbol, price, change, change_percent, volume, turnover, high, low, open, prev_close, ...}
    """
    tc = _to_tencent_code(symbol)
    url = 'http://qt.gtimg.cn/q={}'.format(tc)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.encoding = 'gbk'
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ProviderError('tencent', '请求失败: {}'.format(e))

    items = _parse_fields(resp.text)
    if not items:
        raise ProviderError('tencent', '解析失败: 无数据')

    code, parts = items[0]
    if len(parts) < 45:
        raise ProviderError('tencent', '字段不足')

    price = float(parts[3]) if parts[3] else 0.0
    pre_close = float(parts[4]) if parts[4] else 0.0
    open_p = float(parts[5]) if parts[5] else 0.0
    volume = int(parts[6]) if parts[6] else 0
    turnover = float(parts[37]) if len(parts) > 37 and parts[37] else 0.0
    high = float(parts[33]) if len(parts) > 33 and parts[33] else 0.0
    low = float(parts[34]) if len(parts) > 34 and parts[34] else 0.0
    pe = float(parts[39]) if len(parts) > 39 and parts[39] else 0.0
    market_cap = float(parts[45]) if len(parts) > 45 and parts[45] else 0.0

    change = price - pre_close
    change_pct = (change / pre_close * 100) if pre_close > 0 else 0.0

    return {
        'symbol': symbol,
        'name': parts[1],
        'price': price,
        'change': round(change, 4),
        'change_percent': round(change_pct, 2),
        'volume': volume,
        'turnover': turnover,
        'market_cap': market_cap,
        'pe': pe,
        'pb': 0.0,
        'high': high,
        'low': low,
        'open': open_p,
        'prev_close': pre_close,
        'source': 'tencent',
        'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    }


if __name__ == '__main__':
    import json
    print('=== 大盘指数 ===')
    data = get_indices()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print('\n=== 个股 ===')
    q = get_quote('600519.SH')
    print(json.dumps(q, ensure_ascii=False, indent=2))
