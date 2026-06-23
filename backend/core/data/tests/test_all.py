#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_layer 整合测试

验证所有 API 接口可用性
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_layer import DataAPI, FundAPI

PASS = 0
FAIL = 0

def ok(name, detail=''):
    global PASS
    PASS += 1
    print(f"  ✅ {name}" + (f"  →  {detail}" if detail else ""))

def fail(name, err):
    global FAIL
    FAIL += 1
    print(f"  ❌ {name}  →  {err}")

# ========================================
print("=" * 60)
print("1. DataAPI 测试")
print("=" * 60)

api = DataAPI()

# 1.1 大盘指数
print("\n[1.1] get_indices()")
try:
    indices = api.get_indices()
    if indices and len(indices) > 0:
        for name, d in list(indices.items())[:3]:
            ok(f"大盘指数 {name}", f"{d['price']}  {d['change_pct']:+.2f}%")
    else:
        fail("大盘指数", "返回空")
except Exception as e:
    fail("大盘指数", str(e))

# 1.2 个股行情
print("\n[1.2] get_quote()")
for symbol in ['600519.SH', '000001.SZ']:
    try:
        q = api.get_quote(symbol)
        ok(f"个股行情 {symbol}", f"¥{q.price}  {q.change_percent:+.2f}%  来源:{q.source}")
    except Exception as e:
        fail(f"个股行情 {symbol}", str(e))

# 1.3 财报
print("\n[1.3] get_financials()")
try:
    fin = api.get_financials('600519.SH')
    ok("财报 600519.SH", f"ROE:{fin.roe}%  EPS:{fin.eps}  来源:{fin.source}")
except Exception as e:
    fail("财报 600519.SH", str(e))

# 1.4 新闻搜索
print("\n[1.4] search_news()")
try:
    news = api.search_news('A股 市场')
    ok(f"新闻搜索", f"找到 {len(news)} 条")
    for n in news[:2]:
        print(f"      - {n['title'][:50]}")
except Exception as e:
    fail("新闻搜索", str(e))

# ========================================
print("\n" + "=" * 60)
print("2. FundAPI 测试")
print("=" * 60)

fund = FundAPI()
TEST_FUND = '005827'  # 易方达蓝筹精选混合

# 2.1 搜索
print("\n[2.1] search()")
try:
    results = fund.search('沪深300')
    ok(f"基金搜索 '沪深300'", f"找到 {len(results)} 只")
    for r in results[:2]:
        print(f"      - {r['fund_code']} {r['fund_name']}")
except Exception as e:
    fail("基金搜索", str(e))

# 2.2 估值
print(f"\n[2.2] get_estimated_nav('{TEST_FUND}')")
try:
    gz = fund.get_estimated_nav(TEST_FUND)
    ok("基金估值", f"{gz.get('fund_name','')} 净值:{gz.get('nav',0)} 估值:{gz.get('estimated_nav',0)} 估涨幅:{gz.get('estimated_return',0)}%")
except Exception as e:
    fail("基金估值", str(e))

# 2.3 详情
print(f"\n[2.3] get_detail('{TEST_FUND}')")
try:
    d = fund.get_detail(TEST_FUND)
    ok("基金详情", f"{d.get('fund_name','')} 类型:{d.get('fund_type','')} 规模:{d.get('fund_size',0)}亿 经理:{d.get('manager_name','')}")
except Exception as e:
    fail("基金详情", str(e))

# 2.4 业绩
print(f"\n[2.4] get_performance('{TEST_FUND}')")
try:
    perf = fund.get_performance(TEST_FUND)
    returns = perf.get('returns', {})
    ok("基金业绩", f"近1年:{returns.get('1y','N/A')}% 近3年:{returns.get('3y','N/A')}%")
except Exception as e:
    fail("基金业绩", str(e))

# 2.5 净值
print(f"\n[2.5] get_nav_history('{TEST_FUND}')")
try:
    nav = fund.get_nav_history(TEST_FUND, page_size=5)
    records = nav.get('records', [])
    ok("历史净值", f"最近 {len(records)} 条")
    for r in records[:3]:
        print(f"      - {r['date']}  净值:{r['nav']}  涨幅:{r['daily_return']}%")
except Exception as e:
    fail("历史净值", str(e))

# 2.6 持仓
print(f"\n[2.6] get_holdings('{TEST_FUND}')")
try:
    h = fund.get_holdings(TEST_FUND)
    ok("重仓股", f"前10占比:{h.get('top10_percent',0):.1f}%")
    for s in h.get('stocks', [])[:3]:
        print(f"      - {s['name']}({s['code']}) {s['percent']}%")
except Exception as e:
    fail("重仓股", str(e))

# 2.7 配置
print(f"\n[2.7] get_asset_allocation('{TEST_FUND}')")
try:
    alloc = fund.get_asset_allocation(TEST_FUND)
    latest = alloc.get('latest', {})
    if latest:
        ok("资产配置", f"股票:{latest.get('stock_pct',0)}% 债券:{latest.get('bond_pct',0)}% 现金:{latest.get('cash_pct',0)}%")
    else:
        fail("资产配置", "无数据")
except Exception as e:
    fail("资产配置", str(e))

# 2.8 完整档案
print(f"\n[2.8] get_full_profile('{TEST_FUND}')")
try:
    profile = fund.get_full_profile(TEST_FUND)
    parts_ok = sum(1 for k in ['detail','performance','holdings','asset_allocation','nav_history'] if 'error' not in profile.get(k, {}))
    ok("完整档案", f"{parts_ok}/5 模块成功")
except Exception as e:
    fail("完整档案", str(e))

# ========================================
print("\n" + "=" * 60)
print(f"结果：✅ {PASS} 通过  ❌ {FAIL} 失败")
print("=" * 60)
