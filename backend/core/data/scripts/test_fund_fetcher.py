#!/usr/bin/env python3
"""
测试基金数据获取器
验证各 API 接口可用性
"""

import sys
import os
import json

# 添加 data_fetcher 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher import FundDataFetcher
from data_fetcher.providers import fund_eastmoney

TEST_FUND = '005827'  # 易方达蓝筹精选混合

def test_search():
    print("=" * 60)
    print("1. 测试基金搜索")
    print("=" * 60)
    try:
        results = fund_eastmoney.search_fund('沪深300')
        print(f"✅ 搜索'沪深300'，找到 {len(results)} 只基金")
        for r in results[:3]:
            print(f"   {r['fund_code']} {r['fund_name']}")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    print()

def test_estimated_nav():
    print("=" * 60)
    print("2. 测试基金估值（盘中实时）")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_estimated_nav(TEST_FUND)
        print(f"✅ {data.get('fund_name', '')}({data.get('fund_code', '')})")
        print(f"   净值: {data.get('nav', 0)}")
        print(f"   估值: {data.get('estimated_nav', 0)}")
        print(f"   估算涨幅: {data.get('estimated_return', 0)}%")
        print(f"   估算时间: {data.get('estimate_time', '')}")
    except Exception as e:
        print(f"❌ 估值获取失败: {e}")
    print()

def test_detail():
    print("=" * 60)
    print("3. 测试基金详情")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_detail(TEST_FUND)
        print(f"✅ {data.get('fund_name', '')}({data.get('fund_code', '')})")
        print(f"   类型: {data.get('fund_type', '')}")
        print(f"   规模: {data.get('fund_size', 0)} 亿")
        print(f"   净值: {data.get('nav', 0)}（{data.get('nav_date', '')}）")
        print(f"   日涨幅: {data.get('daily_return', 0)}%")
        print(f"   管理费: {data.get('management_fee', 0)}%")
        print(f"   托管费: {data.get('custody_fee', 0)}%")
        print(f"   基金公司: {data.get('fund_company_name', '')}")
        print(f"   经理: {data.get('manager_name', '')}（任职{data.get('manager_days', 0)}天）")
        print(f"   风险等级: {data.get('risk_level', '')}")
    except Exception as e:
        print(f"❌ 详情获取失败: {e}")
    print()

def test_performance():
    print("=" * 60)
    print("4. 测试基金业绩")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_performance(TEST_FUND)
        print(f"✅ 基金 {data.get('fund_code', '')} 阶段收益:")
        returns = data.get('returns', {})
        ranks = data.get('ranks', {})
        for period, ret in returns.items():
            rank = ranks.get(period, '')
            rank_str = f" 排名: {rank}" if rank else ""
            print(f"   {period}: {ret}%{rank_str}")
    except Exception as e:
        print(f"❌ 业绩获取失败: {e}")
    print()

def test_nav_history():
    print("=" * 60)
    print("5. 测试历史净值")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_nav_history(TEST_FUND, page_size=5)
        print(f"✅ 基金 {data.get('fund_code', '')} 最近 {len(data.get('records', []))} 条净值:")
        for rec in data.get('records', []):
            print(f"   {rec['date']}  净值: {rec['nav']}  累计: {rec['acc_nav']}  涨幅: {rec['daily_return']}%")
    except Exception as e:
        print(f"❌ 净值获取失败: {e}")
    print()

def test_holdings():
    print("=" * 60)
    print("6. 测试重仓股")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_holdings(TEST_FUND)
        print(f"✅ 基金 {data.get('fund_code', '')} 重仓股（{data.get('report_date', '')}）:")
        print(f"   前10大持仓占比: {data.get('top10_percent', 0):.2f}%")
        for s in data.get('stocks', [])[:5]:
            print(f"   {s['name']}({s['code']}) {s['percent']}%")
    except Exception as e:
        print(f"❌ 持仓获取失败: {e}")
    print()

def test_asset_allocation():
    print("=" * 60)
    print("7. 测试资产配置")
    print("=" * 60)
    try:
        data = fund_eastmoney.fetch_fund_asset_allocation(TEST_FUND)
        latest = data.get('latest', {})
        if latest:
            print(f"✅ 基金 {data.get('fund_code', '')} 资产配置（{latest.get('date', '')}）:")
            print(f"   股票: {latest.get('stock_pct', 0)}%")
            print(f"   债券: {latest.get('bond_pct', 0)}%")
            print(f"   现金: {latest.get('cash_pct', 0)}%")
            print(f"   其他: {latest.get('other_pct', 0)}%")
        else:
            print("⚠️ 无资产配置数据")
    except Exception as e:
        print(f"❌ 资产配置获取失败: {e}")
    print()

def test_full_profile():
    print("=" * 60)
    print("8. 测试完整基金档案（FundDataFetcher）")
    print("=" * 60)
    try:
        fetcher = FundDataFetcher()
        profile = fetcher.get_full_profile(TEST_FUND)
        
        detail = profile.get('detail', {})
        perf = profile.get('performance', {})
        holdings = profile.get('holdings', {})
        alloc = profile.get('asset_allocation', {})
        
        print(f"✅ 完整档案 {TEST_FUND}:")
        
        if 'error' not in detail:
            print(f"   名称: {detail.get('fund_name', '')} | 类型: {detail.get('fund_type', '')}")
            print(f"   经理: {detail.get('manager_name', '')} | 规模: {detail.get('fund_size', 0)}亿")
        else:
            print(f"   详情: ❌ {detail['error']}")
        
        if 'error' not in perf:
            returns = perf.get('returns', {})
            print(f"   近1年: {returns.get('1y', 'N/A')}% | 近3年: {returns.get('3y', 'N/A')}%")
        else:
            print(f"   业绩: ❌ {perf['error']}")
        
        if 'error' not in holdings:
            print(f"   前10重仓: {holdings.get('top10_percent', 0):.1f}% | 重仓股数: {holdings.get('stock_count', 0)}")
        else:
            print(f"   持仓: ❌ {holdings['error']}")
        
        if 'error' not in alloc:
            latest = alloc.get('latest', {})
            print(f"   配置: 股{latest.get('stock_pct', 0)}% 债{latest.get('bond_pct', 0)}% 现金{latest.get('cash_pct', 0)}%")
        else:
            print(f"   配置: ❌ {alloc['error']}")
    
    except Exception as e:
        print(f"❌ 完整档案获取失败: {e}")
    print()

if __name__ == '__main__':
    print("🚀 基金数据获取器测试")
    print(f"测试基金: {TEST_FUND}（易方达蓝筹精选混合）")
    print()
    
    test_search()
    test_estimated_nav()
    test_detail()
    test_performance()
    test_nav_history()
    test_holdings()
    test_asset_allocation()
    test_full_profile()
    
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
