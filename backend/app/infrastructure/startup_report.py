import sys
import unicodedata
from typing import Iterable

from .capabilities import get_all_capabilities

_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_RESET = "\033[0m"
_NAME_COL_WIDTH = 16
_STATUS_COL_WIDTH = 8


_CAPABILITY_META = {
    "database": ("数据库", "核心读写能力不可用，服务无法正常提供业务能力"),
    "redis": ("Redis", "缓存、限流、实时消息与异步任务将进入降级模式"),
    "mail": ("邮件", "注册/重置密码等邮件通知不可用"),
    "storage_qiniu": ("对象存储", "图片上传与签名访问不可用"),
    "cache": ("缓存", "将使用进程内缓存，命中率与一致性下降"),
    "limiter": ("限流", "将退化为本地限流，跨实例限流精度下降"),
    "jwt_blocklist": ("JWT 黑名单", "令牌撤销校验降级，安全风控能力下降"),
    "oauth": ("OAuth", "第三方登录不可用"),
    "celery": ("Celery", "异步任务退化为同步执行，吞吐下降"),
    "socketio": ("SocketIO", "实时消息能力受限或不可用"),
}


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _style(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{_RESET}"


def _display_width(text: str) -> int:
    width = 0
    for ch in text:
        width += 2 if unicodedata.east_asian_width(ch) in {"W", "F"} else 1
    return width


def _pad_right_display(text: str, width: int) -> str:
    pad = max(0, width - _display_width(text))
    return text + (" " * pad)


def _pad_left_display(text: str, width: int) -> str:
    pad = max(0, width - _display_width(text))
    return (" " * pad) + text


def _status_row(name: str, state: dict, impact: str) -> str:
    enabled = bool(state.get("enabled"))
    degraded = bool(state.get("degraded"))
    reason = state.get("reason") or ""

    if enabled and not degraded:
        icon = _style("✓", _GREEN)
        name_col = _pad_right_display(name, _NAME_COL_WIDTH)
        status_col = _style(_pad_left_display("已配置", _STATUS_COL_WIDTH), _GREEN)
        tail = f" | {reason}" if reason else ""
        return f"{icon} {name_col} {status_col}{tail}"

    if enabled and degraded:
        icon = _style("✗", _YELLOW)
        name_col = _pad_right_display(name, _NAME_COL_WIDTH)
        status_col = _style(_pad_left_display("已降级", _STATUS_COL_WIDTH), _YELLOW)
        return f"{icon} {name_col} {status_col} | {reason} | 影响: {impact}"

    icon = _style("✗", _RED)
    name_col = _pad_right_display(name, _NAME_COL_WIDTH)
    status_col = _style(_pad_left_display("未配置", _STATUS_COL_WIDTH), _RED)
    detail = reason or "未初始化"
    return f"{icon} {name_col} {status_col} | {detail} | 影响: {impact}"


def print_startup_report(profile: str, capabilities: Iterable[str]) -> None:
    capability_states = get_all_capabilities()
    title = _style(f"[Infra] {profile} 基础设施状态", _CYAN)
    print(title)
    for key in capabilities:
        label, impact = _CAPABILITY_META.get(key, (key, "对应能力不可用"))
        state = capability_states.get(key, {})
        print(_status_row(label, state, impact))
