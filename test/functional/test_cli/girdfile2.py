import pathlib

import gird

path_target = pathlib.Path("target")


def create_target():
    path_target.touch()


gird.rule(
    target=path_target,
    recipe=create_target,
    help="Create\ntarget.",
)
