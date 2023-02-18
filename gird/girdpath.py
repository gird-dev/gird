"""Code for managing the directory used by Gird."""

import os
import pathlib

ENV_GIRD_PATH = "GIRD_PATH"
ENV_GIRD_PATH_RUN = "GIRD_PATH_RUN"


def assert_dir(path: pathlib.Path):
    if not path.is_dir():
        raise RuntimeError(f"'{path}' is not a directory.")


def init_gird_path(gird_path: pathlib.Path, girdfile: pathlib.Path):
    """Remove temporary files from gird_path and make the functions get_gird_path,
    get_gird_path_tmp, & get_gird_path_run work in this & all subprocesses.
    """
    os.environ[ENV_GIRD_PATH] = str(gird_path.resolve())
    os.environ[ENV_GIRD_PATH_RUN] = str(girdfile.parent.resolve())

    if gird_path.exists():
        assert_dir(gird_path)
    else:
        gird_path.mkdir()

    gird_path_tmp = get_gird_path_tmp()
    if gird_path_tmp.exists():
        assert_dir(gird_path_tmp)
    else:
        gird_path_tmp.mkdir()
    for path in gird_path_tmp.iterdir():
        if path.is_file():
            path.unlink()


def get_gird_path() -> pathlib.Path:
    """Get directory for "permanent" & temporary files stored by Gird."""
    if ENV_GIRD_PATH not in os.environ:
        raise RuntimeError(f"Environment variable '{ENV_GIRD_PATH}' not defined.")
    return pathlib.Path(os.environ[ENV_GIRD_PATH])


def get_gird_path_tmp() -> pathlib.Path:
    """Get directory for temporary files stored by Gird."""
    return get_gird_path() / "tmp"


def get_gird_path_run() -> pathlib.Path:
    """Get directory where all recipes will be run, i.e., the directory with
    girdfile.py.
    """
    if ENV_GIRD_PATH_RUN not in os.environ:
        raise RuntimeError(f"Environment variable '{ENV_GIRD_PATH_RUN}' not defined.")
    return pathlib.Path(os.environ[ENV_GIRD_PATH_RUN])
