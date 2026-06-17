"""
腾讯财经数据修复模块

修复涨跌幅字段返回 N/A 的问题
"""

import requests
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def get_indices_fixed(codes: Optional[List[str]] = None) -> Dict:
    """
    获取大盘指数（修复版）

    修复涨跌幅字段返回 N/A 的问题

    Args:
        codes: 指数代码列表

    Returns:
        dict: {指数名: {price, change_percent, ...}}
    """
    if codes is None:
        codes = ['1.000001', '0.399001', '0.399006', '1.000300']

    index_names = {
        '1.000001': '上证指数',
        '0.399001': '深证成指',
        '0.399006': '创业板指',
        '1.000300': '沪深 300',
        '1.000016': '上证 50',
        '0.399005': '中小综指',
        '0.399106': '创业板综',
    }

    try:
        url = 'https://qt.gtimg.cn/q=' + ','.join(codes)
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://finance.qq.com'
        })
        resp.raise_for_status()

        result = {}
        for line in resp.text.strip().split(';'):
            line = line.strip()
            if not line or '=' not in line:
                continue

            code_part, data_part = line.split('=', 1)
            code = code_part.split('_')[-1]

            if not data_part or data_part == '"':
                continue

            # 解析数据
            fields = data_part.split('~')
            if len(fields) < 50:
                continue

            name = index_names.get(code, fields[1] if len(fields) > 1 else code)

            # 价格
            try:
                price = float(fields[3])
            except (ValueError, IndexError):
                price = 0.0

            # 涨跌额
            try:
                change = float(fields[31])
            except (ValueError, IndexError):
                change = 0.0

            # 涨跌幅（修复：直接从字段 32 获取）
            try:
                change_percent_str = fields[32]
                if change_percent_str and change_percent_str != '-':
                    change_percent = float(change_percent_str)
                else:
                    # 如果字段 32 为空，计算涨跌幅
                    prev_close = float(fields[4]) if len(fields) > 4 and fields[4] else 0.0
                    if prev_close > 0:
                        change_percent = round((price - prev_close) / prev_close * 100, 2)
                    else:
                        change_percent = 0.0
            except (ValueError, IndexError):
                change_percent = 0.0

            # 成交量
            try:
                volume = int(float(fields[6]))
            except (ValueError, IndexError):
                volume = 0

            # 成交额
            try:
                turnover = float(fields[37])
            except (ValueError, IndexError):
                turnover = 0.0

            # 开盘价
            try:
                open_price = float(fields[5])
            except (ValueError, IndexError):
                open_price = 0.0

            # 最高价
            try:
                high = float(fields[33])
            except (ValueError, IndexError):
                high = 0.0

            # 最低价
            try:
                low = float(fields[34])
            except (ValueError, IndexError):
                low = 0.0

            # 昨收
            try:
                prev_close = float(fields[4])
            except (ValueError, IndexError):
                prev_close = 0.0

            result[name] = {
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'turnover': turnover,
                'open': open_price,
                'high': high,
                'low': low,
                'prev_close': prev_close,
                'source': 'tencent',
                'timestamp': datetime.now().isoformat(),
            }

        logger.info(f"📊 获取大盘指数成功：{len(result)} 个")
        return result

    except Exception as e:
        logger.error(f"❌ 获取大盘指数失败：{str(e)}")
        return _get_mock_indices()


def _get_mock_indices() -> Dict:
    """获取模拟指数数据"""
    return {
        '上证指数': {
            'price': 4155.85,
            'change': 42.30,
            'change_percent': 1.03,
            'volume': 0,
            'turnover': 0,
            'open': 4113.55,
            'high': 4160.00,
            'low': 4100.00,
            'prev_close': 4113.55,
            'source': '模拟数据',
            'timestamp': datetime.now().isoformat(),
        },
        '深证成指': {
            'price': 15444.62,
            'change': 358.22,
            'change_percent': 2.36,
            'volume': 0,
            'turnover': 0,
            'open': 15086.40,
            'high': 15450.00,
            'low': 15000.00,
            'prev_close': 15086.40,
            'source': '模拟数据',
            'timestamp': datetime.now().isoformat(),
        },
        '创业板指': {
            'price': 3774.79,
            'change': 110.88,
            'change_percent': 3.07,
            'volume': 0,
            'turnover': 0,
            'open': 3663.91,
            'high': 3780.00,
            'low': 3650.00,
            'prev_close': 3663.91,
            'source': '模拟数据',
            'timestamp': datetime.now().isoformat(),
        },
        '沪深 300': {
            'price': 4771.73,
            'change': 73.24,
            'change_percent': 1.73,
            'volume': 0,
            'turnover': 0,
            'open': 4698.49,
            'high': 4775.00,
            'low': 4690.00,
            'prev_close': 4698.49,
            'source': '模拟数据',
            'timestamp': datetime.now().isoformat(),
        },
    }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("\n📊 测试大盘指数（修复版）：")
    result = get_indices_fixed()

    for name, data in result.items():
        print(f"  {name}: {data['price']} ({data['change_percent']}%)")

    print("\n✅ 测试完成")
