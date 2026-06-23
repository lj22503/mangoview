from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ...models.database import get_db, Report
from ...services.report_service import generate_report

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("")
async def list_reports(
    type: str = Query("daily"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取报告列表"""
    query = db.query(Report).filter(Report.type == type)
    total = query.count()
    reports = (
        query.order_by(Report.report_date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "code": 0,
        "data": {
            "reports": [
                {
                    "id": r.id,
                    "type": r.type,
                    "report_date": str(r.report_date),
                    "title": r.title,
                    "summary": r.summary,
                    "is_locked": bool(r.is_locked),
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reports
            ],
            "total": total,
            "page": page,
            "limit": limit,
        },
    }


@router.get("/{report_id}")
async def get_report_detail(
    report_id: int,
    is_premium: bool = Query(False),
    db: Session = Depends(get_db),
):
    """获取报告详情 — 付费用户返回全文"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return {"code": 404, "message": "报告不存在"}

    return {
        "code": 0,
        "data": {
            "report": {
                "id": report.id,
                "type": report.type,
                "report_date": str(report.report_date),
                "title": report.title,
                "summary": report.summary,
                "full_content": report.full_content if is_premium else None,
                "is_locked": bool(report.is_locked),
                "created_at": report.created_at.isoformat() if report.created_at else None,
            }
        },
    }


@router.post("/generate")
async def trigger_generate(
    type: str = Query("daily"),
    db: Session = Depends(get_db),
):
    """手动触发生成报告"""
    if type not in ("daily", "weekly", "monthly"):
        return {"code": 400, "message": "不支持的报告类型，可选 daily/weekly/monthly"}
    try:
        report = generate_report(type, db)
        return {
            "code": 0,
            "data": {
                "report_id": report.id,
                "type": report.type,
                "title": report.title,
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"生成失败: {str(e)}"}
