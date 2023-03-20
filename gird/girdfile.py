"""Code for processing a rule definition file."""

import importlib.util
import os
import pathlib
import sys
from typing import List, Optional, Set

from .common import Rule, format_target


class GirdfileContext:
    """Context manager to control access to a Rule register during the import
    of a girdfile.py.
    """

    def __init__(self):
        self._rules: Optional[List[Rule]] = None
        self._targets_formatted: Optional[Set[str]] = None

    def __enter__(self):
        if self._rules is not None:
            raise RuntimeError("This GirdfileContext is already active.")
        self._rules = []
        self._targets_formatted = set()

    def __exit__(self, *args):
        self._rules = None
        self._targets_formatted = None

    def is_active(self) -> bool:
        """Is this GirdfileContext active, i.e., can Rules be added with add_rule()."""
        return self._rules is not None

    def add_rule(self, rule: Rule):
        """Register a Rule with this GirdfileContext. Raise a ValueError if the
        Rule can't be added, and a RuntimeError if the GirdfileContext is not
        active.
        """
        if self._rules is not None:
            target_formatted = format_target(rule.target)
            if target_formatted in self._targets_formatted:
                raise ValueError(
                    f"A Rule with the target name '{target_formatted}' has "
                    "already been registered."
                )
            self._rules.append(rule)
            self._targets_formatted.add(target_formatted)
        else:
            raise RuntimeError(f"This {type(self).__name__} is not active.")

    def get_rules(self) -> Optional[List[Rule]]:
        """Get the Rules registered with this GirdfileContext."""
        return self._rules


# GirdfileContext instance to be activated when importing a girdfile.py.
GIRDFILE_CONTEXT = GirdfileContext()


def import_girdfile(girdfile_path: pathlib.Path) -> List[Rule]:
    """Define rules by importing a 'girdfile.py'. Add the file's directory to
    sys.path.
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = girdfile_path.stem
    girdfile_str = os.path.relpath(girdfile_path, pathlib.Path.cwd())
    if not girdfile_path.exists():
        raise ImportError(f"{girdfile_str} does not exist.")
    spec = importlib.util.spec_from_file_location(module_name, girdfile_path)
    if spec is None:
        raise ImportError(f"Module spec cannot be loaded from {girdfile_str}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # Append the girdfile's directory to PYTHONPATH to enable imports in the file.
    sys.path.append(str(pathlib.Path(girdfile_path.parent).resolve()))
    with GIRDFILE_CONTEXT:
        spec.loader.exec_module(module)
        rules = GIRDFILE_CONTEXT.get_rules()
    return rules
