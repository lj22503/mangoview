from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import asyncio

from ...models.database import get_db
from ...services.market_service import (
    fetch_macro_indicators, fetch_north_money, fetch_industries
)

router = APIRouter(prefix="/v1/market", tags=["market"])


@router.get("/macro")
async def get_macro_data(db: Session = Depends(get_db)):
    """获取宏观数据 - 带超时保护，5秒超时则返回兜底数据"""
    data = await asyncio.to_thread(fetch_macro_indicators, db)
    return {"code": 0, "data": data}


@router.get("/north-money")
async def get_north_money(db: Session = Depends(get_db)):
    """获取北向资金数据 - 带超时保护"""
    data = await asyncio.to_thread(fetch_north_money, db)
    return {"code": 0, "data": data}


@router.get("/industries")
async def get_industries(db: Session = Depends(get_db)):
    """获取行业板块数据 - 带超时保护，失败返回兜底行业"""
    data = await asyncio.to_thread(fetch_industries, db)
    return {"code": 0, "data": data}