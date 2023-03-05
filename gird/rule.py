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
    parallel: bool = False,
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
        Run the rule in parallel, when invoked as the main rule (`gird <target>`).
        All dependencies of the rule will also be run in parallel. Output will
        be buffered per each target. (E.g., colored output may be turned off by
        some programs.) Recipes that require input may fail due to temporary
        input stream invalidation.

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

    >>> @gird.dep
    >>> def is_remote_newer():
    >>>     return get_timestamp_local() < get_timestamp_remote()
    >>>
    >>> gird.rule(
    >>>     target=JSON1,
    >>>     deps=is_remote_newer,
    >>>     recipe=fetch_remote,
    >>> )

    Compound recipes for, e.g., setup & teardown. All subrecipes of a rule are
    run in a single shell instance.

    >>> gird.rule(
    >>>     target=JSON2,
    >>>     deps=JSON1,
    >>>     recipe=[
    >>>         "export VALUE2=value2",
    >>>         create_target,
    >>>         "unset VALUE2",
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
    # From this point onwards deps & recipe must be iterables.
    if deps is not None:
        if not isinstance(deps, Iterable):
            deps = [deps]
        # Using List to turn possible Iterators to non-Iterators.
        deps = list(deps)
    if recipe is not None:
        if not isinstance(recipe, Iterable) or isinstance(recipe, str):
            recipe = [recipe]
        recipe = list(recipe)

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
