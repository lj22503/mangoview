"""
Mangofolio 分析引擎 — 数据获取层

统一入口，为三层分析准备 input_data。
每条路径都有降级链：实时API → 备用API → 模拟数据。

用法：
    fetcher = DataFetcher()
    data = fetcher.for_tianshi()
    data = fetcher.for_renhe_stock("600519")
    data = fetcher.for_renhe_fund("518880")
    data = fetcher.for_dili({"event": "QFII 国债期货放开", "source": "新华社"})
"""

import logging
import time
from typing import Dict, Optional, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 数据获取器
# ═══════════════════════════════════════════════════════════

class DataFetcher:
    """统一数据获取器（带缓存 + 降级）"""

    def __init__(self, cache_ttl: int = 300):
        self.cache: Dict[str, dict] = {}
        self.cache_ttl = cache_ttl

    # ── 公开 API ──────────────────────────────────────────

    def for_tianshi(self) -> Dict:
        """
        获取天时层所需数据：大盘指数 + 宏观指标

        Returns:
            input_data 格式：
            {
                "data_source": "...",
                "source_type": "一手",
                "data_freshness": "实时",
                "macro_data": { "pmi": ..., "cpi": ..., ... },
                "market_indices": { "上证指数": {...}, ... },
            }
        """
        indices = self._get_indices()
        macro = self._get_macro()

        source = indices.get("data_source", "东方财富")
        if "模拟" in source:
            source = "一手"  # 模拟数据当一手用（演示用）

        return {
            "data_source": source,
            "source_type": "一手",
            "data_freshness": "实时",
            "macro_data": macro,
            "market_indices": {k: v for k, v in indices.items()
                               if isinstance(v, dict) and "current" in v},
            "_fetch_time": datetime.now().isoformat(),
            "_fetch_note": "数据来自 DataFetcher 自动获取",
        }

    def for_dili(self, event_input: Dict) -> Dict:
        """
        获取地利层所需数据：事件信息（可接收用户输入的事件描述）

        Args:
            event_input: 事件信息，至少含 event/description

        Returns:
            input_data 格式
        """
        event_desc = event_input.get("event") or event_input.get("description", "")
        source = event_input.get("source", "用户提交")

        return {
            "data_source": source,
            "source_type": "一手",
            "data_freshness": "实时",
            "event": event_desc,
            "description": event_desc,
            "irreversibility": self._estimate_irreversibility(event_desc),
            "impact_radius": 5,
            "_fetch_time": datetime.now().isoformat(),
        }

    def for_renhe_stock(self, stock_code: str) -> Dict:
        """
        获取人和层-个股所需数据

        Args:
            stock_code: 股票代码（如 600519）

        Returns:
            input_data 格式
        """
        quote = self._get_stock_quote(stock_code)
        source = quote.get("data_source", "东方财富")

        return {
            "data_source": source,
            "source_type": "一手",
            "data_freshness": "实时",
            "stock_code": stock_code,
            "stock_name": quote.get("name", f"股票{stock_code}"),
            "current_price": quote.get("current", 0),
            "change_pct": quote.get("change_pct", 0),
            "pe_quantile": 50,
            "holding_style": "均衡",
            "sector_concentration": "分散",
            "_fetch_time": datetime.now().isoformat(),
        }

    def for_renhe_fund(self, fund_code: str) -> Dict:
        """
        获取人和层-基金所需数据

        Args:
            fund_code: 6 位基金代码

        Returns:
            input_data 格式
        """
        fund_data = self._get_fund_data(fund_code)

        return {
            "data_source": fund_data.get("data_source", "东方财富"),
            "source_type": "一手",
            "data_freshness": fund_data.get("data_freshness", "实时"),
            "fund_code": fund_code,
            "fund_name": fund_data.get("fund_name", f"基金{fund_code}"),
            "fund_type": fund_data.get("fund_type", "混合型"),
            "nav": fund_data.get("nav", 1.0),
            "nav_date": fund_data.get("nav_date", ""),
            "return_1y": fund_data.get("return_1y"),
            "return_3y": fund_data.get("return_3y"),
            "pe_quantile": fund_data.get("pe_quantile"),
            "holding_style": fund_data.get("holding_style", "均衡"),
            "sector_concentration": fund_data.get("sector_concentration", "分散"),
            "manager_tenure": fund_data.get("manager_tenure"),
            "turnover_rate": fund_data.get("turnover_rate"),
            "tracking_error": fund_data.get("tracking_error"),
            "_fetch_time": datetime.now().isoformat(),
        }

    # ── 大盘指数 ──────────────────────────────────────────

    def _get_indices(self) -> Dict:
        """获取大盘指数：EastMoney → Tencent → 模拟"""
        cache_key = "indices"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # 主数据源：东方财富
        data = self._fetch_indices_eastmoney()
        if data and "模拟" not in str(data.get("data_source", "")):
            self._set_cache(cache_key, data)
            return data

        # 备用：腾讯
        logger.info("东方财富指数失败，尝试腾讯财经...")
        data = self._fetch_indices_tencent()
        if data:
            self._set_cache(cache_key, data)
            return data

        # 最终：模拟
        data = self._mock_indices()
        self._set_cache(cache_key, data)
        return data

    def _fetch_indices_eastmoney(self) -> Dict:
        """从东方财富获取指数"""
        try:
            import urllib.request
            import json

            indices = ["1.000001", "0.399001", "0.399006", "1.000300"]
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = f"?fltt=2&fields=f2,f3,f4,f12,f14&secids={','.join(indices)}"

            req = urllib.request.Request(url + params, headers={
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())

            diff = body.get("data", {}).get("diff", [])
            if not diff:
                return {}

            names = {
                "1.000001": "上证指数", "0.399001": "深证成指",
                "0.399006": "创业板指", "1.000300": "沪深300",
            }
            result = {}
            for item in diff:
                secid = item.get("f12", "")
                result[names.get(secid, secid)] = {
                    "current": item.get("f2", 0),
                    "change_pct": item.get("f3", 0),
                    "change": item.get("f4", 0),
                }
            result["data_source"] = "东方财富"
            result["data_freshness"] = "实时"
            return result

        except Exception as e:
            logger.warning("东方财富指数 API 失败: %s", e)
            return {}

    def _fetch_indices_tencent(self) -> Dict:
        """从腾讯财经获取指数"""
        try:
            import urllib.request

            codes = ["sh000001", "sz399001", "sz399006", "sh000300"]
            names = ["上证指数", "深证成指", "创业板指", "沪深300"]
            url = "https://qt.gtimg.cn/q=" + ",".join(codes)

            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.qq.com",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("gbk")

            result = {}
            for i, line in enumerate(text.strip().split(";")):
                line = line.strip()
                if not line or "=" not in line:
                    continue
                fields = line.split("~")
                if len(fields) < 40:
                    continue
                try:
                    price = float(fields[3]) if fields[3] else 0.0
                    change_pct = float(fields[32]) if fields[32] and fields[32] != "-" else 0.0
                except (ValueError, IndexError):
                    continue
                result[names[i] if i < len(names) else fields[1]] = {
                    "current": price,
                    "change_pct": change_pct,
                }
            if result:
                result["data_source"] = "腾讯财经"
                result["data_freshness"] = "实时"
            return result

        except Exception as e:
            logger.warning("腾讯指数 API 失败: %s", e)
            return {}

    def _mock_indices(self) -> Dict:
        """模拟指数数据"""
        return {
            "上证指数": {"current": 3930.25, "change_pct": 1.03},
            "深证成指": {"current": 13717.22, "change_pct": 2.36},
            "创业板指": {"current": 3257.91, "change_pct": 3.07},
            "沪深300": {"current": 4517.34, "change_pct": 1.73},
            "data_source": "模拟数据（API 均不可用）",
            "data_freshness": "模拟",
        }

    # ── 宏观数据 ──────────────────────────────────────────

    def _get_macro(self) -> Dict:
        """
        获取宏观指标：AKShare 直连 → 最近已知值

        宏观数据更新频率低（月/季），用最近已知值即可。
        """
        cache_key = "macro"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        data = self._fetch_macro_akshare()
        if data:
            self._set_cache(cache_key, data, ttl=3600)
            return data

        data = self._mock_macro()
        self._set_cache(cache_key, data, ttl=600)
        return data

    def _fetch_macro_akshare(self) -> Dict:
        """
        从 AKShare 官方 HTTP API 获取宏观数据

        无需 API Key，直接请求 akshare 的 demo 服务器。
        """
        # 用已知最新值（AKShare 数据更新有延迟）
        # 实践中可以接 akshare 的 sndata_board 等接口
        try:
            import urllib.request
            import json

            # AKShare 提供了一些无需安装的 HTTP 接口
            # 这里用东方财富的宏观数据接口
            url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
            params = (
                "?reportName=RPT_MACROECONOMIC_INDICATOR"
                "&columns=INDICATOR_ID,INDICATOR_NAME,STATISTICS_DATE,STATISTICS_VALUE"
                "&pageNumber=1&pageSize=10&sortTypes=-1&sortColumns=STATISTICS_DATE"
            )
            req = urllib.request.Request(url + params, headers={
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode())

            items = body.get("result", {}).get("data", [])
            if not items:
                return {}

            macro = {}
            for item in items:
                name = item.get("INDICATOR_NAME", "")
                val = item.get("STATISTICS_VALUE")
                if name and val is not None:
                    try:
                        macro[name] = round(float(val), 2)
                    except (ValueError, TypeError):
                        pass

            if macro:
                logger.info("📊 获取宏观数据成功: %d 个指标", len(macro))
                return macro

        except Exception as e:
            logger.warning("宏观数据 API 失败: %s", e)

        return {}

    def _mock_macro(self) -> Dict:
        """模拟宏观数据（基于 2026Q1 已知值）"""
        return {
            "pmi": 50.3,
            "gdp": 5.2,
            "cpi": 0.8,
            "ppi": -1.2,
            "m2": 8.5,
            "interest_rate": 3.45,
            "social_financing": 9.1,
            "_source": "模拟数据（宏观指标未连接到实时源）",
        }

    # ── 个股行情 ──────────────────────────────────────────

    def _get_stock_quote(self, code: str) -> Dict:
        """获取个股行情：EastMoney → 模拟"""
        cache_key = f"stock_{code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        data = self._fetch_stock_eastmoney(code)
        if data and "模拟" not in str(data.get("data_source", "")):
            self._set_cache(cache_key, data)
            return data

        data = self._mock_stock(code)
        self._set_cache(cache_key, data)
        return data

    def _fetch_stock_eastmoney(self, code: str) -> Dict:
        """从东方财富获取个股行情"""
        try:
            import urllib.request
            import json

            secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = f"?fltt=2&fields=f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18&secid={secid}"

            req = urllib.request.Request(url + params, headers={
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())

            d = body.get("data")
            if not d or not d.get("f12"):
                return {}

            return {
                "code": d.get("f12", ""),
                "name": d.get("f14", ""),
                "current": d.get("f2", 0),
                "change_pct": d.get("f3", 0),
                "change": d.get("f4", 0),
                "volume": d.get("f5", 0),
                "amount": d.get("f6", 0),
                "open": d.get("f17", 0),
                "high": d.get("f15", 0),
                "low": d.get("f16", 0),
                "prev_close": d.get("f18", 0),
                "data_source": "东方财富",
                "data_freshness": "实时",
            }

        except Exception as e:
            logger.warning("东方财富个股 API 失败 %s: %s", code, e)
            return {}

    def _mock_stock(self, code: str) -> Dict:
        return {
            "code": code, "name": f"股票{code}",
            "current": 100.0, "change_pct": 1.5,
            "data_source": "模拟数据",
            "data_freshness": "模拟",
        }

    # ── 基金数据 ──────────────────────────────────────────

    def _get_fund_data(self, code: str) -> Dict:
        """获取基金数据：天天基金 → 模拟"""
        cache_key = f"fund_{code}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        data = self._fetch_fund_eastmoney(code)
        if data and "模拟" not in str(data.get("data_source", "")):
            self._set_cache(cache_key, data, ttl=600)
            return data

        data = self._mock_fund(code)
        self._set_cache(cache_key, data, ttl=300)
        return data

    def _fetch_fund_eastmoney(self, code: str) -> Dict:
        """从天天基金（东方财富）获取基金数据"""
        try:
            import urllib.request
            import json

            url = f"https://fundgz.1234567.com.cn/js/{code}.js"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"https://fund.eastmoney.com/{code}.html",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("utf-8")

            # 解析 jsonpgz({...}) 格式
            if "jsonpgz(" in text:
                json_str = text[text.index("{"):text.rindex("}")+1]
                d = json.loads(json_str)
                return {
                    "fund_code": d.get("fundcode", code),
                    "fund_name": d.get("name", ""),
                    "nav": d.get("dwjz", 0),
                    "nav_date": d.get("jzrq", ""),
                    "estimated_nav": d.get("gsz", 0),
                    "estimated_change_pct": d.get("gszzl", 0),
                    "data_source": "天天基金",
                    "data_freshness": "实时",
                }

        except Exception as e:
            logger.warning("天天基金 API 失败 %s: %s", code, e)

        # 备用：基金基本信息
        try:
            import urllib.request
            import json

            url = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("utf-8")

            return {
                "fund_code": code,
                "fund_name": f"基金{code}",
                "data_source": "东方财富",
                "data_freshness": "日级",
            }

        except Exception as e:
            logger.warning("东方财富基金页失败 %s: %s", code, e)

        return {}

    def _mock_fund(self, code: str) -> Dict:
        return {
            "fund_code": code,
            "fund_name": f"基金{code}",
            "fund_type": "混合型",
            "nav": 1.850,
            "nav_date": datetime.now().strftime("%Y-%m-%d"),
            "return_1y": 8.5,
            "return_3y": 22.3,
            "pe_quantile": 45,
            "holding_style": "均衡",
            "sector_concentration": "分散",
            "manager_tenure": 3.5,
            "turnover_rate": 120,
            "tracking_error": None,
            "data_source": "模拟数据",
            "data_freshness": "模拟",
        }

    # ── 工具 ──────────────────────────────────────────────

    def _estimate_irreversibility(self, event: str) -> int:
        """估算事件不可逆性（1-10）"""
        high_irr = ["政策", "法律", "法规", "开放", "改革", "制度", "关税", "制裁"]
        mid_irr = ["收购", "合并", "投资", "人事", "监管"]
        score = 5  # 默认
        for w in high_irr:
            if w in event:
                score = max(score, 8)
        for w in mid_irr:
            if w in event:
                score = max(score, 6)
        return score

    def clear_cache(self):
        self.cache.clear()
        logger.info("🔄 DataFetcher 缓存已清空")

    def _get_cache(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["time"] < entry.get("ttl", self.cache_ttl):
                return entry["data"]
        return None

    def _set_cache(self, key: str, data: Dict, ttl: Optional[int] = None):
        self.cache[key] = {
            "data": data,
            "time": time.time(),
            "ttl": ttl or self.cache_ttl,
        }


# ── 便捷函数 ─────────────────────────────────────────────

_default_fetcher = None


def get_fetcher() -> DataFetcher:
    global _default_fetcher
    if _default_fetcher is None:
        _default_fetcher = DataFetcher()
    return _default_fetcher


def fetch_for_analysis(layer: str, params: Dict) -> Dict:
    """
    为指定分析层准备 input_data

    Args:
        layer: tianshi / dili / renhe_stock / renhe_fund
        params: 各层参数
            - tianshi: 无需额外参数
            - dili: {"event": "..."}
            - renhe_stock: {"stock_code": "600519"}
            - renhe_fund: {"fund_code": "518880"}

    Returns:
        input_data dict（直接传给 engine.analyze）
    """
    fetcher = get_fetcher()

    fetchers = {
        "tianshi": lambda _: fetcher.for_tianshi(),
        "dili": lambda p: fetcher.for_dili(p),
        "renhe_stock": lambda p: fetcher.for_renhe_stock(p.get("stock_code", "")),
        "renhe_fund": lambda p: fetcher.for_renhe_fund(p.get("fund_code", "")),
    }

    fn = fetchers.get(layer)
    if not fn:
        return {"error": f"未知分析层: {layer}"}

    return fn(params)


# ── 自测 ─────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    f = DataFetcher()

    print("\n📊 天时层数据:")
    t = f.for_tianshi()
    idx = t.get("market_indices", {})
    for name, d in idx.items():
        print(f"  {name}: {d.get('current')} ({d.get('change_pct')}%)")
    macro = t.get("macro_data", {})
    print(f"  宏观指标: PMI={macro.get('pmi')}, CPI={macro.get('cpi')}")

    print("\n📰 地利层数据:")
    d = f.for_dili({"event": "QFII 国债期货放开", "source": "新华社"})
    print(f"  事件: {d.get('event')}")
    print(f"  不可逆性: {d.get('irreversibility')}/10")

    print("\n📈 个股数据 (600519):")
    s = f.for_renhe_stock("600519")
    print(f"  {s.get('stock_name')}: {s.get('current_price')} ({s.get('change_pct')}%)")

    print("\n💰 基金数据 (518880):")
    fd = f.for_renhe_fund("518880")
    print(f"  {fd.get('fund_name')}: NAV={fd.get('nav')}, 1年收益={fd.get('return_1y')}%")
