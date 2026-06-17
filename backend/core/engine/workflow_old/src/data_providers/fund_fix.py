"""
基金数据修复模块

解决 518880 等 ETF 基金数据获取问题
添加 fallback 到网页版 API 和 AKShare
"""

import requests
import json
import re
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_fund_detail_web(fund_code: str, timeout: int = 10) -> Dict:
    """
    获取基金详情（网页版 API）

    移动端 API 失败时的 fallback

    Args:
        fund_code: 6 位基金代码
        timeout: 超时秒数

    Returns:
        dict: 基金详情
    """
    # 网页版 API
    url = f"https://funds.eastmoney.com/f10/FundArchives.aspx"
    params = {
        "code": fund_code,
        "topline": 10,
        "page": 1,
        "sort": "fsr",
        "order": "desc",
    }

    try:
        resp = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"https://fund.eastmoney.com/{fund_code}.html"
            }
        )
        resp.raise_for_status()

        # 解析网页数据
        text = resp.text

        # 提取基金名称
        name_match = re.search(r'name:\s*["\'](.*?)["\']', text)
        fund_name = name_match.group(1) if name_match else ""

        # 提取净值
        nav_match = re.search(r'dwjz:\s*["\'](.*?)["\']', text)
        nav = float(nav_match.group(1)) if nav_match else 0.0

        # 提取累计净值
        acc_nav_match = re.search(r'ljjz:\s*["\'](.*?)["\']', text)
        acc_nav = float(acc_nav_match.group(1)) if acc_nav_match else 0.0

        # 提取净值日期
        nav_date_match = re.search(r'fsrq:\s*["\'](.*?)["\']', text)
        nav_date = nav_date_match.group(1) if nav_date_match else ""

        # 提取日增长率
        daily_return_match = re.search(r'rzf:\s*["\'](.*?)["\']', text)
        daily_return = float(daily_return_match.group(1)) if daily_return_match else 0.0

        result = {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "nav": nav,
            "acc_nav": acc_nav,
            "nav_date": nav_date,
            "daily_return": daily_return,
            "source": "fund_eastmoney_web",
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"📊 网页版 API 获取基金{fund_code}成功")
        return result

    except Exception as e:
        logger.error(f"❌ 网页版 API 获取基金{fund_code}失败：{str(e)}")
        raise


def fetch_fund_detail_akshare(fund_code: str, timeout: int = 10) -> Dict:
    """
    获取基金详情（AKShare）

    零 API Key 方案

    Args:
        fund_code: 6 位基金代码
        timeout: 超时秒数

    Returns:
        dict: 基金详情
    """
    try:
        import akshare as ak

        # 获取基金基本信息
        fund_info = ak.fund_individual_basic_info(fund_code)

        # 获取基金净值
        fund_nav = ak.fund_open_fund_info_em(fund_code, indicator="单位净值走势")

        # 提取最新净值
        if fund_nav is not None and len(fund_nav) > 0:
            latest = fund_nav.iloc[-1]
            nav = float(latest.get("单位净值", 0))
            acc_nav = float(latest.get("累计净值", 0))
            nav_date = str(latest.get("净值日期", ""))
            daily_return = float(latest.get("日增长率", 0))
        else:
            nav = 0.0
            acc_nav = 0.0
            nav_date = ""
            daily_return = 0.0

        result = {
            "fund_code": fund_code,
            "fund_name": fund_info.get("基金名", fund_code),
            "fund_type": fund_info.get("基金类型", ""),
            "nav": nav,
            "acc_nav": acc_nav,
            "nav_date": nav_date,
            "daily_return": daily_return,
            "fund_size": float(fund_info.get("最新规模", 0)),
            "manager_name": fund_info.get("基金经理", ""),
            "source": "akshare",
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"📊 AKShare 获取基金{fund_code}成功")
        return result

    except ImportError:
        logger.warning("⚠️ AKShare 未安装，跳过")
        raise
    except Exception as e:
        logger.error(f"❌ AKShare 获取基金{fund_code}失败：{str(e)}")
        raise


def get_fund_data_with_fallback(fund_code: str) -> Dict:
    """
    获取基金数据（带 fallback）

    降级链：移动端 API → 网页版 API → AKShare → 模拟数据

    Args:
        fund_code: 基金代码

    Returns:
        dict: 基金数据
    """
    from data_layer import FundAPI

    # 1. 尝试移动端 API（data_layer）
    try:
        fund_api = FundAPI()
        profile = fund_api.get_full_profile(fund_code)

        # 检查数据是否有效
        if profile.get("fund_name") and profile.get("nav"):
            logger.info(f"✅ 移动端 API 获取基金{fund_code}成功")
            return profile
        else:
            logger.warning(f"⚠️ 移动端 API 返回数据不完整")
    except Exception as e:
        logger.warning(f"⚠️ 移动端 API 失败：{str(e)}")

    # 2. 尝试网页版 API
    try:
        data = fetch_fund_detail_web(fund_code)
        logger.info(f"✅ 网页版 API 获取基金{fund_code}成功")
        return data
    except Exception as e:
        logger.warning(f"⚠️ 网页版 API 失败：{str(e)}")

    # 3. 尝试 AKShare
    try:
        data = fetch_fund_detail_akshare(fund_code)
        logger.info(f"✅ AKShare 获取基金{fund_code}成功")
        return data
    except Exception as e:
        logger.warning(f"⚠️ AKShare 失败：{str(e)}")

    # 4. 返回模拟数据
    logger.warning(f"⚠️ 所有 API 失败，返回模拟数据")
    return {
        "fund_code": fund_code,
        "fund_name": f"基金{fund_code}",
        "nav": 1.0,
        "acc_nav": 1.0,
        "nav_date": datetime.now().strftime("%Y-%m-%d"),
        "daily_return": 0.0,
        "source": "模拟数据",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 测试 518880
    print("\n📊 测试基金 518880（黄金 ETF）：")
    result = get_fund_data_with_fallback("518880")
    print(f"  代码：{result.get('fund_code')}")
    print(f"  名称：{result.get('fund_name')}")
    print(f"  净值：{result.get('nav')}")
    print(f"  来源：{result.get('source')}")

    # 测试 005827
    print("\n📊 测试基金 005827（易方达蓝筹）：")
    result = get_fund_data_with_fallback("005827")
    print(f"  代码：{result.get('fund_code')}")
    print(f"  名称：{result.get('fund_name')}")
    print(f"  净值：{result.get('nav')}")
    print(f"  来源：{result.get('source')}")
