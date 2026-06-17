"""
Skill Interface - Skill 接口规范

所有 Mangofolio Skill 必须实现此接口，才能被工作流引擎调用。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SkillInterface(ABC):
    """
    Skill 接口基类

    所有 Skill 必须继承此类并实现以下方法：
    - name: Skill 名称
    - version: Skill 版本
    - execute: 执行逻辑
    - validate_input: 输入验证
    - get_metadata: 元数据
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill 名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Skill 版本"""
        pass

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Skill 逻辑

        Args:
            input_data: 输入数据

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            是否有效
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取 Skill 元数据

        Returns:
            元数据字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__doc__ or "",
            "author": "燃冰 & ant"
        }

    def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使 Skill 可调用

        Args:
            input_data: 输入数据

        Returns:
            执行结果
        """
        if not self.validate_input(input_data):
            raise ValueError(f"输入数据验证失败：{input_data}")

        logger.info(f"🔧 执行 Skill：{self.name} v{self.version}")
        result = self.execute(input_data)
        logger.info(f"✅ Skill 完成：{self.name}")

        return result


class BaseSkill(SkillInterface):
    """
    Skill 基类

    提供通用实现，子类只需覆盖必要方法。
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """默认验证：输入不能为空"""
        return bool(input_data)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """默认实现：返回输入数据"""
        return {
            "skill": self.name,
            "version": self.version,
            "input": input_data,
            "status": "success"
        }


# Skill 注册表
_skill_registry: Dict[str, SkillInterface] = {}


def register_skill(skill: SkillInterface):
    """
    注册 Skill

    Args:
        skill: Skill 实例
    """
    _skill_registry[skill.name] = skill
    logger.info(f"📝 注册 Skill：{skill.name} v{skill.version}")


def get_skill(name: str) -> Optional[SkillInterface]:
    """
    获取 Skill

    Args:
        name: Skill 名称

    Returns:
        Skill 实例
    """
    return _skill_registry.get(name)


def list_skills() -> Dict[str, str]:
    """
    列出所有已注册 Skill

    Returns:
        {名称：版本}
    """
    return {name: skill.version for name, skill in _skill_registry.items()}


def clear_registry():
    """清空注册表"""
    _skill_registry.clear()


# 便捷装饰器
def skill(name: str, version: str = "1.0.0"):
    """
    Skill 装饰器

    用法：
    ```python
    @skill("my_skill", "1.0.0")
    class MySkill(BaseSkill):
        def execute(self, input_data):
            return {"result": "done"}
    ```
    """
    def decorator(cls):
        cls.name = property(lambda self: name)
        cls.version = property(lambda self: version)

        # 自动注册
        instance = cls()
        register_skill(instance)

        return cls
    return decorator


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 创建示例 Skill
    @skill("test_skill", "1.0.0")
    class TestSkill(BaseSkill):
        def execute(self, input_data):
            return {"result": "test passed", "input": input_data}

    # 测试调用
    skill_instance = get_skill("test_skill")
    if skill_instance:
        result = skill_instance({"test": "data"})
        print(f"结果：{result}")

    # 列出所有 Skill
    print(f"\n已注册 Skill：{list_skills()}")
