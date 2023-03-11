"""Code for defining rules."""

from typing import Iterable, Optional, Union

from .common import Dependency, Rule, SubRecipe, Target
from .girdfile import GIRDFILE_CONTEXT


def rule(
    target: Target,
    deps: Optional[
        Union[
            Dependency,
            Iterable[Dependency],
        ]
    ] = None,
    recipe: Optional[
        Union[
            SubRecipe,
            Iterable[SubRecipe],
        ]
    ] = None,
    help: Optional[str] = None,
    parallel: bool = True,
) -> Rule:
    """Define & register a Rule.

    Parameters
    ----------
    target
        Target of the rule.
    deps
        Dependencies of the target.
    recipe
        Recipe to update the target.
    help
        Helptext/description of the rule.
    parallel
        Run the rule in parallel with other rules, i.e., in a separate process.
        Recipes that require input may fail.

    Examples
    --------

    A rule with files as its target & dependency. When the rule is invoked, the
    recipe is executed only if the dependency file has been or will be updated,
    or if the target file doesn't exist.

    >>> import pathlib
    >>> import gird
    >>> WHEEL = pathlib.Path("package.whl")
    >>>
    >>> RULE_BUILD = gird.rule(
    >>>     target=WHEEL,
    >>>     deps=pathlib.Path("module.py"),
    >>>     recipe="python -m build --wheel",
    >>> )

    A rule with a phony target (not a file). The rule is always executed when
    invoked.

    >>> RULE_TEST = gird.rule(
    >>>     target=gird.Phony("test"),
    >>>     deps=WHEEL,
    >>>     recipe="pytest",
    >>> )

    A rule with other rules as dependencies, to group multiple rules together,
    and to set the order of execution between rules.

    >>> gird.rule(
    >>>     target=gird.Phony("all"),
    >>>     deps=[
    >>>         RULE_TEST,
    >>>         RULE_BUILD,
    >>>     ],
    >>> )

    A rule with a Python function recipe.

    >>> import json
    >>> JSON1 = pathlib.Path("file1.json")
    >>> JSON2 = pathlib.Path("file2.json")
    >>>
    >>> def create_target():
    >>>      JSON2.write_text(
    >>>          json.dumps(
    >>>              json.loads(
    >>>                  JSON1.read_text()
    >>>              ).update(value2="value2")
    >>>          )
    >>>      )
    >>>
    >>> gird.rule(
    >>>     target=JSON2,
    >>>     deps=JSON1,
    >>>     recipe=create_target,
    >>> )

    A Python function as a dependency to arbitrarily trigger rules. Below, have
    a local file re-fetched if a remote version is updated.

    >>> def is_remote_newer():
    >>>     return get_timestamp_local() < get_timestamp_remote()
    >>>
    >>> gird.rule(
    >>>     target=JSON1,
    >>>     deps=is_remote_newer,
    >>>     recipe=fetch_remote,
    >>> )

    Compound recipes for, e.g., setup & teardown.

    >>> gird.rule(
    >>>     target=JSON1,
    >>>     recipe=[
    >>>         "login",
    >>>         fetch_remote,
    >>>     ],
    >>> )

    Define rules in a loop, or however you like.

    >>> RULES = [
    >>>     gird.rule(
    >>>         target=source.with_suffix(".json.gz"),
    >>>         deps=source,
    >>>         recipe=f"gzip -k {source.resolve()}",
    >>>     )
    >>>     for source in [JSON1, JSON2]
    >>> ]
    """
    # Turn deps into tuple of Path or Phony instances, not Rules.
    if deps is not None:
        if not isinstance(deps, Iterable):
            deps = [deps]
        deps_unruly = []
        for dep in deps:
            if isinstance(dep, Rule):
                dep = dep.target
            deps_unruly.append(dep)
        deps = tuple(deps_unruly)

    # Turn recipe into a tuple if it isn't.
    if recipe is not None:
        if not isinstance(recipe, Iterable) or isinstance(recipe, str):
            recipe = [recipe]
        recipe = tuple(recipe)

    rule = Rule(
        target=target,
        deps=deps,
        recipe=recipe,
        help=help,
        parallel=parallel,
    )

    if GIRDFILE_CONTEXT.rules is not None:
        GIRDFILE_CONTEXT.rules.append(rule)

    return rule
