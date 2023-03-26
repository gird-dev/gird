import pathlib

import gird

target_name = "target"


class CustomObject:
    def __init__(self, name: str):
        self._name = name

    @property
    def id(self):
        return self._name

    @property
    def timestamp(self):
        return None


def create_target():
    pathlib.Path(target_name).touch()


gird.rule(
    target=CustomObject(target_name),
    recipe=create_target,
)
