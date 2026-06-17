from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("")
async def get_reports(type: str = "daily", page: int = 1, limit: int = 10):
    """获取报告列表"""

    # Mock data - 实际应从数据库读取
    reports = []

    if type == "daily":
        for i in range(5):
            reports.append({
                "id": f"RPT{i:03d}",
                "type": "daily",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": f"{datetime.now().strftime('%Y-%m-%d')} 日报",
                "summary": "大盘情绪中性偏多，北向资金净流入，行业轮动加速。",
                "is_locked": False
            })
    elif type == "weekly":
        for i in range(3):
            reports.append({
                "id": f"WRPT{i:03d}",
                "type": "weekly",
                "date": "2026-06-01",
                "title": f"2026 年第 {i+22} 周周报",
                "summary": "本周市场震荡上行，消费板块表现强势，科技板块分化。",
                "is_locked": False
            })
    else:
        reports.append({
            "id": "MRPT001",
            "type": "monthly",
            "date": "2026-05-31",
            "title": "2026 年 5 月月报",
            "summary": "5月市场回顾：宏观数据边际改善，行业估值分化。",
            "is_locked": True
        })

    return {
        "code": 0,
        "data": {
            "reports": reports,
            "total": len(reports),
            "page": page,
            "limit": limit
        }
    }