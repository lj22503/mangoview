"""
Mangofolio 提炼传递工具

每步之间只传递精炼后的核心信息，不传递完整分析文本。
按 PROJECT_INVENTORY.md 需求 7.2 定义实现。
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .schema_definitions import SCHEMA_VERSION
from .schema_validator import sanitize_for_transfer

logger = logging.getLogger(__name__)


def build_refined_output(
    step: int,
    core_variables: List[Dict],
    confidence: float,
    key_assumptions: Optional[List[str]] = None,
    pending_validations: Optional[List[str]] = None,
    from_agent: str = "",
    to_agent: str = "",
) -> Dict:
    """
    构建提炼传递输出

    只传递判断结果，不传递分析过程。

    Args:
        step: 当前步骤 0-6
        core_variables: 核心变量列表（≤5 个）
        confidence: 置信度 0-1
        key_assumptions: 关键假设（≤3 条）
        pending_validations: 待验证项（≤3 项）
        from_agent: 发送方 Agent 名称
        to_agent: 接收方 Agent 名称

    Returns:
        符合 REFINED_TRANSFER_SCHEMA 的数据包
    """
    # 计算置信度标签
    if confidence >= 0.7:
        confidence_label = "高"
    elif confidence >= 0.4:
        confidence_label = "中"
    else:
        confidence_label = "低"

    # 限制数组长度
    core_variables = (core_variables or [])[:5]
    key_assumptions = (key_assumptions or [])[:3]
    pending_validations = (pending_validations or [])[:3]

    packet = {
        "schema_version": SCHEMA_VERSION,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "step": step,
        "refined_data": {
            "core_variables": core_variables,
            "confidence": confidence,
            "key_assumptions": key_assumptions,
            "pending_validations": pending_validations,
            "confidence_label": confidence_label,
        },
        "pass_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return sanitize_for_transfer(packet)


def extract_refined_data(packet: Dict) -> Dict:
    """
    从提炼传递包中提取精炼数据

    Args:
        packet: 符合 REFINED_TRANSFER_SCHEMA 的数据包

    Returns:
        refined_data 字典
    """
    return packet.get("refined_data", {})


def merge_refined_inputs(
    current_step: int,
    previous_refined: Optional[Dict],
    new_data: Dict,
) -> Dict:
    """
    将上一步的提炼数据合并到当前步输入

    Args:
        current_step: 当前步骤
        previous_refined: 上一步的提炼数据
        new_data: 当前步的新输入

    Returns:
        合并后的输入数据
    """
    merged = dict(new_data)

    if previous_refined:
        # 传递核心变量（上一步的精炼结果作为当前步的基础）
        merged["core_variables"] = previous_refined.get("core_variables", [])
        merged["previous_confidence"] = previous_refined.get("confidence", 0)
        merged["previous_assumptions"] = previous_refined.get("key_assumptions", [])
        merged["pending_validations"] = previous_refined.get("pending_validations", [])

    merged["_step"] = current_step
    return merged


def build_fallback_packet(
    step: int,
    reason: str,
    previous_packet: Optional[Dict] = None,
) -> Dict:
    """
    构建回退数据包（某步失败，回退到上一步）

    Args:
        step: 当前失败的步骤
        reason: 回退原因
        previous_packet: 上一步的数据包（如有）

    Returns:
        回退标记数据包
    """
    packet = {
        "schema_version": SCHEMA_VERSION,
        "fallback": True,
        "fallback_from_step": step,
        "fallback_reason": reason,
        "pass_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if previous_packet:
        packet["previous_refined"] = extract_refined_data(previous_packet)

    return packet


def limit_variables(
    variables: List[Dict],
    max_count: int = 5,
) -> List[Dict]:
    """
    按重要性截断核心变量列表

    Args:
        variables: 核心变量列表（需含 importance 字段）
        max_count: 最大数量

    Returns:
        截断后的列表
    """
    if len(variables) <= max_count:
        return variables

    priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    sorted_vars = sorted(
        variables,
        key=lambda v: priority.get(v.get("importance", "LOW"), 99)
    )
    logger.info("变量超出限制 (%d > %d)，按重要性截断", len(variables), max_count)
    return sorted_vars[:max_count]
