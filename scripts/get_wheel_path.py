import pathlib

import tomli


def get_wheel_path() -> pathlib.Path:
    """Get the Path of a wheel that would be generated for the current project
    version.
    """
    with open(pathlib.Path("pyproject.toml"), "rb") as f:
        toml = tomli.load(f)
    name = toml["tool"]["poetry"]["name"].replace(".", "_")
    version = toml["tool"]["poetry"]["version"]
    return pathlib.Path("dist") / f"{name}-{version}-py3-none-any.whl"
