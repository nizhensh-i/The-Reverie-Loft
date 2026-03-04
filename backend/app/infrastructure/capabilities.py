"""
基础设施能力注册表。
用于记录各组件的可用性，供依赖组件降级决策使用。
"""

from copy import deepcopy
from datetime import datetime

_CAPABILITIES = {}


def set_capability(name: str, enabled: bool, degraded: bool = False, reason: str = ""):
    _CAPABILITIES[name] = {
        "enabled": bool(enabled),
        "degraded": bool(degraded),
        "reason": reason or "",
        "updated_at": datetime.utcnow().isoformat(),
    }


def capability_enabled(name: str, default: bool = True) -> bool:
    state = _CAPABILITIES.get(name)
    if state is None:
        return default
    return bool(state.get("enabled"))


def get_capability(name: str):
    state = _CAPABILITIES.get(name)
    return deepcopy(state) if state else None


def get_all_capabilities():
    return deepcopy(_CAPABILITIES)
