"""Code for processing a rule definition file."""

import importlib.util
import pathlib
import sys
from typing import List, Optional

from .common import Rule


class GirdfileContext:
    """Context manager to control access to GirdfileDefinition during the import
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
    """Define rules by importing a 'girdfile.py'. Set environment variable
    ENV_GIRD_PATH_RUN.
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = girdfile_path.stem
    error = ImportError(f"Could not import girdfile '{girdfile_path}'.")
    spec = importlib.util.spec_from_file_location(module_name, girdfile_path)
    if spec is None:
        raise error
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    with GIRDFILE_CONTEXT:
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise error from e
        rules = GIRDFILE_CONTEXT.rules
    return rules
