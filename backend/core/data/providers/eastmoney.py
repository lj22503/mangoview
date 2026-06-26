"""
东方财富数据中心 API 宏观数据爬虫
直接调用 datacenter-web 公开接口，替代 AKShare 宏观数据源。
"""
import logging
import requests
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

BASE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
TIMEOUT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://data.eastmoney.com/",
}

# 各指标的 reportName 与取值字段映射
REPORT_CONFIG = {
    "PMI":  {"reportName": "RPT_ECONOMY_PMI",             "field": "MAKE_INDEX"},
    "CPI":  {"reportName": "RPT_ECONOMY_CPI",             "field": "NATIONAL_SAME"},
    "PPI":  {"reportName": "RPT_ECONOMY_PPI",             "field": "BASE_SAME"},
    "GDP":  {"reportName": "RPT_ECONOMY_GDP",             "field": "SUM_SAME"},
    "M2":   {"reportName": "RPT_ECONOMY_CURRENCY_SUPPLY", "field": "BASIC_CURRENCY_SAME"},
    "社零": {"reportName": "RPT_ECONOMY_TOTAL_RETAIL",    "field": "RETAIL_TOTAL_SAME"},
    "出口": {"reportName": "RPT_ECONOMY_CUSTOMS",         "field": "EXIT_BASE_SAME"},
    "固投": {"reportName": "RPT_ECONOMY_ASSET_INVEST",    "field": "BASE_SAME"},
}


class EastMoneyMacroFetcher:
    """东方财富宏观数据获取器"""

    @staticmethod
    def _request(report_name: str) -> Optional[Dict[str, Any]]:
        """通用请求方法，返回解析后的 JSON 或 None"""
        params = {
            "pageSize": 5,
            "pageNumber": 1,
            "sortColumns": "REPORT_DATE",
            "sortTypes": -1,
            "columns": "ALL",
            "reportName": report_name,
        }
        try:
            resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and data.get("result") and data["result"].get("data"):
                return data
            logger.warning("东方财富 API 返回空数据: reportName=%s", report_name)
            return None
        except requests.Timeout:
            logger.error("东方财富 API 请求超时: reportName=%s", report_name)
        except requests.RequestException as e:
            logger.error("东方财富 API 请求失败: reportName=%s, error=%s", report_name, e)
        except ValueError as e:
            logger.error("东方财富 API JSON 解析失败: reportName=%s, error=%s", report_name, e)
        return None

    @staticmethod
    def _parse_response(
        data: Dict[str, Any], field: str
    ) -> Optional[Dict[str, Any]]:
        """
        从 API 返回中提取最新一条记录的日期和值。
        返回: {"date": "2026-05-01", "value": 8.6, "prev_value": 8.5, "unit": "%"}
        """
        rows = data["result"]["data"]
        if not rows:
            return None

        latest = rows[0]
        date = latest.get("REPORT_DATE", "")
        value = _safe_float(latest.get(field))

        prev_value = value  # 默认与前值相同
        if len(rows) > 1:
            prev_value = _safe_float(rows[1].get(field, value))

        return {"date": str(date)[:10], "value": value, "prev_value": prev_value, "unit": "%"}

    # ---- 各指标获取方法 ----

    @classmethod
    def fetch_pmi(cls) -> Optional[Dict[str, Any]]:
        cfg = REPORT_CONFIG["PMI"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_cpi(cls) -> Optional[Dict[str, Any]]:
        cfg = REPORT_CONFIG["CPI"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_ppi(cls) -> Optional[Dict[str, Any]]:
        cfg = REPORT_CONFIG["PPI"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_gdp(cls) -> Optional[Dict[str, Any]]:
        cfg = REPORT_CONFIG["GDP"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_m2(cls) -> Optional[Dict[str, Any]]:
        cfg = REPORT_CONFIG["M2"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_social_retail(cls) -> Optional[Dict[str, Any]]:
        """社零"""
        cfg = REPORT_CONFIG["社零"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_export(cls) -> Optional[Dict[str, Any]]:
        """出口"""
        cfg = REPORT_CONFIG["出口"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_fixed_investment(cls) -> Optional[Dict[str, Any]]:
        """固投"""
        cfg = REPORT_CONFIG["固投"]
        data = cls._request(cfg["reportName"])
        return cls._parse_response(data, cfg["field"]) if data else None

    @classmethod
    def fetch_all(cls) -> Dict[str, Optional[Dict[str, Any]]]:
        """一次性获取所有指标，返回 {指标key: 结果dict 或 None}"""
        result = {}
        fetchers = [
            ("PMI", cls.fetch_pmi),
            ("CPI", cls.fetch_cpi),
            ("PPI", cls.fetch_ppi),
            ("GDP", cls.fetch_gdp),
            ("M2", cls.fetch_m2),
            ("社零", cls.fetch_social_retail),
            ("出口", cls.fetch_export),
            ("固投", cls.fetch_fixed_investment),
        ]
        for key, func in fetchers:
            try:
                result[key] = func()
            except Exception as e:
                logger.error("fetch_all 中 %s 异常: %s", key, e)
                result[key] = None
        return result


def _safe_float(val, default=0.0) -> float:
    """安全转为 float，处理 None / NaN / 非数字字符串"""
    if val is None:
        return default
    try:
        f = float(val)
        if f != f or f == float("inf") or f == float("-inf"):  # NaN / Inf
            return default
        return f
    except (ValueError, TypeError):
        return default
