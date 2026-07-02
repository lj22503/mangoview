"""种子脚本：从东方财富 API 获取申万31个一级行业并写入 SQLite DB"""

import sqlite3
import requests
import json
from datetime import datetime

DB_PATH = r"D:\claudework\workspace\data\mangoview.db"

# === 1. 获取申万行业列表 ===
INDUSTRY_URL = "https://push2.eastmoney.com/api/qt/clist/get"
params = {
    "pn": "1",
    "pz": "50",
    "po": "1",
    "np": "1",
    "fields": "f12,f14",
    "fid": "f12",
    "fs": "m:90+t2",
}

print("[1/3] 请求东方财富申万行业列表...")
resp = requests.get(INDUSTRY_URL, params=params, timeout=15)
resp.raise_for_status()
data = resp.json()

diff_list = data.get("data", {}).get("diff", [])
if not diff_list:
    print("ERROR: 未获取到行业列表，响应结构异常")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    exit(1)

industries = []
for item in diff_list:
    code = item.get("f12", "")
    name = item.get("f14", "")
    if code and name:
        industries.append((code, name))

print(f"获取到 {len(industries)} 个行业")

# 打印前10个
for i, (code, name) in enumerate(industries[:10], 1):
    print(f"  {i}. [{code}] {name}")
if len(industries) > 10:
    print(f"  ... 共 {len(industries)} 个")

# === 2. 写入 industry_info 表 ===
print("\n[2/3] 写入 industry_info 表...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for code, name in industries:
    cursor.execute(
        """INSERT OR REPLACE INTO industry_info 
           (industry_code, industry_name, cycle_stage, penetration, cr3, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (code, name, "复苏", 0.0, 0.0, now_str)
    )

conn.commit()

# 验证
cursor.execute("SELECT COUNT(*) FROM industry_info")
count = cursor.fetchone()[0]
print(f"industry_info 表共 {count} 行")

# === 3. 验证前5行 ===
print("\n[3/3] 验证前5行数据：")
cursor.execute("SELECT * FROM industry_info LIMIT 5")
rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(industry_info)")
cols = [c[1] for c in cursor.fetchall()]
print(f"  列: {cols}")
for row in rows:
    print(f"  {row}")

conn.close()
print("\n✅ 种子数据填充完成！")
