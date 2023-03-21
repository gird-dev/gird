"""Common types & type aliases."""

import dataclasses
import os
import pathlib
from typing import Any, Callable, Optional, Tuple, Union

# Type aliases
Target = Union[pathlib.Path, "Phony"]
DependencyInternal = Union[pathlib.Path, "Phony", Callable[[], bool]]
Dependency = Union[DependencyInternal, "Rule"]
SubRecipe = Union[str, Callable[[], Any]]


class Phony:
    """Target that is not a file.

    Parameters
    ----------
    name
        Name of the phony target. Must not be empty.
    """

    def __init__(self, name):
        if not name:
            raise ValueError("The name of a Phony target must not be empty.")
        self.name = str(name)

    def __str__(self) -> str:
        return self.name


@dataclasses.dataclass(frozen=True)
class Rule:
    """Gird rule. For documentation of the fields, see the function '.rule.rule'."""

    target: Target
    deps: Optional[Tuple[DependencyInternal]] = None
    recipe: Optional[Tuple[SubRecipe]] = None
    help: Optional[str] = None
    parallel: bool = True
    listed: bool = True


def format_path(path: pathlib.Path) -> str:
    """Format/normalize a Path to be relative to girdfile's directory, i.e., the
    current working directory.
    """
    return os.path.relpath(path, pathlib.Path.cwd())


def format_target(target: Target) -> str:
    """Format a target."""
    if isinstance(target, Phony):
        node = target.name
    elif isinstance(target, pathlib.Path):
        node = format_path(target)
    else:
        raise ValueError(f"Unsupported target '{target}' of type '{type(target)}'.")
    return node
