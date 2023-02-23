import pathlib

import gird

path_dep = pathlib.Path("dep")
path_target = pathlib.Path("target")


def create_dep():
    path_dep.touch()


def create_target():
    path_target.touch()


gird.rule(
    target=path_dep,
    recipe=create_dep,
)


rule = gird.rule(
    target=gird.Phony("phony_target"),
    deps=path_dep,
    recipe=create_target,
)
