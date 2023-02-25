"""Common types & type aliases."""

import dataclasses
import pathlib
from typing import Any, Callable, Iterable, Optional, Union

# Type aliases
Target = Union[pathlib.Path, "Phony"]
Dependency = Union[pathlib.Path, "Rule", "gird.dependency.DependencyFunction"]
SubRecipe = Union[str, Callable[[Any], Any]]


class Phony:
    def __init__(self, name):
        if not name:
            raise ValueError("The name of a Phony target must not be empty.")
        self.name = str(name)

    def __str__(self) -> str:
        return self.name


@dataclasses.dataclass
class Rule:
    """Gird rule. For documentation of the fields, see the function '.rule.rule'."""

    target: Target
    deps: Optional[Iterable[Dependency]] = None
    recipe: Optional[Iterable[SubRecipe]] = None
    help: Optional[str] = None
