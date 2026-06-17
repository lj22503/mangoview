"""
统一配置管理

支持 .env（API Key） + config.yaml（数据源偏好）
"""

import os
import yaml
from typing import Dict, Any, Optional

CONFIG_DIR = os.path.expanduser('~/.investment_framework')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yaml')
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

DEFAULT_CONFIG = {
    'data_sources': {
        'priority': ['tencent', 'sina', 'eastmoney'],
        'tencent': {'enabled': True},
        'sina': {'enabled': True},
        'eastmoney': {'enabled': True},
        'tushare': {'enabled': False},
        'qveris': {'enabled': True},
    },
    'api_keys': {
        'tushare': {'token': '', 'enabled': False},
        'qveris': {'token': '', 'enabled': True},
    },
    'cache': {
        'default_ttl': 300,
        'use_file_cache': True,
    },
    'fallback': {
        'cache_ttl': 300,
        'timeout': 10,
    },
}


def _deep_merge(base: Dict, update: Dict) -> None:
    for k, v in update.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def _load_env() -> Dict[str, str]:
    """加载 .env 文件"""
    env_vars = {}
    for p in [ENV_PATH, os.path.join(os.path.dirname(__file__), '..', '.env')]:
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip()
            break
    return env_vars


def load_config(config_path: str = None) -> Dict[str, Any]:
    """加载配置（config.yaml + .env 合并）"""
    path = config_path or CONFIG_PATH
    config = DEFAULT_CONFIG.copy()

    # 加载 yaml
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                yaml_cfg = yaml.safe_load(f) or {}
            _deep_merge(config, yaml_cfg)
        except Exception:
            pass

    # 加载 .env 中的 API Key
    env = _load_env()
    if env.get('TUSHARE_TOKEN'):
        config['api_keys']['tushare']['token'] = env['TUSHARE_TOKEN']
        config['api_keys']['tushare']['enabled'] = True
    if env.get('QVERIS_API_KEY'):
        config['api_keys']['qveris']['token'] = env['QVERIS_API_KEY']
        config['api_keys']['qveris']['enabled'] = True

    # 环境变量优先
    if os.environ.get('TUSHARE_TOKEN'):
        config['api_keys']['tushare']['token'] = os.environ['TUSHARE_TOKEN']
        config['api_keys']['tushare']['enabled'] = True
    if os.environ.get('QVERIS_API_KEY'):
        config['api_keys']['qveris']['token'] = os.environ['QVERIS_API_KEY']
        config['api_keys']['qveris']['enabled'] = True

    return config


def get_api_key(provider: str, config: Dict = None) -> Optional[str]:
    """获取 API Key"""
    if config is None:
        config = load_config()
    api_keys = config.get('api_keys', {})
    prov_cfg = api_keys.get(provider, {})
    if not prov_cfg.get('enabled', False):
        return None
    token = prov_cfg.get('token', '')
    return token if token else None


def save_config(config: Dict[str, Any], config_path: str = None) -> None:
    """保存配置"""
    path = config_path or CONFIG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    os.chmod(path, 0o600)
