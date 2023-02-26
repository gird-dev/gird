from itertools import chain
from pathlib import Path

from gird import Phony, rule
from scripts import assert_readme_updated, get_wheel_path, render_readme

WHEEL_PATH = get_wheel_path()

RULE_PYTEST = rule(
    target=Phony("pytest"),
    recipe="pytest",
    help="Run pytest.",
)

RULE_CHECK_FORMATTING = rule(
    target=Phony("check_formatting"),
    recipe=[
        "black --check gird scripts test girdfile.py",
        "isort --check gird scripts test girdfile.py",
    ],
    help="Check formatting with Black & isort.",
)

RULE_CHECK_README_UPDATED = rule(
    target=Phony("check_readme_updated"),
    recipe=assert_readme_updated,
    help="Check that README.md is updated based on README_template.md.",
)

RULES_TEST = [
    RULE_PYTEST,
    RULE_CHECK_FORMATTING,
    RULE_CHECK_README_UPDATED,
]

rule(
    target=Phony("test"),
    deps=RULES_TEST,
    help="\n".join(f"- {rule.help}" for rule in RULES_TEST),
)

rule(
    target=Path("README.md"),
    deps=chain(
        *(Path(path).iterdir() for path in ("scripts", "gird")),
        [Path("girdfile.py")],
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
