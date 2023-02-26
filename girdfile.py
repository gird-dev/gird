from itertools import chain
from pathlib import Path

from gird import Phony, rule
from scripts import assert_readme_updated, get_wheel_path, render_readme

WHEEL_PATH = get_wheel_path()

rule_pytest = rule(
    target=Phony("pytest"),
    recipe="pytest",
    help="Run pytest.",
)

rule_check_formatting = rule(
    target=Phony("check_formatting"),
    recipe=[
        "black --check gird scripts test girdfile.py",
        "isort --check gird scripts test girdfile.py",
    ],
    help="Check formatting with Black & isort.",
)

rule_check_readme_updated = rule(
    target=Phony("check_readme_updated"),
    recipe=assert_readme_updated,
    help="Check that README.md is updated based on README_template.md.",
)

rules_test = [
    rule_pytest,
    rule_check_formatting,
    rule_check_readme_updated,
]

rule(
    target=Phony("test"),
    deps=rules_test,
    help="\n".join(f"- {rule.help}" for rule in rules_test),
)

rule(
    target=Path("README.md"),
    deps=list(
        chain(
            *(Path(path).iterdir() for path in ("scripts", "gird")),
            [Path("girdfile.py")],
        ),
    ),
    recipe=render_readme,
    help="Render README.md based on README_template.md.",
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
