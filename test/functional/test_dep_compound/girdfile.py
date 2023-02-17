import pathlib

import gird

path_dep_path = pathlib.Path("dep_path")
path_dep_rule = pathlib.Path("dep_rule")
path_target_false = pathlib.Path("target_false")
path_target_true = pathlib.Path("target_true")


@gird.dep
def dep_false():
    return False


@gird.dep
def dep_true():
    return True


def create_dep_rule():
    path_dep_rule.touch()


rule_dep = gird.rule(
    target=path_dep_rule,
    recipe=create_dep_rule,
)


def create_target_false():
    path_target_false.touch()


def create_target_true():
    path_target_true.touch()


gird.rule(
    target=path_target_false,
    deps=[
        path_dep_path,
        rule_dep,
        dep_false,
    ],
    recipe=create_target_false,
)


gird.rule(
    target=path_target_true,
    deps=[
        path_dep_path,
        rule_dep,
        dep_true,
    ],
    recipe=create_target_true,
)
