from pathlib import Path

from gird import Phony, rule
from scripts import get_wheel_path, render_readme

WHEEL_PATH = get_wheel_path()

rule_pytest = rule(
    target=Phony("pytest"),
    recipe="pytest",
)

rule_assert_formatting = rule(
    target=Phony("assert_formatting"),
    recipe=[
        "black --check gird scripts girdfile.py",
        "isort --check gird scripts girdfile.py",
    ],
)

rule(
    target=Phony("tests"),
    deps=[
        rule_pytest,
        rule_assert_formatting,
    ],
    help="Run tests & other checks.",
)

rule(
    target=Path("README.md"),
    deps=Path("scripts/README_template.md"),
    recipe=render_readme,
    help="Render README.md based on scripts/README.md",
)

rule(
    target=WHEEL_PATH,
    recipe="poetry build --format wheel",
    help="Build distribution packages for the current version.",
)

rule(
    target=Phony("publish"),
    deps=WHEEL_PATH,
    recipe=f"twine upload --repository gird {WHEEL_PATH}",
    help="Publish packages of the current version to PyPI.",
)
