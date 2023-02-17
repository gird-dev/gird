import pathlib

import gird

path_target_false = pathlib.Path("target_false")
path_target_true = pathlib.Path("target_true")


@gird.dep
def dep_false():
    return False


@gird.dep
def dep_true():
    return True


def create_target_false():
    path_target_false.touch()


def create_target_true():
    path_target_true.touch()


gird.rule(
    target=path_target_false,
    deps=dep_false,
    recipe=create_target_false,
)


gird.rule(
    target=path_target_true,
    deps=dep_true,
    recipe=create_target_true,
)
