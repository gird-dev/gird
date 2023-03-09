import pathlib

import gird

path_target = pathlib.Path("target")
path_target_with_error = pathlib.Path("target_with_error")


def create_target():
    path_target.touch()


def create_target_with_error():
    raise Exception("Exception")


gird.rule(
    target=path_target,
    recipe=create_target,
    help="Create\ntarget.",
)


gird.rule(
    target=path_target_with_error,
    recipe=create_target_with_error,
)
