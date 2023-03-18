import functools
import pathlib

import gird

path_target = pathlib.Path("target")
path_target_partial = pathlib.Path("target_partial")
path_target_local = pathlib.Path("target_local")
path_target_lambda = pathlib.Path("target_lambda")


def create_target():
    path_target.touch()


def create_target_partial(path: pathlib.Path):
    path.touch()


def get_create_target_local():
    def create_target_local():
        path_target_local.touch()

    return create_target_local


create_target_lambda = lambda: path_target_lambda.touch()


gird.rule(
    target=path_target,
    recipe=create_target,
)


gird.rule(
    target=path_target_partial,
    recipe=functools.partial(create_target_partial, path_target_partial),
)


gird.rule(
    target=path_target_local,
    recipe=get_create_target_local(),
    parallel=False,
)


gird.rule(
    target=path_target_lambda,
    recipe=create_target_lambda,
    parallel=False,
)
