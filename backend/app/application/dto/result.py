from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PageResult(Generic[T]):
    data: T
    total: int


@dataclass(frozen=True)
class ListResult(Generic[T]):
    data: T


@dataclass(frozen=True)
class ItemResult(Generic[T]):
    data: T


@dataclass(frozen=True)
class ActionResult:
    ok: bool = True
    message: str = "success"
    data: Any | None = None
