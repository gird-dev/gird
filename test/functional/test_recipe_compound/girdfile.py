import pathlib

import gird

PATH_TARGET = pathlib.Path("target")


def create_target():
    PATH_TARGET.write_text("line1\n")


gird.rule(
    target=PATH_TARGET,
    recipe=[
        create_target,
        f"echo 'line2' >> {PATH_TARGET.resolve()}",
    ],
)
