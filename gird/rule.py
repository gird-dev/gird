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
) -> Rule:
    """Define & register a Gird Rule.

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

    Examples
    --------

    A rule with files as its target & dependency. When the rule is invoked, the
    recipe is executed only if the dependency file has been or will be updated,
    or if the target file doesn't exist.

    >>> import pathlib
    >>> import gird
    >>> wheel = pathlib.Path("package.whl")
    >>>
    >>> rule_build = gird.rule(
    >>>     target=wheel,
    >>>     deps=pathlib.Path("module.py"),
    >>>     recipe=f"python -m build --wheel",
    >>> )

    A (phony) rule with no target file. Phony rules are always executed when
    invoked.

    >>> rule_test = gird.rule(
    >>>     target=gird.Phony("test"),
    >>>     deps=wheel,
    >>>     recipe="pytest",
    >>> )

    A rule with other rules as dependencies, to group multiple rules together,
    and to set the order of execution between rules.

    >>> gird.rule(
    >>>     target=gird.Phony("all"),
    >>>     deps=[
    >>>         rule_test,
    >>>         rule_build,
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

    A Python function as a dependency to arbitrarily trigger rules.

    >>> import datetime
    >>> EPOCH = datetime.datetime(2030, 1, 1)
    >>>
    >>> @gird.dep
    >>> def unconditional_until_epoch():
    >>>     \"""Return the "updated" state of this dependency. Here, render a
    >>>     depending target outdated (trigger its recipe to be executed) always
    >>>     before EPOCH.
    >>>     \"""
    >>>     return datetime.datetime.now() < EPOCH
    >>>
    >>> gird.rule(
    >>>     target=JSON2,
    >>>     deps=[JSON1, unconditional_until_epoch],
    >>>     recipe=create_target,
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

    >>> rules = [
    >>>     gird.rule(
    >>>         target=source.with_suffix(".json.gz"),
    >>>         deps=source,
    >>>         recipe=f"gzip -k {source.resolve()}",
    >>>     )
    >>>     for source in [JSON1, JSON2]
    >>> ]
    """
    # From this point onwards deps & recipe must be iterables.
    if deps is not None and not isinstance(deps, Iterable):
        deps = [deps]
    if recipe is not None and (
        not isinstance(recipe, Iterable) or isinstance(recipe, str)
    ):
        recipe = [recipe]

    main_rule = Rule(
        target=target,
        deps=deps,
        recipe=recipe,
        help=help,
    )

    if GIRDFILE_CONTEXT.rules is not None:
        GIRDFILE_CONTEXT.rules.append(main_rule)

    return main_rule
