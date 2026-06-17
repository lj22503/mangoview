"""
Mangofolio 信号系统 FastAPI 路由

提供 RESTful API 供外部调用分析引擎。
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, Field

from .. import create_engine
from ..data_fetcher import fetch_for_analysis, get_fetcher
from ..middleware.tier_model import UserTier
from ..middleware.upgrade_triggers import (
    evaluate_upgrade, get_tracker, format_upgrade_prompt,
)
from .signal_registry import get_registry
from .signal_aggregator import aggregate_all, aggregate_by_layer
from .signal_model import SignalLayer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# 引擎单例
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def _parse_tier(x_tier: Optional[str]) -> UserTier:
    if not x_tier:
        return UserTier.FREE
    try:
        return UserTier(x_tier.upper())
    except ValueError:
        return UserTier.FREE


# ── 请求/响应模型 ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """单层分析请求"""
    layer: str = Field(description="分析层: tianshi / dili / renhe_company / renhe_fund")
    input_data: Dict = Field(description="输入数据")
    layer_name: Optional[str] = None


class MultiLayerRequest(BaseModel):
    """多层分析请求"""
    layers: List[str] = Field(description="分析层列表")
    input_data: Dict = Field(description="各层输入数据")


class AnalyzeResponse(BaseModel):
    """分析响应"""
    status: str
    data: Optional[Dict] = None
    upgrade_prompt: Optional[str] = None
    error: Optional[str] = None


class SignalListResponse(BaseModel):
    """信号列表响应"""
    total: int
    signals: List[Dict]


class FetchRequest(BaseModel):
    """数据获取请求"""
    layer: str = Field(description="目标层: tianshi / dili / renhe_stock / renhe_fund")
    params: Dict = Field(default_factory=dict, description="取数参数，如 {'stock_code':'600519'}")


class AutoAnalyzeRequest(BaseModel):
    """自动取数+分析请求"""
    layer: str = Field(description="分析层: tianshi / dili / renhe_stock / renhe_fund")
    params: Dict = Field(default_factory=dict, description="取数参数")
    user_input: Optional[str] = Field(None, description="dili 层用: 事件描述文本")
    layer_name: Optional[str] = None


# ── API 端点 ──────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_tier: Optional[str] = Header(None),
):
    """
    执行单层分析

    Headers:
        X-User-Tier: GUEST / FREE / BASIC / VIP（默认 FREE）
        X-User-Id: 用户标识（用于使用量追踪）
    """
    tier = _parse_tier(x_user_tier)
    engine = _get_engine()
    tracker = get_tracker()

    result = engine.analyze(
        layer=req.layer,
        input_data=req.input_data,
        user_tier=tier,
        layer_name=req.layer_name or req.layer,
    )

    # 记录使用量
    user_id = x_user_id or "anonymous"
    tracker.record_view(user_id)
    if result.get("completed"):
        tracker.record_analysis(user_id)

    # 检查是否需要引导升级
    daily = tracker.get_daily_views(user_id)
    monthly = tracker.get_monthly_analyses(user_id)
    upgrade = evaluate_upgrade(tier, {
        "daily_views": daily,
        "monthly_analyses": monthly,
        "active_monitors": 0,
    })

    response_data = {
        "status": "ok" if result.get("completed") else "partial",
        "data": result,
    }

    if upgrade:
        response_data["upgrade_prompt"] = format_upgrade_prompt(upgrade)

    if result.get("error"):
        response_data["error"] = result["error"]
        response_data["status"] = "error"

    return response_data


@router.post("/analyze/multi", response_model=AnalyzeResponse)
async def analyze_multi(
    req: MultiLayerRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_tier: Optional[str] = Header(None),
):
    """
    执行多层聚合分析

    Headers 同 /analyze
    """
    tier = _parse_tier(x_user_tier)
    engine = _get_engine()

    result = engine.analyze_multi_layer(
        layers=req.layers,
        input_data=req.input_data,
        user_tier=tier,
    )

    # 记录使用量
    if x_user_id:
        tracker = get_tracker()
        tracker.record_view(x_user_id)
        tracker.record_analysis(x_user_id)

    return {
        "status": "ok",
        "data": result,
    }


@router.get("/signals", response_model=SignalListResponse)
async def list_signals(
    x_user_tier: Optional[str] = Header(None),
    layer: Optional[str] = Query(None, description="按层过滤: TIANSHI / DILI / RENHE"),
):
    """
    列出所有活跃信号
    """
    registry = get_registry()
    tier = _parse_tier(x_user_tier)

    if layer:
        try:
            layer_enum = SignalLayer(layer.upper())
            signals = registry.list_by_layer(layer_enum, tier=tier)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的层: {layer}")
    else:
        signals = registry.list_active(tier=tier)

    return {
        "total": len(signals),
        "signals": [s.to_dict() for s in signals],
    }


@router.get("/signals/{signal_id}")
async def get_signal(signal_id: str):
    """获取单个信号详情"""
    registry = get_registry()
    signal = registry.get(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    return signal.to_dict()


@router.get("/stats")
async def get_stats():
    """获取分析引擎统计"""
    engine = _get_engine()
    return engine.get_stats()


@router.get("/aggregate")
async def get_aggregate(
    x_user_tier: Optional[str] = Header(None),
):
    """获取全量信号聚合结果"""
    registry = get_registry()
    tier = _parse_tier(x_user_tier)

    agg_all = aggregate_all(registry, tier=tier)
    agg_by_layer = aggregate_by_layer(registry, tier=tier)

    def _agg_to_dict(a):
        return {
            "direction": a.direction.value,
            "intensity": a.intensity.value,
            "confidence": a.confidence,
            "conflict_detected": a.conflict_detected,
        }

    return {
        "aggregate": _agg_to_dict(agg_all),
        "by_layer": {k: _agg_to_dict(v) for k, v in agg_by_layer.items()},
        "component_count": len(agg_all.component_signals),
    }


# ── 数据获取端点 ─────────────────────────────────────────────


@router.post("/fetch")
async def fetch_data(req: FetchRequest):
    """
    预览某层的数据获取结果（不触发分析）

    用于调试或前端先看数据再决策。
    """
    data = fetch_for_analysis(req.layer, req.params)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return {"layer": req.layer, "data": data}


@router.post("/analyze/auto", response_model=AnalyzeResponse)
async def analyze_auto(
    req: AutoAnalyzeRequest,
    x_user_id: Optional[str] = Header(None),
    x_user_tier: Optional[str] = Header(None),
):
    """
    自动取数 + 分析（一步到位）

    用法示例：
        {"layer": "tianshi", "params": {}}   → 取大盘+宏观数据后分析
        {"layer": "renhe_stock", "params": {"stock_code": "600519"}}
        {"layer": "renhe_fund", "params": {"fund_code": "518880"}}
        {"layer": "dili", "user_input": "QFII 国债期货放开"}
    """
    tier = _parse_tier(x_user_tier)
    engine = _get_engine()
    tracker = get_tracker()

    # 1. 如果有 user_input，转为 dili params
    params = dict(req.params)
    if req.user_input and not params.get("event"):
        params["event"] = req.user_input

    # 2. 获取数据
    input_data = fetch_for_analysis(req.layer, params)
    if "error" in input_data:
        return {"status": "error", "error": input_data["error"]}

    # 3. 分析
    result = engine.analyze(
        layer=req.layer,
        input_data=input_data,
        user_tier=tier,
        layer_name=req.layer_name or req.layer,
    )

    # 4. 使用量追踪
    user_id = x_user_id or "anonymous"
    tracker.record_view(user_id)
    if result.get("completed"):
        tracker.record_analysis(user_id)

    # 5. 升级引导
    daily = tracker.get_daily_views(user_id)
    monthly = tracker.get_monthly_analyses(user_id)
    upgrade = evaluate_upgrade(tier, {
        "daily_views": daily,
        "monthly_analyses": monthly,
        "active_monitors": 0,
    })

    response_data = {
        "status": "ok" if result.get("completed") else "partial",
        "data": result,
        "_fetched_data_preview": {
            "source": input_data.get("data_source", "unknown"),
            "freshness": input_data.get("data_freshness", "unknown"),
        },
    }
    if upgrade:
        response_data["upgrade_prompt"] = format_upgrade_prompt(upgrade)
    if result.get("error"):
        response_data["error"] = result["error"]
        response_data["status"] = "error"

    return response_data
