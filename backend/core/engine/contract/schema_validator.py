"""
Mangofolio Schema 校验器

功能：
- 验证 Agent 间传递的数据是否符合定义的 JSON Schema
- 版本兼容性检查
- 输入净化（去除 NaN/Inf）
"""

import json
import math
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from .schema_definitions import (
    get_schema, check_version_compatibility,
    SCHEMA_REGISTRY, SCHEMA_VERSION
)

logger = logging.getLogger(__name__)


class SchemaValidationError(ValueError):
    """Schema 校验失败"""
    pass


def _sanitize_value(obj: Any) -> Any:
    """递归去除 NaN/Inf，替换为 None"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_value(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_value(v) for v in obj]
    return obj


def _validate_required_fields(data: Dict, required: List[str], path: str = "") -> List[str]:
    """递归检查必填字段"""
    errors = []
    for field in required:
        if field not in data:
            errors.append(f"{path}.{field}: 缺少必填字段")
        elif data[field] is None:
            errors.append(f"{path}.{field}: 字段值为 None")
    # 检查嵌套对象中的 required
    for key, value in data.items():
        if isinstance(value, dict) and "required" in value:
            errors.extend(_validate_required_fields(
                value, value.get("required", []), f"{path}.{key}"
            ))
    return errors


def _validate_max_items(data: Dict, schema: Dict, path: str = "") -> List[str]:
    """递归检查数组 maxItems 约束"""
    errors = []
    props = schema.get("properties", {})

    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        field_schema = props.get(key, {})

        if isinstance(value, list):
            max_items = field_schema.get("maxItems")
            if max_items is not None and len(value) > max_items:
                errors.append(
                    f"{current_path}: 超出最大数量限制 {max_items}（当前 {len(value)}）"
                )

        if isinstance(value, dict):
            # 递归时传入当前字段的 schema 定义
            errors.extend(_validate_max_items(value, field_schema, current_path))

    return errors


def _validate_minimum_maximum(data: Dict, schema: Dict, path: str = "") -> List[str]:
    """递归检查数值的 minimum/maximum 约束"""
    errors = []
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key

        props = schema.get("properties", {})
        if key in props:
            field_def = props[key]
            if isinstance(value, (int, float)):
                min_val = field_def.get("minimum")
                max_val = field_def.get("maximum")
                if min_val is not None and value < min_val:
                    errors.append(f"{current_path}: {value} 低于最小值 {min_val}")
                if max_val is not None and value > max_val:
                    errors.append(f"{current_path}: {value} 高于最大值 {max_val}")

        if isinstance(value, dict):
            errors.extend(_validate_minimum_maximum(value, schema, current_path))

    return errors


def validate_step_data(step: int, data: Dict) -> Tuple[bool, List[str]]:
    """
    校验某步的输出数据是否符合定义的 Schema

    Args:
        step: 步骤编号 0-6
        data: 待校验数据

    Returns:
        (is_valid, errors)
    """
    schema_key = f"step{step}"
    if schema_key not in SCHEMA_REGISTRY:
        return False, [f"未知步骤: {step}"]

    schema = get_schema(schema_key)
    errors = []

    # 1. 基础结构校验
    if "output" not in data:
        errors.append("缺少 output 字段")

    # 2. 必须字段校验
    required = schema.get("required", [])
    errors.extend(_validate_required_fields(data, required))

    # 3. NaN/Inf 检查
    sanitized = _sanitize_value(data)

    # 4. maxItems 校验（core_variables ≤ 5）
    errors.extend(_validate_max_items(data, schema))

    # 5. 数值范围校验
    errors.extend(_validate_minimum_maximum(data, schema))

    # 6. 枚举值校验
    if "output" in data:
        output = data["output"]
        props = schema["properties"]["output"]["properties"]
        for field_name, field_def in props.items():
            if field_name in output:
                enum_values = field_def.get("enum")
                if enum_values and output[field_name] not in enum_values:
                    errors.append(
                        f"output.{field_name}: '{output[field_name]}' 不在允许值 {enum_values} 中"
                    )

    return len(errors) == 0, errors


def validate_refined_transfer(data: Dict) -> Tuple[bool, List[str]]:
    """
    校验提炼传递数据

    Args:
        data: 待校验的提炼传递数据

    Returns:
        (is_valid, errors)
    """
    schema = get_schema("refined_transfer")
    errors = []

    # 1. schema_version 必填
    if "schema_version" not in data:
        errors.append("缺少 schema_version 字段")

    # 2. step 范围
    if "step" in data and not (0 <= data["step"] <= 6):
        errors.append(f"step 必须在 0-6 之间，当前: {data['step']}")

    # 3. core_variables ≤ 5
    refined = data.get("refined_data", {})
    if "core_variables" in refined:
        cv = refined["core_variables"]
        if len(cv) > 5:
            errors.append(f"core_variables 超出最大数量 5（当前 {len(cv)}）")

    # 4. key_assumptions ≤ 3
    if "key_assumptions" in refined and len(refined["key_assumptions"]) > 3:
        errors.append(f"key_assumptions 超出最大数量 3（当前 {len(refined['key_assumptions'])}）")

    # 5. pending_validations ≤ 3
    if "pending_validations" in refined and len(refined["pending_validations"]) > 3:
        errors.append(f"pending_validations 超出最大数量 3（当前 {len(refined['pending_validations'])}）")

    # 6. confidence 范围
    if "confidence" in refined:
        c = refined["confidence"]
        if not (0 <= c <= 1):
            errors.append(f"confidence 必须在 0-1 之间，当前: {c}")

    # 7. version 格式
    if "schema_version" in data:
        sv = data["schema_version"]
        if not sv.startswith("v") or len(sv.split(".")) != 3:
            errors.append(f"schema_version 格式无效: {sv}，应为 vX.Y.Z")

    return len(errors) == 0, errors


def check_agent_compatibility(sender_version: str, receiver_version: str) -> str:
    """
    检查 Agent 间版本兼容性

    Args:
        sender_version: 发送方版本号
        receiver_version: 接收方版本号

    Returns:
        兼容性结果
    """
    result = check_version_compatibility(sender_version, receiver_version)
    if result == "incompatible":
        logger.warning(
            "Agent 版本不兼容: sender=%s, receiver=%s",
            sender_version, receiver_version
        )
    return result


def sanitize_for_transfer(data: Dict) -> Dict:
    """
    传输前净化数据

    - 去除 NaN/Inf
    - 截断超出 maxItems 的数组
    - 添加 schema_version 和 timestamp
    """
    cleaned = _sanitize_value(data)

    # 截断 core_variables
    if "refined_data" in cleaned:
        rd = cleaned["refined_data"]
        if "core_variables" in rd and len(rd["core_variables"]) > 5:
            rd["core_variables"] = rd["core_variables"][:5]
        if "key_assumptions" in rd and len(rd["key_assumptions"]) > 3:
            rd["key_assumptions"] = rd["key_assumptions"][:3]
        if "pending_validations" in rd and len(rd["pending_validations"]) > 3:
            rd["pending_validations"] = rd["pending_validations"][:3]

    cleaned.setdefault("schema_version", SCHEMA_VERSION)
    cleaned.setdefault("pass_timestamp", datetime.now(timezone.utc).isoformat())

    return cleaned
