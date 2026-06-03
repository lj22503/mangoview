from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MangoView API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MangoView API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "mangoview-api"}

@app.get("/api/v1/market/macro")
async def get_macro_data():
    """获取宏观数据"""
    return {
        "code": 0,
        "data": {
            "indicators": [
                {
                    "name": "PMI",
                    "current": 50.8,
                    "previous": 50.2,
                    "direction": "up",
                    "percentile": 65.2,
                    "date": "2026-05-31",
                    "source": "国家统计局"
                },
                {
                    "name": "CPI",
                    "current": 102.3,
                    "previous": 102.1,
                    "direction": "up",
                    "percentile": 58.5,
                    "date": "2026-05-31",
                    "source": "国家统计局"
                },
                {
                    "name": "GDP",
                    "current": 5.2,
                    "previous": 5.0,
                    "direction": "up",
                    "percentile": 62.0,
                    "date": "2026-Q1",
                    "source": "国家统计局"
                }
            ],
            "updated_at": "2026-06-03T06:25:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
