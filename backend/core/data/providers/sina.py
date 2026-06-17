#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新浪财经数据源 - 个股/指数实时行情

无需 API Key
接口：http://hq.sinajs.cn/
"""

import re
import requests
from typing import List, Dict
from datetime import datetime
from data_layer.exceptions import ProviderError


def _to_sina_code(symbol: str) -> str:
    """转换为新浪代码格式"""
    symbol = symbol.upper().strip()
    INDEX_MAP = {
        '000001.SH': 's_sh000001',
        '399001.SZ': 's_sz399001',
        '399006.SZ': 's_sz399006',
        '000300.SH': 's_sh000300',
    }
    if symbol in INDEX_MAP:
        return INDEX_MAP[symbol]
    if '.SH' in symbol:
        return f'sh{symbol.replace(".SH", "")}'
    elif '.SZ' in symbol:
        return f'sz{symbol.replace(".SZ", "")}'
    return f'sh{symbol}' if symbol.startswith('6') else f'sz{symbol}'


def get_quote(symbol: str, timeout: int = 5) -> Dict:
    """获取新浪个股行情

    Args:
        symbol: 股票代码（如 600519.SH）
        timeout: 超时秒数

    Returns:
        dict: {symbol, price, change, change_percent, volume, ...}
    """
    sina_code = _to_sina_code(symbol)
    url = f"http://hq.sinajs.cn/list={sina_code}"

    try:
        resp = requests.get(url, timeout=timeout, headers={
            'Referer': 'http://finance.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0',
        })
        resp.raise_for_status()
        resp.encoding = 'gbk'
        text = resp.text.strip()
        if not text:
            raise ProviderError('sina', '返回空数据')

        match = re.search(r'var hq_str_\w+="(.*?)"', text)
        if not match:
            raise ProviderError('sina', '解析失败')

        fields = match.group(1).split(',')
        if len(fields) < 10:
            raise ProviderError('sina', '字段不足')

        open_price = float(fields[1]) if fields[1] else 0.0
        prev_close = float(fields[2]) if fields[2] else 0.0
        price = float(fields[3]) if fields[3] else 0.0
        high = float(fields[4]) if fields[4] else 0.0
        low = float(fields[5]) if fields[5] else 0.0
        volume = int(float(fields[8])) if fields[8] else 0
        turnover = float(fields[9]) if fields[9] else 0.0

        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0.0

        return {
            'symbol': symbol,
            'price': price,
            'change': round(change, 4),
            'change_percent': round(change_pct, 2),
            'volume': volume,
            'turnover': turnover,
            'market_cap': 0.0,
            'pe': 0.0,
            'pb': 0.0,
            'high': high,
            'low': low,
            'open': open_price,
            'prev_close': prev_close,
            'source': 'sina',
            'timestamp': datetime.now().isoformat(),
        }
    except requests.RequestException as e:
        raise ProviderError('sina', f'请求失败: {e}')


def get_indices(symbols: List[str] = None, timeout: int = 5) -> Dict[str, Dict]:
    """获取新浪大盘指数（批量）

    Returns:
        dict: {symbol: {price, change, change_percent, ...}}
    """
    if symbols is None:
        symbols = ['000001.SH', '399001.SZ', '399006.SZ']

    sina_codes = [_to_sina_code(s) for s in symbols]
    url = f"http://hq.sinajs.cn/list={','.join(sina_codes)}"

    try:
        resp = requests.get(url, timeout=timeout, headers={
            'Referer': 'http://finance.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0',
        })
        resp.raise_for_status()
        resp.encoding = 'gbk'

        reverse_map = dict(zip(sina_codes, symbols))
        results = {}

        for match in re.finditer(r'var hq_str_(\w+)="(.*?)"', resp.text):
            code, data = match.group(1), match.group(2)
            fields = data.split(',')
            if len(fields) < 4:
                continue
            symbol = reverse_map.get(code, code)
            open_price = float(fields[1]) if fields[1] else 0.0
            prev_close = float(fields[2]) if fields[2] else 0.0
            price = float(fields[3]) if fields[3] else 0.0
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0.0

            results[symbol] = {
                'price': price,
                'change': round(change, 2),
                'change_percent': round(change_pct, 2),
                'open': open_price,
                'prev_close': prev_close,
                'source': 'sina',
            }

        return results
    except requests.RequestException as e:
        raise ProviderError('sina', f'请求失败: {e}')


if __name__ == '__main__':
    import json
    q = get_quote('600519.SH')
    print(json.dumps(q, ensure_ascii=False, indent=2))
