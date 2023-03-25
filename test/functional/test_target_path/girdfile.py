import pathlib

import gird

path_dep = pathlib.Path("dep")
path_target_with_dep = pathlib.Path("target_with_dep")
path_target_without_dep = pathlib.Path("target_without_dep")


def create_dep():
    path_dep.touch()


def create_target_with_dep():
    path_target_with_dep.touch()


def create_target_without_dep():
    path_target_without_dep.touch()


gird.rule(
    target=path_dep,
    recipe=create_dep,
)


gird.rule(
    target=path_target_with_dep,
    deps=path_dep,
    recipe=create_target_with_dep,
)


gird.rule(
    target=path_target_without_dep,
    recipe=create_target_without_dep,
)
