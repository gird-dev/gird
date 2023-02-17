"""General utility code"""

import datetime
import inspect
import os
import pathlib
from typing import Callable, Iterable

from gird.common import Rule
from gird.girddir import get_girddir_tmp


def get_python_function_shell_command(
    function: Callable,
    cwd: pathlib.Path,
) -> str:
    """Get a shell command for running a Python function.

    Parameters
    ----------
    function
        The function to call.
    cwd
        The directory from which the command is run.
    """
    module_path = pathlib.Path(inspect.getfile(function))
    module_dir = os.path.relpath(module_path.parent, cwd)
    module_name = module_path.stem
    function_name = function.__name__
    shell_command = (
        f"(cd {module_dir}; "
        f"python -c 'from {module_name} import {function_name}; "
        f"{function_name}()')"
    )
    return shell_command


def get_path_modified_time(path: pathlib.Path) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime_ns // 1e9)


def convert_cli_target_for_make(
    target: str,
    rules: Iterable[Rule],
) -> str:
    """Convert a target name given as a CLI argument to be used as the target
    for Make.

    For example, if the CLI argument is a path to a file, the path must be
    modified to be relative to the directory of the Makefiles.
    """
    makefile_dir = get_girddir_tmp()
    current_dir = pathlib.Path.cwd()
    target_path = (current_dir / target).resolve()
    for rule in rules:
        if (
            isinstance(rule.target, pathlib.Path)
            and rule.target.resolve() == target_path
        ):
            target_for_make = os.path.relpath(target_path, makefile_dir)
            break
    else:
        target_for_make = None

    target_for_make = target_for_make or target

    return target_for_make
