import functools
import pathlib
from typing import Callable

import gird

target1 = pathlib.Path("target1")
target2 = pathlib.Path("target2")
target3 = pathlib.Path("target3")
target4 = pathlib.Path("target4")
target5 = pathlib.Path("target5")


def _create_file(path: pathlib.Path):
    path.touch()


def create_file(path: pathlib.Path) -> Callable[[], None]:
    return functools.partial(_create_file, path)


gird.rule(
    target=target1,
    recipe=create_file(target1),
)


gird.rule(
    target=target2,
    deps=target1,
    recipe=create_file(target2),
)


gird.rule(
    target=target3,
    recipe=create_file(target3),
)


gird.rule(
    target=target4,
    deps=target3,
    recipe=create_file(target4),
)


gird.rule(
    target=target5,
    deps=[target2, target3],
    recipe=create_file(target5),
)
