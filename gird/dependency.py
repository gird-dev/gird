"""Code for using functions as rule dependencies."""

import os
from typing import Callable

from .girdpath import get_gird_path_tmp


class DependencyFunction:
    """Decorator for using a function as a dependency in a rule.

    The function should return `True` when the dependency is "updated", i.e.,
    when the dependency should cause the targets depending on it to also be
    updated by their rules.
    """

    def __init__(self, function: Callable[[], bool]):
        self._function = function

    def __call__(self):
        """Call the function & create a tag file.

        If the function returns True, the tag file will be set as "updated" by
        setting its modified time to the time of calling. If it returns False,
        the modified time will be set to "0".

        The function will be called and the tag file created/modified only on
        the first invocation of this method.
        """
        tag_path = self.tag_path
        if not tag_path.exists():
            tag_path.touch()
            updated = self.function()
            if not updated:
                os.utime(tag_path, (0, 0))

    @property
    def function(self):
        return self._function

    @property
    def name(self):
        return self.function.__name__

    @property
    def tag_path(self):
        return get_gird_path_tmp() / self.name


# "Decorative" alias
dep = DependencyFunction
