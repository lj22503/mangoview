from fastapi import APIRouter

router = APIRouter(prefix="/v1/tools", tags=["tools"])

# Tools API — 工具路由（待扩展，当前使用 /v1/analysis/cycle-locator）