[//]: # (This README.md is autogenerated from README_template.md with the script
         render_readme.py)

[![pypi](https://img.shields.io/pypi/v/gird)](https://pypi.org/project/gird/)
![python](https://img.shields.io/pypi/pyversions/gird)
![license](https://img.shields.io/github/license/gird-dev/gird)
[![codecov](https://codecov.io/gh/gird-dev/gird/branch/master/graph/badge.svg?token=CVLPXCSHZF)](https://codecov.io/gh/gird-dev/gird)

# Gird

Gird is a lightweight & general-purpose [Make][make]-like build tool & task
runner for Python.

[make]: https://en.wikipedia.org/wiki/Make_(software)

### Features

- A simple, expressive, and intuitive rule definition and execution scheme very
  close to that of Make.
- Configuration in Python, allowing straightforward and familiar usage, without
  the need for a dedicated rule definition syntax.
- Ability to take advantage of Python's flexibility and possibility to easily
  integrate with Python libraries and tools.
- Emphasis on API simplicity & ease of use.

### Example use cases

- Data science & data analytics workflows.
- Portable CI tasks.
- Less rule-heavy application build setups. (Build time overhead may become
  noticeable with thousands of rules.)
- Any project with tasks that need to be executed automatically when some
  dependencies are updated.

## Installation

Install Gird from PyPI with `pip install gird`, or from sources with
`pip install .`.

Gird requires Python version 3.9 or newer, and is supported on Linux & macOS.

## Usage

Define "rules" in *girdfile.py*. Depending on the composition of a rule
definition, a rule can, for example,

- define a recipe to run a task, e.g., to update a target file,
- define prerequisites for the target, such as dependency files or other rules,
  and
- use Python functions for more complex dependency & recipe functionality.

A rule is invoked by `gird {target}`. To list rules, run `gird list`.

### Example girdfile.py

This is the girdfile.py of the project itself.

```python
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
        [Path("girdfile.py"), Path("pyproject.toml")],
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
```

Respective output from `gird list`:

```
pytest
    Run pytest & get code coverage report.
check_formatting
    Check formatting with Black & isort.
check_readme_updated
    Check that README.md is updated based on README_template.md.
test
    - Run pytest & get code coverage report.
    - Check formatting with Black & isort.
    - Check that README.md is updated based on README_template.md.
README.md
    Render README.md based on README_template.md.
dist/gird-2.0.2-py3-none-any.whl
    Build distribution packages for the current version.
publish
    Publish packages of the current version to PyPI.
```

### Example rules

#### A rule with files as its target & dependency

```python
import pathlib
import gird
WHEEL = pathlib.Path("package.whl")

RULE_BUILD = gird.rule(
    target=WHEEL,
    deps=pathlib.Path("module.py"),
    recipe="python -m build --wheel",
)
```

#### A rule with a phony target (not a file)

```python
RULE_TEST = gird.rule(
    target=gird.Phony("test"),
    deps=WHEEL,
    recipe="pytest",
)
```

#### A rule with other rules as dependencies

Group multiple rules together, and set the order of execution between rules.

```python
gird.rule(
    target=gird.Phony("all"),
    deps=[
        RULE_TEST,
        RULE_BUILD,
    ],
)
```

#### A rule with a Python function recipe

To parameterize a function recipe for reusability, use, e.g., `functools.partial`.

```python
import json
import functools
JSON1 = pathlib.Path("file1.json")
JSON2 = pathlib.Path("file2.json")

def create_target(json_in: pathlib.Path, json_out: pathlib.Path):
     json_out.write_text(
         json.dumps(
             json.loads(
                 json_in.read_text()
             ).update(value2="value2")
         )
     )

gird.rule(
    target=JSON2,
    deps=JSON1,
    recipe=functools.partial(create_target, JSON1, JSON2),
    parallel=True,
)
```

#### A Python function as a dependency to arbitrarily trigger rules

Below, have a remote file re-fetched if it has been updated.

```python
def is_remote_newer():
    return get_timestamp_local() < get_timestamp_remote()

gird.rule(
    target=JSON1,
    deps=is_remote_newer,
    recipe=fetch_remote,
)
```

#### Compound recipes for mixing shell commands with Python functions

```python
gird.rule(
    target=JSON1,
    recipe=[
        "login",
        fetch_remote,
    ],
)
```

#### Flexible rule definition with loops and other constructs

```python
RULES = [
    gird.rule(
        target=source.with_suffix(".json.gz"),
        deps=gird.rule(
            target=source,
            recipe=functools.partial(fetch_remote, source),
        ),
        recipe=f"gzip -k {source.resolve()}",
    )
    for source in [JSON1, JSON2]
]

```
