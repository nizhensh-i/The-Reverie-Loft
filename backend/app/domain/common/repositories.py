from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PageEntities(Generic[T]):
    items: Sequence[T]
    total: int
