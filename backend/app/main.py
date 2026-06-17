from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1 import market, tools, portfolio, reports, analysis
from app.models.database import init_db

app = FastAPI(
    title="MangoView API",
    description="基于经典框架的 SaaS 投资辅助工具 API",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)