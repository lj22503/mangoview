#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取层 - AKShare 数据源适配器

通过 mcp-aktools 获取 A 股/港股/美股/ETF/加密货币数据。
零 API Key，基于 AKShare（免费、无需注册）。

v1.0.0 - 2026-04-24
"""

import json
import subprocess
from typing import Dict, List, Optional, Any
from data_layer.exceptions import ProviderError, DataFetchError


def _run_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """运行 MCP 工具并返回结果"""
    proc = subprocess.Popen(
        ['mcp-aktools'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # 初始化
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "data-layer", "version": "1.0"}
        }
    }
    proc.stdin.write(json.dumps(init_request) + '\n')
    proc.stdin.flush()
    proc.stdout.readline()  # 忽略初始化响应

    # 调用工具
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    proc.stdin.write(json.dumps(tool_request) + '\n')
    proc.stdin.flush()

    # 读取响应
    response = proc.stdout.readline()
    data = json.loads(response)

    proc.terminate()

    if 'error' in data:
        raise ProviderError(f"MCP 工具 {tool_name} 调用失败: {data['error']}")

    content = data.get('result', {}).get('content', [])
    if content:
        return content[0].get('text', '')
    return ''


# ========== 股票搜索 ==========

def search_stock(keyword: str) -> List[Dict]:
    """搜索股票代码

    Args:
        keyword: 股票名称/公司简称

    Returns:
        List[Dict]: 搜索结果列表
    """
    result = _run_mcp_tool('search', {'keyword': keyword})
    # 解析结果：code    600519\nname      贵州茅台\n交易市场: sh
    stocks = []
    info = {}
    for line in result.strip().split('\n'):
        if ':' in line:
            # 格式：交易市场: sh
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
        elif '    ' in line:
            # 格式：code    600519（4 个空格分隔）
            parts = line.split('    ', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            info[key] = value
    if info:
        # 统一字段名
        stocks.append({
            'code': info.get('code', ''),
            'name': info.get('name', ''),
            'market': info.get('交易市场', '')
        })
    return stocks


# ========== 股票信息 ==========

def get_stock_info(symbol: str, market: str = 'sh') -> Dict:
    """获取股票基本信息

    Args:
        symbol: 股票代码（如 600519）
        market: 市场（sh/sz/hk/us）

    Returns:
        Dict: 股票信息
    """
    result = _run_mcp_tool('stock_info', {'symbol': symbol, 'market': market})
    # 解析结果：code    600519\nname      贵州茅台
    info = {}
    for line in result.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
        elif '    ' in line:
            parts = line.split('    ', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            info[key] = value
    return info


# ========== 股票价格 ==========

def get_stock_prices(symbol: str, market: str = 'sh', period: str = 'daily') -> List[Dict]:
    """获取股票历史价格

    Args:
        symbol: 股票代码
        market: 市场
        period: 周期（daily/weekly/monthly）

    Returns:
        List[Dict]: 价格数据列表（含技术指标）
    """
    result = _run_mcp_tool('stock_prices', {
        'symbol': symbol,
        'market': market,
        'period': period
    })
    # 解析 CSV 格式
    stocks = []
    lines = result.strip().split('\n')
    if not lines:
        return []

    headers = lines[0].split(',')
    for line in lines[1:]:
        values = line.split(',')
        if len(values) == len(headers):
            stocks.append(dict(zip(headers, values)))
    return stocks


# ========== A 股财务指标 ==========

def get_stock_indicators_a(symbol: str) -> List[Dict]:
    """获取 A 股财务指标

    Args:
        symbol: 股票代码

    Returns:
        List[Dict]: 财务指标列表
    """
    result = _run_mcp_tool('stock_indicators_a', {'symbol': symbol})
    # 解析 CSV 格式
    indicators = []
    lines = result.strip().split('\n')
    if not lines:
        return []

    headers = lines[0].split(',')
    for line in lines[1:]:
        values = line.split(',')
        if len(values) == len(headers):
            indicators.append(dict(zip(headers, values)))
    return indicators


# ========== 涨停池 ==========

def get_zt_pool() -> List[Dict]:
    """获取 A 股涨停池

    Returns:
        List[Dict]: 涨停股列表
    """
    result = _run_mcp_tool('stock_zt_pool_em', {})
    # 解析 CSV 格式（跳过第一行 "共 XX 只涨停股"）
    stocks = []
    lines = result.strip().split('\n')
    if not lines:
        return []

    # 找到 CSV 头部行（包含 "代码" 的行）
    header_idx = 0
    for i, line in enumerate(lines):
        if '代码' in line and '名称' in line:
            header_idx = i
            break

    headers = lines[header_idx].split(',')
    for line in lines[header_idx + 1:]:
        values = line.split(',')
        if len(values) == len(headers):
            stocks.append(dict(zip(headers, values)))
    return stocks


# ========== 强势股池 ==========

def get_strong_pool() -> List[Dict]:
    """获取 A 股强势股池

    Returns:
        List[Dict]: 强势股列表
    """
    result = _run_mcp_tool('stock_zt_pool_strong_em', {})
    stocks = []
    lines = result.strip().split('\n')
    if not lines:
        return []

    # 找到 CSV 头部行
    header_idx = 0
    for i, line in enumerate(lines):
        if '代码' in line and '名称' in line:
            header_idx = i
            break

    headers = lines[header_idx].split(',')
    for line in lines[header_idx + 1:]:
        values = line.split(',')
        if len(values) == len(headers):
            stocks.append(dict(zip(headers, values)))
    return stocks


# ========== 龙虎榜 ==========

def get_lhb() -> List[Dict]:
    """获取 A 股龙虎榜

    Returns:
        List[Dict]: 龙虎榜列表
    """
    result = _run_mcp_tool('stock_lhb_ggtj_sina', {})
    stocks = []
    lines = result.strip().split('\n')
    if not lines:
        return []

    # 找到 CSV 头部行
    header_idx = 0
    for i, line in enumerate(lines):
        if '代码' in line and '名称' in line:
            header_idx = i
            break

    headers = lines[header_idx].split(',')
    for line in lines[header_idx + 1:]:
        values = line.split(',')
        if len(values) == len(headers):
            stocks.append(dict(zip(headers, values)))
    return stocks


# ========== 个股新闻 ==========

def get_stock_news(symbol: str) -> List[Dict]:
    """获取个股新闻

    Args:
        symbol: 股票代码或加密货币符号

    Returns:
        List[Dict]: 新闻列表
    """
    result = _run_mcp_tool('stock_news', {'symbol': symbol})
    # 解析结果（JSON 格式）
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return [{'content': result}]


# ========== 全球财经快讯 ==========

def get_global_news() -> List[Dict]:
    """获取全球财经快讯

    Returns:
        List[Dict]: 新闻列表
    """
    result = _run_mcp_tool('stock_news_global', {})
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return [{'content': result}]


# ========== 交易建议 ==========

def get_trading_suggest(symbol: str, market: str = 'sh') -> Dict:
    """获取交易建议

    Args:
        symbol: 股票代码
        market: 市场

    Returns:
        Dict: 交易建议
    """
    result = _run_mcp_tool('trading_suggest', {
        'symbol': symbol,
        'market': market
    })
    # 解析结果
    suggest = {}
    for line in result.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            suggest[key.strip()] = value.strip()
    return suggest


# ========== 当前时间 ==========

def get_current_time() -> Dict:
    """获取当前时间和 A 股交易日信息

    Returns:
        Dict: 时间和交易日信息
    """
    result = _run_mcp_tool('get_current_time', {})
    info = {}
    for line in result.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()
    return info
