import pathlib

import gird

path_dep = pathlib.Path("dep")
path_target = pathlib.Path("target")
path_target_no_rule = pathlib.Path("target_no_rule")
phony_no_rule = gird.Phony("phony_no_rule")


def create_dep():
    path_dep.touch()


def create_target():
    path_target.touch()


def create_target_no_rule():
    path_target_no_rule.touch()


rule_dep = gird.rule(
    target=gird.Phony("dep"),
    recipe=create_dep,
)


gird.rule(
    target=path_target,
    deps=rule_dep,
    recipe=create_target,
)


gird.rule(
    target=path_target_no_rule,
    deps=phony_no_rule,
    recipe=create_target_no_rule,
)
