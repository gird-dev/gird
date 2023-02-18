"""General utility code"""

import datetime
import inspect
import pathlib
from typing import Callable


def get_python_function_shell_command(
    function: Callable,
) -> str:
    """Get a shell command for running a Python function.

    Parameters
    ----------
    function
        The function to call. The module that contains the function must be
        found in PYTHONPATH.
    """
    module = inspect.getmodule(function)
    module_name = module.__name__
    function_name = function.__name__
    shell_command = (
        f"python -c 'from {module_name} import {function_name}; " f"{function_name}()'"
    )
    return shell_command


def get_path_modified_time(path: pathlib.Path) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime_ns // 1e9)
