from pathlib import Path

from gird import Phony, rule
from scripts import assert_readme_updated, get_wheel_path, render_readme

WHEEL_PATH = get_wheel_path()

rule_pytest = rule(
    target=Phony("pytest"),
    recipe="pytest",
    help="Run pytest.",
)

rule_assert_formatting = rule(
    target=Phony("assert_formatting"),
    recipe=[
        "black --check gird scripts girdfile.py",
        "isort --check gird scripts girdfile.py",
    ],
    help="Check formatting with Black & isort.",
)

rule_assert_readme_updated = rule(
    target=Phony("assert_readme_updated"),
    recipe=assert_readme_updated,
    help="Check that README.md is updated based on README_template.md.",
)

deps_tests = [
    rule_pytest,
    rule_assert_formatting,
    rule_assert_readme_updated,
]

rule(
    target=Phony("tests"),
    deps=deps_tests,
    help="\n".join(f"- {rule.help}" for rule in deps_tests),
)

rule(
    target=Path("README.md"),
    deps=Path("scripts/README_template.md"),
    recipe=render_readme,
    help="Render README.md based on scripts/README_template.md.",
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
