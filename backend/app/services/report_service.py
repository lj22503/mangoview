"""报告生成服务 — 从 market_service 取真实数据，按模板组装日报/周报/月报"""
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from ..models.database import Report
from .market_service import (
    fetch_macro_indicators,
    fetch_north_money,
    fetch_industries,
)


def _fmt_pct(val: float) -> str:
    """格式化百分比，正数加+号"""
    if val > 0:
        return f"+{val:.1f}%"
    return f"{val:.1f}%"


def _pmi_text(val: float) -> str:
    if val >= 52:
        return "制造业强劲扩张"
    elif val >= 50:
        return "制造业温和扩张"
    else:
        return "制造业收缩，需关注"


def _north_text(net: float) -> str:
    if net > 50:
        return "北向资金大幅净流入，外资积极做多"
    elif net > 0:
        return "北向资金小幅净流入"
    elif net > -20:
        return "北向资金小幅净流出"
    else:
        return "北向资金明显净流出，外资避险情绪升温"


def _direction_arrow(d: str) -> str:
    return "↑" if d == "up" else "↓" if d == "down" else "→"


def _generate_daily(db: Session) -> Report:
    today = date.today()
    macro = fetch_macro_indicators(db)
    north = fetch_north_money(db)

    # 取 PMI
    pmi = next((i for i in macro["indicators"] if i["name"] == "PMI"), None)
    cpi = next((i for i in macro["indicators"] if i["name"] == "CPI"), None)

    pmi_val = pmi["current"] if pmi else 50.0
    cpi_val = cpi["current"] if cpi else 102.0
    north_net = north.get("net_buy", 0.0)

    summary = f"PMI {pmi_val}, CPI {cpi_val}, 北向净{'流入' if north_net >= 0 else '流出'} {abs(north_net):.1f}亿"

    full = f"""## 宏观快照
- PMI: {pmi_val} — {_pmi_text(pmi_val)}
- CPI: {cpi_val}
- 北向资金净额: {north_net:+.1f}亿 — {_north_text(north_net)}
- 沪深300涨跌: {north.get('hs300_change', 0):+.2f}%

## 一句话
当前宏观信号{'' if pmi_val >= 50 else '不'}支持权益资产，北向资金{'积极' if north_net > 0 else '谨慎'}。"""

    return Report(
        type="daily",
        report_date=today,
        title=f"{today.isoformat()} 日报",
        summary=summary,
        full_content=full,
        is_locked=0,
        created_at=datetime.utcnow(),
    )


def _generate_weekly(db: Session) -> Report:
    today = date.today()
    macro = fetch_macro_indicators(db)
    north = fetch_north_money(db)
    industries = fetch_industries(db)

    # 宏观指标变化
    macro_lines = []
    for ind in macro["indicators"]:
        arrow = _direction_arrow(ind["direction"])
        macro_lines.append(f"- {ind['name']}: {ind['current']} {arrow}（前值 {ind['previous']}）")

    # 行业排序
    sorted_ind = sorted(industries["industries"], key=lambda x: x["net_profit_growth"], reverse=True)
    top3 = sorted_ind[:3]
    bottom3 = sorted_ind[-3:]

    top_lines = "\n".join(
        f"  {i+1}. {ind['name']}（净利润增速 {_fmt_pct(ind['net_profit_growth'])}）"
        for i, ind in enumerate(top3)
    )
    bottom_lines = "\n".join(
        f"  {i+1}. {ind['name']}（净利润增速 {_fmt_pct(ind['net_profit_growth'])}）"
        for i, ind in enumerate(bottom3)
    )

    north_net = north.get("net_buy", 0.0)
    summary = f"宏观指标{len(macro['indicators'])}项，北向净{'流入' if north_net >= 0 else '流出'}{abs(north_net):.1f}亿"

    full = f"""## 本周宏观概览
{chr(10).join(macro_lines)}

## 北向资金
- 净额: {north_net:+.1f}亿 — {_north_text(north_net)}
- 沪深300: {north.get('hs300_change', 0):+.2f}%

## 行业表现
### 涨幅 Top3
{top_lines}

### 跌幅 Bottom3
{bottom_lines}"""

    return Report(
        type="weekly",
        report_date=today,
        title=f"{today.isoformat()} 周报",
        summary=summary,
        full_content=full,
        is_locked=0,
        created_at=datetime.utcnow(),
    )


def _generate_monthly(db: Session) -> Report:
    today = date.today()
    macro = fetch_macro_indicators(db)
    north = fetch_north_money(db)
    industries = fetch_industries(db)

    # 复用周报结构，叠加行业估值
    weekly = _generate_weekly(db)

    pe_lines = []
    for ind in sorted(industries["industries"], key=lambda x: x["pe_percentile"]):
        risk = "低估" if ind["pe_percentile"] < 30 else "合理" if ind["pe_percentile"] < 70 else "高估"
        pe_lines.append(f"- {ind['name']}: PE分位 {ind['pe_percentile']:.1f}%（{risk}）")

    north_net = north.get("net_buy", 0.0)
    summary = f"月报 — 宏观指标{len(macro['indicators'])}项，行业{len(industries['industries'])}个"

    full = weekly.full_content + f"""

## 行业估值分位
{chr(10).join(pe_lines)}

## 配置建议
根据当前周期定位，建议关注 PE 分位低于 30% 的行业，回避高于 70% 的行业。

> 数据更新时间: {datetime.utcnow().isoformat()}
> 北向资金月度累计: {north_net:+.1f}亿"""

    return Report(
        type="monthly",
        report_date=today,
        title=f"{today.strftime('%Y年%m月')} 月报",
        summary=summary,
        full_content=full,
        is_locked=1,
        created_at=datetime.utcnow(),
    )


_GENERATORS = {
    "daily": _generate_daily,
    "weekly": _generate_weekly,
    "monthly": _generate_monthly,
}


def generate_report(report_type: str, db: Session) -> Report:
    """生成指定类型的报告，写入DB并返回"""
    if report_type not in _GENERATORS:
        raise ValueError(f"不支持的报告类型: {report_type}")
    report = _GENERATORS[report_type](db)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
