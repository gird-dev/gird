"""General utility code"""

import datetime
import pathlib


def get_path_modified_time(path: pathlib.Path) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime_ns / 1e9)
