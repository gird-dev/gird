"""Common types & type aliases."""

import dataclasses
from typing import Any, Callable, Optional, Union

from .object import Phony, TimeTracked

# Type aliases
Target = Union[Phony, TimeTracked]
Dependency = Union[Callable[[], bool], Target]
SubRecipe = Union[str, Callable[[], Any]]


@dataclasses.dataclass(frozen=True)
class Rule:
    """Gird rule. For documentation of the fields, see the function '.rule.rule'."""

    target: Target
    deps: Optional[tuple[Dependency, ...]] = None
    recipe: Optional[tuple[SubRecipe, ...]] = None
    help: Optional[str] = None
    parallel: bool = True
    listed: bool = True
