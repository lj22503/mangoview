"""Mangofolio 分析引擎 — 部署入口"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.signals.signal_api import router

# ── 日志 ──
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ── App ──
app = FastAPI(
    title="Mangofolio 分析引擎",
    version="2.0.0",
    description="天时/地利/人和 三层分析 + 信号系统",
)

# ── CORS ──
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 路由 ──
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Mangofolio 分析引擎",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "multi_analyze": "POST /api/v1/analyze/multi",
            "signals": "GET /api/v1/signals",
            "signal_detail": "GET /api/v1/signals/{id}",
            "stats": "GET /api/v1/stats",
            "aggregate": "GET /api/v1/aggregate",
        },
        "auth": "Headers: X-User-Id, X-User-Tier (FREE|BASIC|VIP)",
    }
