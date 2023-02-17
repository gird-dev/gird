import os
import pathlib

import gird

path_target = pathlib.Path("target")
ENVVAR = "ENVVAR"


def check_env():
    assert os.environ[ENVVAR] == ENVVAR


gird.rule(
    target=path_target,
    recipe=[
        f"export {ENVVAR}={ENVVAR}",
        check_env,
        f"touch {path_target.resolve()}",
    ],
)
