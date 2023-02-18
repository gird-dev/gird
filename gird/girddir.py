"""Code for managing the directory used by Gird."""

import os
import pathlib

ENV_GIRDDIR = "GIRDDIR"


def assert_dir(path: pathlib.Path):
    if not path.is_dir():
        raise RuntimeError(f"'{path}' is not a directory.")


def init_girddir(girddir: pathlib.Path):
    """Remove temporary files from girddir and make the functions get_girddir &
    get_girddir_tmp work in this & all subprocesses.
    """
    os.environ[ENV_GIRDDIR] = str(girddir.resolve())

    if girddir.exists():
        assert_dir(girddir)
    else:
        girddir.mkdir()

    girddir_tmp = get_girddir_tmp()
    if girddir_tmp.exists():
        assert_dir(girddir_tmp)
    else:
        girddir_tmp.mkdir()
    for path in girddir_tmp.iterdir():
        if path.is_file():
            path.unlink()


def get_girddir() -> pathlib.Path:
    """Get directory for "permanent" & temporary files stored by Gird."""
    if ENV_GIRDDIR not in os.environ:
        raise RuntimeError(f"Environment variable '{ENV_GIRDDIR}' not defined.")
    return pathlib.Path(os.environ[ENV_GIRDDIR])


def get_girddir_tmp() -> pathlib.Path:
    """Get directory for temporary files stored by Gird."""
    return get_girddir() / "tmp"
