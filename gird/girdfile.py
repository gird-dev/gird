"""Code for processing a rule definition file."""

import importlib.util
import os
import pathlib
import sys
from typing import List, Optional

from .common import Rule


class GirdfileContext:
    """Context manager to control access to a Rule register during the import
    of a girdfile.py.
    """

    def __init__(self):
        self.rules: Optional[List[Rule]] = None

    def __enter__(self):
        if self.rules is not None:
            raise RuntimeError("This GirdfileContext is already active.")
        self.rules = []

    def __exit__(self, *args):
        self.rules = None


# GirdfileContext instance to be activated when importing a girdfile.py.
GIRDFILE_CONTEXT = GirdfileContext()


def import_girdfile(girdfile_path: pathlib.Path) -> List[Rule]:
    """Define rules by importing a 'girdfile.py'. Add the file's directory to
    sys.path.
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = girdfile_path.stem
    current_dir = pathlib.Path.cwd()
    error_message = (
        f"Could not import girdfile '{os.path.relpath(girdfile_path, current_dir)}'."
    )
    if not girdfile_path.exists():
        raise ImportError(error_message)
    spec = importlib.util.spec_from_file_location(module_name, girdfile_path)
    if spec is None:
        raise ImportError(error_message)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # Append the girdfile's directory to PYTHONPATH to enable imports in the file.
    sys.path.append(str(pathlib.Path(girdfile_path.parent).resolve()))
    with GIRDFILE_CONTEXT:
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(error_message + f" Reason: {e.args[0]}") from e
        rules = GIRDFILE_CONTEXT.rules
    return rules
