"""MangoView API — 应用入口"""
import sys
import os
import logging

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1 import market, tools, portfolio, reports, analysis
from app.models.database import init_db, SessionLocal, IndustryInfo

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MangoView API",
    description="基于经典框架的 SaaS 投资辅助工具 API",
    version="0.1.0"
)

# CORS 配置 — 环境变量 CORS_ORIGINS（逗号分隔），默认本地开发
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(market.router)
app.include_router(tools.router)
app.include_router(portfolio.router)
app.include_router(reports.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    return {"message": "MangoView API is running", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "mangoview-api"}


@app.on_event("startup")
async def startup_event():
    # 确保数据目录存在
    os.makedirs(os.environ.get("MANGOVIEW_DATA_DIR", "data"), exist_ok=True)
    # 初始化数据库
    init_db()

    # 种子数据：行业信息（首次部署 / 重建后自动填充）
    try:
        db = SessionLocal()
        existing = db.query(IndustryInfo).count()
        db.close()
        if existing == 0:
            from scripts.seed_industries import seed_db
            seed_db()
            logger.info("种子数据填充完成 (industry)")
        else:
            logger.info("行业数据已存在，跳过种子填充")
    except Exception as e:
        logger.warning("种子数据填充失败: %s", e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
