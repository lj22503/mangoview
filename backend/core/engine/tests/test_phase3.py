"""
Phase 3 工程化测试

覆盖：
1. upgrade_triggers — 升级转化逻辑
2. signal_api — FastAPI 路由
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.middleware.upgrade_triggers import (
    evaluate_upgrade, format_upgrade_prompt, get_tracker, reset_tracker, UsageTracker,
)
from engine.middleware.tier_model import UserTier


# ── Upgrade Triggers 测试 ─────────────────────────────────────

def test_upgrade_free_daily_limit():
    """免费用户每日查看近上限时触发"""
    result = evaluate_upgrade(UserTier.FREE, {"daily_views": 9, "monthly_analyses": 1})
    assert result is not None
    assert result["current_tier"] == "FREE"
    assert result["recommended_tier"] == "BASIC"
    assert "9 次" in result["message"]


def test_upgrade_free_deep_analysis():
    """免费用户月度分析近上限时触发"""
    result = evaluate_upgrade(UserTier.FREE, {"daily_views": 2, "monthly_analyses": 2})
    assert result is not None
    assert result["reason"] == "deep_analysis"


def test_upgrade_free_no_trigger():
    """免费用户使用量低时不触发"""
    result = evaluate_upgrade(UserTier.FREE, {"daily_views": 1, "monthly_analyses": 0})
    assert result is None


def test_upgrade_basic_monitor():
    """BASIC 用户监控近上限时触发"""
    result = evaluate_upgrade(UserTier.BASIC, {"active_monitors": 9})
    assert result is not None
    assert result["recommended_tier"] == "VIP"


def test_upgrade_basic_advanced_feature():
    """BASIC 用户请求高级功能时触发"""
    result = evaluate_upgrade(UserTier.BASIC, {"requested_feature": "backtest"})
    assert result is not None
    assert "backtest" in result["message"]


def test_upgrade_vip_no_upgrade():
    """VIP 用户无进一步升级"""
    result = evaluate_upgrade(UserTier.VIP, {})
    assert result is None


def test_upgrade_empty_context():
    """空上下文字典返回 None"""
    result = evaluate_upgrade(UserTier.FREE, {})
    assert result is None


def test_format_upgrade_prompt():
    """格式化升级提示"""
    info = {
        "current_tier": "FREE",
        "recommended_tier": "BASIC",
        "reason": "daily_limit",
        "message": "今日已查看 9 次信号，免费版每日限 10 次。升级 BASIC 解锁无限查看。",
        "benefits": ["完整六步分析报告", "每日无限信号查看"],
    }
    prompt = format_upgrade_prompt(info)
    assert prompt is not None
    assert "BASIC" in prompt
    assert "完整六步分析报告" in prompt


def test_format_upgrade_prompt_none():
    """None 返回 None"""
    assert format_upgrade_prompt(None) is None


def test_usage_tracker():
    """使用量追踪器"""
    reset_tracker()
    tracker = get_tracker()

    tracker.record_view("user1")
    tracker.record_view("user1")
    assert tracker.get_daily_views("user1") >= 2

    tracker.record_analysis("user1")
    assert tracker.get_monthly_analyses("user1") >= 1


def test_usage_tracker_reset():
    """追踪器重置"""
    tracker = UsageTracker()
    tracker.record_view("u1")
    tracker.record_view("u2")
    tracker.reset()
    assert tracker.get_daily_views("u1") == 0


# ── FastAPI 路由测试 ──────────────────────────────────────────

def test_api_analyze():
    """验证 /api/v1/analyze 端点"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.post("/api/v1/analyze", json={
        "layer": "tianshi",
        "input_data": {
            "data_source": "Wind",
            "source_type": "官方",
            "raw_data": {"macro_data": {"pmi": 50.2}},
        },
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("ok", "partial")


def test_api_analyze_multi():
    """验证 /api/v1/analyze/multi 端点"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    # 清理 registry
    from engine.signals.signal_registry import reset_registry
    reset_registry()
    client = TestClient(app)

    resp = client.post("/api/v1/analyze/multi", json={
        "layers": ["tianshi", "dili"],
        "input_data": {
            "tianshi": {
                "data_source": "Wind",
                "source_type": "官方",
                "raw_data": {"macro_data": {"pmi": 50.2}},
            },
            "dili": {
                "data_source": "新华社",
                "raw_data": {"event": "降息 25bp"},
            },
        },
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "layers" in body["data"]


def test_api_analyze_with_tier():
    """不同用户层级的分析"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # FREE 用户应有 upgrade_prompt 触发
    resp = client.post("/api/v1/analyze", json={
        "layer": "tianshi",
        "input_data": {
            "data_source": "Wind",
            "source_type": "官方",
            "raw_data": {"macro_data": {"pmi": 50.2}},
        },
    }, headers={"X-User-Tier": "FREE", "X-User-Id": "test_free_user"})

    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body

    # VIP 用户
    resp2 = client.post("/api/v1/analyze", json={
        "layer": "tianshi",
        "input_data": {
            "data_source": "Wind",
            "source_type": "官方",
            "raw_data": {"macro_data": {"pmi": 50.2}},
        },
    }, headers={"X-User-Tier": "VIP", "X-User-Id": "test_vip_user"})
    assert resp2.status_code == 200


def test_api_list_signals():
    """验证 GET /api/v1/signals"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from engine.signals.signal_registry import reset_registry
    from fastapi import FastAPI

    reset_registry()

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/api/v1/signals")
    assert resp.status_code == 200
    assert "total" in resp.json()
    assert "signals" in resp.json()


def test_api_stats():
    """验证 GET /api/v1/stats"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/api/v1/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "signals" in body
    assert "executions" in body


def test_api_aggregate():
    """验证 GET /api/v1/aggregate"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from engine.signals.signal_registry import reset_registry
    from fastapi import FastAPI

    reset_registry()

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/api/v1/aggregate")
    assert resp.status_code == 200
    body = resp.json()
    assert "aggregate" in body
    assert "by_layer" in body


def test_api_get_signal_not_found():
    """不存在的信号返回 404"""
    from fastapi.testclient import TestClient
    from engine.signals.signal_api import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/api/v1/signals/nonexistent-id")
    assert resp.status_code == 404
