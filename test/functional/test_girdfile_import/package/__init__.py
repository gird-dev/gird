import pathlib

PATH_TARGET = pathlib.Path(__file__).parents[1] / "target"


def create_target():
    PATH_TARGET.touch()
