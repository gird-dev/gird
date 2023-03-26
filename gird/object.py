import datetime
import os
import pathlib
from typing import Any, Optional, Protocol


class Object(Protocol):
    """Protocol for objects with an identifier."""

    @property
    def id(self) -> str:
        """Unique identifier of the object."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.id


class TimeTracked(Object, Protocol):
    """Protocol for targets & dependencies that have their outdatedness
    determined by timestamps.
    """

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        """Timestamp of the object, e.g., time of modification. None if the
        object doesn't exist.
        """
        raise NotImplementedError


class Phony(Object):
    """Object that never exists. When used as a target of a rule, causes the
    rule to always be executed when invoked.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def id(self) -> str:
        return self._name


class TimeTrackedPath(TimeTracked):
    def __init__(self, path: pathlib.Path):
        self._path = path

    @property
    def id(self) -> str:
        return os.path.relpath(self._path, pathlib.Path.cwd())

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        if not self._path.exists():
            return None
        return datetime.datetime.fromtimestamp(self._path.stat().st_mtime_ns / 1e9)


def is_timetracked(instance: Any):
    """Does an instance have the members required by the TimeTracked protocol.
    Use this as a lighter version of isinstance(instance, TimeTracked).
    """
    return hasattr(instance, "id") and hasattr(instance, "timestamp")
