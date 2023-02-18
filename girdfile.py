import pathlib

import tomli

import gird


def get_wheel_path() -> pathlib.Path:
    with open(pathlib.Path("pyproject.toml"), "rb") as f:
        toml = tomli.load(f)
    name = toml["tool"]["poetry"]["name"].replace(".", "_")
    version = toml["tool"]["poetry"]["version"]
    return pathlib.Path("dist") / f"{name}-{version}-py3-none-any.whl"


WHEEL_PATH = get_wheel_path()

rule_pytest = gird.rule(
    target=gird.Phony("pytest"),
    recipe="pytest",
)

gird.rule(
    target=gird.Phony("tests"),
    deps=[
        rule_pytest,
    ],
    help="Run tests & other checks.",
)

gird.rule(
    target=WHEEL_PATH,
    recipe="poetry build --format wheel",
    help="Build distribution packages for the current version.",
)

gird.rule(
    target=gird.Phony("publish"),
    deps=WHEEL_PATH,
    recipe=f"twine upload {WHEEL_PATH}",
    help="Publish packages of the current version to PyPI.",
)
