"""
Mangofolio 六步执行器

三层（天时/地利/人和）共用的六步模板方法。
每步执行：校验 → 执行 → 完成检查 → 回退或进入下一步。
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from .completion_checker import check_step, LayerType
from .fallback_manager import FallbackTracker, determine_fallback, should_skip_step
from ..contract.refined_transfer import (
    build_refined_output, merge_refined_inputs, build_fallback_packet
)
from ..contract.schema_validator import validate_step_data

logger = logging.getLogger(__name__)

# 步骤名称映射
STEP_NAMES = {
    0: "校验", 1: "拆解", 2: "传导",
    3: "历史", 4: "情景", 5: "行动", 6: "失效",
}


class StepContext:
    """六步执行上下文"""

    def __init__(
        self,
        layer: LayerType,
        raw_input: Dict,
        step_handlers: Dict[int, Callable],
        layer_name: str = "",
    ):
        self.layer = layer
        self.raw_input = raw_input
        self.step_handlers = step_handlers
        self.layer_name = layer_name or layer.value

        self.current_step: int = 0
        self.results: Dict[int, Dict] = {}
        self.refined_packets: Dict[int, Dict] = {}
        self.fallbacks: List[Dict] = []
        self.skipped_steps: List[int] = []
        self.completed: bool = False
        self.error: Optional[str] = None
        self.tracker = FallbackTracker()

    def get_previous_refined(self, step: int) -> Optional[Dict]:
        """获取上一步的提炼传递数据"""
        if step > 0 and (step - 1) in self.refined_packets:
            return self.refined_packets[step - 1]
        return None


class StepExecutor:
    """六步执行器"""

    def __init__(self):
        self.execution_log: List[Dict] = []

    def execute(
        self,
        layer: LayerType,
        raw_input: Dict,
        step_handlers: Dict[int, Callable],
        layer_name: str = "",
        start_step: int = 0,
        end_step: int = 6,
    ) -> Dict:
        """
        执行完整的六步分析流程

        Args:
            layer: 分析层类型
            raw_input: 原始输入数据
            step_handlers: 每步的处理器映射 {step: handler_func}
            layer_name: 层名称（日志用）
            start_step: 起始步骤
            end_step: 结束步骤

        Returns:
            {
                "layer": str,
                "completed": bool,
                "results": {step: output},
                "refined_packets": {step: refined_data},
                "fallbacks": [...],
                "skipped_steps": [...],
                "final_signal": Dict or None,
                "error": str or None,
            }
        """
        ctx = StepContext(layer, raw_input, step_handlers, layer_name)
        logger.info("=" * 50)
        logger.info("[%s] 六步分析开始", layer_name)

        step = start_step
        while start_step <= step <= end_step and not ctx.completed:
            step_name = STEP_NAMES.get(step, f"Step{step}")
            logger.info("-" * 40)
            logger.info("[%s Step %d] %s", layer_name, step, step_name)

            try:
                # 1. 构建输入（含上一步精炼数据）
                prev_refined = ctx.get_previous_refined(step)
                step_input = merge_refined_inputs(step, prev_refined, raw_input)

                # 2. 执行处理器
                handler = step_handlers.get(step)
                if handler is None:
                    raise ValueError(f"Step {step} 未注册处理器")

                step_output = handler(step_input)
                if not isinstance(step_output, dict):
                    raise TypeError(f"Step {step} 处理器返回类型错误: {type(step_output)}")

                # 3. Schema 校验
                is_valid, schema_errors = validate_step_data(step, {
                    "step": step,
                    "input": step_input,
                    "output": step_output,
                })
                if not is_valid:
                    logger.warning(
                        "[%s Step %d] Schema 校验警告: %s",
                        layer_name, step, schema_errors
                    )

                # 4. 完成标准检查
                passed, fail_reason = check_step(layer, step, step_output)

                if not passed:
                    logger.info(
                        "[%s Step %d] 完成标准未通过: %s",
                        layer_name, step, fail_reason
                    )

                    # 尝试回退
                    fallback_to, fallback_action = determine_fallback(
                        layer, step, fail_reason, ctx.tracker
                    )

                    if fallback_to is not None:
                        ctx.fallbacks.append({
                            "from_step": step,
                            "to_step": fallback_to,
                            "reason": fail_reason,
                            "action": fallback_action,
                        })
                        logger.info(
                            "[%s Step %d] → 回退到 Step %d",
                            layer_name, step, fallback_to
                        )
                        step = fallback_to
                        continue

                    # 判断是否跳过
                    if should_skip_step(layer, step, fail_reason):
                        ctx.skipped_steps.append(step)
                        logger.info(
                            "[%s Step %d] 跳过（%s）",
                            layer_name, step, fail_reason
                        )
                    else:
                        # 标记为通过但附警告
                        step_output["_warning"] = fail_reason

                # 5. 构建提炼传递包
                core_vars = step_output.get("core_variables", [])
                confidence = step_output.get("confidence", 0.5)
                assumptions = step_output.get("key_assumptions", [])
                pending = step_output.get("pending_validations", [])

                refined = build_refined_output(
                    step=step,
                    core_variables=core_vars,
                    confidence=confidence,
                    key_assumptions=assumptions,
                    pending_validations=pending,
                    from_agent=f"{layer_name}-step{step}",
                    to_agent=f"{layer_name}-step{step+1}" if step < 6 else "aggregator",
                )

                # 6. 存储结果
                ctx.results[step] = step_output
                ctx.refined_packets[step] = refined

                logger.info(
                    "[%s Step %d] ✅ 完成 (conf=%.2f, vars=%d)",
                    layer_name, step, confidence, len(core_vars)
                )

                step += 1

            except Exception as e:
                logger.error("[%s Step %d] 异常: %s", layer_name, step, str(e))
                ctx.error = f"Step {step} 执行异常: {str(e)}"
                break

        # 执行结束
        ctx.completed = (step > end_step and ctx.error is None)

        # 构建最终信号
        final_signal = self._build_final_signal(ctx) if ctx.completed else None

        result = {
            "layer": layer_name,
            "completed": ctx.completed,
            "results": ctx.results,
            "refined_packets": ctx.refined_packets,
            "fallbacks": ctx.fallbacks,
            "skipped_steps": ctx.skipped_steps,
            "final_signal": final_signal,
            "error": ctx.error,
        }

        # 记录日志
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "layer": layer_name,
            "completed": ctx.completed,
            "steps_done": list(ctx.results.keys()),
            "fallbacks": len(ctx.fallbacks),
            "error": ctx.error,
        })

        logger.info(
            "[%s] 六步分析 %s（%d/%d 步完成, %d 次回退）",
            layer_name,
            "✅ 完成" if ctx.completed else "❌ 未完成",
            len(ctx.results), 7,
            len(ctx.fallbacks),
        )

        return result

    def _build_final_signal(self, ctx: StepContext) -> Optional[Dict]:
        """从执行结果构建最终信号"""
        # 取 Step 5（行动）的结果作为信号基础
        step5 = ctx.results.get(5, {})
        step6 = ctx.results.get(6, {})

        if not step5:
            return None

        base_action = step5.get("base_action", {})
        exit_signals = step6.get("exit_signals", [])

        return {
            "layer": ctx.layer_name,
            "direction": base_action.get("direction", "观望"),
            "intensity": base_action.get("intensity", "观察"),
            "confidence": step5.get("confidence", 0),
            "step5_exit_signals": len(exit_signals),
            "key_variables": self._collect_key_variables(ctx),
            "key_assumptions": self._collect_assumptions(ctx),
        }

    def _collect_key_variables(self, ctx: StepContext) -> List[Dict]:
        """汇总所有步骤的核心变量（去重）"""
        seen = set()
        variables = []
        for step in sorted(ctx.results.keys()):
            for var in ctx.results[step].get("core_variables", []):
                name = var.get("name", "") if isinstance(var, dict) else str(var)
                if name and name not in seen:
                    seen.add(name)
                    variables.append(var)
        return variables[:5]

    def _collect_assumptions(self, ctx: StepContext) -> List[str]:
        """汇总关键假设"""
        seen = set()
        assumptions = []
        for step in sorted(ctx.results.keys()):
            for a in ctx.results[step].get("key_assumptions", []):
                if a not in seen:
                    seen.add(a)
                    assumptions.append(a)
        return assumptions[:3]
