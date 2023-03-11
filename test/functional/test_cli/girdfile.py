import pathlib

import gird

path_target = pathlib.Path("target")
path_target_with_error1 = pathlib.Path("target_with_error1")
path_target_with_error2 = pathlib.Path("target_with_error2")


def create_target():
    path_target.touch()


def create_target_with_error1():
    raise Exception("Exception")


gird.rule(
    target=path_target,
    recipe=create_target,
    help="Create\ntarget.",
)


gird.rule(
    target=path_target_with_error1,
    recipe=create_target_with_error1,
)


gird.rule(
    target=path_target_with_error2,
    recipe="exit 1",
)
