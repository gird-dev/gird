import pathlib

import gird

path_target = pathlib.Path("target")


def create_target():
    path_target.touch()


def raise_exception():
    raise Exception("Exception")


gird.rule(
    target=path_target,
    recipe=create_target,
    help="Create\ntarget.",
)


gird.rule(
    target=gird.Phony("target_with_error"),
    recipe=raise_exception,
)
