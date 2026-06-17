"""
MangoView 每日数据推送飞书群机器人
"""
import sys, os, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from app.models.database import SessionLocal, MacroIndicator, NorthMoneyFlow


FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/032658bd-15c5-47b6-bcad-521907194736"


def fetch_data():
    db = SessionLocal()
    try:
        # 宏观指标
        macro_recs = db.query(MacroIndicator).order_by(
            MacroIndicator.data_date.desc()
        ).limit(4).all()
        macro_map = {r.indicator_code: r for r in macro_recs}

        # 北向资金
        north = db.query(NorthMoneyFlow).filter(
            NorthMoneyFlow.net_buy != None
        ).order_by(NorthMoneyFlow.date.desc()).first()

        # 北向汇总（沪+深）
        if north:
            records = db.query(NorthMoneyFlow).filter(
                NorthMoneyFlow.date == north.date,
                NorthMoneyFlow.net_buy != None
            ).all()
            total_net_buy = sum(r.net_buy for r in records)
            total_buy = sum(r.buy_amount or 0 for r in records)
            total_sell = sum(r.sell_amount or 0 for r in records)
        else:
            total_net_buy = total_buy = total_sell = 0
            north = None

        return macro_map, north, total_net_buy, total_buy, total_sell
    finally:
        db.close()


def build_message(macro_map, north, total_net_buy, total_buy, total_sell):
    today = datetime.now().strftime("%Y-%m-%d")

    # 宏观指标
    pmi = macro_map.get("PMI")
    cpi = macro_map.get("CPI")
    gdp = macro_map.get("GDP")
    ppi = macro_map.get("PPI")

    def fmt(val, suffix=""):
        if val is None: return "—"
        if isinstance(val, float):
            return f"{val:.2f}{suffix}"
        return str(val)

    def dir_emoji(d):
        return "up" if d == "up" else "down"

    # 周期判断
    pmi_val = pmi.current_value if pmi else None
    if pmi_val and pmi_val > 50:
        cycle_comment = "制造业处于扩张区间"
    elif pmi_val:
        cycle_comment = "制造业处于收缩区间"
    else:
        cycle_comment = "数据暂无"

    # 宏观部分
    macro_text = f"""**宏观指标** ({today})

* **PMI**: {fmt(pmi.current_value if pmi else None)} {dir_emoji(pmi.direction) if pmi else ""} | 较前: {fmt(pmi.previous_value if pmi else None)}
* **CPI**: {fmt(cpi.current_value if cpi else None)} {dir_emoji(cpi.direction) if cpi else ""} | 较前: {fmt(cpi.previous_value if cpi else None)}
* **GDP**: {fmt(gdp.current_value if gdp else None, "%")} {dir_emoji(gdp.direction) if gdp else ""}
* **PPI**: {fmt(ppi.current_value if ppi else None)} {dir_emoji(ppi.direction) if ppi else ""}

{cycle_comment}"""

    # 北向资金
    if north and total_net_buy != 0:
        north_text = f"""**北向资金** ({north.date})

* 当日净买入: **{total_net_buy:+.2f} 亿**
* 买入额: {total_buy:.2f} 亿 | 卖出额: {total_sell:.2f} 亿
* 沪深300涨跌: {fmt(north.hs300_change, "%")}"""
    else:
        north_text = f"""**北向资金**

今日数据暂无（可能为非交易日）"""

    # 行业部分（fallback数据）
    industries_text = """**行业机会** (数据来源受限，仅供参考)

* **消费** - 复苏早期：关注库存变化
* **科技** - 成长期：关注渗透率提升
* **医药** - 成熟期：防御性配置

> 行业实时数据接口受限，详细分析需接入完整数据源"""

    # 事件部分
    events_text = """**事件信号** (本周关注)

* 央行公开市场操作（逆回购/SLF/MLF）
* 北向资金单日大幅净流入/出（>50亿信号意义）
* 美联储议息会议（影响全球流动性）
* 国内重要宏观数据发布（每月10日前后）

> 完整事件库 + AI研判 -> [加入星球解锁]"""

    full_text = f"""{macro_text}

---

{north_text}

---

{industries_text}

---

{events_text}

---

*MangoView · 自上而下，看清每一笔投资*
"""

    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"MangoView 每日投资速览 {today}",
                    "content": [[{"tag": "text", "text": full_text}]]
                }
            }
        }
    }


def send_to_feishu(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        FEISHU_WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    print(f"[{datetime.now().isoformat()}] Fetching data...")
    macro_map, north, total_net_buy, total_buy, total_sell = fetch_data()

    print(f"[{datetime.now().isoformat()}] Pushing to Feishu...")
    msg = build_message(macro_map, north, total_net_buy, total_buy, total_sell)

    try:
        result = send_to_feishu(msg)
        if result.get("code") == 0 or result.get("StatusCode") == 0:
            print("[OK] Feishu push succeeded")
        else:
            print(f"[WARN] Feishu response: {result}")
    except Exception as e:
        print(f"[ERROR] Feishu push failed: {e}")


if __name__ == "__main__":
    main()