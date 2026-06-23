#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据层单元测试"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加路径: data-layer 目录名有连字符，需要特殊处理
DATA_LAYER_DIR = os.path.join(os.path.dirname(__file__), '..')
WORKSPACE_DIR = os.path.join(DATA_LAYER_DIR, '..')
sys.path.insert(0, WORKSPACE_DIR)

# 由于 data-layer 有连字符，不能直接 import，改用直接导入 providers
sys.path.insert(0, DATA_LAYER_DIR)

def test_tencent_indices():
    """测试腾讯财经 - 大盘指数"""
    print('=== [1] 腾讯财经 - 大盘指数 ===')
    from providers.tencent import get_indices
    data = get_indices()
    
    assert len(data) > 0, "未获取到任何指数"
    for name, info in data.items():
        assert 'price' in info, f"{name} 缺少 price"
        assert 'change_pct' in info, f"{name} 缺少 change_pct"
        assert info['price'] > 0 or info['pre_close'] > 0, f"{name} 价格异常"
        print(f"  ✅ {name}: {info['price']} ({info['change_pct']}%)")
    
    print(f'  总计: {len(data)} 个指数\n')
    return True


def test_tushare_daily():
    """测试 Tushare - 个股日线"""
    print('=== [2] Tushare - 个股日线 ===')
    from providers.tushare_api import get_daily
    
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
    
    try:
        df = get_daily('000001.SZ', start, end)
        assert df is not None and len(df) > 0, "未获取到日线数据"
        print(f"  ✅ 平安银行日线: {len(df)} 条")
        print(f"  最新: {df.iloc[0]['trade_date']} 收盘={df.iloc[0]['close']} 涨跌幅={df.iloc[0]['pct_chg']}%\n")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}\n")
        return False


def test_tushare_limit():
    """测试 Tushare - 涨跌停统计"""
    print('=== [3] Tushare - 涨跌停统计 ===')
    from providers.tushare_api import get_limit_list
    
    # 取最近交易日
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')
    
    try:
        df = get_limit_list(end, 'U')
        if df is None or len(df) == 0:
            # 今天可能还没数据，试前一天
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            df = get_limit_list(yesterday, 'U')
        
        if df is not None and len(df) > 0:
            print(f"  ✅ 涨停数: {len(df)}")
            print(f"  前3: {df.head(3)[['name','pct_chg']].to_string()}\n")
            return True
        else:
            print("  ⚠️ 无数据（可能非交易时段）\n")
            return True  # 非交易时间正常
    except Exception as e:
        print(f"  ❌ 失败: {e}\n")
        return False


def test_tushare_northbound():
    """测试 Tushare - 北向资金"""
    print('=== [4] Tushare - 北向资金 ===')
    from providers.tushare_api import get_northbound
    
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    
    try:
        df = get_northbound(start, end)
        assert df is not None and len(df) > 0, "未获取到北向资金数据"
        latest = df.iloc[0]
        print(f"  ✅ 最新日期: {latest['trade_date']}")
        print(f"  沪股通: {latest['hgt']}万, 深股通: {latest['sgt']}万")
        print(f"  北向合计: {latest['north_money']}万\n")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}\n")
        return False


def test_searxng():
    """测试 SearXNG - 新闻搜索"""
    print('=== [5] SearXNG - 新闻搜索 ===')
    from providers.searxng import search_news
    
    results = search_news('A股 市场')
    if results and len(results) > 0:
        print(f"  ✅ 搜索结果: {len(results)} 条")
        for r in results[:2]:
            print(f"  - {r['title'][:50]}")
        print()
        return True
    else:
        print("  ⚠️ 无搜索结果\n")
        return True  # SearXNG 可能暂时无结果


def run_all():
    print('=' * 50)
    print('数据层单元测试')
    print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 50 + '\n')
    
    results = {}
    tests = [
        ('腾讯财经-大盘指数', test_tencent_indices),
        ('Tushare-个股日线', test_tushare_daily),
        ('Tushare-涨跌停', test_tushare_limit),
        ('Tushare-北向资金', test_tushare_northbound),
        ('SearXNG-新闻搜索', test_searxng),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            ok = test_fn()
            results[name] = '✅' if ok else '❌'
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            results[name] = f'❌ {e}'
            failed += 1
    
    print('=' * 50)
    print('测试汇总')
    print('=' * 50)
    for name, status in results.items():
        print(f"  {status} {name}")
    print(f"\n通过: {passed}/{passed+failed}")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)
