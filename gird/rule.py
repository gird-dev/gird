"""The rule function."""
import pathlib
from typing import Iterable, Optional, Union

from .common import Dependency, Rule, SubRecipe, Target
from .girdfile import GIRDFILE_CONTEXT
from .object import Phony, TimeTrackedPath, is_timetracked

# Type aliases for the rule function API
ApiTarget = Union[pathlib.Path, Target]
ApiDependency = Union[pathlib.Path, "Rule", Dependency]


def rule(
    target: ApiTarget,
    deps: Optional[
        Union[
            ApiDependency,
            Iterable[ApiDependency],
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
    listed: bool = True,
) -> Rule:
    """Define & register a Rule.

    Parameters
    ----------
    target
        Target of the rule.
    deps
        Dependencies of the target.
    recipe
        Recipe to update the target. Strings will be executed as shell commands.
    help
        Helptext/description of the rule.
    parallel
        Run the rule in parallel with other rules, i.e., in a separate process.
        Recipes that require input may fail.
    listed
        Include the rule in 'gird list'.

    Notes
    -----

    When invoked, a rule will be run if its target is considered outdated. This
    is the case if the rule
    1) has a `Phony` target,
    2) has a `Path`/`TimeTracked` target that does not exist,
    5) has a `Path`/`TimeTracked` target and a `Path`/`TimeTracked` dependency that is more recent than the target,
    4) has an outdated `Rule`/target as a dependency, or
    3) has a function dependency that returns `True`.

    Rules with outdated targets are run in topological order within the
    dependency graph, i.e., all outdated dependencies are updated before the
    respective targets.

    Python functions used as recipes need to be picklable when used in rules
    defined with `parallel=True` (default). I.e., Lambda functions and locally
    defined functions require `parallel=False`.

    Examples
    --------

    A rule with files as its target & dependency.

    >>> import pathlib
    >>> import gird
    >>> WHEEL = pathlib.Path("package.whl")
    >>>
    >>> RULE_BUILD = gird.rule(
    >>>     target=WHEEL,
    >>>     deps=pathlib.Path("module.py"),
    >>>     recipe="python -m build --wheel",
    >>> )

    A rule with a phony target.

    >>> RULE_TEST = gird.rule(
    >>>     target=gird.Phony("test"),
    >>>     deps=WHEEL,
    >>>     recipe="pytest",
    >>> )

    A rule with other rules as dependencies. Group multiple rules together, and
    set the order of execution between rules.

    >>> gird.rule(
    >>>     target=gird.Phony("all"),
    >>>     deps=[
    >>>         RULE_TEST,
    >>>         RULE_BUILD,
    >>>     ],
    >>> )

    A rule with a Python function recipe. To parameterize a function recipe for
    reusability, use, e.g., `functools.partial`.

    >>> import json
    >>> import functools
    >>> JSON1 = pathlib.Path("file1.json")
    >>> JSON2 = pathlib.Path("file2.json")
    >>>
    >>> def create_target(json_in: pathlib.Path, json_out: pathlib.Path):
    >>>      json_out.write_text(
    >>>          json.dumps(
    >>>              json.loads(
    >>>                  json_in.read_text()
    >>>              ).update(value2="value2")
    >>>          )
    >>>      )
    >>>
    >>> gird.rule(
    >>>     target=JSON2,
    >>>     deps=JSON1,
    >>>     recipe=functools.partial(create_target, JSON1, JSON2),
    >>>     parallel=True,
    >>> )

    A Python function as a dependency to arbitrarily trigger rules. Below, have
    a remote file re-fetched if it has changed.

    >>> def has_remote_changed():
    >>>     return get_checksum_local() != get_checksum_remote()
    >>>
    >>> gird.rule(
    >>>     target=JSON1,
    >>>     deps=has_remote_changed,
    >>>     recipe=fetch_remote,
    >>> )

    Compound recipes for mixing shell commands with Python functions.

    >>> gird.rule(
    >>>     target=JSON1,
    >>>     recipe=[
    >>>         "login",
    >>>         fetch_remote,
    >>>     ],
    >>> )

    Implement the `TimeTracked` protocol for custom targets & dependencies.
    For example, define platform-specific logic to apply dependency tracking on
    a remote file.

    >>> class RemoteFile(gird.TimeTracked):
    >>>     def __init__(self, url: str):
    >>>         self._url = url
    >>>     @property
    >>>     def id(self):
    >>>         return self._url
    >>>     @property
    >>>     def timestamp(self):
    >>>         return get_remote_file_timestamp(self._url)
    >>>
    >>> gird.rule(
    >>>     target=JSON1,
    >>>     deps=RemoteFile(URL),
    >>>     recipe=fetch_remote,
    >>> )

    Flexible rule definition with loops and other constructs.

    >>> RULES = [
    >>>     gird.rule(
    >>>         target=source.with_suffix(".json.gz"),
    >>>         deps=gird.rule(
    >>>             target=source,
    >>>             recipe=functools.partial(fetch_remote, source),
    >>>         ),
    >>>         recipe=f"gzip -k {source.resolve()}",
    >>>     )
    >>>     for source in [JSON1, JSON2]
    >>> ]
    """
    if isinstance(target, pathlib.Path):
        target = TimeTrackedPath(target)
    elif not is_timetracked(target) and not isinstance(target, Phony):
        raise TypeError(f"Invalid target type: '{target}'.")

    if deps is not None:
        if not isinstance(deps, Iterable):
            deps = [deps]

        deps_cast = []
        for dep in deps:
            if isinstance(dep, Rule):
                dep = dep.target
            if isinstance(dep, pathlib.Path):
                dep = TimeTrackedPath(dep)
            elif (
                not callable(dep)
                and not is_timetracked(dep)
                and not isinstance(dep, Phony)
            ):
                raise TypeError(f"Invalid deps type: '{dep}'.")
            deps_cast.append(dep)

        deps = tuple(deps_cast)

    if recipe is not None:
        if not isinstance(recipe, Iterable) or isinstance(recipe, str):
            recipe = [recipe]

        # Ensure recipe is not a single-pass Iterator.
        recipe = list(recipe)

        for subrecipe in recipe:
            if not isinstance(subrecipe, str) and not callable(subrecipe):
                raise TypeError(f"Invalid recipe type: '{subrecipe}'.")

        recipe = tuple(recipe)

    rule_instance = Rule(
        target=target,
        deps=deps,
        recipe=recipe,
        help=help,
        parallel=parallel,
        listed=listed,
    )

    if GIRDFILE_CONTEXT.is_active():
        GIRDFILE_CONTEXT.add_rule(rule_instance)

    return rule_instance
