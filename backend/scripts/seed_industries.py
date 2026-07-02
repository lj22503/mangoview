"""
seed_industries.py — 申万31个一级行业数据填充脚本

数据来源：东方财富公开 API（requests 直接调用，无 akshare 依赖）
填充表：industry_info / industry_financials / industry_valuation
"""
import os, sys, json, time
from datetime import datetime, date

import requests

# ── 确保能 import 项目模块 ──
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_ROOT)

from app.models.database import (
    init_db, SessionLocal,
    IndustryInfo, IndustryFinancials, IndustryValuation,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://data.eastmoney.com/",
}

# ════════════════════════════════════════════════════════════
# 第 1 步：获取申万31个一级行业列表
# ════════════════════════════════════════════════════════════

def fetch_industry_list():
    """从东方财富获取申万一级行业列表。返回 [(code, name), ...]"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": 50,
        "po": 1,
        "np": 1,
        "fields": "f12,f14",
        "fid": "f12",
        "fs": "m:90+t2",
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", {}).get("diff", [])
    if not items:
        raise RuntimeError("东方财富行业列表返回为空")

    industries = []
    for item in items:
        code = item.get("f12", "").strip()
        name = item.get("f14", "").strip()
        if code and name:
            industries.append((code, name))
    print(f"[1/4] 获取到 {len(industries)} 个申万一级行业")
    return industries


# ════════════════════════════════════════════════════════════
# 第 2 步：获取行业估值数据（PE/PB/股息率）
# ════════════════════════════════════════════════════════════

def fetch_industry_valuations():
    """获取申万行业最新估值数据。
    返回 {industry_code: {pe_ttm, pb_lf, dividend_yield, pe_percentile, pb_percentile, ...}}
    """
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "reportName": "RPT_VALUEANALY_DET",
        "columns": "ALL",
        "pageSize": 50,
        "sortColumns": "TRADE_DATE",
        "sortTypes": "-1",
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("result", {})
    rows = result.get("data", [])
    if not rows:
        print("[2/4] 行业估值 API 返回为空，将使用估算值")
        return {}

    val_map = {}
    for row in rows:
        code = str(row.get("SW_INDEX_CODE", "")).strip()
        if not code:
            continue
        pe_ttm = safe_float(row.get("PE_TTM"))
        pb_lf = safe_float(row.get("PB_LF"))
        div_yield = safe_float(row.get("DIVIDEND_YIELD"))
        pe_percentile = safe_float(row.get("PE_TTM_HIST_RANK", 50.0))
        pb_percentile = safe_float(row.get("PB_LF_HIST_RANK", 50.0))
        div_percentile = safe_float(row.get("DIVIDEND_YIELD_HIST_RANK", 50.0))
        stat_date_str = row.get("TRADE_DATE", "")

        val_map[code] = {
            "pe_ttm": pe_ttm,
            "pb_lf": pb_lf,
            "dividend_yield": div_yield,
            "pe_percentile": pe_percentile,
            "pb_percentile": pb_percentile,
            "dividend_percentile": div_percentile,
            "stat_date": parse_date(stat_date_str),
        }
    print(f"[2/4] 获取到 {len(val_map)} 个行业估值数据")
    return val_map


# ════════════════════════════════════════════════════════════
# 第 3 步：填充数据库
# ════════════════════════════════════════════════════════════

# 行业周期阶段映射（基于常识映射，后续可由分析引擎动态更新）
CYCLE_STAGE_MAP = {
    "808012": "复苏晚期",  # 电子
    "808013": "扩张期",    # 计算机
    "808014": "扩张期",    # 通信
    "808015": "复苏晚期",  # 传媒
    "808016": "放缓",      # 电力设备（新能源高位消化估值）
    "808017": "放缓",      # 国防军工
    "808018": "衰退后期",  # 房地产
    "808019": "放缓",      # 建筑装饰
    "808020": "放缓",      # 建筑材料
    "808021": "衰退后期",  # 钢铁
    "808022": "衰退后期",  # 有色金属
    "808023": "衰退后期",  # 基础化工
    "808024": "衰退后期",  # 石油石化
    "808025": "复苏早期",  # 煤炭
    "808026": "扩张期",    # 公用事业
    "808027": "扩张期",    # 交通运输
    "808028": "复苏晚期",  # 汽车
    "808029": "复苏晚期",  # 机械设备
    "808030": "复苏早期",  # 家用电器
    "808031": "复苏早期",  # 轻工制造
    "808032": "复苏早期",  # 纺织服饰
    "808033": "复苏早期",  # 商贸零售
    "808034": "复苏早期",  # 社会服务
    "808035": "扩张期",    # 食品饮料
    "808036": "放缓",      # 农林牧渔
    "808037": "扩张期",    # 医药生物
    "808038": "扩张期",    # 银行
    "808039": "扩张期",    # 非银金融
    "808040": "复苏晚期",  # 综合
    "808041": "复苏早期",  # 环保
    "808042": "衰退后期",  # 美容护理
}

# 渗透率估算（产业常识）
PENETRATION_MAP = {
    "808012": 85.0,  # 电子
    "808013": 90.0,  # 计算机
    "808014": 92.0,  # 通信
    "808015": 75.0,  # 传媒
    "808016": 60.0,  # 电力设备
    "808017": 40.0,  # 国防军工
    "808018": 85.0,  # 房地产
    "808019": 80.0,  # 建筑装饰
    "808020": 78.0,  # 建筑材料
    "808021": 70.0,  # 钢铁
    "808022": 65.0,  # 有色金属
    "808023": 72.0,  # 基础化工
    "808024": 68.0,  # 石油石化
    "808025": 60.0,  # 煤炭
    "808026": 88.0,  # 公用事业
    "808027": 82.0,  # 交通运输
    "808028": 70.0,  # 汽车
    "808029": 75.0,  # 机械设备
    "808030": 85.0,  # 家用电器
    "808031": 65.0,  # 轻工制造
    "808032": 60.0,  # 纺织服饰
    "808033": 70.0,  # 商贸零售
    "808034": 55.0,  # 社会服务
    "808035": 80.0,  # 食品饮料
    "808036": 50.0,  # 农林牧渔
    "808037": 75.0,  # 医药生物
    "808038": 90.0,  # 银行
    "808039": 85.0,  # 非银金融
    "808040": 50.0,  # 综合
    "808041": 45.0,  # 环保
    "808042": 40.0,  # 美容护理
}

# CR3（前3大公司集中度估算）
CR3_MAP = {
    "808012": 25.0,
    "808013": 30.0,
    "808014": 55.0,
    "808015": 50.0,
    "808016": 45.0,
    "808017": 60.0,
    "808018": 20.0,
    "808019": 30.0,
    "808020": 40.0,
    "808021": 45.0,
    "808022": 35.0,
    "808023": 20.0,
    "808024": 70.0,
    "808025": 50.0,
    "808026": 40.0,
    "808027": 35.0,
    "808028": 40.0,
    "808029": 25.0,
    "808030": 55.0,
    "808031": 20.0,
    "808032": 25.0,
    "808033": 30.0,
    "808034": 15.0,
    "808035": 35.0,
    "808036": 15.0,
    "808037": 20.0,
    "808038": 45.0,
    "808039": 40.0,
    "808040": 10.0,
    "808041": 25.0,
    "808042": 40.0,
}


def seed_db():
    # 初始化数据库（确保表已建）
    init_db()
    db = SessionLocal()

    try:
        # ── 检查是否已填充 ──
        existing = db.query(IndustryInfo).count()
        if existing > 0:
            print(f"[skip] industry_info 已有 {existing} 条记录，跳过填充")
            return

        # ── 获取行业列表 ──
        industries = fetch_industry_list()
        if not industries:
            print("❌ 未获取到行业列表，退出")
            return

        # ── 获取估值数据 ──
        val_map = fetch_industry_valuations()

        # ── 清空旧数据（如果有） ──
        db.query(IndustryValuation).delete()
        db.query(IndustryFinancials).delete()
        db.query(IndustryInfo).delete()
        db.commit()

        now = datetime.utcnow()

        info_count = 0
        fin_count = 0
        val_count = 0

        for code, name in industries:
            # ── 1. industry_info ──
            stage = CYCLE_STAGE_MAP.get(code, "观察")
            penetration = PENETRATION_MAP.get(code, 50.0)
            cr3 = CR3_MAP.get(code, 25.0)

            info = IndustryInfo(
                industry_code=code,
                industry_name=name,
                cycle_stage=stage,
                penetration=penetration,
                cr3=cr3,
                updated_at=now,
            )
            db.add(info)
            info_count += 1

            # ── 2. industry_financials（填一份近期季度数据） ──
            # 根据周期阶段估算净利润增速
            growth_est = _estimate_growth(stage)
            fin = IndustryFinancials(
                industry_code=code,
                year=2026,
                quarter=1,
                net_profit_growth=growth_est,
                revenue_growth=growth_est * 0.7 + 2.0,
                updated_at=now,
            )
            db.add(fin)
            fin_count += 1

            # ── 3. industry_valuation ──
            vdata = val_map.get(code, {})
            pe = vdata.get("pe_ttm") or _estimate_pe(stage)
            pb = vdata.get("pb_lf") or _estimate_pb(stage)
            div_yield = vdata.get("dividend_yield") or _estimate_dividend(stage)
            pe_pct = vdata.get("pe_percentile") or _estimate_pe_percentile(stage)
            pb_pct = vdata.get("pb_percentile") or 50.0
            div_pct = vdata.get("dividend_percentile") or 50.0
            stat_date = vdata.get("stat_date") or date.today()

            # 象限判定
            quadrant = _determine_quadrant(pe_pct, pb_pct)

            val = IndustryValuation(
                industry_code=code,
                stat_date=stat_date,
                pe_ttm=pe,
                pe_percentile=pe_pct,
                pb_lf=pb,
                pb_percentile=pb_pct,
                dividend_yield=div_yield,
                dividend_percentile=div_pct,
                quadrant=quadrant,
                updated_at=now,
            )
            db.add(val)
            val_count += 1

        db.commit()
        print(f"[3/4] 填充完成: industry_info={info_count}, "
              f"industry_financials={fin_count}, industry_valuation={val_count}")

        # ── 验证 ──
        print("[4/4] 验证：")
        for table, model in [
            ("industry_info", IndustryInfo),
            ("industry_financials", IndustryFinancials),
            ("industry_valuation", IndustryValuation),
        ]:
            cnt = db.query(model).count()
            print(f"  {table}: {cnt} 条")

    except Exception as e:
        db.rollback()
        print(f"❌ 填充失败: {e}")
        raise
    finally:
        db.close()


# ════════════════════════════════════════════════════════════
# 辅助函数
# ════════════════════════════════════════════════════════════

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        f = float(val)
        if f != f or abs(f) == float("inf"):
            return default
        return f
    except (ValueError, TypeError):
        return default


def parse_date(val):
    if not val:
        return date.today()
    s = str(val)[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return date.today()


def _estimate_growth(stage):
    """根据周期阶段估算净利增速"""
    mapping = {
        "复苏早期": 15.0,
        "复苏晚期": 10.0,
        "扩张期": 8.0,
        "放缓": 3.0,
        "衰退后期": -5.0,
        "观察": 5.0,
    }
    return mapping.get(stage, 5.0)


def _estimate_pe(stage):
    mapping = {
        "复苏早期": 18.0,
        "复苏晚期": 22.0,
        "扩张期": 25.0,
        "放缓": 15.0,
        "衰退后期": 10.0,
        "观察": 20.0,
    }
    return mapping.get(stage, 20.0)


def _estimate_pb(stage):
    mapping = {
        "复苏早期": 1.8,
        "复苏晚期": 2.2,
        "扩张期": 2.8,
        "放缓": 1.5,
        "衰退后期": 1.0,
        "观察": 1.8,
    }
    return mapping.get(stage, 1.8)


def _estimate_dividend(stage):
    mapping = {
        "复苏早期": 1.5,
        "复苏晚期": 1.2,
        "扩张期": 0.8,
        "放缓": 2.0,
        "衰退后期": 3.0,
        "观察": 1.5,
    }
    return mapping.get(stage, 1.5)


def _estimate_pe_percentile(stage):
    mapping = {
        "复苏早期": 30.0,
        "复苏晚期": 55.0,
        "扩张期": 65.0,
        "放缓": 40.0,
        "衰退后期": 15.0,
        "观察": 50.0,
    }
    return mapping.get(stage, 50.0)


def _determine_quadrant(pe_pct, pb_pct):
    if pe_pct < 30 and pb_pct < 30:
        return "低估值区域"
    elif pe_pct < 30:
        return "PE低估/PB适中"
    elif pe_pct > 70 and pb_pct > 70:
        return "高估值区域"
    elif pe_pct > 70:
        return "PE高估/PB适中"
    elif pb_pct < 30:
        return "PB低估/PE适中"
    else:
        return "估值适中"


if __name__ == "__main__":
    seed_db()
