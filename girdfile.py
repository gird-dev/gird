from itertools import chain
from pathlib import Path

from gird import Phony, rule
from scripts import assert_readme_updated, get_wheel_path, render_readme

WHEEL_PATH = get_wheel_path()

RULE_PYTEST = rule(
    target=Phony("pytest"),
    recipe="pytest -n auto --cov=gird --cov-report=xml",
    help="Run pytest & get code coverage report.",
)

RULE_MYPY = rule(
    target=Phony("mypy"),
    recipe="mypy --check-untyped-defs -p gird",
    help="Run mypy.",
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
    RULE_MYPY,
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
        [Path("girdfile.py"), Path("pyproject.toml")],
    ),
    recipe=render_readme,
    help="Render README.md based on README_template.md.",
)

# Wrap the rule to build WHEEL_PATH in a phony rule for simpler invocation.
# Don't include the inner rule in `gird list`.
rule(
    target=Phony("build"),
    deps=rule(
        target=WHEEL_PATH,
        recipe="poetry build --format wheel",
        listed=False,
    ),
    help="Build distribution packages for the current version.",
)
