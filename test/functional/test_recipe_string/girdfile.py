import pathlib

import gird

path_target = pathlib.Path("target")

gird.rule(
    target=path_target,
    recipe=f"touch {path_target.resolve()}",
)
