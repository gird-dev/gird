"""Code for processing a rule definition file."""

import importlib.util
import os
import pathlib
import sys
from typing import Optional

from .common import Rule


class GirdfileContext:
    """Context manager to control access to a Rule register during the import
    of a girdfile.py.
    """

    _not_active_error = RuntimeError(f"This GirdfileContext is not active.")

    def __init__(self):
        self._rules: Optional[list[Rule]] = None
        self._target_ids: Optional[set[str]] = None

    def __enter__(self):
        if self._rules is not None:
            raise RuntimeError("This GirdfileContext is already active.")
        self._rules = []
        self._target_ids = set()

    def __exit__(self, *args):
        self._rules = None
        self._target_ids = None

    def is_active(self) -> bool:
        """Is this GirdfileContext active, i.e., can Rules be added with add_rule()."""
        return self._rules is not None and self._target_ids is not None

    def add_rule(self, rule: Rule):
        """Register a Rule with this GirdfileContext. Raise a ValueError if the
        Rule can't be added, and a RuntimeError if the GirdfileContext is not
        active.
        """
        target_id = rule.target.id
        if self._rules is not None and self._target_ids is not None:
            if target_id in self._target_ids:
                raise ValueError(
                    f"A Rule with the target name '{target_id}' has "
                    "already been registered."
                )
            self._rules.append(rule)
            self._target_ids.add(target_id)
        else:
            raise self._not_active_error

    def get_rules(self) -> list[Rule]:
        """Get the Rules registered with this GirdfileContext."""
        if self._rules is None:
            raise self._not_active_error
        return self._rules


# GirdfileContext instance to be activated when importing a girdfile.py.
GIRDFILE_CONTEXT = GirdfileContext()


def import_girdfile(girdfile_path: pathlib.Path) -> list[Rule]:
    """Define rules by importing a 'girdfile.py'. Add the file's directory to
    sys.path.
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = girdfile_path.stem
    girdfile_str = os.path.relpath(girdfile_path, pathlib.Path.cwd())
    if not girdfile_path.exists():
        raise ImportError(f"{girdfile_str} does not exist.")
    spec = importlib.util.spec_from_file_location(module_name, girdfile_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Module spec cannot be loaded from {girdfile_str}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # Append the girdfile's directory to PYTHONPATH to enable imports in the file.
    sys.path.append(str(pathlib.Path(girdfile_path.parent).resolve()))
    with GIRDFILE_CONTEXT:
        spec.loader.exec_module(module)
        rules = GIRDFILE_CONTEXT.get_rules()
    return rules
