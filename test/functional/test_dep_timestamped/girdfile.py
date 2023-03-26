import datetime
import pathlib

import gird

dep_name = "dep"
path_target = pathlib.Path("target")


class CustomObject:
    def __init__(self, name: str):
        self._name = name

    @property
    def id(self):
        return self._name

    @property
    def timestamp(self):
        return datetime.datetime.now()


def create_target():
    path_target.touch()


gird.rule(
    target=path_target,
    deps=CustomObject(dep_name),
    recipe=create_target,
)
