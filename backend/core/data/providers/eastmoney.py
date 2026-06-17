#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富数据源 - 个股行情 + 财报数据

无需 API Key
接口：https://push2.eastmoney.com/, https://datacenter.eastmoney.com/
"""

import requests
from datetime import datetime
from typing import Dict
from data_layer.exceptions import ProviderError


def _safe_float(value, default: float = 0.0) -> float:
    """安全转换为 float"""
    if value is None or value == '' or value == '--':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _to_secid(symbol: str) -> str:
    """转换为东方财富 secid 格式（1.600519 / 0.000001）"""
    code = symbol.upper().replace('.SH', '').replace('.SZ', '')
    return f"1.{code}" if code.startswith('6') or code.startswith('1') else f"0.{code}"


def _to_secucode(symbol: str) -> str:
    """转换为东方财富 secucode 格式（600519.SH）"""
    s = symbol.upper().strip()
    if '.SH' in s or '.SZ' in s:
        return s
    return f"{s}.SH" if s.startswith('6') else f"{s}.SZ"


def get_quote(symbol: str, timeout: int = 5) -> Dict:
    """获取东方财富个股行情

    Args:
        symbol: 股票代码（如 600519.SH）
        timeout: 超时秒数

    Returns:
        dict: 行情数据
    """
    secid = _to_secid(symbol)
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        'secid': secid,
        'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f60',
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get('rc') != 0 or not data.get('data'):
            raise ProviderError('eastmoney', '返回数据为空或错误')

        d = data['data']
        price = (d.get('f43') or 0) / 100
        prev_close = (d.get('f60') or 0) / 100
        change = price - prev_close
        change_pct = (d.get('f44') or 0) / 100 if d.get('f44') else (change / prev_close * 100 if prev_close > 0 else 0)

        return {
            'symbol': symbol,
            'price': price,
            'change': round(change, 4),
            'change_percent': round(change_pct, 2),
            'volume': d.get('f47', 0),
            'turnover': d.get('f48', 0.0),
            'market_cap': d.get('f55', 0.0),
            'pe': (d.get('f49') or 0) / 100 if d.get('f49') else 0.0,
            'pb': (d.get('f50') or 0) / 100 if d.get('f50') else 0.0,
            'high': (d.get('f51') or 0) / 100,
            'low': (d.get('f52') or 0) / 100,
            'open': (d.get('f46') or 0) / 100,
            'prev_close': prev_close,
            'source': 'eastmoney',
            'timestamp': datetime.now().isoformat(),
        }
    except requests.RequestException as e:
        raise ProviderError('eastmoney', f'请求失败: {e}')
    except (KeyError, ValueError, TypeError) as e:
        raise ProviderError('eastmoney', f'解析失败: {e}')


def get_financials(symbol: str, timeout: int = 5) -> Dict:
    """获取东方财富财报数据

    Args:
        symbol: 股票代码
        timeout: 超时秒数

    Returns:
        dict: 财报数据
    """
    secucode = _to_secucode(symbol)
    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    params = {
        'reportName': 'RPT_F10_FINANCE_MAINFINADATA',
        'columns': 'SECUCODE,SECURITY_CODE,REPORT_DATE,EPSJB,PARENTNETPROFIT,ROEJQ,OPERATE_INCOME_PK,NETCASH_OPERATE_PK',
        'filter': f'(SECUCODE="{secucode}")',
        'pageNumber': '1',
        'pageSize': '4',
        'sortTypes': '-1',
        'sortColumns': 'REPORT_DATE',
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        if not data.get('success') or not data.get('result') or not data['result'].get('data'):
            raise ProviderError('eastmoney', f'财报数据为空：{data.get("message", "未知错误")}')

        latest = data['result']['data'][0]

        return {
            'symbol': symbol,
            'report_date': latest.get('REPORT_DATE', '')[:10] if latest.get('REPORT_DATE') else '',
            'revenue': float(latest.get('OPERATE_INCOME_PK', 0) or 0),
            'net_profit': float(latest.get('PARENTNETPROFIT', 0) or 0),
            'roe': float(latest.get('ROEJQ', 0) or 0),
            'eps': float(latest.get('EPSJB', 0) or 0),
            'operating_cash_flow': float(latest.get('NETCASH_OPERATE_PK', 0) or 0),
            'source': 'eastmoney',
            'timestamp': datetime.now().isoformat(),
        }
    except requests.RequestException as e:
        raise ProviderError('eastmoney', f'请求失败: {e}')
    except (KeyError, ValueError, TypeError, IndexError) as e:
        raise ProviderError('eastmoney', f'解析失败: {e}')


if __name__ == '__main__':
    import json
    q = get_quote('600519.SH')
    print(json.dumps(q, ensure_ascii=False, indent=2))


# ============================================================
# 行业板块行情（东方财富）
# ============================================================

def fetch_sector_performance(timeout: int = 10) -> Dict:
    """
    获取行业板块涨跌幅排行
    
    来源：东方财富行业板块
    
    Args:
        timeout: 超时秒数
    
    Returns:
        dict: {
            'top_sectors': [{'name': '银行', 'change': 3.5}, ...],
            'bottom_sectors': [{'name': '计算机', 'change': -5.2}, ...]
        }
    """
    # 东方财富行业板块 API
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        'pn': '1',
        'pz': '100',
        'po': '1',
        'np': '1',
        'ut': 'bd1d9dff06b34768984bfef77040bd9f',
        'fltt': '2',
        'invt': '2',
        'fid': 'f3',
        'fs': 'm:90 t:3',
        'fields': 'f12,f14,f3,f2',
    }
    
    try:
        resp = requests.get(url, params=params, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        resp.raise_for_status()
        data = resp.json()
        
        if data.get('data', {}).get('diff', None) is None:
            return {'top_sectors': [], 'bottom_sectors': []}
        
        items = data['data']['diff']
        
        # 解析板块数据
        sectors = []
        for item in items:
            name = item.get('f14', '')  # 板块名称
            change = _safe_float(item.get('f3', 0))  # 涨跌幅
            if name and change != 0:
                sectors.append({
                    'name': name,
                    'change': change,
                    'code': item.get('f12', ''),
                })
        
        # 排序
        sectors_sorted = sorted(sectors, key=lambda x: x['change'], reverse=True)
        
        return {
            'top_sectors': sectors_sorted[:5],  # 前 5 领涨
            'bottom_sectors': sectors_sorted[-5:],  # 后 5 领跌
            'all_sectors': sectors_sorted,
            'source': 'eastmoney_sector',
            'timestamp': datetime.now().isoformat(),
        }
    
    except requests.RequestException as e:
        return {'top_sectors': [], 'bottom_sectors': [], 'error': str(e)}
    except Exception as e:
        return {'top_sectors': [], 'bottom_sectors': [], 'error': str(e)}
