"""
Mangofolio 六步分析 JSON Schema 定义

每步定义输入/输出的 JSON Schema，用于 Agent 间数据契约校验。
版本：v1.0.0
"""

from typing import Dict, Any

SCHEMA_VERSION = "1.0.0"

# ── Step 0：校验 ──────────────────────────────────────────────

STEP0_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step0_Verify",
    "type": "object",
    "properties": {
        "step": {"const": 0},
        "input": {
            "type": "object",
            "properties": {
                "data_source": {"type": "string"},
                "source_type": {
                    "type": "string",
                    "enum": ["一手", "二手", "官方", "媒体", "机构分析"]
                },
                "interest_relevance": {
                    "type": "string",
                    "enum": ["直接利益", "间接利益", "无明显利益"]
                },
                "historical_credibility": {
                    "type": "string",
                    "enum": ["高", "中", "低", "未知"]
                }
            },
            "required": ["data_source", "source_type"]
        },
        "output": {
            "type": "object",
            "properties": {
                "source_credibility": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "bias_types": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "final_rating": {
                    "type": "string",
                    "enum": ["直接使用", "需验证后使用", "仅作参考", "不可用"]
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["source_credibility", "final_rating", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 1：拆解 ──────────────────────────────────────────────

STEP1_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step1_Decompose",
    "type": "object",
    "properties": {
        "step": {"const": 1},
        "input": {
            "type": "object",
            "properties": {
                "raw_data": {"type": "object"}
            },
            "required": ["raw_data"]
        },
        "output": {
            "type": "object",
            "properties": {
                "core_variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {},
                            "importance": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "LOW"]
                            },
                            "variable_type": {
                                "type": "string",
                                "enum": ["直接", "间接", "可观测", "潜变量"]
                            }
                        },
                        "required": ["name", "importance"]
                    },
                    "maxItems": 5
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "key_assumptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3
                },
                "pending_validations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3
                }
            },
            "required": ["core_variables", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 2：传导 ──────────────────────────────────────────────

STEP2_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step2_Transmission",
    "type": "object",
    "properties": {
        "step": {"const": 2},
        "input": {
            "type": "object",
            "properties": {
                "core_variables": {
                    "type": "array",
                    "items": {"type": "object"},
                    "minItems": 1
                }
            },
            "required": ["core_variables"]
        },
        "output": {
            "type": "object",
            "properties": {
                "causal_chain": {"type": "string"},
                "feedback_loops": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["正反馈", "负反馈"]
                            },
                            "description": {"type": "string"}
                        },
                        "required": ["type", "description"]
                    }
                },
                "blockage_points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["location", "reason"]
                    }
                },
                "transmission_strength": {
                    "type": "string",
                    "enum": ["强", "中", "弱"]
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["causal_chain", "transmission_strength", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 3：历史 ──────────────────────────────────────────────

STEP3_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step3_History",
    "type": "object",
    "properties": {
        "step": {"const": 3},
        "input": {
            "type": "object",
            "properties": {
                "core_variables": {
                    "type": "array",
                    "items": {"type": "object"},
                    "minItems": 1
                },
                "causal_chain": {"type": "string"}
            },
            "required": ["core_variables"]
        },
        "output": {
            "type": "object",
            "properties": {
                "similar_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "time": {"type": "string"},
                            "location": {"type": "string"},
                            "core_features": {"type": "string"},
                            "outcome": {"type": "string"}
                        },
                        "required": ["time", "core_features", "outcome"]
                    }
                },
                "similarity": {
                    "type": "object",
                    "properties": {
                        "variable_match": {"type": "number", "minimum": 0, "maximum": 1},
                        "context_match": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "key_differences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "difference": {"type": "string"},
                            "potential_impact": {"type": "string"}
                        }
                    }
                },
                "transferable_patterns": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["similar_cases", "similarity", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 4：情景 ──────────────────────────────────────────────

STEP4_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step4_Scenario",
    "type": "object",
    "properties": {
        "step": {"const": 4},
        "input": {
            "type": "object",
            "properties": {
                "causal_chain": {"type": "string"},
                "historical_cases": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["causal_chain"]
        },
        "output": {
            "type": "object",
            "properties": {
                "base_case": {
                    "type": "object",
                    "properties": {
                        "probability": {"type": "string", "enum": ["高", "中", "低"]},
                        "assumptions": {"type": "array", "items": {"type": "string"}},
                        "path": {"type": "string"},
                        "impact": {"type": "string"}
                    },
                    "required": ["probability", "path", "impact"]
                },
                "bull_case": {
                    "type": "object",
                    "properties": {
                        "probability": {"type": "string"},
                        "trigger": {"type": "string"},
                        "path": {"type": "string"},
                        "impact": {"type": "string"}
                    }
                },
                "bear_case": {
                    "type": "object",
                    "properties": {
                        "probability": {"type": "string"},
                        "trigger": {"type": "string"},
                        "path": {"type": "string"},
                        "impact": {"type": "string"}
                    }
                },
                "key_bifurcation": {
                    "type": "object",
                    "properties": {
                        "variable": {"type": "string"},
                        "threshold": {},
                        "direction": {"type": "string"}
                    }
                },
                "consistency_check": {"type": "boolean"},
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["base_case", "consistency_check", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 5：行动 ──────────────────────────────────────────────

STEP5_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step5_Action",
    "type": "object",
    "properties": {
        "step": {"const": 5},
        "input": {
            "type": "object",
            "properties": {
                "scenarios": {
                    "type": "object",
                    "properties": {
                        "base_case": {"type": "object"},
                        "bull_case": {"type": "object"},
                        "bear_case": {"type": "object"}
                    }
                }
            },
            "required": ["scenarios"]
        },
        "output": {
            "type": "object",
            "properties": {
                "base_action": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["买入", "卖出", "持有", "观望"]
                        },
                        "object": {"type": "string"},
                        "logic": {"type": "string"},
                        "intensity": {
                            "type": "string",
                            "enum": ["观察", "轻仓", "重仓", "对冲"]
                        },
                        "time_window": {"type": "string"}
                    },
                    "required": ["direction", "intensity"]
                },
                "bull_action": {
                    "type": "object",
                    "properties": {
                        "intensity": {"type": "string"},
                        "logic": {"type": "string"}
                    }
                },
                "bear_action": {
                    "type": "object",
                    "properties": {
                        "intensity": {"type": "string"},
                        "logic": {"type": "string"}
                    }
                },
                "constraint_check": {
                    "type": "object",
                    "properties": {
                        "risk_capacity": {"type": "boolean"},
                        "fund_size": {"type": "boolean"},
                        "execution": {"type": "boolean"}
                    }
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["base_action", "constraint_check", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── Step 6：失效 ──────────────────────────────────────────────

STEP6_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Step6_Invalidation",
    "type": "object",
    "properties": {
        "step": {"const": 6},
        "input": {
            "type": "object",
            "properties": {
                "scenarios": {"type": "object"},
                "assumptions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["assumptions"]
        },
        "output": {
            "type": "object",
            "properties": {
                "logical_conditions": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "variable_thresholds": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "variable": {"type": "string"},
                            "threshold": {},
                            "direction": {"type": "string"},
                            "effect": {"type": "string"}
                        },
                        "required": ["variable", "threshold", "direction"]
                    }
                },
                "time_boundary": {
                    "type": "object",
                    "properties": {
                        "valid_period": {"type": "string"},
                        "reassess_after": {"type": "number"}
                    }
                },
                "exit_signals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "signal": {"type": "string"},
                            "observable": {"type": "boolean"},
                            "trigger_action": {"type": "string"}
                        },
                        "required": ["signal", "trigger_action"]
                    }
                },
                "monitoring_frequency": {
                    "type": "string",
                    "enum": ["每日", "每周", "每月", "季度", "事件驱动"]
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["exit_signals", "monitoring_frequency", "confidence"]
        }
    },
    "required": ["step", "input", "output"]
}

# ── 提炼传递 Schema ───────────────────────────────────────────

REFINED_TRANSFER_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RefinedTransfer",
    "type": "object",
    "properties": {
        "schema_version": {
            "type": "string",
            "pattern": "^v\\d+\\.\\d+\\.\\d+$"
        },
        "from_agent": {"type": "string"},
        "to_agent": {"type": "string"},
        "step": {
            "type": "integer",
            "minimum": 0,
            "maximum": 6
        },
        "refined_data": {
            "type": "object",
            "properties": {
                "core_variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {},
                            "importance": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "LOW"]
                            }
                        },
                        "required": ["name", "importance"]
                    },
                    "maxItems": 5
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "key_assumptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3
                },
                "pending_validations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3
                },
                "confidence_label": {
                    "type": "string",
                    "enum": ["高", "中", "低"]
                }
            },
            "required": ["core_variables", "confidence"]
        },
        "pass_timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["schema_version", "step", "refined_data", "pass_timestamp"]
}

# ── 聚合信号 Schema ───────────────────────────────────────────

AGGREGATE_SIGNAL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AggregateSignal",
    "type": "object",
    "properties": {
        "aggregate_signal": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["BULLISH", "BEARISH", "NEUTRAL"]
                },
                "intensity": {
                    "type": "string",
                    "enum": ["STRONG", "MEDIUM", "WEAK"]
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "component_signals": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "conflict_detected": {"type": "boolean"},
                "conflict_resolution": {"type": "string"}
            },
            "required": ["direction", "intensity", "confidence"]
        }
    },
    "required": ["aggregate_signal"]
}

# ── 版本管理 ──────────────────────────────────────────────────

SCHEMA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "step0": {"schema": STEP0_SCHEMA, "version": SCHEMA_VERSION},
    "step1": {"schema": STEP1_SCHEMA, "version": SCHEMA_VERSION},
    "step2": {"schema": STEP2_SCHEMA, "version": SCHEMA_VERSION},
    "step3": {"schema": STEP3_SCHEMA, "version": SCHEMA_VERSION},
    "step4": {"schema": STEP4_SCHEMA, "version": SCHEMA_VERSION},
    "step5": {"schema": STEP5_SCHEMA, "version": SCHEMA_VERSION},
    "step6": {"schema": STEP6_SCHEMA, "version": SCHEMA_VERSION},
    "refined_transfer": {"schema": REFINED_TRANSFER_SCHEMA, "version": SCHEMA_VERSION},
    "aggregate_signal": {"schema": AGGREGATE_SIGNAL_SCHEMA, "version": SCHEMA_VERSION},
}


def get_schema(step_key: str) -> Dict[str, Any]:
    """按 key 获取 Schema"""
    entry = SCHEMA_REGISTRY.get(step_key)
    if not entry:
        raise KeyError(f"未知 Schema key: {step_key}，可用：{list(SCHEMA_REGISTRY.keys())}")
    return entry["schema"]


def list_schemas() -> Dict[str, str]:
    """列出所有可用 Schema 及版本"""
    return {k: v["version"] for k, v in SCHEMA_REGISTRY.items()}


def check_version_compatibility(sender_version: str, receiver_version: str) -> str:
    """
    检查版本兼容性

    Returns:
        "compatible" | "compatible_with_warnings" | "incompatible"
    """
    try:
        s_parts = [int(x) for x in sender_version.lstrip("v").split(".")]
        r_parts = [int(x) for x in receiver_version.lstrip("v").split(".")]
    except (ValueError, IndexError):
        return "incompatible"

    # 大版本不同 = 不兼容
    if s_parts[0] != r_parts[0]:
        return "incompatible"
    # 同大版本，发送方小版本 <= 接收方 = 兼容
    if s_parts[1] <= r_parts[1]:
        return "compatible"
    # 同大版本，发送方小版本 > 接收方 = 可能不识别额外字段
    return "compatible_with_warnings"
